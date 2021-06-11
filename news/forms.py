from django import forms
from .models import Article, Comment, AdvUser, CommentUser
from django.core.exceptions import ValidationError
from .utilities import send_activation
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import password_validation


class AddCommentForm(forms.ModelForm):
    """Форма добавления комментария"""

    class Meta:
        model = Comment
        fields = ('article', 'author', 'comment_text', 'reply')
        widgets = {
            'article': forms.HiddenInput,
            'author': forms.HiddenInput,
            'reply': forms.HiddenInput,
        }


class RegistrationForm(forms.ModelForm):
    """Форма регистрации"""

    email = forms.EmailField(label='Адрес эл. почты', required=True, help_text='Обязательное поле')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)', widget=forms.PasswordInput,
                                help_text='Введите пароль еще раз')
    username = forms.CharField(max_length=20, label='Имя пользователя', help_text="Обязательное поле")

    def clean_email(self):
        email = self.cleaned_data['email']
        users = AdvUser.objects.filter(email=email).count()

        if users > 0:
            raise ValidationError('Пользователь с такой эл.почтой уже существует')

            return email

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean_password2(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            raise ValidationError('Введенные пароли не совпадают')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.save()
        send_activation(user, 'register')
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2')


class EditProfileForm(forms.ModelForm):
    """Форма редактирования профиля"""

    birthday = forms.DateField(required=False)
    username = forms.CharField(max_length=20, label='Имя пользователя', help_text="Обязательное поле")

    class Meta:
        model = AdvUser
        fields = ('avatar', 'username', 'email', 'phone', 'first_name', 'last_name', 'birthday', 'country', 'aboutUser',
                  'private')


class AddUserCommentForm(forms.ModelForm):
    """Форма добалвения комментария для пользователя"""

    class Meta:
        model = CommentUser
        fields = ('author', 'comment_text', 'object_id', 'reply')
        widgets = {
            'author': forms.HiddenInput,
            'reply': forms.HiddenInput,
            'object_id': forms.HiddenInput,
        }


class Add_Article(forms.ModelForm):
    """Добавить статью"""

    class Meta:
        model = Article
        fields = ('rubric', 'title', 'content', 'image', 'author')
        widgets = {'author': forms.HiddenInput}


class SearchForm(forms.Form):
    """Форма поиска"""

    keyword = forms.CharField(label='', required=True)


class DeleteProfileForm(forms.ModelForm):
    """Форма удаления профиля"""

    password = forms.CharField(label='Введите пароль', widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data['password']

    class Meta:
        model = AdvUser
        fields = ('password',)


class ChangePassword(forms.Form):
    """Форма смены пароля"""

    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Введите пароль еще раз', widget=forms.PasswordInput)

    class Meta:
        model = AdvUser
        fields = ('old_password', 'new_password1', 'new_password2', 'captcha')


class ResetPasswordForm(forms.Form):
    """Форма сброса пароля"""

    username = forms.CharField(label='Имя пользователя', max_length=20)
    email = forms.EmailField(label='Эл.почта', max_length=254)

    def clean(self):
        super().clean()
        errors = {}
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        try:
            if not AdvUser.objects.get(username=username).email == email:
                errors['email'] = ValidationError('Введенный Вами эл.почта не совпадает с почтой пользователя')
        except:
            errors['username'] = ValidationError('Пользователь с таким именем не существует')

        if errors:
            raise ValidationError(errors)

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        user = AdvUser.objects.get(username=username)

        if len(settings.ALLOWED_HOSTS) > 0:
            host = 'https://' + settings.ALLOWED_HOSTS[0]
        else:
            host = 'http://127.0.0.1:8000'
        context = {
            'user': username,
            'email': email,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user),
            'host': host,
        }
        subject = render_to_string('email/reset_password_sended_subject.txt', context)
        body = render_to_string('email/reset_password_sended_body.txt', context)
        send_mail(subject, body, settings.EMAIL_HOST_USER, (email,))


class RecoveryProfileForm(forms.Form):
    """Форма восстановления профиля"""

    username = forms.CharField(label='Имя пользователя', max_length=20)
    email = forms.EmailField(label='Адрес эл.почты', max_length=254)
