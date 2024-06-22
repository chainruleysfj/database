from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect,Http404
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.urls import reverse
from django.db import connection,transaction
from django.conf import settings
from django.template.defaultfilters import urlencode
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test,login_required
from .models import Movie, ProductionCompany, Person,MovieGenre, MovieGenreAssociation,Users
from .forms import ProductionCompanyForm,MovieForm,PersonForm,RegisterForm
from functools import wraps
import json,os,uuid



def is_admin(user):
    return user.is_authenticated and user.is_staff

def admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_staff:

            return function(request, *args, **kwargs)
        else:
            messages.error(request, "缺少权限")
         
            return redirect(request.META.get('HTTP_REFERER', '/'))  # 重定向到来源页面
    return wrap

def super_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:

            return function(request, *args, **kwargs)
        else:
            messages.error(request, "缺少权限")
         
            return redirect(request.META.get('HTTP_REFERER', '/'))  # 重定向到来源页面
    return wrap

@login_required
def home(request):
    return render(request, 'home.html')  # 创建一个名为 home.html 的模板文件，并返回给客户端

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
            with connection.cursor() as cursor:
                cursor.callproc('add_productioncompany', [name, city, description])
            return redirect('list_production_companies')    # 重定向到公司一览页面
    else:
        form = ProductionCompanyForm()
    return render(request, 'add_production_company.html', {'form': form})

@login_required
@transaction.atomic
def list_production_companies(request):
  
    companies = []
    with connection.cursor() as cursor:
        cursor.callproc('get_all_production_companies')
        for result in cursor.fetchall():
            companies.append({
                'company_id': result[0],
                'name': result[1],
                'city': result[2],
                'company_description': result[3],
            })
    return render(request, 'list_production_companies.html', {'companies': companies})

@login_required
@admin_required
@transaction.atomic
def update_production_company(request, company_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        city = request.POST.get('city')
        description = request.POST.get('company_description')
        with connection.cursor() as cursor:
            cursor.callproc('update_production_company', [company_id, name, city, description])
        return redirect('list_production_companies')

    company = None
    with connection.cursor() as cursor:
        cursor.callproc('get_company_by_id', [company_id])
        company = cursor.fetchone()
    
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

        with connection.cursor() as cursor:
            cursor.callproc('delete_production_company', [company_id])
        return redirect('list_production_companies')
    else:

        return render(request, 'confirm_delete_production_company.html', {'company_id': company_id})

@login_required
@transaction.atomic
def search_production_companies(request):
    name = request.GET.get('name', '')
    city = request.GET.get('city', '')

    with connection.cursor() as cursor:
        cursor.callproc('search_production_companies', [name, city])
        companies = cursor.fetchall()

    company_list = []
    for company in companies:
        company_list.append({
            'company_id': company[0],
            'name': company[1],
            'city': company[2],
            'company_description': company[3],
        })

    return render(request, 'list_production_companies.html', {'companies': company_list})

@login_required
@admin_required
@transaction.atomic
def add_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES,is_update=False)
        if form.is_valid():
            print("电影表单无误")
            # 从表单中获取数据
            moviename = form.cleaned_data['moviename']
            length = form.cleaned_data['length']
            releaseyear = form.cleaned_data['releaseyear']
            plot_summary = form.cleaned_data['plot_summary']
            production_company_id = form.cleaned_data['production_company'].company_id
            # 如果上传了视频文件，保存文件并获取文件路径
            resource_link = None
            if 'video_file' in request.FILES:
                video_file = request.FILES['video_file']
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
                with connection.cursor() as cursor:
                    for director_id in director_ids_list:
                        cursor.callproc('add_director_movie', [movie_id, int(director_id)])
            # 添加类型关联
            genre_ids = request.POST.getlist('genres')
            for genre_id in genre_ids:
                with connection.cursor() as cursor:
                    cursor.callproc('add_movie_genre_association', [movie_id, genre_id])

            return redirect('list_movies')
        print("电影表单有误")
    else:
        form = MovieForm(is_update=False)

    # 获取所有电影类型
    with connection.cursor() as cursor:
        cursor.callproc('select_all_genre')
        genres = cursor.fetchall()
    return render(request, 'add_movie.html', {'form': form, 'genres': genres})

