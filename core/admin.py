from django.contrib import admin
from django.utils.html import format_html
from .models import (UserProfile, Worker, HiringRequest,
                     Contract, Review, ReplacementRequest)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'phone']
    search_fields = ['user__username', 'phone']


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display  = [
        'photo_preview', 'name', 'age', 'location',
        'skills', 'salary', 'work_type', 'availability','accepts_short_term', 
        'daily_rate',
        'is_verified', 'avg_rating', 'total_hires'
    ]
    list_filter   = [
        'location', 'skills', 'availability',
        'is_verified', 'work_type', 'day_off', 'accepts_short_term'
    ]
    search_fields = ['name', 'nid_number', 'phone',
                     'guardian_name', 'guardian_phone']
    list_editable = ['is_verified', 'availability']
    ordering      = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'age', 'phone', 'address',
                       'photo', 'nid_number')
        }),
        ('Short-Term / Daily Hire', {
    'fields': ('accepts_short_term', 'daily_rate', 'min_days')
        }), 
        ('Work Details', {
            'fields': ('skills', 'experience', 'salary', 'location')
        }),
        # ── Feature 7: Working Schedule ───────────────────────────────────────
        ('Working Schedule', {
            'fields': ('work_type', 'work_hours', 'day_off', 'extra_notes')
        }),
        ('Status', {
            'fields': ('is_verified', 'availability')
        }),
        # ── Feature 2: Emergency Contact ──────────────────────────────────────
        ('Emergency / Guardian Contact', {
            'fields': ('guardian_name', 'guardian_phone',
                       'guardian_relation'),
            'classes': ('collapse',)
        }),
        # ── Feature 5: Admin Private Notes ────────────────────────────────────
        ('Admin Private Notes (NOT shown to users)', {
            'fields': ('admin_notes',),
            'classes': ('collapse',)
        }),
        ('Ratings (Auto-calculated)', {
            'fields': ('avg_rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['avg_rating', 'total_reviews']

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;'
                'border-radius:50%;object-fit:cover;">',
                obj.photo.url
            )
        return format_html(
            '<div style="width:40px;height:40px;border-radius:50%;'
            'background:#dc3545;color:white;display:flex;'
            'align-items:center;justify-content:center;'
            'font-weight:bold;">{}</div>',
            obj.name[0].upper()
        )
    photo_preview.short_description = 'Photo'

    # ── Feature 4: Show hiring count in admin ─────────────────────────────────
    def total_hires(self, obj):
        count = obj.hiring_requests.filter(status='Approved').count()
        return format_html(
            '<span style="color:green;font-weight:bold;">'
            '✅ {} hire{}</span>',
            count, 's' if count != 1 else ''
        )
    total_hires.short_description = 'Total Hires'


@admin.register(HiringRequest)
class HiringRequestAdmin(admin.ModelAdmin):
    list_display  = ['user', 'worker', 'status',
                     'proposed_salary', 'salary_status', 'created_at']
    list_filter   = ['status', 'created_at']
    search_fields = ['user__username', 'worker__name']
    list_editable = ['status']
    ordering      = ['-created_at']

    # ── Feature 3: Show salary negotiation ────────────────────────────────────
    def salary_status(self, obj):
        if not obj.proposed_salary:
            return format_html(
                '<span style="color:green;">Accepted ৳{}</span>',
                obj.worker.salary
            )
        if obj.proposed_salary < obj.worker.salary:
            return format_html(
                '<span style="color:orange;">Proposed ৳{} '
                '(asked ৳{})</span>',
                obj.proposed_salary, obj.worker.salary
            )
        return format_html(
            '<span style="color:blue;">Proposed ৳{}</span>',
            obj.proposed_salary
        )
    salary_status.short_description = 'Salary Negotiation'


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display  = ['hiring_request', 'start_date',
                     'end_date', 'salary_agreed', 'created_at']
    search_fields = ['hiring_request__user__username',
                     'hiring_request__worker__name']
    ordering      = ['-created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ['user', 'worker', 'score', 'created_at']
    list_filter   = ['score', 'created_at']
    search_fields = ['user__username', 'worker__name']
    ordering      = ['-created_at']


@admin.register(ReplacementRequest)
class ReplacementRequestAdmin(admin.ModelAdmin):
    list_display  = ['user', 'hiring_request', 'status', 'created_at']
    list_filter   = ['status']
    search_fields = ['user__username']
    list_editable = ['status']
    ordering      = ['-created_at']


admin.site.site_header  = "GetBua Admin Panel"
admin.site.site_title   = "GetBua"
admin.site.index_title  = "Welcome to GetBua Admin Dashboard"