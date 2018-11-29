import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from blog.models import Blog
from read_statistic.utils import get_seven_day_read_data, get_yesterday_hot_data


def get_today_hot_data():
    today = timezone.now().date()
    read_details = Blog.objects.filter(read_details__date=today)
    return read_details[:7]


def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today,
                                read_details__date__gte=date).values('id',
                                                                     'title').annotate(
        read_num_sum=Sum('read_details__read_num')).order_by('-read_num_sum')
    return blogs[:7]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_day_read_data(blog_content_type)

    # 获取7天热门数据的缓存表
    hot_blog_for_seven_days = cache.get('hot_blog_for_seven_days')
    if hot_blog_for_seven_days is None:
        hot_blog_for_seven_days = get_7_days_hot_blogs()
        cache.set('hot_blog_for_seven_days', hot_blog_for_seven_days, 3600)
        print('cache')
    else:
        print('use cache')
    yesterday_hot_data = get_yesterday_hot_data(blog_content_type)

    context = {'dates': dates, 'read_nums': read_nums,
               'today_hot_data': get_today_hot_data,
               'yesterday_hot_data': yesterday_hot_data,
               'hot_blog_for_seven_days': hot_blog_for_seven_days}

    return render(request, 'home.html', context)


