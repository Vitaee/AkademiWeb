"""AkademiWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from AkademiApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('girisSayfasi/', views.girisSayfasi, name="girisSayfasi"),
    path('anasayfa/', views.AnaSayfa, name="anasayfa"),
    path('', views.girisSayfasi, name=""),
    path('kullaniciCikis', views.kullaniciCikis, name="kullaniciCikis"),
    path('forum/', views.forum, name="forum"),
    path('forumContent/<str:forum_name>',views.forumIcerik,name="forumContent"),
    path('forumYeniKonu/', views.forumYeniKonu, name="forumYeniKonu"),
    path('notDefteri/', views.notDefteri,name="notDefteri"),
    path('ayarlar/', views.ayarlar,name="ayarlar"),
    path('kodYaz/', views.kodYaz,name="kodYaz"),
    path('sifreSifirlama/', views.reset_password, name="sifreSifirlama"),
    path('otherprofile/<str:otherUser>',views.other_profiles, name='other_profiles'),
    path('tutorial_dashboard/', views.tutorial_dashboard, name="tutorial_dashboard"),
    path('bulten/', views.news, name="bulten"),
    path('tutorial_detail/<str:lesson_names>/', views.tutorial_detail, name="tutorial_detail"),
    path('lesson_detail/<str:unitsNames>/',views.gotoLesson,name = "lesson_detail"),
    path('kitaplar/', views.books, name="books"),
    path('coupons/',views.coupons,name="coupons"),


    ]
handler404 = 'AkademiApp.views.custom_page_not_found_view'
handler500 = 'AkademiApp.views.custom_error_view'