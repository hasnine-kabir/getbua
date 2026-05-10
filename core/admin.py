from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (UserProfile, Worker, HiringRequest,
                     Contract, Review, ReplacementRequest,
                     SalaryPayment, Message)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'phone', 'birthday', 'address']
    search_fields = ['user__username', 'phone']


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display  = [
        'photo_preview', 'name', 'age', 'location',
        'skills', 'salary', 'daily_rate',
        'accepts_short_term', 'availability',
        'is_verified', 'avg_rating'
    ]
    list_filter   = ['location', 'skills', 'availability',
                     'is_verified', 'accepts_short_term',
                     'work_type', 'day_off']
    search_fields = ['name', 'nid_number', 'phone',
                     'guardian_name', 'guardian_phone']
    list_editable = ['is_verified', 'availability',
                     'accepts_short_term']
    ordering      = ['-created_at']
    readonly_fields = ['avg_rating', 'total_reviews']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'age', 'phone',
                       'address', 'photo', 'nid_number')
        }),
        ('Work Details', {
            'fields': ('skills', 'experience',
                       'salary', 'location')
        }),
        ('Short-Term / Daily Hire', {
            'fields': ('accepts_short_term',
                       'daily_rate', 'min_days'),
            'classes': ('collapse',)
        }),
        ('Working Schedule', {
            'fields': ('work_type', 'work_hours',
                       'day_off', 'extra_notes')
        }),
        ('Status', {
            'fields': ('is_verified', 'availability')
        }),
        ('Emergency / Guardian Contact', {
            'fields': ('guardian_name', 'guardian_phone',
                       'guardian_relation'),
            'classes': ('collapse',)
        }),
        ('Admin Private Notes', {
            'fields': ('admin_notes',),
            'classes': ('collapse',)
        }),
        ('Ratings (Auto-calculated)', {
            'fields': ('avg_rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;'
                'border-radius:50%;object-fit:cover;">',
                obj.photo.url
            )
        return format_html(
            '<div style="width:40px;height:40px;border-radius:50%;'
            'background:#4A90E2;color:white;display:flex;'
            'align-items:center;justify-content:center;'
            'font-weight:bold;">{}</div>',
            obj.name[0].upper()
        )
    photo_preview.short_description = 'Photo'


@admin.register(HiringRequest)
class HiringRequestAdmin(admin.ModelAdmin):
    list_display  = ['user', 'worker', 'status',
                     'hire_type', 'delivery_address_short',
                     'salary_info', 'created_at']
    list_filter   = ['status', 'hire_type', 'created_at']
    search_fields = ['user__username', 'worker__name',
                     'delivery_address']
    list_editable = ['status']
    ordering      = ['-created_at']

    def delivery_address_short(self, obj):
        if obj.delivery_address:
            return obj.delivery_address[:40] + ('...' if len(
                obj.delivery_address) > 40 else '')
        return '—'
    delivery_address_short.short_description = 'Delivery Address'

    def salary_info(self, obj):
        if obj.hire_type == 'Short Term':
            cost = obj.total_cost()
            return format_html(
                '<span style="color:#8E44AD;">⚡ ৳{}/day × {}d = ৳{}</span>',
                obj.worker.daily_rate or 0,
                obj.duration_days or 0,
                cost or 0
            )
        if obj.proposed_salary:
            return format_html(
                '<span style="color:#F39C12;">৳{} proposed</span>',
                obj.proposed_salary
            )
        return format_html(
            '<span style="color:#27AE60;">৳{}/mo</span>',
            obj.worker.salary
        )
    salary_info.short_description = 'Salary / Cost'


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display  = ['hiring_request', 'start_date',
                     'contract_type', 'payment_info',
                     'created_at']
    search_fields = ['hiring_request__user__username',
                     'hiring_request__worker__name']
    ordering      = ['-created_at']

    def contract_type(self, obj):
        if obj.is_short_term():
            return format_html(
                '<span style="color:#8E44AD;">⚡ Short Term</span>')
        return format_html(
            '<span style="color:#27AE60;">📅 Full Time</span>')
    contract_type.short_description = 'Type'

    def payment_info(self, obj):
        if obj.is_short_term():
            return format_html(
                '৳{}/day × {} days = <strong>৳{}</strong>',
                obj.daily_rate_agreed or 0,
                obj.duration_days or 0,
                obj.total_amount or 0
            )
        return format_html('৳{}/month', obj.salary_agreed)
    payment_info.short_description = 'Payment'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ['user', 'worker', 'score', 'created_at']
    list_filter   = ['score', 'created_at']
    search_fields = ['user__username', 'worker__name']
    ordering      = ['-created_at']


@admin.register(ReplacementRequest)
class ReplacementRequestAdmin(admin.ModelAdmin):
    list_display  = ['user', 'hiring_request',
                     'status', 'created_at']
    list_filter   = ['status']
    search_fields = ['user__username']
    list_editable = ['status']
    ordering      = ['-created_at']


@admin.register(SalaryPayment)
class SalaryPaymentAdmin(admin.ModelAdmin):
    list_display  = ['hiring_request', 'month',
                     'year', 'amount', 'paid_on']
    list_filter   = ['month', 'year']
    search_fields = ['hiring_request__worker__name',
                     'hiring_request__user__username']
    ordering      = ['-year', '-created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ['user_info', 'subject_short',
                     'status', 'is_read_by_admin',
                     'created_at', 'reply_button']
    list_filter   = ['status', 'is_read_by_admin',
                     'created_at']
    search_fields = ['user__username', 'subject', 'body']
    list_editable = ['status']
    ordering      = ['-created_at']
    readonly_fields = ['user', 'subject', 'body',
                       'created_at', 'replied_at']

    fieldsets = (
        ('Message from User', {
            'fields': ('user', 'subject', 'body',
                       'created_at', 'is_read_by_admin')
        }),
        ('Admin Reply', {
            'fields': ('admin_reply', 'status', 'replied_at')
        }),
    )

    def user_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>'
            '<small style="color:#718096;">{}</small>',
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )
    user_info.short_description = 'User'

    def subject_short(self, obj):
        return obj.subject[:50] + ('...' if len(
            obj.subject) > 50 else '')
    subject_short.short_description = 'Subject'

    def reply_button(self, obj):
        if obj.status == 'Open':
            return format_html(
                '<a href="/admin/core/message/{}/change/" '
                'style="background:#4A90E2;color:white;'
                'padding:4px 10px;border-radius:6px;'
                'text-decoration:none;font-size:0.8rem;">'
                '✏️ Reply</a>',
                obj.pk
            )
        return format_html(
            '<span style="color:#27AE60;font-size:0.8rem;">'
            '✅ Replied</span>'
        )
    reply_button.short_description = 'Action'

    def save_model(self, request, obj, form, change):
        if obj.admin_reply and obj.status == 'Open':
            obj.status          = 'Replied'
            obj.replied_at      = timezone.now()
            obj.is_read_by_user = False
        super().save_model(request, obj, form, change)


admin.site.site_header  = "GetBua Admin Panel"
admin.site.site_title   = "GetBua"
admin.site.index_title  = "GetBua Dashboard"