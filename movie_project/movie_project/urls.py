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
    path('home/', views.home, name='home'),  # 添加一个根路径的视图处理器
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
    path('add_person/', views.add_person, name='add_person'), #添加人物
    path('persons/', views.list_persons, name='list_persons'), #人物一览
    path('update_person/<int:person_id>/', views.update_person, name='update_person'), #更新人物
    path('delete_person/<int:person_id>/', views.delete_person, name='delete_person'), #删除人物
    path('search_persons/', views.search_persons, name='search_persons'), #查询人物
    path('search_person_by_name/', views.search_person_by_name, name='search_person_by_name'), #按姓名查询人物
    path('all_directors/', views.all_directors, name='all_directors'), #查看导演
    path('manage_genres/', views.manage_genres, name='manage_genres'), #管理电影类型
    path('register/', views.register_view, name='register'), #用户注册
    path('generate-captcha/', views.generate_captcha, name='generate_captcha'), #验证码
    path('', views.login_view, name='login'), #用户登录
    path('logout/', views.logout_view, name='logout'), #用户登出
    path('manage_admins/', views.manage_admins, name='manage_admins'), #超级管理员管理普通管理员
    path('add_admin/<int:user_id>/', views.add_admin, name='add_admin'), #添加管理员
    path('toggle_staff_status/<int:user_id>/', views.toggle_staff_status, name='toggle_staff_status'), #用户状态显示
    path('movies/<int:pk>/comment/', views.add_comment, name='add_comment'),#添加评论
    path('approve-comments/', views.approve_comments, name='approve_comments'),#审核评论
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),#删除评论
    path('toggle_staff_status/<int:user_id>/', views.toggle_staff_status, name='toggle_staff_status'), #管理状态显示
    path('delete_account/', views.delete_account, name='delete_account'), #删除自己的账户
    path('manage_users/', views.manage_users, name='manage_users'), #管理员管理用户
    path('admin_delete_user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'), #管理员删除他人账户
    path('change-password/', views.change_password, name='change_password'), #更改密码
    path('set-security-question/', views.set_security_question, name='set_security_question'), #添加安全问题
    path('reset-password/', views.reset_password, name='reset_password'), #重置密码
    path('user/<str:username>/', views.user_homepage, name='user_homepage'),#用户主页
    path('search_users/', views.search_users, name='search_users'),#搜索用户
    path('add_role/', views.add_role, name='add_role'), #增添角色
    path('roles/', views.role_list, name='role_list'),
    path('roles/<int:role_id>/', views.role_detail, name='role_detail'),
    path('roles/<int:role_id>/edit/', views.edit_role, name='edit_role'),
    path('roles/<int:role_id>/delete/', views.delete_role, name='delete_role'),
    path('roles/<int:role_id>/edit_actor_movie/', views.edit_role_actor_movie, name='edit_role_actor_movie'),
    path('search_roles_by_name/', views.search_roles_by_name, name='search_roles_by_name'),
    path('search_roles_by_actor/', views.search_roles_by_actor, name='search_roles_by_actor'),
    path('search_roles_by_movie/', views.search_roles_by_movie, name='search_roles_by_movie'),
    path('search_role/', views.search_role, name='search_role'),  # 新增的搜索选择页面
    path('actors/', views.list_actors, name='list_actors'),#列举演员
    path('movie/<int:movie_id>/actors/', views.movie_actors, name='movie_actors'),
    path('person/<int:person_id>/movies/', views.person_movies, name='person_movies'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
