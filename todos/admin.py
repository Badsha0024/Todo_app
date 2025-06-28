from django.contrib import admin
from .models import Category, Task, Notification, UserProfile


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
    
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message',)
    
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture')
    search_fields = ('user__username', 'user__email')
    
    def has_add_permission(self, request):
        return False
