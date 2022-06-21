from django.urls import path
from . import views


urlpatterns = [
    path('<int:todo_pk>', views.view_todo, name='view_todo'),
    path('<int:todo_pk>/complete', views.complete_todo, name='complete_todo'),
    path('<int:todo_pk>/delete', views.delete_todo, name='delete_todo'),
]
