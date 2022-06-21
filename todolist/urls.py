"""todolist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib.auth.views import LoginView
from django.contrib import admin
from django.urls import path, include
from todo import views
from todo.views import SignUp

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('sign_up/', views.sign_up_user, name='sign_up_user'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),

    # Todos
    path('', views.home, name='home'),
    path('current/', views.current_todos, name='current_todos'),
    path('completed/', views.completed_todos, name='completed_todos'),
    path('create/ ', views.create_todo, name='create_todo'),
    path('create_tag/', views.create_tag, name="create_tag"),
    path('todo/', include('todo.urls')),
]
