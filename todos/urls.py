from django.urls import path
from . import views
# from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView,LogoutView


urlpatterns = [
    
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task_list/', views.task_list, name = 'task_list'),
    path('task_list/completed/', views.completed_tasks_view, name='completed_tasks'),
    path('task_list/upcoming/', views.upcoming_tasks_view, name='upcoming_tasks'),
    path('task_list/overdue', views.overdue_tasks_view, name='overdue_tasks'),
    path('notifications/mark_read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('create_task/', views.create_task, name = 'create_task'),
    path('task/task_detail/<int:pk>/', views.task_detail_view, name='task_detail'),
    path('task/<int:pk>/edit/', views.edit_task_view, name='edit_task'),
    path('task/<int:pk>/toggle/', views.toggle_task_complete_view, name='toggle_complete'),
    path('tasks/<int:pk>/update-description/', views.update_description_view, name='update_description'),

    path('task/<int:pk>/delete/', views.delete_task_view, name='delete_task'),

    
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_View, name='login'),
    # path('login/', LoginView.as_view(template_name='todos/login.html'), name='login'),
    # path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('logout/', views.logout_View, name='logout'),
    path('register/', views.register, name='register'),
    path('search_tasks/', views.task_list, name = 'search_tasks'),
    
    # path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
    # path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
]