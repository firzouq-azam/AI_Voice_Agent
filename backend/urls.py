from django.urls import path
from .views import StartSessionView, SendCommandView, TranscriptView, EndSessionView

urlpatterns = [
    path('start-session/', StartSessionView.as_view(), name='start-session'),
    path('send-command/', SendCommandView.as_view(), name='send-command'),
    path('transcript/<uuid:session_id>/', TranscriptView.as_view(), name='transcript'),
    path('end-session/<uuid:session_id>/', EndSessionView.as_view(), name='end-session'),
]