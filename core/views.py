import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()
from .forms import (RegisterForm, LoginForm,
                    ProfileEditForm, PasswordResetForm)
from .models import (Worker, HiringRequest, Contract,
                     Review, ReplacementRequest, SalaryPayment)


# ─── HOME ─────────────────────────────────────────────────────────────────────
def home(request):
    featured = Worker.objects.filter(
        is_verified=True,
        availability='Available'
    ).order_by('-avg_rating')[:6]
    return render(request, 'home.html', {'featured': featured})


# ─── REGISTER ─────────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome to GetBua, {user.first_name}! 🎉"
            )
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html',
                  {'form': form})


# ─── LOGIN ────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                messages.success(
                    request,
                    f"Welcome back, "
                    f"{user.first_name or user.username}! 👋"
                )
                return redirect(request.GET.get('next', 'home'))
            else:
                messages.error(request,
                               "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html',
                  {'form': form})


# ─── LOGOUT ───────────────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out. See you soon!")
    return redirect('home')


# ─── CUSTOM PASSWORD RESET (email + birthday) ─────────────────────────────────
def custom_password_reset(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email    = form.cleaned_data['email']
            birthday = form.cleaned_data['birthday']
            new_pass = form.cleaned_data['new_password1']

            # Find user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(
                    request,
                    "No account found with that email address."
                )
                return render(request,
                              'registration/password_reset_custom.html',
                              {'form': form})

            # Verify birthday
            if (not hasattr(user, 'profile') or
                    user.profile.birthday != birthday):
                messages.error(
                    request,
                    "Email and birthday do not match our records."
                )
                return render(request,
                              'registration/password_reset_custom.html',
                              {'form': form})

            # Reset password
            user.set_password(new_pass)
            user.save()
            messages.success(
                request,
                "✅ Password reset successfully! "
                "You can now login with your new password."
            )
            return redirect('login')
    else:
        form = PasswordResetForm()

    return render(request,
                  'registration/password_reset_custom.html',
                  {'form': form})


# ─── PROFILE ──────────────────────────────────────────────────────────────────
@login_required
def profile_view(request):
    hires       = HiringRequest.objects.filter(
                      user=request.user).select_related('worker')
    total_hires = hires.count()
    approved    = hires.filter(status='Approved').count()
    return render(request, 'registration/profile.html', {
        'total_hires': total_hires,
        'approved':    approved,
    })


# ─── PROFILE EDIT ─────────────────────────────────────────────────────────────
@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # Update User model fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name  = form.cleaned_data['last_name']
            request.user.email      = form.cleaned_data['email']
            request.user.save()
            messages.success(request,
                             "✅ Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProfileEditForm(
            instance=profile,
            initial={
                'first_name': request.user.first_name,
                'last_name':  request.user.last_name,
                'email':      request.user.email,
            }
        )
    return render(request, 'registration/profile_edit.html',
                  {'form': form})


# ─── TRAINING PAGE ────────────────────────────────────────────────────────────
def training_page(request):
    return render(request, 'training.html')


# ─── WORKER LIST ──────────────────────────────────────────────────────────────
def worker_list(request):
    workers  = Worker.objects.filter(
                   is_verified=True,
                   accepts_short_term=False
               ) | Worker.objects.filter(
                   is_verified=True,
                   accepts_short_term=True
               )
    workers  = Worker.objects.filter(is_verified=True)

    q        = request.GET.get('q',            '').strip()
    location = request.GET.get('location',     '').strip()
    skill    = request.GET.get('skill',        '').strip()
    min_sal  = request.GET.get('min_salary',   '').strip()
    max_sal  = request.GET.get('max_salary',   '').strip()
    avail    = request.GET.get('availability', '').strip()

    if q:
        workers = workers.filter(
            Q(name__icontains=q)     |
            Q(skills__icontains=q)   |
            Q(location__icontains=q)
        )
    if location:
        workers = workers.filter(location=location)
    if skill:
        workers = workers.filter(skills=skill)
    if min_sal:
        try:
            workers = workers.filter(salary__gte=int(min_sal))
        except ValueError:
            pass
    if max_sal:
        try:
            workers = workers.filter(salary__lte=int(max_sal))
        except ValueError:
            pass
    if avail:
        workers = workers.filter(availability=avail)

    paginator   = Paginator(workers, 9)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)

    return render(request, 'workers/list.html', {
        'workers':          page_obj,
        'page_obj':         page_obj,
        'total_count':      paginator.count,
        'location_choices': Worker.LOCATION_CHOICES,
        'skill_choices':    Worker.SKILL_CHOICES,
        'avail_choices':    Worker.AVAILABILITY_CHOICES,
        'q':                q,
        'location':         location,
        'skill':            skill,
        'min_salary':       min_sal,
        'max_salary':       max_sal,
        'availability':     avail,
    })


