from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect,Http404
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.urls import reverse
from django.db import connection
from django.conf import settings
from .models import Movie, ProductionCompany, Person
from .forms import ProductionCompanyForm,MovieForm,PersonForm
import json,os,uuid


def home(request):
    return render(request, 'home.html')  # 创建一个名为 home.html 的模板文件，并返回给客户端

@csrf_exempt
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


def delete_production_company(request, company_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.callproc('delete_production_company', [company_id])
        return redirect('list_production_companies')
    else:
        return render(request, 'confirm_delete_production_company.html', {'company_id': company_id})
    
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

            return redirect('list_movies')
        print("电影表单有误")
    else:
        form = MovieForm(is_update=False)
    return render(request, 'add_movie.html', {'form': form})

def search_person_by_name(request):
    query = request.GET.get('query', '')
    with connection.cursor() as cursor:
        cursor.callproc('search_person_by_name', [query])
        results = cursor.fetchall()
    directors = [{'person_id': result[0], 'name': result[1]} for result in results]
    return JsonResponse(directors, safe=False)

def save_video_file(video_file):
    unique_filename = str(uuid.uuid4()) + '.mp4'
    file_path = os.path.join(settings.MEDIA_ROOT, 'videos', unique_filename)
    with open(file_path, 'wb+') as destination:
        for chunk in video_file.chunks():
            destination.write(chunk)
    return os.path.join(settings.MEDIA_URL, 'videos', unique_filename)

def get_int_or_default(value, default):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
    

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

def list_movies(request):
    # 获取所有出品公司以供搜索表单使用
    with connection.cursor() as cursor:
        cursor.callproc('get_all_production_companies')
        production_companies = cursor.fetchall()
    production_companies_list = [
        {'company_id': company[0], 'name': company[1], 'city': company[2], 'company_description': company[3]}
        for company in production_companies
    ]

    # 如果有搜索请求，处理搜索
    if request.method == 'GET' and (
        'keyword' in request.GET or
        'min_length' in request.GET or
        'max_length' in request.GET or
        'min_releaseyear' in request.GET or
        'max_releaseyear' in request.GET or
        'production_company' in request.GET
    ):
        keyword = request.GET.get('keyword', '')
        min_length = get_int_or_default(request.GET.get('min_length'), 0)
        max_length = get_int_or_default(request.GET.get('max_length'), 9999)
        min_releaseyear = get_int_or_default(request.GET.get('min_releaseyear'), 0)
        max_releaseyear = get_int_or_default(request.GET.get('max_releaseyear'), 9999)
        production_company_id = get_int_or_default(request.GET.get('production_company'), None)

        with connection.cursor() as cursor:
            cursor.callproc('search_movies_with_directors_and_companies', [
                keyword, 
                min_length, 
                max_length, 
                min_releaseyear, 
                max_releaseyear, 
                production_company_id
            ])
            movies = cursor.fetchall()
    else:
        with connection.cursor() as cursor:
            cursor.callproc('get_all_movies_with_directors_and_companies')
            movies = cursor.fetchall()

    movies_list = [
        {
            'movie_id': movie[0],
            'moviename': movie[1],
            'length': movie[2],
            'releaseyear': movie[3],
            'plot_summary': movie[4],
            'resource_link': movie[5],
            'production_company_name': movie[6],
            'directors': movie[7]
        }
        for movie in movies
    ]

    return render(request, 'list_movies.html', {'movies': movies_list, 'production_companies': production_companies_list})


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
        print(selected_directors_json)
        return render(request, 'update_movie.html', {  
            'form': form,  
            'selected_directors_json': selected_directors_json,  
        })
        
    
def delete_video_file(file_path):
    # 从文件路径中提取文件名
    filename = os.path.basename(file_path)
    # 构建完整的文件路径
    file_path = os.path.join(settings.MEDIA_ROOT, 'videos', filename)
    # 如果文件存在，删除它
    if os.path.exists(file_path):
        os.remove(file_path)

def delete_movie(request, movie_id):
    # 获取电影对象
    movie = Movie.objects.get(pk=movie_id)
    if request.method == 'POST':
        # 删除视频文件
        delete_video_file(movie.resource_link)
        # 调用存储过程删除电影
        with connection.cursor() as cursor:
            cursor.callproc('delete_movie', [movie_id])
        return redirect('list_movies')
    return render(request, 'delete_movie_confirmation.html', {'movie': movie})

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

@csrf_exempt
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
    
@csrf_exempt
def delete_person(request, person_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.callproc('delete_person', [person_id])

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
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
