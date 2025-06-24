from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, TaskForm
from .models import Task, Category
from django.utils import timezone
from django.db.models import Q



def register(request):
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Save user object but don't write to DB yet
            # user.email = request.POST.get('email')
            user.is_staff = True 
            user.save()  # Now save to DB
            messages.success(request, f"Account created for {user.username}!")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'todos/register.html', {'form': form})


def login_View(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')  # or wherever you want
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'todos/login.html')

def logout_View(request):

    messages.success(request, "You have been logged out successfully.")
    logout(request)
    return redirect('login')  # or 'dashboard'



@login_required
def dashboard(request):
    
    user = request.user

    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, completed=True).count()
    upcoming_tasks = Task.objects.filter(user=request.user, completed=False, due_date__gte=timezone.now()).count()
    overdue_tasks = Task.objects.filter(user=request.user, completed=False, due_date__lt=timezone.now()).count()
    
    recent_todos = Task.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'upcoming_tasks': upcoming_tasks,
        'overdue_tasks': overdue_tasks,
        'recent_todos': recent_todos,
    }
    # console.log(context)
    
    messages.success (request, "You are in dashboard")
    return render(request, "todos/dashboard.html", context)

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # set the current user
            task.save()
            return redirect('task_list')  # update with your actual url name
    else:
        form = TaskForm()
    return render(request, 'todos/create_task.html', {'form': form})

@login_required
def task_list(request):
    
    categories = Category.objects.all()
    tasks = Task.objects.filter(user=request.user).order_by('status', '-created_at')
    
    context = {
    'tasks': tasks,
    'categories': categories,
}
    return render(request, 'todos/task_list.html', context)

@login_required
def completed_tasks_view(request):
    completed_tasks = Task.objects.filter(user=request.user, completed=True)

    context = {
        'tasks': completed_tasks,
        'page_title': 'Completed Tasks'
    }

    return render(request, 'todos/task_list.html', context)

@login_required
def upcoming_tasks_view(request):
    upcoming_tasks = Task.objects.filter(
        user=request.user,
        completed=False,
        due_date__gte=timezone.now()
    ).order_by('status','due_date')

    context = {
        'tasks': upcoming_tasks,
        'page_title': 'Upcoming Tasks'
    }
    return render(request, 'todos/task_list.html', context)


@login_required
def overdue_tasks_view(request):
    
    overdue_tasks = Task.objects.filter(
        user=request.user,
        completed=False,
        due_date__lt=timezone.now()
    ).order_by('due_date')
    for task in overdue_tasks:
        task.status = 'O' 
        task.save()

    context = {
        'tasks': overdue_tasks,
        'page_title': 'Overdue Tasks'
    }
    return render(request, 'todos/task_list.html', context)

@login_required
def tasks_by_category(request, index):
    # Get all categories ordered by ID (or name, or any consistent field)
    categories = list(Category.objects.order_by('id'))

    # Index must be 1-based as per your request, so subtract 1
    if 1 <= index <= len(categories):
        category = categories[index - 1]
    else:
        # If index is out of range, show 404
        return render(request, '404.html', status=404)

    tasks = Task.objects.filter(user=request.user, category=category)

    return render(request, 'todos/task_list_by_category.html', {
        'category': category,
        'tasks': tasks,
    })
    # category = get_object_or_404(Category, slug=slug)
    # tasks = Task.objects.filter(user=request.user, category=category).order_by('-created_at')
    
    # context = {
    #     'tasks': tasks,
    # }
    # return render(request, 'todos/task_list_by_category.html', {
    #     'category': category,
    #     'tasks': tasks,
    # })
    
    # return render(request, 'todos/task_list.html',context)



@login_required
def edit_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'GET':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'todos/create_task.html', {'form': form})


@login_required
def delete_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'todos/task_confirm_delete.html', {'task': task})


@login_required
def search_task_view(request):
    query = request.GET.get("q")
    tasks = []
    
    
    if query: 
        tasks = Task.objects.filter(
            Q(user=request.user),
            Q(title__icontains=query) | Q(description__icontains=query) | Q(status__icontains=query)
        ).order_by('-created_at')

    # if query:
    #     tasks = Task.objects.filter(
    #         user=request.user,
    #         title__icontains=query  # search in title, case-insensitive
    #     ).order_by('-created_at')

    return render(request, 'todos/search_results.html', {'tasks': tasks, 'query': query})

# def edit_task(request):
#     return HttpResponse("this is edit_task")

# def delete_task(request):
#     return HttpResponse("this is delete_task")

def todo_list(request):
    return HttpResponse("this is todo list")

def todo_create(request):
    return HttpResponse("this is todo_create")

def category_todos(request):
    return HttpResponse("this is category_todos")

def profile(request):
    return HttpResponse("this is profile")
    
def todo_search(request):
    return HttpResponse("this is todo_search")

    