# ─── SHORT TERM LIST ──────────────────────────────────────────────────────────
def short_term_list(request):
    workers = Worker.objects.filter(
        is_verified=True,
        accepts_short_term=True,
        availability='Available'
    )

    q        = request.GET.get('q',        '').strip()
    location = request.GET.get('location', '').strip()
    skill    = request.GET.get('skill',    '').strip()

    if q:
        workers = workers.filter(
            Q(name__icontains=q) |
            Q(skills__icontains=q) |
            Q(location__icontains=q)
        )
    if location:
        workers = workers.filter(location=location)
    if skill:
        workers = workers.filter(skills=skill)

    paginator   = Paginator(workers, 9)
    page_obj    = paginator.get_page(request.GET.get('page'))

    return render(request, 'workers/short_term_list.html', {
        'workers':          page_obj,
        'page_obj':         page_obj,
        'total_count':      paginator.count,
        'location_choices': Worker.LOCATION_CHOICES,
        'skill_choices':    Worker.SKILL_CHOICES,
        'q':                q,
        'location':         location,
        'skill':            skill,
    })


# ─── WORKER DETAIL ────────────────────────────────────────────────────────────
def worker_detail(request, pk):
    worker  = get_object_or_404(Worker, pk=pk, is_verified=True)
    reviews = worker.reviews.select_related('user').all()

    existing_request = None
    if request.user.is_authenticated:
        existing_request = HiringRequest.objects.filter(
            user=request.user, worker=worker
        ).first()

    return render(request, 'workers/detail.html', {
        'worker':           worker,
        'reviews':          reviews,
        'existing_request': existing_request,
    })


# ─── HIRE WORKER ──────────────────────────────────────────────────────────────
@login_required
def hire_worker(request, worker_id):
    worker = get_object_or_404(Worker, pk=worker_id, is_verified=True)

    if HiringRequest.objects.filter(
            user=request.user, worker=worker).exists():
        messages.warning(
            request,
            f"You already have a request for {worker.name}."
        )
        return redirect('worker_detail', pk=worker_id)

    if worker.availability != 'Available':
        messages.error(
            request,
            f"{worker.name} is currently not available."
        )
        return redirect('worker_detail', pk=worker_id)

    if request.method == 'POST':
        hire_type       = request.POST.get('hire_type', 'Full Time')
        message         = request.POST.get('message', '')
        proposed_salary = request.POST.get('proposed_salary', '').strip()
        duration_days   = request.POST.get('duration_days', '').strip()
        start_date      = request.POST.get('start_date', '').strip()

        hire = HiringRequest(
            user=request.user,
            worker=worker,
            hire_type=hire_type,
            message=message
        )
        if proposed_salary:
            try:
                hire.proposed_salary = int(proposed_salary)
            except ValueError:
                pass
        if duration_days:
            try:
                hire.duration_days = int(duration_days)
            except ValueError:
                pass
        if start_date:
            hire.start_date = start_date

        hire.save()
        messages.success(
            request,
            f"✅ Hiring request for {worker.name} submitted!"
        )
        return redirect('my_hires')

    return render(request, 'hiring/hire_confirm.html',
                  {'worker': worker})


# ─── MY HIRES ─────────────────────────────────────────────────────────────────
@login_required
def my_hires(request):
    hires = HiringRequest.objects.filter(
        user=request.user
    ).select_related('worker').prefetch_related(
        'replacement_requests', 'contract'
    ).order_by('-created_at')
    return render(request, 'hiring/my_hires.html',
                  {'hires': hires})


# ─── VIEW CONTRACT ────────────────────────────────────────────────────────────
@login_required
def view_contract(request, hire_id):
    hire     = get_object_or_404(HiringRequest, pk=hire_id,
                                 user=request.user, status='Approved')
    contract = get_object_or_404(Contract, hiring_request=hire)
    return render(request, 'hiring/contract.html', {
        'hire':     hire,
        'contract': contract,
    })


# ─── SUBMIT RATING ────────────────────────────────────────────────────────────
@login_required
def submit_rating(request, hire_id):
    hire = get_object_or_404(HiringRequest, pk=hire_id,
                             user=request.user, status='Approved')
    if hasattr(hire, 'review'):
        messages.warning(request, "You already reviewed this worker.")
        return redirect('my_hires')

    if request.method == 'POST':
        score   = request.POST.get('score')
        comment = request.POST.get('comment', '')
        if not score or int(score) not in range(1, 6):
            messages.error(request, "Please select a rating.")
            return render(request, 'hiring/rate.html',
                          {'hire': hire})
        Review.objects.create(
            user=request.user, worker=hire.worker,
            hire=hire, score=int(score), comment=comment
        )
        hire.worker.update_rating()
        messages.success(request,
                         f"⭐ Review for {hire.worker.name} saved!")
        return redirect('my_hires')

    return render(request, 'hiring/rate.html', {'hire': hire})


