"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from web import views as views_web
from django.urls import path, include

urlpatterns = [
    path('', views_web.info, name='info'),  # 確保有為 info 設置 name
    path('article/<int:article_id>/', views_web.article_detail, name='article_detail'),
    path('admin/', admin.site.urls),
    path('bot/', include('bot.urls')),
]
