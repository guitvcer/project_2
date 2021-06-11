import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView
)
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.signing import BadSignature, Signer
from django.db.models import Q
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from .models import (
    Article,
    Comment,
    Rubric,
    AdvUser,
    CommentUser,
)
from . import forms
from .utilities import send_activation, send_deleted_notification, get_or_create_subscribers, get_subscribes


def index(request):
    """Главная страница"""

    articles = []
    last_articles = Article.objects.all()
    all_articles = Article.objects.order_by('-views')

    if 'show' in request.GET:
        show = request.GET['show']
    else:
        show = 'day'

    if show == 'week':
        for i in last_articles:
            if i.pub_date >= (timezone.now() - datetime.timedelta(days=7)):
                articles.append(i)
    elif show == 'month':
        for i in all_articles:
            if i.pub_date >= (timezone.now() - datetime.timedelta(days=30)):
                articles.append(i)
    elif show == 'year':
        for i in all_articles:
            if i.pub_date >= (timezone.now() - datetime.timedelta(days=365)):
                articles.append(i)
    elif show == 'subscribes':
        if request.user.is_authenticated:
            subscribes = get_subscribes(AdvUser.objects.get(pk=request.user.pk))
            for i in last_articles:
                if i.author in subscribes:
                    articles.append(i)
    else:
        for i in last_articles:
            if i.pub_date >= (timezone.now() - datetime.timedelta(days=1)):
                articles.append(i)

    paginator = Paginator(articles, 5)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)

    context = {
        'articles': page.object_list,
        'page': page,
        'show': show,
    }
    return render(request, 'index.html', context)


def rubric(request, pk):
    """Показать статьи определенной рубрики"""

    current_rubric = Rubric.objects.get(pk=pk)
    articles = Article.objects.filter(rubric=current_rubric)

    if 'sort' in request.GET:
        sort = request.GET['sort']
    else:
        sort = ''

    if sort == 'views':
        articles = articles.order_by('-views')

    paginator = Paginator(articles, 5)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)

    context = {
        'articles': page.object_list,
        'rubric': rubric,
        'page': page,
        'sort': sort,
        'show_rubrics': True
    }

    return render(request, 'index.html', context)


def search(request):
    """Страница поиска"""

    keyword = request.GET['keyword']

    if keyword == '':
        return redirect(reverse_lazy('news:index'))

    rubrics = Rubric.objects.all()
    users_list = AdvUser.objects.filter(is_active=True)
    articles = Article.objects.all()

    r = Q(rubric_name__icontains=keyword)
    rubrics = rubrics.filter(r)

    u = Q(username__icontains=keyword) | Q(first_name__icontains=keyword) | \
        Q(last_name__icontains=keyword) | Q(email__icontains=keyword)

    users_list = users_list.filter(u)

    a = Q(title__icontains=keyword) | Q(content__icontains=keyword)
    articles = articles.filter(a)

    search_count = rubrics.count() + users_list.count() + articles.count()

    context = {
        'users_search': users_list,
        'rubrics_search': rubrics,
        'articles_search': articles,
        'key': keyword,
        'search_count': search_count,
        'users_count': users_list.count(),
        'articles_count': articles.count(),
    }

    if 'sort' in request.GET:

        sort = request.GET['sort']
        context['sort'] = sort

        if 'page' in request.GET:
            page_num = request.GET['page']
        else:
            page_num = 1

        paginator = None

        if sort == 'users':
            paginator = Paginator(users, 28)
        elif sort == 'publications':
            paginator = Paginator(articles, 5)

        page = paginator.get_page(page_num)
        context['page'] = page

        if sort == 'users':
            context['users_search'] = page.object_list
        elif sort == 'publications':
            context['articles_search'] = page.object_list

    return render(request, 'searchResults.html', context)


