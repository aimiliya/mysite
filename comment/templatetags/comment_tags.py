from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Coment
from ..forms import CommentForm


register = template.Library()


@register.simple_tag()
def get_comment_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return Coment.objects.filter(content_type=content_type, object_id=obj.pk).count()


@register.simple_tag()
def get_comment_form(obj):
    content_type = ContentType.objects.get_for_model(obj)
    form = CommentForm(initial={
        'content_type': content_type,
        'object_id': obj.pk,
        'reply_comment_id': 0
    })
    return form


@register.simple_tag()
def get_comment_list(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comments = Coment.objects.filter(content_type=content_type,
                                     object_id=obj.pk, parent=None)
    return comments.order_by('-comment_time')
