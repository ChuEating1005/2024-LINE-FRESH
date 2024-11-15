from django.db import models

class User(models.Model):
    line_user_id = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.line_user_id

class AudioMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=50)
    file_path = models.CharField(max_length=255, null=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Audio from {self.user} at {self.created_at}"

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_from_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{'User' if self.is_from_user else 'Bot'}: {self.message[:50]}"