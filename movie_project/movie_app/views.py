from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.urls import reverse
from django.db import connection
from django.conf import settings
from .models import Movie, ProductionCompany
from .forms import ProductionCompanyForm,MovieForm
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
        cursor.execute("SELECT id, name, city, company_description FROM movie_app_productioncompany WHERE id = %s", [company_id])
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
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
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
            return redirect('list_movies')
    else:
        form = MovieForm()
    return render(request, 'add_movie.html', {'form': form})

def save_video_file(video_file):
    unique_filename = str(uuid.uuid4()) + '.mp4'
    file_path = os.path.join(settings.MEDIA_ROOT, 'videos', unique_filename)
    with open(file_path, 'wb+') as destination:
        for chunk in video_file.chunks():
            destination.write(chunk)
    return os.path.join(settings.MEDIA_URL, 'videos', unique_filename)

def list_movies(request):
    with connection.cursor() as cursor:
        cursor.callproc('get_all_movies')
        movies = cursor.fetchall()
    movies_list = [
        {
            'movie_id': movie[0],
            'moviename': movie[1],
            'length': movie[2],
            'releaseyear': movie[3],
            'plot_summary': movie[4],
            'resource_link': movie[5],
            'production_company_id': movie[6]
        } for movie in movies
    ]
    return render(request, 'list_movies.html', {'movies': movies_list})


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
    movie = Movie.objects.get(pk=movie_id)

    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            updated_movie = form.save(commit=False)
            # 检查是否上传了新视频文件
            if 'video_file' in request.FILES:
                video_file = request.FILES['video_file']
                # 生成唯一的文件名
                unique_filename = str(uuid.uuid4()) + '.mp4'
                # 保存新视频文件到指定目录
                file_path = os.path.join(settings.MEDIA_ROOT, 'videos', unique_filename)
                with open(file_path, 'wb+') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)
                # 删除原视频文件
                if movie.resource_link:
                    old_video_path = os.path.join(settings.MEDIA_ROOT, movie.resource_link.lstrip('/'))
                    if os.path.exists(old_video_path):
                        os.remove(old_video_path)
                # 更新电影的视频链接
                updated_movie.resource_link = os.path.join(settings.MEDIA_URL, 'videos', unique_filename)
            updated_movie.save()
            return redirect('home')
    else:
        form = MovieForm(instance=movie)
    return render(request, 'update_movie.html', {'form': form})