from .models import Rubric, AdvUser, Article
from django.utils import timezone
from . import forms
import datetime
from django.contrib import messages
from .views import get_subscribes
from django.urls import reverse_lazy
from django.conf import settings


def news_context_processor(request):
    """Контекстный процессор для приложения новостей"""

    context = {
        'rubrics': Rubric.objects.all(),
        'authors': AdvUser.objects.filter(is_active=True).order_by('-publications')[:5],
        'time_now': datetime.datetime.now(),
    }

    articles = []

    for i in Article.objects.order_by('-views'):
        if i.pub_date >= (timezone.now() - datetime.timedelta(days=30)):
            articles.append(i)

    articles = articles[:10]
    context['articles'] = articles

    if request.user.is_authenticated:
        context['user'] = AdvUser.objects.get(pk=request.user.pk)
        subscribes = get_subscribes(request.user.pk)
        context['subscribes'] = subscribes[:5]
        context['subscribes_count'] = len(subscribes)

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        context['keyword'] = '?keyword=' + keyword
    else:
        keyword = ''
        context['keyword'] = keyword

    if 'show' in request.GET:
        show = request.GET['show']
        context['show'] = '?show=' + show
    else:
        show = ''
        context['show'] = show

    if 'sort' in request.GET:
        sort = request.GET['sort']
        if context['keyword'] != '':
            context['sort'] = '&sort=' + sort
        else:
            context['sort'] = '?sort=' + sort
    else:
        sort = ''
        context['sort'] = sort

    if 'page' in request.GET:
        page = request.GET['page']
        if page != '1':
            if keyword != '' or sort != '' or show != '':
                context['page'] = '&page' + page
            else:
                context['page'] = '?page' + page

    context['all'] = context['keyword'] + context['show'] + context['sort']

    searchform = forms.SearchForm(initial={'keyword': keyword})
    context['searchform'] = searchform

    if 'key' in request.GET:
        context['key'] = request.GET['keyword']
    else:
        context['key'] = ''

    if request.user.is_authenticated:
        if not request.user.is_activated:
            if len(settings.ALLOWED_HOSTS) > 0:
                host = 'https://' + settings.ALLOWED_HOSTS[0]
            else:
                host = 'http://127.0.0.1:8000'

            messages.info(request, 'На Вашу эл.почту была отправлена ссылка для подтверждения эл.почты, перейдите по '
                                   'ней. Для повторной отправки ссылки, нажмите <a href="' + host + str(reverse_lazy(
                'news:send_activation')) + '">сюда</a>.')

    return context