@login_required
@transaction.atomic
def search_person_by_name(request):
    query = request.GET.get('query', '')
    with connection.cursor() as cursor:
        cursor.callproc('search_person_by_name', [query])
        results = cursor.fetchall()
    directors = [{'person_id': result[0], 'name': result[1]} for result in results]
    return JsonResponse(directors, safe=False)

@login_required
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
def list_movies_v1(request):

#     # 不显示导演的list_movies
#     # 获取所有出品公司以供搜索表单使用
#     with connection.cursor() as cursor:
#         cursor.callproc('get_all_production_companies')
#         production_companies = cursor.fetchall()
#     production_companies_list = [
#         {'company_id': company[0], 'name': company[1], 'city': company[2], 'company_description': company[3]}
#         for company in production_companies
#         ]
#     # 如果有搜索请求，处理搜索
#     if request.method == 'GET' and (
#         'keyword' in request.GET or
#         'min_length' in request.GET or
#         'max_length' in request.GET or
#         'min_releaseyear' in request.GET or
#         'max_releaseyear' in request.GET or
#         'production_company' in request.GET
#     ):
#         keyword = request.GET.get('keyword', '')
#         min_length = get_int_or_default(request.GET.get('min_length'), 0)
#         max_length = get_int_or_default(request.GET.get('max_length'), 9999)
#         min_releaseyear = get_int_or_default(request.GET.get('min_releaseyear'), 0)
#         max_releaseyear = get_int_or_default(request.GET.get('max_releaseyear'), 9999)
#         production_company_id = get_int_or_default(request.GET.get('production_company'), None)

#         with connection.cursor() as cursor:
#             cursor.callproc('search_movies', [
#                 keyword, 
#                 min_length, 
#                 max_length, 
#                 min_releaseyear, 
#                 max_releaseyear, 
#                 production_company_id
#             ])
#             movies = cursor.fetchall()

#         movies_list = [{'movie_id': movie[0], 'moviename': movie[1], 'length': movie[2], 'releaseyear': movie[3], 'plot_summary': movie[4], 'resource_link': movie[5], 'production_company_id': movie[6]} for movie in movies]
#     else:
#         with connection.cursor() as cursor:
#             cursor.callproc('get_all_movies')
#             movies = cursor.fetchall()

#         movies_list = [
#             {
#                 'movie_id': movie[0],
#                 'moviename': movie[1],
#                 'length': movie[2],
#                 'releaseyear': movie[3],
#                 'plot_summary': movie[4],
#                 'resource_link': movie[5],
#                 'production_company_id': movie[6]
#             } for movie in movies
#         ]
        
#     return render(request, 'list_movies.html', {'movies': movies_list, 'production_companies': production_companies_list})
    return 0

