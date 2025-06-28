from .models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        return {
            'notifications': Notification.objects.filter(user=request.user, is_read=False)[:5]
        }
    return {}
