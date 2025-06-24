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
    path('task_list/overdue/', views.overdue_tasks_view, name='overdue_tasks'),

    path('create_task/', views.create_task, name = 'create_task'),
    path('task/<int:pk>/edit/', views.edit_task_view, name='edit_task'),
    path('task/<int:pk>/delete/', views.delete_task_view, name='delete_task'),
    
    # path('category/<slug:slug>/', views.tasks_by_category, name='category_todos'),
    path('category_by_index/<int:index>/', views.tasks_by_category, name='category_todos'),
    # path('category_todos/', views.category_todos, name = 'category_todos'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_View, name='login'),
    # path('login/', LoginView.as_view(template_name='todos/login.html'), name='login'),
    # path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('logout/', views.logout_View, name='logout'),
    path('register/', views.register, name='register'),
    path('search_tasks/', views.search_task_view, name = 'search_tasks'),
    
    # path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
    # path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
]