# ─── REQUEST REPLACEMENT ──────────────────────────────────────────────────────
@login_required
def request_replacement(request, hire_id):
    hire = get_object_or_404(HiringRequest, pk=hire_id,
                             user=request.user, status='Approved')
    if hire.replacement_requests.filter(status='Pending').exists():
        messages.warning(request,
                         "You already have a pending replacement.")
        return redirect('my_hires')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, "Please provide a reason.")
            return render(request, 'hiring/replace.html',
                          {'hire': hire})
        ReplacementRequest.objects.create(
            user=request.user,
            hiring_request=hire,
            reason=reason
        )
        messages.success(request, "🔄 Replacement request submitted!")
        return redirect('my_hires')

    return render(request, 'hiring/replace.html', {'hire': hire})


# ─── ADMIN DASHBOARD ──────────────────────────────────────────────────────────
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')

    pending_hires  = HiringRequest.objects.filter(
                         status='Pending').select_related(
                         'user', 'worker')
    approved_hires = HiringRequest.objects.filter(
                         status='Approved').select_related(
                         'user', 'worker')
    all_hires      = HiringRequest.objects.all().select_related(
                         'user', 'worker')
    all_workers    = Worker.objects.all()
    replacements   = ReplacementRequest.objects.filter(
                         status='Pending').select_related(
                         'user', 'hiring_request__worker')

    return render(request, 'dashboard/admin_dashboard.html', {
        'pending_hires':  pending_hires,
        'approved_hires': approved_hires,
        'all_hires':      all_hires,
        'all_workers':    all_workers,
        'replacements':   replacements,
        'total_workers':  all_workers.count(),
        'avail_workers':  all_workers.filter(
                              availability='Available').count(),
        'pending_count':  pending_hires.count(),
        'approved_count': HiringRequest.objects.filter(
                              status='Approved').count(),
        'replace_count':  replacements.count(),
        'total_reviews':  Review.objects.count(),
    })


# ─── APPROVE HIRE ─────────────────────────────────────────────────────────────
@login_required
def approve_hire(request, hire_id):
    if not request.user.is_staff:
        return redirect('home')
    hire        = get_object_or_404(HiringRequest, pk=hire_id)
    hire.status = 'Approved'
    hire.save()
    hire.worker.availability = 'Hired'
    hire.worker.save(update_fields=['availability'])
    agreed = hire.proposed_salary or hire.worker.salary
    if not hasattr(hire, 'contract'):
        Contract.objects.create(
            hiring_request=hire,
            start_date=datetime.date.today(),
            salary_agreed=agreed,
        )
    messages.success(request,
                     f"✅ Hire approved for {hire.worker.name}.")
    return redirect('admin_dashboard')


# ─── REJECT HIRE ──────────────────────────────────────────────────────────────
@login_required
def reject_hire(request, hire_id):
    if not request.user.is_staff:
        return redirect('home')
    hire        = get_object_or_404(HiringRequest, pk=hire_id)
    hire.status = 'Rejected'
    hire.save()
    messages.warning(request,
                     f"❌ Hire for {hire.worker.name} rejected.")
    return redirect('admin_dashboard')


# ─── RESOLVE REPLACEMENT ──────────────────────────────────────────────────────
@login_required
def resolve_replacement(request, rep_id):
    if not request.user.is_staff:
        return redirect('home')
    rep = get_object_or_404(ReplacementRequest, pk=rep_id)
    if request.method == 'POST':
        old_hire                 = rep.hiring_request
        old_hire.status          = 'Cancelled'
        old_hire.save()
        old_hire.worker.availability = 'Available'
        old_hire.worker.save(update_fields=['availability'])
        rep.admin_note = request.POST.get('admin_note', '')
        rep.status     = 'Resolved'
        rep.save()
        messages.success(request, "🔄 Replacement resolved.")
        return redirect('admin_dashboard')
    return render(request, 'dashboard/resolve_replacement.html',
                  {'rep': rep})


# ─── SALARY PAYMENT ───────────────────────────────────────────────────────────
@login_required
def add_salary_payment(request, hire_id):
    hire = get_object_or_404(HiringRequest, pk=hire_id,
                             user=request.user, status='Approved')
    if request.method == 'POST':
        month  = request.POST.get('month')
        year   = request.POST.get('year')
        amount = request.POST.get('amount')
        paid_on= request.POST.get('paid_on')
        note   = request.POST.get('note', '')
        if SalaryPayment.objects.filter(
                hiring_request=hire, month=month, year=year).exists():
            messages.warning(request,
                             f"Salary for {month} {year} already recorded.")
            return redirect('salary_history', hire_id=hire_id)
        try:
            SalaryPayment.objects.create(
                hiring_request=hire, month=month,
                year=int(year), amount=int(amount),
                paid_on=paid_on, note=note
            )
            messages.success(request,
                             f"✅ Payment of ৳{amount} recorded.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('salary_history', hire_id=hire_id)
    return render(request, 'hiring/salary_payment.html',
                  {'hire': hire})


@login_required
def salary_history(request, hire_id):
    hire     = get_object_or_404(HiringRequest, pk=hire_id,
                                 user=request.user)
    payments = SalaryPayment.objects.filter(
                   hiring_request=hire).order_by('-year', '-created_at')
    total    = sum(p.amount for p in payments)
    return render(request, 'hiring/salary_history.html', {
        'hire': hire, 'payments': payments, 'total': total,
    })