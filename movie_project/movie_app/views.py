from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect,Http404,HttpResponseForbidden,FileResponse
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.urls import reverse
from django.db import connection, transaction,IntegrityError
from django.conf import settings
from django.template.defaultfilters import urlencode
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model,update_session_auth_hash
from django.contrib.auth.backends import ModelBackend
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test,login_required
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.files.uploadedfile import UploadedFile
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db.models import Q,Avg,F, ExpressionWrapper, DateTimeField
from django.db.models.functions import Now
from .models import Movie, ProductionCompany, Person,MovieGenre, MovieGenreAssociation, SecurityQA, LoginRecord,Role, RoleActorMovie,Comment,Rating,Narration
from .forms import ProductionCompanyForm,MovieForm,PersonForm,RegisterForm,ChangePasswordForm,SecurityQAForm, PasswordResetForm,UsernameForm,CommentForm,RatingForm,RoleForm, RoleActorMovieForm, NarrationForm
from functools import wraps
import json,os,uuid
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
import string
from datetime import timedelta


def is_admin(user):
    return user.is_authenticated and user.is_staff


def admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_staff:

            return function(request, *args, **kwargs)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': '缺少权限,需要管理员权限'}, status=403)
            else:
                messages.error(request, "缺少权限,需要管理员权限")
                return redirect(request.META.get('HTTP_REFERER', '/')) # 重定向到来源页面
    return wrap


def super_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:

            return function(request, *args, **kwargs)
        else:
            messages.error(request, "缺少权限,需要超级管理员权限")
         
            return redirect(request.META.get('HTTP_REFERER', '/'))  # 重定向到来源页面

    return wrap


@login_required
def home(request):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_active_login_records', [request.user.id])
            count=cursor.fetchall()
        if count[0][0] > 1:
            messages.warning(request, 'There are other active logins detected. Please consider changing your password for security reasons if you do not recognize them.')

    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")

    return render(request, 'home.html')


@login_required
@admin_required
@csrf_exempt
@transaction.atomic
def add_production_company(request):
    if request.method == 'POST':
        form = ProductionCompanyForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            city = form.cleaned_data['city']
            description = form.cleaned_data['company_description']
            # 调用存储过程添加生产公司
            try:
                with connection.cursor() as cursor:
                    cursor.callproc('add_productioncompany', [name, city, description])
            except Exception as e:
                # Handle any exceptions or errors
                messages.error(request,f"Error : {e}")
            return redirect('list_production_companies')    # 重定向到公司一览页面
    else:
        form = ProductionCompanyForm()
    return render(request, 'add_production_company.html', {'form': form})


@login_required
@transaction.atomic
def list_production_companies(request):
    name = request.GET.get('name', '')
    page = request.GET.get('page', 1)
    limit = 10  # 每页显示的公司数量

    
    with connection.cursor() as cursor:
        
        if name:
            print(name,'n')
            cursor.callproc('search_production_companies', [name,""])
        else:
            cursor.callproc('get_all_production_companies')
        results = cursor.fetchall()
        company_id = None
        company = {}
        get_company = []
        for result in results:
            company_id = result[0]
            company = {
                'company_id': company_id,
                'name': result[1],
                'city': result[2],
                'company_description': result[3],
                'movies': []
            }
            get_company.append(company)

    companies = []

    
            # Fetch movies produced by this company
    
    for company in get_company:
        with connection.cursor() as cursor:
            cursor.callproc('get_movies_by_production_company', [company['company_id']])
            for movie in cursor.fetchall():
                company['movies'].append({
                    'movie_id': movie[0],
                    'moviename': movie[1],
                    'length': movie[2],
                    'releaseyear': movie[3],
                    'average_rating': round(2*movie[4],1)
                })
            
            companies.append(company)
    paginator = Paginator(companies, limit)
    try:
        companies_page = paginator.page(page)
    except PageNotAnInteger:
        companies_page = paginator.page(1)
    except EmptyPage:
        companies_page = paginator.page(paginator.num_pages)

    return render(request, 'list_production_companies.html', {'companies': companies_page})


