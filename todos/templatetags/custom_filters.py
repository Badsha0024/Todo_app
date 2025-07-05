# todos/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_username_from_email(email):
    return email.split('@')[0] if '@' in email else email
