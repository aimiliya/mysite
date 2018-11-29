from django.contrib import admin
from .models import Coment


@admin.register(Coment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'text', 'comment_time', 'user', 'parent')


