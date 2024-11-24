from django.urls import path
from . import views

urlpatterns = [
    path('callback/', views.callback, name='callback'),
    path('article/', views.article_list, name='article_list'),  # 列出文章標題
    path('article/<int:article_id>/', views.article_detail, name='article_detail') # 顯示文章內容
]