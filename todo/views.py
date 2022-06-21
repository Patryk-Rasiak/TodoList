from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import TodoForm, CustomUserCreationForm, TagForm
from .models import Todo, Tag
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
import json
from datetime import datetime


class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login_user')
    template_name = 'todo/signupuser.html'


def home(request):
    return render(request, 'todo/home.html')


def login_user(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username and password did not match.'})
        else:
            login(request, user)
            return redirect('current_todos')


def sign_up_user(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('current_todos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'That username has already been taken. Please choose a new username.'})
        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Passwords did not match.'})


@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def create_tag(request):
    if request.method == 'POST':
        post_data = json.loads(request.body.decode('utf-8'))
        form = TagForm(post_data)

        if (not form.is_valid()) or Tag.objects.filter(user=request.user, title=post_data['title']).count() > 0:
            return JsonResponse({'error': 'Bad data passed in!'})

        new_tag = form.save(commit=False)
        new_tag.user = request.user
        new_tag.save()

        return JsonResponse({'title': new_tag.title})


@login_required
def create_todo(request):

    if request.method == 'GET':
        tags = Tag.objects.filter(
            user=request.user).order_by('title')
        return render(request, 'todo/createtodo.html', {'form': TodoForm(), 'tags': tags})
    else:
        form = TodoForm(request.POST)
        if not form.is_valid():
            return render(request, 'todo/createtodo.html', {'form': TodoForm(), 'error': form.errors})
        new_todo = form.save(commit=False)
        new_todo.user = request.user
        new_todo.save()

        return redirect('current_todos')


@login_required
def current_todos(request):
    if request.method == 'GET':
        todos = Todo.objects.filter(
            user=request.user, date_completed__isnull=True).order_by('-created')
        times_remaining, labels = update_times(todos)
        tags = Tag.objects.filter(
            user=request.user).order_by('title')
        return render(request, 'todo/currenttodos.html', {'todos': todos, 'tags': tags, 'times': times_remaining, 'labels': labels})
    else:
        post_data = json.loads(request.body.decode("utf-8"))
        post_tag = post_data.get('tag')
        post_title = post_data.get('title')
        post_sort = post_data.get('sort')

        if post_tag == "All":
            todos = Todo.objects.filter(
                user=request.user, date_completed__isnull=True, title__icontains=post_title
            ).order_by(post_sort)
        else:
            todos = Todo.objects.filter(
                user=request.user, date_completed__isnull=True, tag=post_tag, title__icontains=post_title
            ).order_by(post_sort)
        times_remaining, labels = update_times(todos)
        data = list(todos.values())

        return JsonResponse({'todos': data, 'times': times_remaining, 'labels': labels})


@login_required
def completed_todos(request):
    todos = Todo.objects.filter(
        user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, 'todo/completedtodos.html', {'todos': todos})


@login_required
def view_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    tags = Tag.objects.filter(
        user=request.user).order_by('title')
    if request.method == 'GET':
        form = TodoForm(instance=todo)

        deadline = todo.deadline.strftime(
            "%Y-%m-%dT%H:%M") if todo.deadline else None

        return render(request, 'todo/viewtodo.html', {'todo': todo, 'tags': tags, 'deadline': deadline, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            update_tags(request.user)
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'tags': tags, 'form': form, 'error': 'Bad info'})


@login_required
def complete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.date_completed = timezone.now()
        todo.save()
        update_tags(request.user)
        post_data = json.loads(request.body.decode("utf-8"))
        post_tag = post_data.get('tag')
        post_title = post_data.get('title')
        post_sort = post_data.get('sort')
        if post_tag == "All":
            todos = Todo.objects.filter(
                user=request.user, date_completed__isnull=True, title__icontains=post_title).order_by(post_sort)

        else:
            todos = Todo.objects.filter(
                user=request.user, date_completed__isnull=True, tag=post_tag, title__icontains=post_title).order_by(post_sort)
        times_remaining, labels = update_times(todos)
        return JsonResponse({'todos': list(todos.values()), 'times': times_remaining, 'labels': labels})


@login_required
def delete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        update_tags(request.user)
        return redirect('current_todos')


# Remove all unused tags
def update_tags(user):
    tags_count = dict.fromkeys(
        Tag.objects.filter(user=user).values_list('title', flat=True), 0)
    todos = Todo.objects.filter(user=user, date_completed__isnull=True)
    for todo in todos:
        if todo.tag != 'None':
            tags_count[todo.tag] += 1

    for tag, count in tags_count.items():
        if count == 0:
            Tag.objects.get(user=user, title=tag).delete()


def update_times(todos):
    times_remaining = []
    labels = []
    for todo in todos:
        if todo.deadline:
            time_remaining = int((
                todo.deadline - timezone.now()).total_seconds())
            if time_remaining >= 86400:
                time_remaining //= 86400
                label = "day"
            elif time_remaining >= 3600:
                time_remaining //= 3600
                label = "hour"
            elif time_remaining >= 60:
                time_remaining //= 60
                label = "minute"
            elif time_remaining > 0:
                time_remaining = 1
                label = "less than a minute"
            else:
                time_remaining = 0
                label = "time's up"
            labels.append(label)
            times_remaining.append(time_remaining)

        else:
            times_remaining.append(0)
            labels.append("")

    return times_remaining, labels
