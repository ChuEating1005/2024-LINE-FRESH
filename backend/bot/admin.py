from django.contrib import admin
from .models import User, AudioMessage, Conversation, Question, Answer, Article, Comment

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'line_id', 'display_name', 'age_group', 'created_at']
    search_fields = ['line_id', 'display_name']
    list_filter = ['age_group', 'created_at']

@admin.register(AudioMessage)
class AudioMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message_id', 'processed', 'created_at']
    list_filter = ['processed', 'created_at']
    search_fields = ['user__line_id', 'message_id']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'is_from_user', 'created_at']
    list_filter = ['is_from_user', 'created_at']
    search_fields = ['user__line_id', 'message']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'asker', 'category', 'status', 'response_counter', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['asker__line_id', 'content']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'responder', 'created_at']
    list_filter = ['created_at']
    search_fields = ['question__content', 'responder__line_id']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'likes', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'author__line_id']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'article', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['article__title', 'user__line_id']