def detail(request, pk):
    """Страница определенной статьи"""

    if 'delete' in request.GET:
        delete = request.GET['delete']
        comment = Comment.objects.get(pk=delete)

        if comment.author.pk == request.user.pk:
            comment.is_active = False
            comment.save()
            messages.success(request, 'Вы успешно удалили комментарий.')

        return redirect(reverse_lazy('news:detail', args=(pk,)))

    article = Article.objects.get(pk=pk)
    comments = Comment.objects.filter(article=article.pk)
    likes = AdvUser.objects.filter(likes=article.pk)
    likes_count = likes.count()

    initial = {'article': article.pk, 'author': request.user.pk}
    form_class = forms.AddCommentForm
    form = form_class(initial=initial)

    if 'edit' in request.GET:
        edit = request.GET['edit']
        comment = Comment.objects.get(pk=edit)

        if comment.author.pk is request.user.pk:
            if request.method == 'POST':
                edit_form = forms.AddCommentForm(request.POST, instance=comment)

                if edit_form.is_valid():
                    instance = edit_form.save(commit=False)
                    instance.is_edited = True
                    instance.save()
                    messages.success(request, 'Вы успешно отредактировали комментарий.')
                else:
                    messages.error(request, 'Комментарий не был отредактирован.')

                return redirect(reverse_lazy('news:detail', args=(pk,)))
    else:
        if request.method == 'POST':
            if not request.user.is_activated:
                messages.warning(request, 'Вам необходимо подтвердить свою эл.почту, чтобы добавить комментарий.')

                return redirect(reverse_lazy('news:detail', args=(pk,)))

            author = request.POST['author']

            if int(author) is request.user.pk:
                c_form = form_class(request.POST)

                if c_form.is_valid():
                    c_form.save()
                    messages.success(request, 'Вы успешно добавили комментарий.')
                else:
                    messages.error(request, 'Комментарий не был добавлен.')

            return redirect(reverse_lazy('news:detail', args=(pk,)))
        else:
            article.views += 1
            article.save()

    context = {
        'article': article,
        'comment_form': form,
        'comments': comments,
        'likes_count': likes_count,
        'likes': likes,
    }

    if 'show' in request.GET:
        show = request.GET['show']
        context['show'] = show
        if show == 'liked_users':
            paginator = Paginator(likes, 28)

            if 'page' in request.GET:
                page_num = request.GET['page']
            else:
                page_num = 1

            page = paginator.get_page(page_num)
            context['page'] = page
            context['likes'] = page.object_list

    return render(request, 'detail.html', context)


@login_required
def edit_article(request, pk):
    """Редактировать статью"""

    article = Article.objects.get(pk=pk)

    if article.author.pk is request.user.pk:
        context = {
            'page_name': 'Редактирование статьи',
            'button_text': 'Отредактировать',
            'article': article,
        }

        if request.method == 'POST':
            form = forms.Add_Article(request.POST, request.FILES, instance=article)

            if form.is_valid():
                form.save()
                messages.success(request, 'Вы успешно отредактировали статью.')

                return redirect(reverse_lazy('news:index'))
            else:
                context['form'] = form
                messages.error(request, 'Статья не была отредактирована.')

                return render(request, 'add_article.html', context)
        else:
            form = forms.Add_Article(instance=article)
            context['form'] = form

            return render(request, 'add_article.html', context)
    else:
        return redirect(reverse_lazy('news:detail', args=(pk,)))


@login_required
def like_article(request, pk):
    """Добавить статью в понравившиеся"""

    user_data = AdvUser.objects.get(pk=request.user.pk)
    article = Article.objects.get(pk=pk)

    if article in user_data.likes.all():
        user_data.likes.remove(article)
        messages.success(request, 'Вы успешно убрали эту статью из понравившихся.')
    else:
        user_data.likes.add(article)
        messages.success(request, 'Вы успешно добавили эту статью в понравившиеся.')

    return redirect(reverse_lazy('news:detail', args=(pk,)))


@login_required
def delete_article(request, pk):
    """Удалить статью"""

    if request.method == 'POST':
        article = Article.objects.get(pk=pk)

        if article.author.pk is request.user.pk:
            article.delete()
            messages.success(request, 'Вы успешно удалили статью')

    return redirect(reverse_lazy('news:index'))


