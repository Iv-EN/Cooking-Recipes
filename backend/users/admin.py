from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscriptions


@register(CustomUser)
class MyUserAdmin(UserAdmin):
    """Модель пользователей в админке."""

    list_display = (
        'is_active',
        'username',
        'first_name',
        'last_name',
        'email',
        'password',
    )
    fields = (
        ('is_active',),
        ('password',),
        ('username',),
        ('email',),
        ('first_name',),
        ('last_name',),
    )
    fieldsets = []
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'first_name', 'email',)
    save_on_top = True


@register(Subscriptions)
class SubscriptionsAdmin(ModelAdmin):
    """Модель подписок в админке."""

    list_display = (
        'pk',
        'user',
        'author',
    )
    search_fields = (
        'user',
        'author'
    )
    list_filter = (
        'user',
        'author',
    )
    empty_value_display = '-empty-'

    def get_subscriber_username(self, obj):
        return obj.user.username

    def get_author_username(self, obj):
        return obj.author.username
