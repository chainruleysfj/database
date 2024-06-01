from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.urls import reverse
from django.db import connection
from .models import Movie, ProductionCompany
from .forms import ProductionCompanyForm
import json


def home(request):
    return render(request, 'home.html')  # 创建一个名为 home.html 的模板文件，并返回给客户端

@csrf_exempt
def add_movie(request):
    if request.method == 'POST':
        # 获取请求的Content-Type头
        content_type = request.headers.get('Content-Type')
        print(content_type)
        print(request.body)
        # 检查Content-Type头是否为application/json
        if content_type != 'application/json':
            return JsonResponse({'error': 'Invalid Content-Type'}, status=400)
        try:
            data = json.loads(request.body)
            print("data ok")
            
            production_company = ProductionCompany.objects.get(id=data['production_company_id'])
            print("company ok")
            movie = Movie.objects.create(
                moviename=data['moviename'],
                length=data['length'],
                releaseyear=data['releaseyear'],
                plot_summary=data['plot_summary'],
                resource_link=data['resource_link'],
                production_company=data['production_company']
            )
            print('movie ok')
            return JsonResponse({'message': 'Movie added successfully!'}, status=201)
        except ProductionCompany.DoesNotExist:
            return JsonResponse({'error': 'Production Company does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data in request body'}, status=400)
    else:
        return render(request, 'add_movie.html')

@csrf_exempt
def update_movie(request, id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            movie = Movie.objects.get(id=id)
            production_company = ProductionCompany.objects.get(id=data['production_company_id'])
            movie.moviename = data['moviename']
            movie.length = data['length']
            movie.releaseyear = data['releaseyear']
            movie.plot_summary = data['plot_summary']
            movie.resource_link = data['resource_link']
            movie.production_company = production_company
            movie.save()
            return JsonResponse({'message': 'Movie updated successfully!'}, status=200)
        except Movie.DoesNotExist:
            return JsonResponse({'error': 'Movie does not exist'}, status=400)
        except ProductionCompany.DoesNotExist:
            return JsonResponse({'error': 'Production Company does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def delete_movie(request, id):
    if request.method == 'DELETE':
        try:
            movie = Movie.objects.get(id=id)
            movie.delete()
            return JsonResponse({'message': 'Movie deleted successfully!'}, status=200)
        except Movie.DoesNotExist:
            return JsonResponse({'error': 'Movie does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

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