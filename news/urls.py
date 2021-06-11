from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('accounts/profile/<int:pk>/subscribe/', views.subscribe, name='subscribe'),
    path('accounts/profile/<int:pk>/', views.profile, name='profile'),
    path('accounts/profile/delete/', views.delete_profile, name='delete_profile'),
    path('accounts/profile/edit/', views.edit_profile, name='edit_profile'),
    path('accounts/profile/change_password/', views.ChangePassword.as_view(), name='change_password'),
    path('accounts/profile/reset_password/<uidb64>/<token>/', views.ResetPasswordNew.as_view(),
         name='reset_password_new'),
    path('accounts/profile/reset_password_send/', views.ResetPassword.as_view(), name='reset_password'),
    path('accounts/activate/<str:sign>/', views.user_activate, name='activate'),
    path('accounts/send_activation/', views.activation_send, name='send_activation'),
    path('accounts/recovery/<str:sign>/', views.recovery_profile, name='recovery_profile'),
    path('accounts/request_recovery/', views.request_recovery, name='request_recovery'),
    path('accounts/registration/', views.Registration.as_view(), name='registration'),
    path('accounts/registration/activate/', views.user_activate, name='user_activate'),
    path('accounts/logout/', views.Logout.as_view(), name='logout'),
    path('accounts/login/', views.Login.as_view(), name='login'),

    path('article/<int:pk>/delete/', views.delete_article, name='delete_article'),
    path('article/<int:pk>/like/', views.like_article, name='like_article'),
    path('article/<int:pk>/edit/', views.edit_article, name='edit_article'),
    path('article/<int:pk>/', views.detail, name='detail'),
    path('article/add/', views.add_article, name='add_article'),

    path('rubric/<int:pk>/', views.rubric, name='rubric'),
    path('search/', views.search, name='search'),
    path('users/', views.users, name='users'),
    path('', views.index, name='index'),
]
