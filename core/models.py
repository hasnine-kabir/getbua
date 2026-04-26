from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# ─── USER PROFILE ─────────────────────────────────────────────────────────────
class UserProfile(models.Model):
    user  = models.OneToOneField(User, on_delete=models.CASCADE,
                                 related_name='profile')
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


# ─── WORKER ───────────────────────────────────────────────────────────────────
class Worker(models.Model):

    LOCATION_CHOICES = [
        ('Dhaka',      'Dhaka'),
        ('Chittagong', 'Chittagong'),
        ('Gazipur',    'Gazipur'),
        ('Sylhet',     'Sylhet'),
    ]

    SKILL_CHOICES = [
        ('Cooking',            'Cooking'),
        ('Cleaning',           'Cleaning'),
        ('Childcare',          'Childcare'),
        ('Elderly Care',       'Elderly Care'),
        ('Laundry',            'Laundry'),
        ('Gardening',          'Gardening'),
        ('Cooking & Cleaning', 'Cooking & Cleaning'),
        ('All Rounder',        'All Rounder'),
    ]

    AVAILABILITY_CHOICES = [
        ('Available',   'Available'),
        ('Hired',       'Hired'),
        ('Unavailable', 'Unavailable'),
    ]

    # ── Feature 7: Work Type Choices ──────────────────────────────────────────
    WORK_TYPE_CHOICES = [
        ('Full Time',  'Full Time'),
        ('Part Time',  'Part Time'),
        ('Live-in',    'Live-in'),
        ('Live-out',   'Live-out'),
    ]

    WORK_HOURS_CHOICES = [
        ('Morning (6AM - 12PM)',   'Morning (6AM - 12PM)'),
        ('Afternoon (12PM - 6PM)', 'Afternoon (12PM - 6PM)'),
        ('Evening (6PM - 10PM)',   'Evening (6PM - 10PM)'),
        ('Full Day (8AM - 6PM)',   'Full Day (8AM - 6PM)'),
        ('Flexible',               'Flexible'),
    ]

    DAY_OFF_CHOICES = [
        ('Friday',            'Friday'),
        ('Saturday',          'Saturday'),
        ('Friday & Saturday', 'Friday & Saturday'),
        ('No Fixed Day Off',  'No Fixed Day Off'),
        ('Negotiable',        'Negotiable'),
    ]

    # ── Feature 2: Guardian Relation Choices ──────────────────────────────────
    GUARDIAN_RELATION_CHOICES = [
        ('Husband',  'Husband'),
        ('Father',   'Father'),
        ('Mother',   'Mother'),
        ('Brother',  'Brother'),
        ('Sister',   'Sister'),
        ('Son',      'Son'),
        ('Daughter', 'Daughter'),
        ('Other',    'Other'),
    ]

    # Basic Info
    name         = models.CharField(max_length=100)
    age          = models.PositiveIntegerField()
    location     = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    phone        = models.CharField(max_length=15, blank=True)
    address      = models.TextField(blank=True)

    # Work Info
    skills       = models.CharField(max_length=100, choices=SKILL_CHOICES)
    experience   = models.PositiveIntegerField(default=0,
                       help_text="Years of experience")
    salary       = models.PositiveIntegerField(
                       help_text="Expected monthly salary in BDT")

    # ── Feature 7: Working Schedule ───────────────────────────────────────────
    work_type    = models.CharField(max_length=20,
                       choices=WORK_TYPE_CHOICES,
                       default='Full Time')
    work_hours   = models.CharField(max_length=40,
                       choices=WORK_HOURS_CHOICES,
                       default='Full Day (8AM - 6PM)')
    day_off      = models.CharField(max_length=30,
                       choices=DAY_OFF_CHOICES,
                       default='Friday')
    extra_notes  = models.TextField(blank=True,
                       help_text="Any extra work details e.g. cooking style, "
                                 "dietary restrictions, etc.")

    # Status
    is_verified  = models.BooleanField(default=False)
    availability = models.CharField(max_length=20,
                       choices=AVAILABILITY_CHOICES,
                       default='Available')

    # Photo
    photo        = models.ImageField(upload_to='workers/',
                       blank=True, null=True)

    # NID
    nid_number   = models.CharField(max_length=20, blank=True)

    # ── Feature 2: Emergency / Guardian Contact ────────────────────────────────
    guardian_name     = models.CharField(max_length=100, blank=True)
    guardian_phone    = models.CharField(max_length=15,  blank=True)
    guardian_relation = models.CharField(max_length=20,
                            choices=GUARDIAN_RELATION_CHOICES,
                            blank=True)

    # ── Feature 5: Admin Private Notes ────────────────────────────────────────
    admin_notes  = models.TextField(blank=True,
                       help_text="Private admin notes — NOT shown to users")

    # Ratings
    avg_rating    = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.location})"

    def update_rating(self):
        from django.db.models import Avg
        result = self.reviews.aggregate(Avg('score'))
        self.avg_rating    = round(result['score__avg'] or 0.0, 1)
        self.total_reviews = self.reviews.count()
        self.save(update_fields=['avg_rating', 'total_reviews'])

    # ── Feature 4: Hiring History Count ───────────────────────────────────────
    def total_hires(self):
        return self.hiring_requests.filter(status='Approved').count()

    def star_range(self):
        return range(int(self.avg_rating))

    def empty_star_range(self):
        return range(5 - int(self.avg_rating))


