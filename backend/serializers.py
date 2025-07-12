from rest_framework import serializers
from .models import DemoSession, CommandLog

class DemoSessionSerializer(serializers.ModelSerializer):
    """Serializer for demo sessions"""
    session_id = serializers.UUIDField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)
    ended_at = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = DemoSession
        fields = ['session_id', 'started_at', 'ended_at', 'is_active']

class CommandLogSerializer(serializers.ModelSerializer):
    """Serializer for command logs"""
    session = serializers.UUIDField(source='session.session_id', read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)
    command_text = serializers.CharField(max_length=1000)
    response = serializers.CharField(read_only=True)
    is_ai_response = serializers.BooleanField(read_only=True)
    processing_time_ms = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CommandLog
        fields = [
            'id', 'session', 'timestamp', 'command_text', 
            'response', 'is_ai_response', 'processing_time_ms'
        ]

class CommandRequestSerializer(serializers.Serializer):
    """Serializer for incoming command requests"""
    session_id = serializers.UUIDField()
    command = serializers.CharField(max_length=1000, min_length=1)
    
    def validate_command(self, value):
        """Validate command text"""
        if not value or not value.strip():
            raise serializers.ValidationError("Command cannot be empty")
        return value.strip()

class TranscriptSerializer(serializers.Serializer):
    """Serializer for session transcripts"""
    session_id = serializers.UUIDField()
    started_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField(allow_null=True)
    is_active = serializers.BooleanField()
    total_commands = serializers.IntegerField()
    commands = serializers.ListField(child=serializers.DictField())
