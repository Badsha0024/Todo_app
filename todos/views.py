from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, TaskForm, UserEditForm, ProfilePictureForm, ForgotPasswordForm, ResetPasswordForm
from .models import Task, Category, Notification
from django.utils import timezone
from django.db.models import Q

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import CustomPasswordChangeForm



# password reset imports
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import PasswordResetToken
from django.contrib.auth.hashers import make_password

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.contrib import messages
from django.urls import reverse

# Create your views here.
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
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        remember = request.POST.get('rememberMe')  # ✅ This line is important

        user = authenticate(request, username=username_or_email, password=password)
        if user is not None:
            login(request, user)
            if remember:
                # Set session to expire in 30 days
                request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                # Expire session when browser is closed
                request.session.set_expiry(0)
        
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')  # or wherever you want
        else:
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'todos/login.html')


def logout_View(request):

    messages.success(request, "You have been logged out successfully.")
    logout(request)
    return redirect('login')


def home_view(request):
    return render(request, 'todos/home.html')

    

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
def task_card_view(request):
    tasks = Task.objects.filter(user=request.user).order_by('-status', 'due_date', '-created_at')
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
        'page_title': None
    }

    return render(request, 'todos/task_card_list.html', context)


@login_required
def task_list(request):
    
    tasks = Task.objects.filter(user=request.user).order_by('-status', 'due_date', '-created_at')
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
    
    return render(request, 'todos/task_list_LISTView.html', context)


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


@login_required
def profile_view(request):
    
    total_tasks = request.user.tasks.count()
    completed_tasks = request.user.tasks.filter(status='C').count()
    pending_tasks = request.user.tasks.filter(status='P').count()
    recent_tasks = request.user.tasks.order_by('-created_at')[:5]
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'todos/profile.html', context)


@login_required
def edit_profile(request):
    
    user = request.user
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfilePictureForm(request.POST, request.FILES, instance=user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfilePictureForm(instance=user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'todos/edit_profile.html', context)
    
 
class CustomPasswordChangeView(PasswordChangeView):
    
    form_class = CustomPasswordChangeForm
    template_name = 'todos/password_change.html'
    messages = {
        'success': 'Your password was changed successfully.',
        'invalid_password': 'Please enter a correct old password.',
    }
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        logout(self.request)
        return response

# Helper function to mask email
def mask_email(email):
    name, domain = email.split('@')
    visible = max(1, int(len(name) * 0.3))
    return name[:visible] + "***@" + domain

def forgot_password(request):
    
    form = ForgotPasswordForm()
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(reverse('reset_password', kwargs={'uidb64': uid, 'token': token}))

                send_mail(
                    'Reset Your Password',
                    f'Click the link to reset your password: {reset_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                # masked = mask_email(email)#30% email
                return render(request, 'todos/email_sent.html', {
                    'username': user.username,
                    'masked_email': email
                })
            except User.DoesNotExist:
                return render(request, 'todos/email_not_found.html', {'email': email})
    return render(request, 'todos/forgot_password.html', {'form': form})

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        form = ResetPasswordForm()
        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['password'])
                user.save()
                return render(request, 'todos/password_reset_success.html')
        return render(request, 'todos/reset_password.html', {'form': form})
    else:
        return render(request, 'todos/invalid_link.html')

