from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView,LogoutView


urlpatterns = [
    
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task_list/', views.task_list, name = 'task_list'),
    path('task_list/completed/', views.completed_tasks_view, name='completed_tasks'),
    path('task_list/upcoming/', views.upcoming_tasks_view, name='upcoming_tasks'),
    path('task_list/overdue', views.overdue_tasks_view, name='overdue_tasks'),
    
    
    path('notifications/mark_read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('create_task/', views.create_task, name = 'create_task'),
    path('search_tasks/', views.task_list, name = 'search_tasks'),
    path('task/task_detail/<int:pk>/', views.task_detail_view, name='task_detail'),
    path('task/<int:pk>/edit/', views.edit_task_view, name='edit_task'),
    path('task/<int:pk>/toggle/', views.toggle_task_complete_view, name='toggle_complete'),
    path('tasks/<int:pk>/update-description/', views.update_description_view, name='update_description'),
    path('task/<int:pk>/delete/', views.delete_task_view, name='delete_task'),

    
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),

    # path('login/', LoginView.as_view(template_name='todos/login.html'), name='login'),
    # path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('login/', views.login_View, name='login'),
    path('logout/', views.logout_View, name='logout'),
    path('register/', views.register, name='register'),
    
    
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),    
    
]

