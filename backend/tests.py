from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import DemoSession, CommandLog
from .services import SessionService, CommandService, TranscriptService
import uuid


class DemoSessionModelTest(TestCase):
    """Test DemoSession model functionality"""
    
    def test_session_creation(self):
        """Test that sessions are created correctly"""
        session = DemoSession.objects.create()
        self.assertIsNotNone(session.session_id)
        self.assertTrue(session.is_active)
        self.assertIsNone(session.ended_at)
    
    def test_session_ending(self):
        """Test that sessions can be ended"""
        session = DemoSession.objects.create()
        session.end_session()
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.ended_at)


class CommandLogModelTest(TestCase):
    """Test CommandLog model functionality"""
    
    def setUp(self):
        self.session = DemoSession.objects.create()
    
    def test_command_log_creation(self):
        """Test that command logs are created correctly"""
        command = CommandLog.objects.create(
            session=self.session,
            command_text="Hello",
            response="Hi there!",
            is_ai_response=False,
            processing_time_ms=100
        )
        self.assertEqual(command.command_text, "Hello")
        self.assertEqual(command.response, "Hi there!")
        self.assertFalse(command.is_ai_response)
        self.assertEqual(command.processing_time_ms, 100)


class SessionServiceTest(TestCase):
    """Test SessionService functionality"""
    
    def test_create_session(self):
        """Test session creation service"""
        session = SessionService.create_session()
        self.assertIsInstance(session, DemoSession)
        self.assertTrue(session.is_active)
    
    def test_get_session(self):
        """Test getting session by ID"""
        session = DemoSession.objects.create()
        retrieved = SessionService.get_session(str(session.session_id))
        self.assertEqual(retrieved, session)
    
    def test_get_nonexistent_session(self):
        """Test getting non-existent session"""
        fake_id = str(uuid.uuid4())
        result = SessionService.get_session(fake_id)
        self.assertIsNone(result)
    
    def test_end_session(self):
        """Test ending a session"""
        session = DemoSession.objects.create()
        success = SessionService.end_session(str(session.session_id))
        self.assertTrue(success)
        session.refresh_from_db()
        self.assertFalse(session.is_active)


class CommandServiceTest(TestCase):
    """Test CommandService functionality"""
    
    def setUp(self):
        self.session = DemoSession.objects.create()
    
    def test_process_dummy_command(self):
        """Test processing dummy commands"""
        result, status_code = CommandService.process_command(
            str(self.session.session_id), 
            "hello"
        )
        self.assertEqual(status_code, 200)
        self.assertIn("response", result)
        self.assertIn("Hello", result["response"])
    
    def test_process_empty_command(self):
        """Test processing empty command"""
        result, status_code = CommandService.process_command(
            str(self.session.session_id), 
            ""
        )
        self.assertEqual(status_code, 400)
        self.assertIn("error", result)
    
    def test_process_command_invalid_session(self):
        """Test processing command with invalid session"""
        fake_id = str(uuid.uuid4())
        result, status_code = CommandService.process_command(fake_id, "hello")
        self.assertEqual(status_code, 404)
        self.assertIn("error", result)
    
    def test_process_command_ended_session(self):
        """Test processing command for ended session"""
        self.session.end_session()
        result, status_code = CommandService.process_command(
            str(self.session.session_id), 
            "hello"
        )
        self.assertEqual(status_code, 400)
        self.assertIn("error", result)


class TranscriptServiceTest(TestCase):
    """Test TranscriptService functionality"""
    
    def setUp(self):
        self.session = DemoSession.objects.create()
        # Create some test commands
        CommandLog.objects.create(
            session=self.session,
            command_text="Hello",
            response="Hi there!",
            is_ai_response=False
        )
        CommandLog.objects.create(
            session=self.session,
            command_text="What time is it?",
            response="The current time is 12:00:00",
            is_ai_response=False
        )
    
    def test_get_session_transcript(self):
        """Test getting session transcript"""
        result, status_code = TranscriptService.get_session_transcript(
            str(self.session.session_id)
        )
        self.assertEqual(status_code, 200)
        self.assertIn("session_id", result)
        self.assertIn("commands", result)
        self.assertEqual(len(result["commands"]), 2)
    
    def test_get_nonexistent_transcript(self):
        """Test getting transcript for non-existent session"""
        fake_id = str(uuid.uuid4())
        result, status_code = TranscriptService.get_session_transcript(fake_id)
        self.assertEqual(status_code, 404)
        self.assertIn("error", result)


class APITest(APITestCase):
    """Test API endpoints"""
    
    def test_start_session(self):
        """Test starting a new session via API"""
        url = reverse('start-session')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("session_id", response.data["data"])
        self.assertIn("started_at", response.data["data"])
    
    def test_send_command(self):
        """Test sending a command via API"""
        # First create a session
        session = DemoSession.objects.create()
        
        url = reverse('send-command')
        data = {
            "session_id": str(session.session_id),
            "command": "hello"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("response", response.data)
    
    def test_send_command_invalid_data(self):
        """Test sending command with invalid data"""
        url = reverse('send-command')
        data = {
            "session_id": "invalid-uuid",
            "command": ""
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_transcript(self):
        """Test getting session transcript via API"""
        session = DemoSession.objects.create()
        CommandLog.objects.create(
            session=session,
            command_text="Test command",
            response="Test response",
            is_ai_response=False
        )
        
        url = reverse('transcript', kwargs={'session_id': session.session_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("commands", response.data)
    
    def test_end_session(self):
        """Test ending a session via API"""
        session = DemoSession.objects.create()
        url = reverse('end-session', kwargs={'session_id': session.session_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        session.refresh_from_db()
        self.assertFalse(session.is_active)
