from django.contrib.admin import ModelAdmin, register

from .models import CustomUser, Follow


@register(CustomUser)
class UserAdmin(ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = ('username', 'email')
    save_on_top = True
    empty_value_display = '-пусто-'


@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ('following', 'author',)
    search_fields = (
        'author__following',
        'author__email',
        'user __following',
        'user__email',
    )
    list_per_page = 20
    save_on_top = True
    empty_value_display = '-пусто-'
