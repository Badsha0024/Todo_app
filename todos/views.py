from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, TaskForm
from .models import Task, Category, Notification
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
    
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, completed=True).count()
    upcoming_tasks = Task.objects.filter(user=request.user, completed=False, due_date__gte=timezone.now())
    overdue_tasks = Task.objects.filter(user=request.user, completed=False, due_date__lt=timezone.now())
    recent_todos = Task.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    
    # Create Notification for tomorrow tasks
    for task in upcoming_tasks:
        task.status = 'I'  # Update status to 'I' for upcoming tasks
        task.save()
        
        if not task.notification_set.filter(message__icontains="due tomorrow").exists():
            is_due_tomorrow = task.due_date == (timezone.now() + timezone.timedelta(days=1)).date()
            if is_due_tomorrow:
                Notification.objects.create(
                    user=request.user,
                    task=task,
                    message=f"🔔 Reminder: Task '{task.title}' is due tomorrow on {task.due_date.strftime('%Y-%m-%d')}."
                )
              
    # Create Notification for overdue tasks    
    for task in overdue_tasks:
        task.status = 'O' 
        task.save()
        
        if not task.notification_set.filter(message__icontains="overdue").exists():
            
            Notification.objects.update_or_create(
                user=request.user,
                task=task,
                is_read=False,
                message=f"⚠️ Task '{task.title}' is overdue! Please check it out."
            )
            
    notifications = request.user.notifications.all()
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'upcoming_tasks': upcoming_tasks.count(),
        'overdue_tasks': overdue_tasks.count(),
        'recent_todos': recent_todos,
        'notifications': notifications,
        'unread_count': unread_count,
    }
    # console.log(context)
    messages.success (request, "You are in dashboard")
    return render(request, "todos/dashboard.html", context)


@login_required
def mark_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({"status": "ok"})

@login_required
def create_task(request):
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # set the current user
            task.save()
            
            messages.success(request, "Task created successfully!")
            return redirect('task_list')  # update with your actual url name
    else:
        form = TaskForm()
    return render(request, 'todos/create_task.html', {'form': form})

@login_required
def task_list(request):
    
    tasks = Task.objects.filter(user=request.user).order_by('status', '-created_at')
    categories = Category.objects.all()
    
    query = request.GET.get("q", "")
    category_id = request.GET.get("category", "")
    
    category_name = categories.filter(id=category_id).first() if category_id else None

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category_id:
        tasks = tasks.filter(category_id=category_id)

    context = {
        'tasks': tasks,
        'query': query,
        'categories': categories,
        'selected_category': category_id,
        'category_name': category_name,
    }
    
    return render(request, 'todos/task_list.html', context)

@login_required
def completed_tasks_view(request):
    
    completed_tasks = Task.objects.filter(user=request.user, completed=True)
    
    for task in completed_tasks:
        task.status = 'C'# Update status to 'C' for completed tasks
        task.save()

    context = {
        
        'tasks': completed_tasks,
        'page_title': 'Completed Tasks'
    }

    return render(request, 'todos/task_list.html', context)

@login_required
def upcoming_tasks_view(request):
    
    upcoming_tasks = Task.objects.filter(user=request.user,completed=False,due_date__gte=timezone.now()
    ).order_by('status','due_date')
    
    for task in upcoming_tasks:
        task.status = 'I'  # Update status to 'I' for upcoming tasks
        task.save()
            
    context = {
        'tasks': upcoming_tasks,
        'page_title': 'Upcoming Tasks'
    }
    return render(request, 'todos/task_list.html', context)


@login_required
def overdue_tasks_view(request):
    
    overdue_tasks = Task.objects.filter(user=request.user,completed=False,due_date__lt=timezone.now()
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
def task_detail_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'todos/task_detail.html', {'task': task})


@login_required
def edit_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'todos/create_task.html', {'form': form})

@login_required
@require_POST
def toggle_task_complete_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.status = 'C' if task.completed else 'I'
    task.save()
    return redirect('task_detail', pk=pk)

@login_required
def update_description_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == "POST":
        new_description = request.POST.get("description", "")
        task.description = new_description
        task.save()
        messages.success(request, "Task description updated successfully.")
        return redirect('task_detail', pk=pk)

    return redirect('task_detail', pk=pk)


@login_required
def delete_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        
        task.delete()
        messages.success(request, f"Task '{task.title}' has been deleted successfully.")
        return redirect('task_list')
    
    return render(request, 'todos/task_confirm_delete.html', {'task': task})


@login_required
def search_task_view(request):
    
    query = request.GET.get("q", "")
    category_id = request.GET.get("category", "")
    source = request.GET.get('source', 'Your')  # Default to "Your" if none provided
    
    tasks = Task.objects.filter(user=request.user)

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category_id:
        tasks = tasks.filter(category_id=category_id)

    categories = Category.objects.all()
    category_name = categories.filter(id=category_id).first() if category_id else None
    
    context = {
        'tasks': tasks,
        'query': query,
        'categories': categories,
        'selected_category': category_id,
        'category_name': category_name,
    }

    return render(request, 'todos/search_results.html', context)


def profile(request):
    return HttpResponse("this is profile")
 

    
