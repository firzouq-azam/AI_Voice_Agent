from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import DemoSession, CommandLog


class CommandLogInline(admin.TabularInline):
    """Inline display of commands under sessions"""
    model = CommandLog
    extra = 0
    readonly_fields = ['timestamp', 'processing_time_ms', 'is_ai_response']
    fields = ['timestamp', 'command_text', 'response', 'is_ai_response', 'processing_time_ms']
    max_num = 10  # Show only last 10 commands
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(DemoSession)
class DemoSessionAdmin(admin.ModelAdmin):
    """Admin interface for Voice Assistant Demo Sessions"""
    
    list_display = [
        'session_id_display', 
        'started_at', 
        'ended_at', 
        'is_active', 
        'command_count',
        'duration_display'
    ]
    list_filter = [
        'is_active', 
        'started_at', 
        'ended_at'
    ]
    search_fields = ['session_id']
    readonly_fields = ['session_id', 'started_at', 'ended_at', 'is_active']
    ordering = ['-started_at']
    list_per_page = 20
    inlines = [CommandLogInline]
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'started_at', 'ended_at', 'is_active')
        }),
        ('Session Statistics', {
            'fields': ('command_count_display', 'duration_display'),
            'classes': ('collapse',)
        }),
    )
    
    def session_id_display(self, obj):
        """Display session ID with link to transcript"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:backend_demosession_change', args=[obj.pk]),
            str(obj.session_id)[:8] + '...'
        )
    session_id_display.short_description = 'Session ID'
    session_id_display.admin_order_field = 'session_id'
    
    def command_count(self, obj):
        """Display number of commands in session"""
        count = obj.commands.count()
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if count > 0 else 'gray',
            count
        )
    command_count.short_description = 'Commands'
    command_count.admin_order_field = 'commands__count'
    
    def command_count_display(self, obj):
        """Display command count in detail view"""
        count = obj.commands.count()
        ai_count = obj.commands.filter(is_ai_response=True).count()
        dummy_count = count - ai_count
        
        return format_html(
            '<div style="margin: 10px 0;">'
            '<strong>Total Commands:</strong> {}<br>'
            '<strong>AI Responses:</strong> {}<br>'
            '<strong>Dummy Responses:</strong> {}'
            '</div>',
            count, ai_count, dummy_count
        )
    command_count_display.short_description = 'Command Statistics'
    
    def duration_display(self, obj):
        """Display session duration"""
        if obj.ended_at and obj.started_at:
            duration = obj.ended_at - obj.started_at
            minutes = duration.total_seconds() / 60
            return f"{minutes:.1f} minutes"
        elif obj.is_active:
            return "Active"
        else:
            return "N/A"
    duration_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        """Optimize queryset with command count"""
        return super().get_queryset(request).prefetch_related('commands')


@admin.register(CommandLog)
class CommandLogAdmin(admin.ModelAdmin):
    """Admin interface for Voice Command Logs"""
    
    list_display = [
        'session_link', 
        'timestamp', 
        'command_preview', 
        'response_preview', 
        'is_ai_response', 
        'processing_time_display'
    ]
    list_filter = [
        'is_ai_response', 
        'timestamp', 
        'session__is_active'
    ]
    search_fields = [
        'command_text', 
        'response', 
        'session__session_id'
    ]
    readonly_fields = [
        'session', 
        'timestamp', 
        'processing_time_ms', 
        'is_ai_response'
    ]
    ordering = ['-timestamp']
    list_per_page = 25
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session', 'timestamp', 'is_ai_response')
        }),
        ('Command Details', {
            'fields': ('command_text', 'response')
        }),
        ('Performance', {
            'fields': ('processing_time_ms',),
            'classes': ('collapse',)
        }),
    )
    
    def session_link(self, obj):
        """Display session with link"""
        if obj.session:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:backend_demosession_change', args=[obj.session.pk]),
                str(obj.session.session_id)[:8] + '...'
            )
        return "N/A"
    session_link.short_description = 'Session'
    session_link.admin_order_field = 'session__session_id'
    
    def command_preview(self, obj):
        """Show first 50 characters of command"""
        text = obj.command_text[:50]
        if len(obj.command_text) > 50:
            text += '...'
        return format_html(
            '<span title="{}">{}</span>',
            obj.command_text,
            text
        )
    command_preview.short_description = 'Command'
    command_preview.admin_order_field = 'command_text'
    
    def response_preview(self, obj):
        """Show first 50 characters of response"""
        text = obj.response[:50]
        if len(obj.response) > 50:
            text += '...'
        return format_html(
            '<span title="{}">{}</span>',
            obj.response,
            text
        )
    response_preview.short_description = 'Response'
    response_preview.admin_order_field = 'response'
    
    def processing_time_display(self, obj):
        """Display processing time with color coding"""
        if obj.processing_time_ms:
            color = 'green' if obj.processing_time_ms < 1000 else 'orange' if obj.processing_time_ms < 3000 else 'red'
            return format_html(
                '<span style="color: {};">{}ms</span>',
                color,
                obj.processing_time_ms
            )
        return "N/A"
    processing_time_display.short_description = 'Processing Time'
    processing_time_display.admin_order_field = 'processing_time_ms'
    
    def get_queryset(self, request):
        """Optimize queryset with session data"""
        return super().get_queryset(request).select_related('session')


# Customize admin site
admin.site.site_header = "🎤 Voice Assistant Admin"
admin.site.site_title = "Voice Assistant Admin"
admin.site.index_title = "Voice Assistant Dashboard"