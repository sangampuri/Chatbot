from django.db import models

class Chat(models.Model):
    user_message = models.TextField()
    ai_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(
    max_length=40,
    null=True,
    blank=True,
    db_index=True
)
