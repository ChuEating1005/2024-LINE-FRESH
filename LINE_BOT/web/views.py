from django.shortcuts import render
from django.http import Http404
import markdown
from db_utils.db_handler import DBHandler

# list article title
def info(request):
    db_handler = DBHandler(collection_name='articles')
    articles = db_handler.get_all_json()
    return render(request, 'info.html', {'articles': articles})

# article content
def article_detail(request, article_id):
    db_handler = DBHandler(collection_name='articles')
    article = db_handler.get_item_by_id(article_id)
    article_content = markdown.markdown(article["content"])
    return render(request, 'article.html', {'article': article, 'content': article_content})