@login_required
@admin_required
@transaction.atomic
def update_production_company(request, company_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        city = request.POST.get('city')
        description = request.POST.get('company_description')
        try:
            with connection.cursor() as cursor:
                cursor.callproc('update_production_company', [company_id, name, city, description])
        except Exception as e:
            # Handle any exceptions or errors
            messages.error(request,f"Error : {e}")
        return redirect('list_production_companies')

    company = None
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_company_by_id', [company_id])
            company = cursor.fetchone()
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")
    if company is None:
        return redirect('list_production_companies')

    return render(request, 'update_production_company.html', {
        'id': company[0],
        'name': company[1],
        'city': company[2],
        'company_description': company[3],
    })


@login_required
@admin_required
@transaction.atomic
def delete_production_company(request, company_id):
    if request.method == 'POST':
        try:

            with connection.cursor() as cursor:
                cursor.callproc('get_movies_by_company', [company_id])
                movies = cursor.fetchall()
            for movie in movies:
                with connection.cursor() as cursor:
                    movie_id = movie[0]
                    # 删除视频文件
                    movie_instance = Movie.objects.get(pk=movie_id)
                    delete_video_file(movie_instance.resource_link)
                    # 调用存储过程删除电影及其关联数据
                    cursor.callproc('delete_movie', [movie_id])
            with connection.cursor() as cursor:
                # 删除出品公司
                cursor.callproc('delete_production_company', [company_id])
            
            messages.success(request, 'Production company and all associated movies deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False,'error': f'Error: {str(e)}'}, status=200)
    return JsonResponse({'success': True, 'error': '无错误'}, status=200)


@login_required
@transaction.atomic
def search_production_companies(request):
    name = request.GET.get('name', '')
    city = request.GET.get('city', '')
    try:
        with connection.cursor() as cursor:
            cursor.callproc('search_production_companies', [name, city])
            companies = cursor.fetchall()
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")

    company_list = []
    for company in companies:
        company_list.append({
            'company_id': company[0],
            'name': company[1],
            'city': company[2],
            'company_description': company[3],
        })
    page = request.GET.get('page', 1)
    limit = 10  # 每页显示的公司数量
    paginator = Paginator(company_list, limit)
    try:
        companies_page = paginator.page(page)
    except PageNotAnInteger:
        companies_page = paginator.page(1)
    except EmptyPage:
        companies_page = paginator.page(paginator.num_pages)

    return render(request, 'list_production_companies.html', {'companies': companies_page})


@login_required
@admin_required
@transaction.atomic
def add_movie(request):
    if request.method == 'POST':
        try:
            form = MovieForm(request.POST, request.FILES,is_update=False)
            if form.is_valid():
                # 从表单中获取数据
                moviename = form.cleaned_data['moviename']
                length = form.cleaned_data['length']
                releaseyear = form.cleaned_data['releaseyear']
                plot_summary = form.cleaned_data['plot_summary']
                production_company_id = form.cleaned_data['production_company'].company_id
                # 如果上传了视频文件，验证文件格式是否为mp4
                resource_link = None
                if 'video_file' in request.FILES:
                    video_file = request.FILES['video_file']
                    if not video_file.name.endswith('.mp4'):
                        raise ValidationError("Only MP4 files are allowed.")
                    
                    # Optionally, you can also check the MIME type
                    if video_file.content_type != 'video/mp4':
                        raise ValidationError("The uploaded file is not a valid MP4 video.")
                    
                    resource_link = save_video_file(video_file)
                # 调用存储过程插入电影数据
                with connection.cursor() as cursor:
                    cursor.callproc('add_movie', [moviename, length, releaseyear, plot_summary, resource_link, production_company_id])
                    cursor.callproc('get_last_insert_movie_id')
                    movie_id = cursor.fetchone()[0]
                # 获取选中的导演
                director_ids = request.POST.get('directors', '')
                # 插入导演数据
                if director_ids:
                    director_ids_list = director_ids.split(',')
                    for director_id in director_ids_list:
                        with connection.cursor() as cursor:
                            cursor.callproc('add_director_movie', [movie_id, int(director_id)])
                # 添加类型关联
                genre_ids = request.POST.getlist('genres')
                for genre_id in genre_ids:
                    with connection.cursor() as cursor:
                        cursor.callproc('add_movie_genre_association', [movie_id, genre_id])
        except Exception as e:
            # Handle any exceptions or errors
            messages.error(request,f"Error : {e}")
        return redirect('list_movies')
    else:
        form = MovieForm(is_update=False)
    try:
        # 获取出品公司分页数据
        with connection.cursor() as cursor:
            cursor.callproc('get_all_production_companies')
            production_companies = cursor.fetchall()
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")
    production_companies_list = [
        {'company_id': company[0], 'name': company[1], 'city': company[2], 'company_description': company[3]}
        for company in production_companies
    ]
    production_companies_paginator = Paginator(production_companies_list, 10)
    production_company_page = request.GET.get('production_company_page', 1)
    try:
        production_companies_page = production_companies_paginator.page(production_company_page)
    except PageNotAnInteger:
        production_companies_page = production_companies_paginator.page(1)
    except EmptyPage:
        production_companies_page = production_companies_paginator.page(production_companies_paginator.num_pages)

    try:
        # 获取所有电影类型
        with connection.cursor() as cursor:
            cursor.callproc('select_all_genre')
            genres = cursor.fetchall()
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")
    
    return render(request, 'add_movie.html', {
        'form': form,
        'genres': genres,
        'production_companies_page': production_companies_page
    })


@login_required
@transaction.atomic
def search_person_by_name(request):
    try:
        query = request.GET.get('query', '')
        with connection.cursor() as cursor:
            cursor.callproc('search_person_by_name', [query])
            results = cursor.fetchall()
        directors = [{'person_id': result[0], 'name': result[1]} for result in results]
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")
    return JsonResponse(directors, safe=False)


@transaction.atomic
def save_video_file(video_file):
    unique_filename = str(uuid.uuid4()) + '.mp4'
    file_path = os.path.join(settings.MEDIA_ROOT, 'videos', unique_filename)
    with open(file_path, 'wb+') as destination:
        for chunk in video_file.chunks():
            destination.write(chunk)
    return os.path.join(settings.MEDIA_URL, 'videos', unique_filename)


@transaction.atomic
def get_int_or_default(value, default):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
    



@login_required
@transaction.atomic
def list_movies(request):
    # Get all production companies for the search form
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_all_production_companies')
            production_companies = cursor.fetchall()
    
        production_companies_list = [
            {'company_id': company[0], 'name': company[1], 'city': company[2], 'company_description': company[3]}
            for company in production_companies
        ]

        # Get all genres for the search form
        with connection.cursor() as cursor:
            cursor.callproc('select_all_genre')
            genres = cursor.fetchall()
        genres_list = [
            {'genre_id': genre[0], 'genre_name': genre[1]}
            for genre in genres
        ]

        # Initialize min_rating and max_rating
        min_rating = 0
        max_rating = 10

        # Handle search requests
        if request.method == 'GET' and (
            'keyword' in request.GET or
            'min_length' in request.GET or
            'max_length' in request.GET or
            'min_releaseyear' in request.GET or
            'max_releaseyear' in request.GET or
            'production_company' in request.GET or
            'genre' in request.GET or
            'min_rating' in request.GET or
            'max_rating' in request.GET
        ):
            keyword = request.GET.get('keyword', '')
            min_length = min(get_int_or_default(request.GET.get('min_length'), 0),9999)
            max_length = min(get_int_or_default(request.GET.get('max_length'), 9999),9999)
            min_releaseyear = min(get_int_or_default(request.GET.get('min_releaseyear'), 0),9999)
            max_releaseyear = min(get_int_or_default(request.GET.get('max_releaseyear'), 9999),9999)
            production_company_id = get_int_or_default(request.GET.get('production_company'), None)
            genre_id = get_int_or_default(request.GET.get('genre'), None)
            min_rating = get_float_or_default(request.GET.get('min_rating'), 0)
            max_rating = get_float_or_default(request.GET.get('max_rating'), 10)

            with connection.cursor() as cursor:
                cursor.callproc('search_movies', [
                    keyword, 
                    min_length, 
                    max_length, 
                    min_releaseyear, 
                    max_releaseyear, 
                    production_company_id,
                    genre_id
                ])
                movies = cursor.fetchall()
        else:
            with connection.cursor() as cursor:
                cursor.callproc('get_all_movies')
                movies = cursor.fetchall()

        movies_list = []
        for movie in movies:
            # Preprocess director names into a list
            directors_list = movie[7].split(',') if movie[7] else []

            # Get genres for the movie
            with connection.cursor() as cursor:
                cursor.callproc('get_movie_genre_association_with_name', [movie[0]])
                movie_genres = cursor.fetchall()
                genre_names = [genre[1] for genre in movie_genres]

            # Calculate the average rating for the movie
            average_rating = Rating.objects.filter(movie_id=movie[0]).aggregate(Avg('rating'))['rating__avg']
            if average_rating is not None:
                average_rating = round(average_rating * 2, 1)  # Scale to 10 and round to 1 decimal place
            else:
                average_rating = 'No ratings yet'

            # Apply the rating filter
            if isinstance(average_rating, (int, float)) and not (min_rating <= average_rating <= max_rating):
                continue

            movies_list.append({
                'movie_id': movie[0],
                'moviename': movie[1],
                'length': movie[2],
                'releaseyear': movie[3],
                'plot_summary': movie[4],
                'resource_link': movie[5],
                'production_company_name': movie[6],
                'directors_list': directors_list,
                'genres': genre_names,
                'average_rating': average_rating  # Add the average rating to the movie data
            })
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")
    
    # 实现分页
    try:
        page = request.GET.get('page', 1)
        limit = 5  # Number of movies per page
        paginator = Paginator(movies_list, limit)
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")
    try:
        movies_page = paginator.page(page)
    except PageNotAnInteger:
        movies_page = paginator.page(1)
    except EmptyPage:
        movies_page = paginator.page(paginator.num_pages)
        
    return render(request, 'list_movies.html', {
        'movies': movies_page, 
        'production_companies': production_companies_list,
        'genres': genres_list
    })

def get_float_or_default(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default




@login_required
def movie_detail(request, movie_id):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_movie_detail', [movie_id])
            movie_data = cursor.fetchone()
            if  movie_data[7]:
                actors_role=movie_data[7].split(";")
                actors=[]
                for actor in actors_role:
                    actor=actor.split(":")
                    actors.append({
                        'name':actor[0],
                        'role':actor[1]
                    })

            else:
                actors=None
            if  movie_data[8]:
                directors=movie_data[8].split(";")
            else:
                directors=None
            if  movie_data[9]:
                genres=movie_data[9].split(";")
            else:
                genres=None
            if  movie_data[10]:
                narrations=movie_data[10].split(";")
                narration_list=[]
                for narration in narrations:
                    narration=narration.split("-")
                    narration_list.append({
                        'actor':narration[0],
                        'content':narration[1],
                        'narration_id':narration[2],
                    })
            else:
                narration_list=None
            movie = {
                'movie_id': movie_data[0],
                'moviename': movie_data[1],
                'length': movie_data[2],
                'releaseyear': movie_data[3],
                'plot_summary': movie_data[4],
                'resource_link': movie_data[5],  
                'production_company_name': movie_data[6],
                'actors': actors,
                'directors': directors,
                'genres': genres,
                'narration_list': narration_list,
            }
            
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")
    
    # Fetch comments ordered by comment_time (latest on top)
    # 调整评论时间增加8小时
    comments = Comment.objects.filter(movie_id=movie_id, is_approved=True).annotate(
    adjusted_comment_time=ExpressionWrapper(F('comment_time') + timedelta(hours=8), output_field=DateTimeField())
    ).order_by('-adjusted_comment_time') 

    # Paginate comments
    paginator = Paginator(comments, 10)  # Show 10 comments per page
    page_number = request.GET.get('page')

    try:
        comments_page = paginator.page(page_number)
    except PageNotAnInteger:
        comments_page = paginator.page(1)
    except EmptyPage:
        comments_page = paginator.page(paginator.num_pages)

    # Create a list to hold comments with floors
    comments_with_floors = []
    for idx, comment in enumerate(comments_page):
        floor_number = len(comments) - (comments_page.start_index() + idx - 1)
        comments_with_floors.append({
            'floor': f"F{floor_number}",
            'comment': comment
        })

    rating_form = RatingForm()
    comment_form = CommentForm()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                if 'rating' in request.POST:
                    if Rating.objects.filter(movie_id=movie_id, user=request.user).exists():
                        messages.error(request, "Already rated!")
                    else:
                        rating_form = RatingForm(request.POST)
                        if rating_form.is_valid():
                            rating = rating_form.save(commit=False)
                            rating.movie_id = movie_id
                            rating.user = request.user
                            rating.save()
                            messages.success(request, "Rating submitted successfully!")
                            return redirect('movie_detail', movie_id=movie_id)
                else:
                    comment_form = CommentForm(request.POST)
                    if comment_form.is_valid():
                        comment = comment_form.save(commit=False)
                        comment.movie_id = movie_id
                        comment.user = request.user
                        comment.save()
                        messages.success(request, "Comment submitted successfully!")
                        return redirect('movie_detail', movie_id=movie_id)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            messages.error(request, "An error occurred! Please try again.")

    average_rating = Rating.objects.filter(movie_id=movie_id).aggregate(Avg('rating'))['rating__avg']
    if average_rating is not None:
        average_rating = round(average_rating * 2, 1)  # Scale to 10 and round to 1 decimal place
    

    context = {
        'movie': movie,
        'movie_id': movie_id,
        'comments_with_floors': comments_with_floors,
        'rating_form': rating_form,
        'comment_form': comment_form,
        'average_rating': average_rating,
        'star_range': range(5, 0, -1),  # Pass a range of 5 to 1 for star ratings
        'comments_page': comments_page,  # Add paginated comments to context
    }

    return render(request, 'movie_detail.html', context)

@login_required
@admin_required
@transaction.atomic
def update_movie(request, movie_id):
    # 获取电影对象
    movie = Movie.objects.get(pk=movie_id)
    if request.method == 'POST':
        # 解析表单数据
        moviename = request.POST['moviename']
        length = request.POST['length']
        releaseyear = get_int_or_default(request.POST['releaseyear'], None)
        plot_summary = request.POST['plot_summary']

        # 捕获缺少 production_company 字段的异常
        try:
            production_company_id = request.POST['production_company']
        except KeyError:
            messages.error(request, "Choose a production company!")
            return redirect('update_movie', movie_id=movie_id)

        # 如果上传了新的视频文件，保存并更新资源链接
        if 'video_file' in request.FILES:
            video_file = request.FILES['video_file']
            resource_link = save_video_file(video_file)
            # 删除原视频文件
            delete_video_file(movie.resource_link)
        else:
            resource_link = movie.resource_link

        # 调用存储过程更新电影信息
        with connection.cursor() as cursor:
            cursor.callproc('update_movie', [movie_id, moviename, length, releaseyear, plot_summary, resource_link, production_company_id])
        
        # 获取选中的导演
        director_ids = request.POST.get('directors', '')
        director_ids_list = director_ids.split(',') if director_ids else []
        with connection.cursor() as cursor:
            cursor.callproc('delete_directors_for_movie', [movie_id])
            for director_id in director_ids_list:
                cursor.callproc('add_director_movie', [movie_id, int(director_id)])
        
        # 更新类型关联
        try:
            genre_ids = request.POST.getlist('genres')
            with connection.cursor() as cursor:
                cursor.callproc('select_all_genre')
                genres = cursor.fetchall()
            with connection.cursor() as cursor:
                cursor.callproc('get_movie_genre_association', [movie_id])
                movie_genres = cursor.fetchall()
                movie_genres_ids = [genre[0] for genre in movie_genres]
        
            with connection.cursor() as cursor:
                for genre_id in movie_genres_ids:
                    cursor.callproc('delete_movie_genre_association', [movie_id, genre_id])  # 删除所有现有关联
            with connection.cursor() as cursor:
                for genre_id in genre_ids:
                    cursor.callproc('add_movie_genre_association', [movie_id, genre_id])
        except Exception as e:
            # Handle any exceptions or errors
            messages.error(request,f"Error : {e}")

        return redirect('list_movies')
    else:
        # 如果是 GET 请求，创建一个新的表单实例，并传入电影对象数据
        form = MovieForm(instance=movie, is_update=True)
        
        # 获取当前电影已关联的导演ID列表  
        with connection.cursor() as cursor:  
            cursor.callproc('get_directors_for_movie', [movie_id])
            rows = cursor.fetchall()
            selected_directors = [row[0] for row in rows]
        
        selected_directors_json = json.dumps(selected_directors)
        try:
            # 获取所有电影类型
            with connection.cursor() as cursor:
                cursor.callproc('select_all_genre')
                genres = cursor.fetchall()
            
            with connection.cursor() as cursor:
                cursor.callproc('get_movie_genre_association', [movie_id])
                movie_genres = cursor.fetchall()
                movie_genres_ids = [genre[0] for genre in movie_genres]

        # 获取当前电影的出品公司ID
            with connection.cursor() as cursor:
                cursor.callproc('get_movie_production_company', [movie_id])
                movie_production_company_id = cursor.fetchone()[0]

            # 获取出品公司分页数据
            with connection.cursor() as cursor:
                cursor.callproc('get_all_production_companies')
                production_companies = cursor.fetchall()
        except Exception as e:
            # Handle any exceptions or errors
            messages.error(request,f"Error : {e}")
        
        production_companies_list = [
            {'company_id': company[0], 'name': company[1], 'city': company[2], 'company_description': company[3]}
            for company in production_companies
        ]
        
        production_companies_paginator = Paginator(production_companies_list, 10)
        production_company_page = request.GET.get('production_company_page', 1)
        
        try:
            production_companies_page = production_companies_paginator.page(production_company_page)
        except PageNotAnInteger:
            production_companies_page = production_companies_paginator.page(1)
        except EmptyPage:
            production_companies_page = production_companies_paginator.page(production_companies_paginator.num_pages)

        return render(request, 'update_movie.html', {
            'form': form,
            'selected_directors_json': selected_directors_json,
            'genres': genres,
            'movie_genres_ids': movie_genres_ids,
            'production_companies_page': production_companies_page,
            'movie_production_company_id': movie_production_company_id  # 传递已选择的公司ID
        })

        
@transaction.atomic   
def delete_video_file(file_path):
    # 从文件路径中提取文件名
    filename = os.path.basename(file_path)
    # 构建完整的文件路径
    file_path = os.path.join(settings.MEDIA_ROOT, 'videos', filename)
    # 如果文件存在，删除它
    if os.path.exists(file_path):
        os.remove(file_path)


@login_required
@admin_required
@transaction.atomic
def delete_movie(request, movie_id):
    # 获取电影对象
    movie = Movie.objects.get(pk=movie_id)
    if request.method == 'POST':
        try:
            # 删除视频文件
            delete_video_file(movie.resource_link)
            # 调用存储过程删除电影
            with connection.cursor() as cursor:
                cursor.callproc('delete_movie', [movie_id])
        except Exception as e:
            # Handle any exceptions or errors
            messages.error(request,f"Error : {e}")
        return redirect('list_movies')
    return render(request, 'delete_movie_confirmation.html', {'movie': movie})


@login_required
@admin_required
@transaction.atomic
def add_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            birth_date = form.cleaned_data.get('birth_date') or None
            gender = form.cleaned_data['gender']
            marital_status = form.cleaned_data['marital_status']
            try:
                with connection.cursor() as cursor:
                    cursor.callproc('add_person', [name, birth_date, gender, marital_status])
            except Exception as e:
                # Handle any exceptions or errors
                messages.error(request,f"Error : {e}")
            return redirect('list_persons')
    else:
        form = PersonForm()
    return render(request, 'add_person.html', {'form': form})


@login_required
@transaction.atomic
def list_persons(request):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_all_persons')
            persons = cursor.fetchall()
        persons_list = [
            {'personID': person[0], 'name': person[1], 'birth_date': person[2], 'gender': person[3], 'marital_status': person[4]} 
            for person in persons
        ]
        gender_map = {'M': 'Male', 'F': 'Female', 'U': 'Unknown'}
        marital_status_map = {'S': 'Single', 'M': 'Married', 'W': 'Widowed', 'U': 'Unknown'}
        for person in persons_list:
            person['gender'] = gender_map.get(person['gender'], 'Unknown')
            person['marital_status'] = marital_status_map.get(person['marital_status'], 'Unknown')
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")
    # 实现分页
    page = request.GET.get('page', 1)
    limit = 10 # # 每页显示的人物数量
    paginator = Paginator( persons_list, limit)  
    try:
        person_page = paginator.page(page)
    except PageNotAnInteger:
        person_page = paginator.page(1)
    except EmptyPage:
        person_page = paginator.page(paginator.num_pages)
    return render(request, 'list_persons.html', {'persons': person_page})


@login_required
@admin_required
@csrf_exempt
@transaction.atomic
def update_person(request, person_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        marital_status = request.POST.get('marital_status')
        if not birth_date:
            birth_date = None
        try:
            with connection.cursor() as cursor:
                cursor.callproc('update_person', [person_id, name, birth_date, gender, marital_status])
        except Exception as e:
            # Handle any exceptions or errors
            messages.error(request,f"Error : {e}")

        return JsonResponse({'success': True, 'error': '无错误'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'})


@login_required
@admin_required
@csrf_exempt
@transaction.atomic
def delete_person(request, person_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.callproc('delete_person', [person_id])
        except Exception as e:
            # Handle any exceptions or errors
            messages.error(request,f"Error : {e}")

        return JsonResponse({'success': True, 'error': '无错误'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
@transaction.atomic
@csrf_exempt
def search_persons(request):
    name = request.GET.get('name', '')
    start_birth_date = request.GET.get('start_birth_date', None)
    end_birth_date = request.GET.get('end_birth_date', None)
    gender = request.GET.get('gender', None)
    marital_status = request.GET.get('marital_status', None)

    # Convert empty string to None for birth_date, gender, and marital_status
    if start_birth_date == '':
        start_birth_date = None
    if end_birth_date == '':
        end_birth_date = None
    if gender == '':
        gender = None
    if marital_status == '':
        marital_status = None
    print([name, start_birth_date, end_birth_date, gender, marital_status])
    try:
        with connection.cursor() as cursor:
            cursor.callproc('search_persons', [name, start_birth_date, end_birth_date, gender, marital_status])
            persons = cursor.fetchall()
        persons_list = [
            {'personID': person[0], 'name': person[1], 'birth_date': person[2], 'gender': person[3], 'marital_status': person[4]} 
            for person in persons
        ]
        gender_map = {'M': 'Male', 'F': 'Female', 'U': 'Unknown'}
        marital_status_map = {'S': 'Single', 'M': 'Married', 'W': 'Widowed', 'U': 'Unknown'}
        for person in persons_list:
            person['gender'] = gender_map.get(person['gender'], 'Unknown')
            person['marital_status'] = marital_status_map.get(person['marital_status'], 'Unknown')
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")
    page = request.GET.get('page', 1)
    limit = 10 # # 每页显示的人物数量
    paginator = Paginator( persons_list, limit)  
    try:
        person_page = paginator.page(page)
    except PageNotAnInteger:
        person_page = paginator.page(1)
    except EmptyPage:
        person_page = paginator.page(paginator.num_pages)
    return render(request, 'list_persons.html', {'persons': person_page})

@login_required
@transaction.atomic
def all_directors(request):
    search_director = request.GET.get('search_director', '')
    search_movie = request.GET.get('search_movie', '')
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_all_directors_and_directmovie')
            results = cursor.fetchall()
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")

    directors_with_movies = []
    all_directors_map = {}

    # Process the stored procedure results
    for row in results:
        director_id = row[0]
        director_name = row[1]
        movies = [movie.strip().split(':') for movie in row[2].split(', ')] if row[2] else []
        all_directors_map[director_id] = {
            'id': director_id,
            'name': director_name,
            'movies': [{'id': movie[0], 'name': movie[1]} for movie in movies]
        }

    # Filter directors and movies based on search criteria
    filtered_directors = []
    for director in all_directors_map.values():
        director_name_lower = director['name'].lower()
        matches_director = search_director.lower() in director_name_lower if search_director else True
        matches_movie = any(
            search_movie.lower() in movie['name'].lower() for movie in director['movies']) if search_movie else True
        if matches_director and matches_movie:
            filtered_directors.append(director)
    # Prepare directors and their movies to pass to the template
    for director in filtered_directors:
        director_movies = []
        for movie in director['movies']:
            movie_id = movie['id']
            movie_name = movie['name']
            # Calculate the average rating for the movie
            average_rating = Rating.objects.filter(movie_id=movie_id).aggregate(Avg('rating'))['rating__avg']
            if average_rating is not None:
                print("rate")
                average_rating = round(average_rating*2, 1)  # Round to 1 decimal place
                print(average_rating)
            else:
                print("NOt rate")
                average_rating = None

            director_movies.append({
                'id': movie_id,
                'name': movie_name,
                'average_rating': average_rating
            })

        directors_with_movies.append({
            'id': director['id'],
            'name': director['name'],
            'movies': director_movies
        })

    # Paginate the list of directors
    page = request.GET.get('page', 1)
    d_limit = 10  # Number of directors per page
    paginator = Paginator(filtered_directors, d_limit)
    try:
        directors_page = paginator.page(page)
    except PageNotAnInteger:
        directors_page = paginator.page(1)
    except EmptyPage:
        directors_page = paginator.page(paginator.num_pages)
    # Create pagination for each director's movies
    for director in directors_page:
        m_limit = 5  # Number of movies per page
        movies_paginator = Paginator(director_movies, m_limit)
        movies_page = request.GET.get(f'movies_page_{director["id"]}', 1)
        try:
            director['movies_page'] = movies_paginator.page(movies_page)
        except PageNotAnInteger:
            director['movies_page'] = movies_paginator.page(1)
        except EmptyPage:
            director['movies_page'] = movies_paginator.page(movies_paginator.num_pages)
    return render(request, 'all_directors.html', {
        'directors_with_movies': directors_page,
        'search_director': search_director,
        'search_movie': search_movie
    })
        


@login_required
@admin_required
@transaction.atomic
def manage_genres(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        genre_name = request.POST.get('genre_name', '')
        genre_id = request.POST.get('genre_id', None)
        try:
            if action == 'add' and genre_name:
                with connection.cursor() as cursor:
                    cursor.callproc('add_movie_genre', [genre_name])
            
            elif action == 'delete' and genre_id:
                print('del in')
                with connection.cursor() as cursor:
                    cursor.callproc('delete_movie_genre', [genre_id])
        except IntegrityError as e:
            messages.error(request, 'Error: Already have this genre.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

        return redirect('manage_genres')
    try:
        with connection.cursor() as cursor:
            cursor.callproc('select_all_genre')
            genres = cursor.fetchall()
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")
    
    page = request.GET.get('page', 1)
    limit = 10 # 每页显示电影类型数
    paginator = Paginator(genres, limit)  
    try:
        genres_page = paginator.page(page)
    except PageNotAnInteger:
        genres_page = paginator.page(1)
    except EmptyPage:
        genres_page = paginator.page(paginator.num_pages)
    
    return render(request, 'manage_genres.html', {'genres': genres_page})


@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 验证验证码
            captcha_response = request.POST.get('captcha')
            cached_captcha = cache.get(request.session.session_key + '_captcha')
            if captcha_response and captcha_response.upper() == cached_captcha:
                # 验证通过，处理注册逻辑
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                hashed_password = make_password(password)
                try:
                    with connection.cursor() as cursor:
                        cursor.callproc('create_user_procedure', [username, hashed_password])
                    messages.success(request, 'Registration successful.')
                    return redirect('login')
                except Exception as e:
                    messages.error(request, f'Error: {str(e)}')
            else:
                # 验证码未通过
                messages.error(request, 'Invalid captcha. Please try again.')
        else:
            # 表单验证失败
            messages.error(request, 'Invalid form data. Please check your inputs.')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if 'reset_username' in request.session:
        del request.session['reset_username']  # 清理 reset_username
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Check if there are other active login records for this user
            try:
                with connection.cursor() as cursor:
                    cursor.callproc('manage_login_record', [user.id, request.session.session_key, 'create'])
            except Exception as e:
                # Handle any exceptions or errors
                print(f"Error creating login record: {e}")
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


@login_required
def logout_view(request):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('manage_login_record', [request.user.id, request.session.session_key, 'delete'])
    except Exception as e:
        # Handle any exceptions or errors
        print(f"Error deleting login record: {e}")
    logout(request)
    return redirect('login')


@login_required
@super_required
def manage_admins(request):
    users = []

    # 处理搜索功能
    name_query = request.GET.get('name')
    try:
        with connection.cursor() as cursor:
            if name_query:
                cursor.callproc('get_users_procedure', [name_query])
            else:
                cursor.callproc('get_users_procedure', [None])
            users = cursor.fetchall()
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    # 分页处理
    paginator = Paginator(users, 10)  # 每页显示10个用户
    page_number = request.GET.get('page')

    try:
        users_page = paginator.page(page_number)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)

    context = {
        'users_page': users_page,
    }

    return render(request, 'manage_admins.html', context)


@login_required
@super_required
def add_admin(request, user_id):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('set_staff_status', [user_id, True])
        messages.success(request, "用户已被设置为管理员。")
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('manage_admins')


@login_required
@super_required
def toggle_staff_status(request, user_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.callproc('change_staff_status', [user_id])
            messages.success(request, "用户权限已更新。")
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return redirect('manage_admins')

@login_required
def add_comment(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.movie = movie
            comment.user = request.user
            comment.save()
            return redirect('movie_detail', pk=movie.pk)
    else:
        form = CommentForm()
    return render(request, 'movies/add_comment.html', {'form': form})

@login_required
@admin_required
def approve_comments(request):
    comments = Comment.objects.filter(is_approved=False, is_denied=False)
    if request.method == 'POST':
        if 'approve' in request.POST:
            comment_ids = request.POST.getlist('approve')
            Comment.objects.filter(comment_id__in=comment_ids).update(is_approved=True)
        elif 'deny' in request.POST:
            comment_ids = request.POST.getlist('deny')
            Comment.objects.filter(comment_id__in=comment_ids).update(is_denied=True)
        return redirect('approve_comments')

    return render(request, 'approve_comments.html', {'comments': comments})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user_id = request.user.id
        logout(request)
        try:
            with connection.cursor() as cursor:
                cursor.callproc('delete_user', [user_id])
            messages.success(request, "你的账号已被删除")
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        return redirect('home')
    return render(request, 'delete_account.html')

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, comment_id=comment_id)
    if comment.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this comment.")
    
    if request.method == "POST":
        comment.delete()
        return redirect('movie_detail', movie_id=comment.movie_id)
    
    return render(request, 'confirm_delete_comment.html', {'comment': comment})


@login_required
@admin_required
def manage_users(request):
    query = request.GET.get('q')
    users = []
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_users_procedure', [query])
            users = cursor.fetchall()
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    paginator = Paginator(users, 10)  # 10 users per page
    page_number = request.GET.get('page')

    try:
        users_page = paginator.page(page_number)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)

    context = {
        'users_page': users_page,
        'query': query
    }

    return render(request, 'manage_users.html', context)



@login_required
@admin_required
def admin_delete_user(request, user_id):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('delete_user', [user_id])
        messages.success(request, "用户已被删除")
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('manage_users')

def generate_captcha(request):
    # 确保会话已经在请求中初始化
    if not request.session.session_key:
        request.session.save()
    # 生成随机验证码
    captcha_code = ''.join(random.choices('0123456789ABCDEFGHJKLMNPQRSTUVWXYZ', k=6))

    # 将验证码保存到缓存中，有效期为5分钟
    cache.set(request.session.session_key + '_captcha', captcha_code, 300)

    # 创建图像
    width, height = 200, 50
    image = Image.new('RGB', (width, height), color = (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 设置字体和字体大小
    font = ImageFont.truetype('arial.ttf', size=30)

    # 在图像上绘制验证码
    draw.text((10, 10), captcha_code, font=font, fill=(0, 0, 0))

    # 将图像保存到内存中
    image_buffer = BytesIO()
    image.save(image_buffer, format='JPEG')
    image_buffer.seek(0)

    return HttpResponse(image_buffer, content_type='image/jpeg')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password1']
            hashed_password = make_password(new_password)
            user = request.user

            # Verify current password
            if user.check_password(old_password):
                try:
                    # Call a stored procedure to update password
                    with connection.cursor() as cursor:
                        cursor.callproc('update_password_procedure', [user.id, hashed_password])

                    # Update session authentication hash
                    update_session_auth_hash(request, user)

                    messages.success(request, 'Your password was successfully updated!')
                except Exception as e:
                    # Handle any exceptions or errors
                    messages.error(request,f"Error : {e}")
                return redirect('home')
            else:
                messages.error(request, 'Please enter your current password correctly.')

    else:
        form = ChangePasswordForm()

    return render(request, 'change_password.html', {'form': form})

@login_required
def set_security_question(request):

    if request.method == 'POST':
        form = SecurityQAForm(request.POST)
        if form.is_valid():
            security_question = form.cleaned_data['security_question']
            security_answer = form.cleaned_data['security_answer']
            # Call the stored procedure to update security question and answer
            try:
                with connection.cursor() as cursor:
                    cursor.callproc('set_security_question_proc', [request.user.id, security_question, security_answer])
                messages.success(request, 'Security question and answer set successfully.')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = SecurityQAForm()
    
    return render(request, 'set_security_question.html', {'form': form})

def reset_password(request):
    username_form = UsernameForm()
    form = PasswordResetForm()
    if request.method == 'POST':
        if 'username' in request.POST:
            username_form = UsernameForm(request.POST)
            if username_form.is_valid():
                username = username_form.cleaned_data['username']
                try:
                    with connection.cursor() as cursor:
                        cursor.callproc('get_security_question_proc', [username, '', ''])
                        result = cursor.fetchone()
                        security_question, message = result[0], result[1]
                        if security_question:
                            request.session['reset_username'] = username
                            request.session['security_question'] = security_question
                            return redirect('reset_password')
                        else:
                            messages.error(request, message)
                except Exception as e:
                    print("error when get security question proc")
                    messages.error(request, f'Error: {str(e)}')
        else:
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                username = request.session.get('reset_username')
                security_answer = form.cleaned_data['security_answer']
                new_password = form.cleaned_data['new_password']
                hashed_password = make_password(new_password)
                try:
                    with connection.cursor() as cursor:
                        cursor.callproc('reset_password_proc', [username, security_answer, hashed_password, 0, ''])
                        result = cursor.fetchone()
                        success, message = result[0], result[1]
                        if success:
                            del request.session['reset_username']
                            messages.success(request, message)
                            return redirect('login')
                        else:
                            messages.error(request, message)
                except Exception as e:
                    print("error when reset password")
                    messages.error(request, f'Error: {str(e)}')
    else:
        username_form = UsernameForm()
        form = PasswordResetForm()

    return render(request, 'reset_password.html', {
        'username_form': username_form,
        'form': form,
        'security_question': request.session.get('security_question', None)
    })

@login_required
@admin_required
def add_role(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        person_id = request.POST.get('person_id')
        role_name = request.POST.get('role_name')
        role_description = request.POST.get('role_description', '')

        # Create or get the role
        role, created = Role.objects.get_or_create(role_name=role_name, defaults={'role_description': role_description})

        # Get the movie and person instances
        try:
            movie = Movie.objects.get(movie_id=movie_id)
            person = Person.objects.get(personID=person_id)
        except (Movie.DoesNotExist, Person.DoesNotExist):
            return HttpResponse("Movie or Person not found", status=404)

        # Create the RoleActorMovie instance
        RoleActorMovie.objects.create(movie=movie, person=person, role=role)

        return redirect('role_list')  # You can change 'success' to the name of your success page

    return render(request, 'add_role.html')

def search_movies(request):
    query = request.GET.get('q', '')
    movies = Movie.objects.filter(moviename__icontains=query) if query else []
    return render(request, 'search_movies.html', {'query': query, 'movies': movies})

def search_persons_role(request):
    query = request.GET.get('q', '')
    persons = Person.objects.filter(name__icontains=query) if query else []
    return render(request, 'search_persons_role.html', {'query': query, 'persons': persons})


@login_required
def role_list(request):
    roles = Role.objects.all()
    return render(request, 'role_list.html', {'roles': roles})

@login_required
def role_detail(request, role_id):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_role_detail', [role_id])
            role_data = cursor.fetchone()
            cursor.nextset()
            role_actor_movies_data = cursor.fetchall()
            
            role = {
                'role_name': role_data[0],
                'role_description': role_data[1],
                'role_id':role_id
            }
            role_actor_movies = [
                {
                    'movie': {
                        'title': row[1],
                        'movie_id': row[0]
                    },
                    'person': {
                        'name': row[3]
                    }
                }
                for row in role_actor_movies_data
            ]

    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request, f"Error: {e}")
        role = None
        role_actor_movies = []
        print(role,'role',e)
    return render(request, 'role_detail.html', {'role': role, 'role_actor_movies': role_actor_movies})


@login_required
@admin_required
def edit_role(request, role_id):
    role = get_object_or_404(Role, pk=role_id)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return redirect('role_list')
    else:
        form = RoleForm(instance=role)
    return render(request, 'edit_role.html', {'form': form, 'role': role})


@login_required
def search_roles_by_name(request):
    query = request.GET.get('query', '')
    roles = Role.objects.filter(role_name__icontains=query)
    return render(request, 'search_roles.html', {'roles': roles, 'query': query, 'search_type': 'name'})


@login_required
def search_roles_by_actor(request):
    query = request.GET.get('query', '')
    roles = Role.objects.filter(roleactormovie__person__name__icontains=query).distinct()
    return render(request, 'search_roles.html', {'roles': roles, 'query': query, 'search_type': 'actor'})

@login_required
def search_roles_by_movie(request):
    query = request.GET.get('query', '')
    roles = Role.objects.filter(roleactormovie__movie__moviename__icontains=query).distinct()
    return render(request, 'search_roles.html', {'roles': roles, 'query': query, 'search_type': 'movie'})

@login_required
@admin_required
def delete_role(request, role_id):
    role = get_object_or_404(Role, pk=role_id)
    if request.method == 'POST':
        role.delete()
        return redirect('role_list')
    return render(request, 'delete_role.html', {'role': role})

@login_required
@admin_required
def edit_role_actor_movie(request, role_id):
    role = get_object_or_404(Role, pk=role_id)
    role_actor_movie = get_object_or_404(RoleActorMovie, role=role)
    if request.method == 'POST':
        form = RoleActorMovieForm(request.POST, instance=role_actor_movie)
        if form.is_valid():
            form.save()
            return redirect('role_detail', role_id=role_id)
    else:
        form = RoleActorMovieForm(instance=role_actor_movie)
    return render(request, 'edit_role_actor_movie.html', {'form': form, 'role': role})

@login_required
def search_role(request):
    return render(request, 'search_role.html')

@login_required
def user_homepage(request, username):
    user = get_object_or_404(User, username=username)
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_user_activity', [user.id])
            
            # Fetch ratings
            ratings = cursor.fetchall()
            cursor.nextset()  # Move to the next result set
            
            # Fetch comments
            comments = cursor.fetchall()
    except Exception as e:
        # Handle any exceptions or errors
        messages.error(request,f"Error : {e}")

    ratings_list = []
    for rating in ratings:
        ratings_list.append({
            'rating_id': rating[0],
            'user_id': rating[1],
            'movie_id': rating[2],
            'movie_name': rating[3],
            'rating': round(rating[4] * 2, 1)  # Scale rating to 10 and round to 1 decimal place
        })

    comments_list = []
    for comment in comments:
        comments_list.append({
            'comment_id': comment[0],
            'user_id': comment[1],
            'movie_id': comment[2],
            'movie_name': comment[3],
            'content': comment[4],
            'comment_time': comment[5]
        })

    return render(request, 'user_homepage.html', {
        'user_profile': user,
        'ratings': ratings_list,
        'comments': comments_list,
    })

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = []
    
    if query:
        users = User.objects.filter(username__icontains=query)
    
    context = {
        'query': query,
        'users': users
    }
    
    return render(request, 'search_users.html', context)

@login_required
def list_actors(request):
    search_name = request.GET.get('search_name', '')
    with connection.cursor() as cursor:
        cursor.callproc('get_all_actors', [search_name])
        actors = cursor.fetchall()

    actors_list = [{'personID': actor[0], 'name': actor[1]} for actor in actors]

    # 获取每个演员出演的电影
    for actor in actors_list:
        with connection.cursor() as cursor:
            cursor.callproc('get_actor_movies_with_id', [actor['personID']])
            movies = cursor.fetchall()
            actor['movies'] = [{'movie_id': movie[0], 'title': movie[1], 'rating': round(movie[2]*2,1)} for movie in movies]

    return render(request, 'list_actors.html', {'actors': actors_list, 'search_name': search_name})

@login_required
def movie_actors(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    actors = movie.actors.all()
    return render(request, 'movie_actors.html', {'movie': movie, 'actors': actors})

@login_required
def person_movies(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    movies_as_actor = person.movies_acted.all()
    movies_as_narrator = person.narrated_movies.all()
    return render(request, 'person_movies.html', {
        'person': person,
        'movies_as_actor': movies_as_actor,
        'movies_as_narrator': movies_as_narrator,
    })

@login_required
@admin_required
def add_narration(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    if request.method == 'POST':
        form = NarrationForm(request.POST)
        if form.is_valid():
            narration = form.save(commit=False)
            narration.movie = movie
            narration.save()
            messages.success(request, 'Narration added successfully!')
            return redirect('movie_detail', movie_id=movie_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NarrationForm()

    return render(request, 'add_narration.html', {'form': form, 'movie': movie})

@login_required
@admin_required
def delete_narration(request, movie_id, narration_id):
    narration = get_object_or_404(Narration, pk=narration_id)
    narration.delete()
    messages.success(request, 'Narration deleted successfully!')
    return redirect('movie_detail', movie_id=movie_id)