@login_required
def add_article(request):
    """Создать статью"""

    if not request.user.is_activated:
        messages.warning(request, 'Вам необходимо подтвердить свою эл.почту, чтобы написать статью.')
        return redirect(reverse_lazy('news:index'))

    if request.method == 'POST':
        form = forms.Add_Article(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            user = AdvUser.objects.get(pk=request.user.pk)
            user.publications += 1
            user.save()
            subscribers_mail = []
            subscribers = get_or_create_subscribers(user).subscribers.all()

            for i in subscribers:
                subscribers_mail.append(i.email)

            new_article = user.article_set.last()

            if settings.ALLOWED_HOSTS:
                address = 'http://' + settings.ALLOWED_HOSTS[0]
            else:
                address = 'http://127.0.0.1:8000'

            context = {
                'user': user,
                'article': new_article,
                'address': address,
            }

            subject = render_to_string('email/new_article_subject.txt', context)
            body = render_to_string('email/new_article_body.txt', context)
            send_mail(subject, body, settings.EMAIL_HOST_USER, subscribers_mail)
            messages.success(request, 'Вы успешно добавили статью.')

            return redirect(reverse_lazy('news:index'))
        else:
            context = {
                'form': form,
            }

            return render(request, 'add_article.html', context)
    else:
        initial = {
            'author': request.user.pk,
        }

        form = forms.Add_Article(initial=initial)

        context = {
            'form': form,
            'page_name': 'Публикация статьи',
            'button_text': 'Опубликовать',
        }

        return render(request, 'add_article.html', context)


def users(request):
    """Страница со всеми пользователями"""

    if 'show' in request.GET:
        show = request.GET['show']
    else:
        show = ''

    if show == 'subscribes':
        users_list = get_subscribes(request.user.pk)
    else:
        users_list = AdvUser.objects.filter(is_active=True)

    paginator = Paginator(users_list, 28)

    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1

    page = paginator.get_page(page_num)

    context = {
        'users': page.object_list,
        'page': page,
        'show': show,
    }

    return render(request, 'users.html', context)


class Login(LoginView):
    """Авторизация"""

    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class Logout(LoginRequiredMixin, LogoutView):
    """Выход из аккаунта"""

    pass


class Registration(CreateView):
    """Регистрация"""

    model = AdvUser
    template_name = 'accounts/registration.html'
    form_class = forms.RegistrationForm
    success_url = reverse_lazy('news:login')

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super(CreateView, self).get(request, *args, **kwargs)
        else:
            messages.info(request, 'Вы уже зарегистрированы.')
            return reverse_lazy('news:index')


def user_activate(request, sign):
    """Активировать пользователя"""

    signer = Signer()

    try:
        username = signer.unsign(sign)
    except BadSignature:
        messages.error(request, 'Плохая подпись. Подтвердить эл.почту не удалось.')
        return redirect(reverse_lazy('news:index'))

    user = AdvUser.objects.get(username=username)

    if user.is_activated:
        messages.info(request, 'Ваша эл.почты уже подтверждена.')
    else:
        user.is_activated = True
        user.save()
        messages.success(request, 'Вы успешно подтвердили свою эл.почту.')

    return redirect(reverse_lazy('news:index'))


@login_required
def activation_send(request):
    """Отправить письмо для подтверждения почты"""

    if not request.user.is_activated:
        user = AdvUser.objects.get(pk=request.user.pk)
        send_activation(user, 'again')
        messages.info(request, 'На Вашу эл.почту повторно была отправлено ссылка для потверждения.')
    else:
        messages.warning(request, 'Ваша эл.почта была подтверждена ранее.')

    return redirect(reverse_lazy('news:index'))


def profile(request, pk):
    """Страница профиля"""

    user_data = AdvUser.objects.get(pk=pk)
    form = None

    if 'delete' in request.GET:
        delete = request.GET['delete']
        comment = CommentUser.objects.get(pk=delete)

        if comment.author.pk is request.user.pk:
            comment.is_active = False
            comment.save()
            messages.success(request, 'Вы успешно удалили комментарий.')

        return redirect(reverse_lazy('news:profile', args=(pk,)))

    publications = Article.objects.filter(author=user_data.pk).order_by('-views')
    favourites = user_data.likes.all()
    subscribers = get_or_create_subscribers(user_data).subscribers.all()
    subscribed = False

    if request.user in subscribers:
        subscribed = True

    if request.method == 'POST':
        if not request.user.is_activated:
            messages.warning(request, 'Вам необходимо подтвердить свою эл.почту, чтобы написать комментарий.')
            return redirect(reverse_lazy('news:profile', args=(pk,)))

        if 'edit' in request.GET:
            edit = request.GET['edit']
            comment = CommentUser.objects.get(pk=edit)
            if comment.author.pk is request.user.pk and int(comment.object_id) is user_data.pk:
                form = forms.AddUserCommentForm(request.POST, instance=comment)
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.is_edited = True
                    instance.save()
                    messages.success(request, 'Вы успешно отредактировали комментарий.')
                else:
                    messages.error(request, 'Комментарий не был отредактирован.')
                return redirect(reverse_lazy('news:profile', args=(user_data.pk,)))
        else:
            author = int(request.POST['author'])
            object_id = int(request.POST['object_id'])
            if author is request.user.pk and object_id is user_data.pk:
                form = forms.AddUserCommentForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Вы успешно добавили комментарий.')
                else:
                    messages.error(request, 'Комментарий не был добавлен.')
                return redirect(reverse_lazy('news:profile', args=(pk,)))
    else:
        user_data.views += 1
        user_data.save()

        initial = {'author': request.user.pk, 'object_id': user_data.pk}
        form = forms.AddUserCommentForm(initial=initial)

    comments = CommentUser.objects.filter(object_id=user_data.pk)
    context = {
        'user_data': user_data,
        'form': form,
        'subscribed': subscribed,
        'publications_count': publications.count(),
        'favourites_count': favourites.count(),
        'comments': comments,
    }

    if 'show' in request.GET:
        show = request.GET['show']
        context['show'] = show

        if 'page' in request.GET:
            page_num = request.GET['page']
        else:
            page_num = 1

        if show == 'publications':
            paginator = Paginator(publications, 5)
        elif show == 'subscribes':
            paginator = Paginator(subscribers, 28)
        elif show == 'favourites':
            paginator = Paginator(favourites, 5)

        page = paginator.get_page(page_num)
        context['page'] = page

        if show == 'publications':
            context['publications'] = page.object_list
        elif show == 'subscribes':
            context['subscribers'] = page.object_list
        elif show == 'favourites':
            context['favourites'] = page.object_list
    else:
        show = ''
        context['show'] = show

    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Изменить профиль"""

    user_data = AdvUser.objects.get(pk=request.user.pk)

    if request.method == 'POST':
        form = forms.EditProfileForm(request.POST, request.FILES, instance=user_data)
        if form.is_valid():
            if 'email' in form.changed_data:
                user_data.is_activated = False
                user_data.save()
                send_activation(user_data, 'edited')

            form.save()
            messages.success(request, 'Вы успешно отредактировали свой профиль.')

            return redirect(reverse_lazy('news:profile', args=(request.user.pk,)))
        else:
            context = {
                'form': form,
            }

            return render(request, 'accounts/edit_profile.html', context)
    else:
        form = forms.EditProfileForm(instance=user_data)

        context = {
            'form': form,
        }

        return render(request, 'accounts/edit_profile.html', context)


class ChangePassword(PasswordChangeView, LoginRequiredMixin):
    """Изменить пароль"""

    template_name = 'add_article.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['page_name'] = 'Изменение пароля'
        return context

    def get_success_url(self):
        messages.success(self.request, 'Вы успешно изменили пароль.')
        return reverse_lazy('news:index')


class ResetPassword(PasswordResetView):
    """Страница сроса пароля"""

    template_name = 'accounts/reset_password_user.html'
    form_class = forms.ResetPasswordForm

    def get_success_url(self):
        messages.info(self.request, 'На Вашу эл. почту было отправлено письмо с ссылкой на страницу сброса пароля.')
        return reverse_lazy('news:index')


class ResetPasswordNew(PasswordResetConfirmView):
    """Сбросить пароль"""

    template_name = 'accounts/reset_password_new.html'
    success_url = reverse_lazy('news:login')


@login_required
def delete_profile(request):
    """Удалить профиль"""

    delete_form = forms.DeleteProfileForm

    context = {
        'delete_form': delete_form,
        'page_name': 'Удаление аккаунта'
    }

    if request.method == 'POST':
        password = request.POST['password']
        user = AdvUser.objects.get(pk=request.user.pk)

        if request.user.check_password(password):
            user.is_active = False
            user.save()
            send_deleted_notification(user, 'deleted')
            messages.success(request, 'Вы успешно удалили свой профиль.')
            return redirect(reverse_lazy('news:index'))
        else:
            messages.error(request, 'Неверный пароль.')
            return render(request, 'add_article.html', context)

    return render(request, 'add_article.html', context)


def recovery_profile(request, sign):
    """Восстановить профиль"""

    signer = Signer()

    try:
        username = signer.unsign(sign)
    except BadSignature:
        messages.error(request, 'Плохая подпись. Аккаунт не был восстановлен.')
        return redirect(reverse_lazy('news:index'))

    user = AdvUser.objects.get(username=username)

    if user.is_active:
        messages.warning(request, 'Нет необходимости восстанавливать Ваш аккаунт.')
    else:
        user.is_active = True
        user.save()
        messages.success(request, 'Вы успешно восстановили свой аккаунт.')

    return redirect(reverse_lazy('news:index'))


def request_recovery(request):
    """Восстановить профиль"""

    if request.method == 'POST':
        form = forms.RecoveryProfileForm(request.POST)

        if form.is_valid():
            username = request.POST['username']
            errors = []

            try:
                email = request.POST['email']
                if not AdvUser.objects.get(username=username).email == email:
                    errors.append('Введенный Вами эл.почта не совпадает с почтой пользователя')
            except AdvUser.DoesNotExist:
                errors.append('Пользователь с таким именем не существует')

            if len(errors) == 0:
                user = AdvUser.objects.get(username=username)
                if user.is_active:
                    messages.warning(request, 'Нет необходимости восставнавливать Ваш аккаунт.')
                else:
                    send_deleted_notification(user, 'recovery')
                    messages.success(request,
                                     'На Вашу эл.почту было отправлено письмо с ссылкой на восстановление аккаунта.')
                return redirect(reverse_lazy('news:index'))
            else:
                form = forms.RecoveryProfileForm
                context = {
                    'form': form,
                    'errors': errors,
                }
                return render(request, 'accounts/recovery_profile.html', context)
    else:
        form = forms.RecoveryProfileForm

        context = {
            'form': form
        }

        return render(request, 'accounts/recovery_profile.html', context)


@login_required
def subscribe(request, pk):
    """Подписаться на пользователя"""

    user = AdvUser.objects.get(pk=request.user.pk)
    user_data = AdvUser.objects.get(pk=pk)

    if not user_data.pk is request.user.pk:

        if user.is_activated:
            subscribe = get_or_create_subscribers(user=user_data)

            if user in subscribe.subscribers.all():
                subscribe.subscribers.remove(user.pk)
                messages.success(request, 'Вы успешно отписались от пользователя.')
            else:
                subscribe.subscribers.add(user.pk)

                context = {
                    'user': user_data,
                }

                subject = render_to_string('email/subscribe-subject.txt')
                body = render_to_string('email/subscribe-body.txt', context)
                send_mail(subject, body, settings.EMAIL_HOST_USER, (user_data.email,))
                messages.success(request, 'Вы успешно подписались на пользователя.')
        else:
            messages.warning(request, 'Подтвердите свою эл.почту, прежде чем подписаться на пользователя.')

    return redirect(reverse_lazy('news:profile', args=(pk,)))
