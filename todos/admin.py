from django.contrib import admin
from .models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'category', 'title', 'due_date', 'completed',
        'priority', 'status', 'created_at', 'updated_at', 'user'
    )
    list_filter = ('completed', 'category', 'priority', 'status', 'user')
    search_fields = ('title', 'description')
    
    ordering = ('user', 'pk',)  # New ordering here