# ─── HIRING REQUEST ───────────────────────────────────────────────────────────
class HiringRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending',   'Pending'),
        ('Approved',  'Approved'),
        ('Rejected',  'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]

    user    = models.ForeignKey(User,   on_delete=models.CASCADE,
                                related_name='hiring_requests')
    worker  = models.ForeignKey(Worker, on_delete=models.CASCADE,
                                related_name='hiring_requests')
    status  = models.CharField(max_length=20,
                                choices=STATUS_CHOICES,
                                default='Pending')
    message = models.TextField(blank=True)

    # ── Feature 3: Salary Negotiation ─────────────────────────────────────────
    proposed_salary = models.PositiveIntegerField(
                          null=True, blank=True,
                          help_text="Salary proposed by family (BDT/month). "
                                    "Leave blank to accept worker's asking salary.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering        = ['-created_at']
        unique_together = ['user', 'worker']

    def __str__(self):
        return f"{self.user.username} → {self.worker.name} [{self.status}]"

    # ── Feature 3: Show negotiation status ────────────────────────────────────
    def salary_status(self):
        if not self.proposed_salary:
            return "Accepted asking salary"
        if self.proposed_salary == self.worker.salary:
            return "Accepted asking salary"
        elif self.proposed_salary < self.worker.salary:
            return f"Proposed ৳{self.proposed_salary} (lower)"
        else:
            return f"Proposed ৳{self.proposed_salary} (higher)"


# ─── CONTRACT ─────────────────────────────────────────────────────────────────
class Contract(models.Model):
    hiring_request = models.OneToOneField(HiringRequest,
                         on_delete=models.CASCADE,
                         related_name='contract')
    start_date     = models.DateField()
    end_date       = models.DateField(null=True, blank=True)
    salary_agreed  = models.PositiveIntegerField()
    terms          = models.TextField(
                         default=(
                             "1. The worker shall report on time every day.\n"
                             "2. The family shall pay the agreed salary monthly.\n"
                             "3. Either party may terminate with 7 days notice.\n"
                             "4. The worker shall be treated with respect.\n"
                             "5. Disputes shall be resolved through GetBua admin."
                         ))
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f"Contract: {self.hiring_request.user.username} ↔ "
                f"{self.hiring_request.worker.name}")


# ─── REVIEW ───────────────────────────────────────────────────────────────────
class Review(models.Model):
    SCORE_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user       = models.ForeignKey(User,   on_delete=models.CASCADE,
                                   related_name='reviews')
    worker     = models.ForeignKey(Worker, on_delete=models.CASCADE,
                                   related_name='reviews')
    hire       = models.OneToOneField(HiringRequest,
                                      on_delete=models.CASCADE,
                                      related_name='review',
                                      null=True, blank=True)
    score      = models.IntegerField(choices=SCORE_CHOICES)
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} rated {self.worker.name}: {self.score}★"

    def star_range(self):
        return range(self.score)

    def empty_star_range(self):
        return range(5 - self.score)


# ─── REPLACEMENT REQUEST ──────────────────────────────────────────────────────
class ReplacementRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending',  'Pending'),
        ('Resolved', 'Resolved'),
    ]

    user           = models.ForeignKey(User,
                         on_delete=models.CASCADE,
                         related_name='replacement_requests')
    hiring_request = models.ForeignKey(HiringRequest,
                         on_delete=models.CASCADE,
                         related_name='replacement_requests')
    reason         = models.TextField()
    status         = models.CharField(max_length=20,
                         choices=STATUS_CHOICES,
                         default='Pending')
    admin_note     = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Replacement for {self.hiring_request} [{self.status}]"