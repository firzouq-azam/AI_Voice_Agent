from django.db import models
from django.core.validators import MinLengthValidator
import uuid

class DemoSession(models.Model):
    """Represents a voice assistant demo session"""
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "Demo Session"
        verbose_name_plural = "Demo Sessions"

    def __str__(self):
        return f"Session {self.session_id} ({'Active' if self.is_active else 'Ended'})"
    
    def end_session(self):
        """End the current session"""
        from django.utils import timezone
        self.ended_at = timezone.now()
        self.is_active = False
        self.save()

class CommandLog(models.Model):
    """Logs all commands and responses in a session"""
    session = models.ForeignKey(
        DemoSession, 
        on_delete=models.CASCADE, 
        related_name='commands'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    command_text = models.TextField(
        validators=[MinLengthValidator(1, "Command cannot be empty")]
    )
    response = models.TextField()
    is_ai_response = models.BooleanField(default=False)
    processing_time_ms = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = "Command Log"
        verbose_name_plural = "Command Logs"

    def __str__(self):
        return f"[{self.timestamp}] {self.command_text[:50]}..."
