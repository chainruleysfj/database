"""
URL configuration for movie_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from movie_app import views

urlpatterns = [
    path('', views.home, name='home'),  # 添加一个根路径的视图处理器
    path('admin/', admin.site.urls),  #管理员
    path('add_production_company/', views.add_production_company, name='add_production_company'), #添加电影公司
    path('production_companies/', views.list_production_companies, name='list_production_companies'), #公司一览
    path('update_production_company/<int:company_id>/', views.update_production_company, name='update_production_company'), #修改电影公司
    path('delete_production_company/<int:company_id>/', views.delete_production_company, name='delete_production_company'), #删除电影公司
    path('search_production_companies/', views.search_production_companies, name='search_production_companies'), #查询电影公司
    path('add_movie/', views.add_movie, name='add_movie'), #添加电影
    path('movies/', views.list_movies, name='list_movies'), #电影一览
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'), # 单个电影的详细信息
    path('movies/<int:movie_id>/update/', views.update_movie, name='update_movie'), # 更新电影
    path('movies/<int:movie_id>/delete/', views.delete_movie, name='delete_movie'), # 删除电影
    path('movies/search/', views.list_movies, name='search_movies'),  # 查询电影
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