@login_required
@transaction.atomic
def list_movies(request):
    # 获取所有出品公司以供搜索表单使用
    with connection.cursor() as cursor:
        cursor.callproc('get_all_production_companies')
        production_companies = cursor.fetchall()
    production_companies_list = [
        {'company_id': company[0], 'name': company[1], 'city': company[2], 'company_description': company[3]}
        for company in production_companies
    ]

    # 获取所有电影类型以供搜索表单使用
    with connection.cursor() as cursor:
        cursor.callproc('select_all_genre')
        genres = cursor.fetchall()
    genres_list = [
        {'genre_id': genre[0], 'genre_name': genre[1]}
        for genre in genres
    ]

    # 如果有搜索请求，处理搜索
    if request.method == 'GET' and (
        'keyword' in request.GET or
        'min_length' in request.GET or
        'max_length' in request.GET or
        'min_releaseyear' in request.GET or
        'max_releaseyear' in request.GET or
        'production_company' in request.GET or
        'genre' in request.GET
    ):
        keyword = request.GET.get('keyword', '')
        min_length = get_int_or_default(request.GET.get('min_length'), 0)
        max_length = get_int_or_default(request.GET.get('max_length'), 9999)
        min_releaseyear = get_int_or_default(request.GET.get('min_releaseyear'), 0)
        max_releaseyear = get_int_or_default(request.GET.get('max_releaseyear'), 9999)
        production_company_id = get_int_or_default(request.GET.get('production_company'), None)
        genre_id = get_int_or_default(request.GET.get('genre'), None)


        with connection.cursor() as cursor:
            cursor.callproc('search_movies_with_directors_and_companies_and_genres', [
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
            cursor.callproc('get_all_movies_with_directors_and_companies')
            movies = cursor.fetchall()

    movies_list = []
    for movie in movies:
        # 对导演名进行预处理，将其拆分为列表
        directors_list = movie[7].split(',') if movie[7] else []

        # 获取该电影的类型
        with connection.cursor() as cursor:
            cursor.callproc('get_movie_genre_association_with_name', [movie[0]])
            movie_genres = cursor.fetchall()
            genre_names = [genre[1] for genre in movie_genres]

        movies_list.append({
            'movie_id': movie[0],
            'moviename': movie[1],
            'length': movie[2],
            'releaseyear': movie[3],
            'plot_summary': movie[4],
            'resource_link': movie[5],
            'production_company_name': movie[6],
            'directors_list': directors_list,  # 添加预处理后的导演名列表
            'genres':genre_names
        })
        

    return render(request, 'list_movies.html', {
        'movies': movies_list, 
        'production_companies': production_companies_list,
        'genres': genres_list})

@login_required
@transaction.atomic
def movie_detail(request, movie_id):
    with connection.cursor() as cursor:
        cursor.callproc('get_movie_detail', [movie_id])
        movie_data = cursor.fetchone()

    movie = {
        'movie_id': movie_data[0],
        'moviename': movie_data[1],
        'length': movie_data[2],
        'releaseyear': movie_data[3],
        'plot_summary': movie_data[4],
        'resource_link': movie_data[5],
        'production_company_id': movie_data[6]
    }

    return render(request, 'movie_detail.html', {'movie': movie})

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
        releaseyear = get_int_or_default(request.POST['releaseyear'],None)
        plot_summary = request.POST['plot_summary']
        production_company_id = request.POST['production_company']
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
            # 插入导演数据
            director_ids_list = director_ids.split(',') if director_ids else []
            with connection.cursor() as cursor:
                cursor.callproc('delete_directors_for_movie', [movie_id])
                for director_id in director_ids_list:
                    cursor.callproc('add_director_movie', [movie_id, int(director_id)])
        # 更新类型关联
        genre_ids = request.POST.getlist('genres')
        # 获取所有电影类型
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
            for genre_id in genre_ids:
                cursor.callproc('add_movie_genre_association', [movie_id, genre_id])
        return redirect('list_movies')
    else:
        # 如果是 GET 请求，创建一个新的表单实例，并传入电影对象数据
        form = MovieForm(instance=movie,is_update=True)
        # 获取当前电影已关联的导演ID列表  
        # 假设你有一个方法可以从数据库中获取这些ID，例如 get_directors_for_movie(movie_id)  
        with connection.cursor() as cursor:  
            # 调用存储过程，这里不需要输出参数  
            cursor.callproc('get_directors_for_movie', [movie_id])  
              
            # fetchall()获取查询结果的所有行  
            rows = cursor.fetchall()  
            selected_directors = [row[0] for row in rows]  # 假设每行只有一个值，即导演ID  
            
        selected_directors_json = json.dumps(selected_directors)
        # 获取所有电影类型
        with connection.cursor() as cursor:
            cursor.callproc('select_all_genre')
            genres = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.callproc('get_movie_genre_association', [movie_id])
            movie_genres = cursor.fetchall()
            movie_genres_ids = [genre[0] for genre in movie_genres]

        return render(request, 'update_movie.html', {  
            'form': form,  
            'selected_directors_json': selected_directors_json,  
            'genres': genres, 
            'movie_genres_ids': movie_genres_ids
        })

@login_required        
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
        # 删除视频文件
        delete_video_file(movie.resource_link)
        # 调用存储过程删除电影
        with connection.cursor() as cursor:
            cursor.callproc('delete_movie_and_directormovie_and_genre', [movie_id])
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
            with connection.cursor() as cursor:
                cursor.callproc('add_person', [name, birth_date, gender, marital_status])
            return redirect('home')
    else:
        form = PersonForm()
    return render(request, 'add_person.html', {'form': form})

@login_required
@transaction.atomic
def list_persons(request):
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
    return render(request, 'list_persons.html', {'persons': persons_list})

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

        with connection.cursor() as cursor:
            cursor.callproc('update_person', [person_id, name, birth_date, gender, marital_status])

        return redirect('list_persons')
    else:
        return JsonResponse({'error': 'Invalid request method'})

@login_required    
@admin_required
@csrf_exempt
@transaction.atomic
def delete_person(request, person_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.callproc('delete_person_and_directormovie', [person_id])

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required    
@transaction.atomic
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
    return render(request, 'list_persons.html', {'persons': persons_list})

@login_required
@transaction.atomic
def all_directors(request):

    search_director = request.GET.get('search_director', '')
    search_movie = request.GET.get('search_movie', '')
    with connection.cursor() as cursor:
        cursor.callproc('get_all_directors_and_directmovie')
        results = cursor.fetchall()

    directors_with_movies = []
    all_directors_map = {}

    # 处理存储过程的结果
    for row in results:
        director_id = row[0]
        director_name = row[1]
        movies = [movie.strip().split(':') for movie in row[2].split(', ')] if row[2] else []
        all_directors_map[director_id] = {
            'id': director_id,
            'name': director_name,
            'movies': [{'id': movie[0], 'name': movie[1]} for movie in movies]
        }

    # 根据搜索条件筛选导演和电影
    filtered_directors = []
    for director in all_directors_map.values():
        director_name_lower = director['name'].lower()
        matches_director = search_director.lower() in director_name_lower if search_director else True
        matches_movie = any(search_movie.lower() in movie['name'].lower() for movie in director['movies']) if search_movie else True
        if matches_director and matches_movie:
            filtered_directors.append(director)
            

    # 准备要传递给模板的导演及其电影
    for director in filtered_directors:
        directors_with_movies.append({
            'id': director['id'],
            'name': director['name'],
            'movies': director['movies']
        })

    return render(request, 'all_directors.html', {
        'directors_with_movies': directors_with_movies,
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
        
        if action == 'add' and genre_name:
            with connection.cursor() as cursor:
                cursor.callproc('add_movie_genre', [genre_name])
        
        elif action == 'delete' and genre_id:
            with connection.cursor() as cursor:
                cursor.callproc('delete_movie_genre', [genre_id])

        return redirect('manage_genres')

    with connection.cursor() as cursor:
        cursor.callproc('select_all_genre')
        genres = cursor.fetchall()
    
    return render(request, 'manage_genres.html', {'genres': genres})

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            try:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                messages.success(request, 'Registration successful.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@super_required
def manage_admins(request):
    users = User.objects.all()

    # 处理搜索功能
    name_query = request.GET.get('name')
    if name_query:
        users = users.filter(username__icontains=name_query)

    context = {
        'users': users
    }
    return render(request, 'manage_admins.html', context)

@login_required
@super_required
def add_admin(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_staff = True
    user.save()
    return redirect('manage_admins')

@login_required
@super_required
def toggle_staff_status(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        user.is_staff = not user.is_staff  # 切换 staff 状态
        user.save()
    return redirect('manage_admins')

@login_required
def delete_account(request):
    user = request.user
    logout(request)
    user.delete()
    messages.success(request, "你的账号已被删除")
    return redirect('home')

@login_required
@admin_required
def admin_delete_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user.is_staff:
        messages.error(request, "管理员不能删除其他管理员")
    else:
        target_user.delete()
        messages.success(request, "用户已被删除")
    return redirect('manage_admins')


