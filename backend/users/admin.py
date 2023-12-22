from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscriptions


@register(CustomUser)
class MyUserAdmin(UserAdmin):
    """Модель пользователей в админке."""

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_active',
    )
    list_display_links = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    fields = (
        ('is_active',),
        ('username',),
        ('email',),
        ('first_name',),
        ('last_name',),
    )
    fieldsets = []
    search_fields = ('username', 'email', 'first_name', 'last_name',)
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
        'user__username',
        'author__username'
    )
    list_filter = (
        'user',
        'author',
    )
    empty_value_display = '-empty-'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'author')
