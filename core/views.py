import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import RegisterForm, LoginForm
from .models import (Worker, HiringRequest, Contract,
                     Review, ReplacementRequest)


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
                f"Welcome to GetBua, {user.first_name}! 🎉 "
                "Your account has been created."
            )
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


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
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


# ─── LOGOUT ───────────────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out. See you soon! 👋")
    return redirect('home')


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


# ─── WORKER LIST ──────────────────────────────────────────────────────────────
def worker_list(request):
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

    context = {
        'workers':          workers,
        'location_choices': Worker.LOCATION_CHOICES,
        'skill_choices':    Worker.SKILL_CHOICES,
        'avail_choices':    Worker.AVAILABILITY_CHOICES,
        'q':                q,
        'location':         location,
        'skill':            skill,
        'min_salary':       min_sal,
        'max_salary':       max_sal,
        'availability':     avail,
    }
    return render(request, 'workers/list.html', context)


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

    # Prevent duplicate request for same worker
    if HiringRequest.objects.filter(
            user=request.user, worker=worker).exists():
        messages.warning(
            request,
            f"You already have a hiring request for {worker.name}."
        )
        return redirect('worker_detail', pk=worker_id)

    if worker.availability != 'Available':
        messages.error(
            request,
            f"{worker.name} is currently not available for hire."
        )
        return redirect('worker_detail', pk=worker_id)

    if request.method == 'POST':
        message         = request.POST.get('message', '')
        # Feature 3: Salary Negotiation
        proposed_salary = request.POST.get('proposed_salary', '').strip()

        hire = HiringRequest(
            user=request.user,
            worker=worker,
            message=message
        )
        if proposed_salary:
            try:
                hire.proposed_salary = int(proposed_salary)
            except ValueError:
                pass
        hire.save()

        messages.success(
            request,
            f"✅ Hiring request for {worker.name} submitted! "
            "Admin will review shortly."
        )
        return redirect('my_hires')

    return render(request, 'hiring/hire_confirm.html', {'worker': worker})


# ─── MY HIRES ─────────────────────────────────────────────────────────────────
@login_required
def my_hires(request):
    hires = HiringRequest.objects.filter(
        user=request.user
    ).select_related('worker').prefetch_related(
        'replacement_requests', 'contract'
    ).order_by('-created_at')
    return render(request, 'hiring/my_hires.html', {'hires': hires})


# ─── VIEW CONTRACT ────────────────────────────────────────────────────────────
@login_required
def view_contract(request, hire_id):
    hire     = get_object_or_404(
                   HiringRequest, pk=hire_id,
                   user=request.user, status='Approved')
    contract = get_object_or_404(Contract, hiring_request=hire)
    return render(request, 'hiring/contract.html', {
        'hire':     hire,
        'contract': contract,
    })


# ─── SUBMIT RATING ────────────────────────────────────────────────────────────
@login_required
def submit_rating(request, hire_id):
    # Only approved hires can rate
    hire = get_object_or_404(
        HiringRequest, pk=hire_id,
        user=request.user, status='Approved'
    )

    if hasattr(hire, 'review'):
        messages.warning(request,
                         "You have already reviewed this worker.")
        return redirect('my_hires')

    if request.method == 'POST':
        score   = request.POST.get('score')
        comment = request.POST.get('comment', '')

        if not score or int(score) not in range(1, 6):
            messages.error(request,
                           "Please select a rating between 1 and 5.")
            return render(request, 'hiring/rate.html', {'hire': hire})

        Review.objects.create(
            user=request.user,
            worker=hire.worker,
            hire=hire,
            score=int(score),
            comment=comment
        )
        hire.worker.update_rating()
        messages.success(
            request,
            f"⭐ Thank you! Your review for "
            f"{hire.worker.name} has been saved."
        )
        return redirect('my_hires')

    return render(request, 'hiring/rate.html', {'hire': hire})


# ─── REQUEST REPLACEMENT ──────────────────────────────────────────────────────
@login_required
def request_replacement(request, hire_id):
    hire = get_object_or_404(
        HiringRequest, pk=hire_id,
        user=request.user, status='Approved'
    )

    if hire.replacement_requests.filter(status='Pending').exists():
        messages.warning(
            request,
            "You already have a pending replacement for this hire."
        )
        return redirect('my_hires')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request,
                           "Please provide a reason for replacement.")
            return render(request,
                          'hiring/replace.html', {'hire': hire})

        ReplacementRequest.objects.create(
            user=request.user,
            hiring_request=hire,
            reason=reason
        )
        messages.success(
            request,
            "🔄 Replacement request submitted. "
            "Admin will assign a new worker soon."
        )
        return redirect('my_hires')

    return render(request, 'hiring/replace.html', {'hire': hire})


# ─── ADMIN DASHBOARD ──────────────────────────────────────────────────────────
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admins only.")
        return redirect('home')

    pending_hires  = HiringRequest.objects.filter(
                         status='Pending').select_related('user', 'worker')
    approved_hires = HiringRequest.objects.filter(
                         status='Approved').select_related('user', 'worker')
    all_hires      = HiringRequest.objects.all().select_related(
                         'user', 'worker')
    all_workers    = Worker.objects.all()
    replacements   = ReplacementRequest.objects.filter(
                         status='Pending').select_related(
                         'user', 'hiring_request__worker')

    context = {
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
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


# ─── APPROVE HIRE ─────────────────────────────────────────────────────────────
@login_required
def approve_hire(request, hire_id):
    if not request.user.is_staff:
        return redirect('home')
    hire        = get_object_or_404(HiringRequest, pk=hire_id)
    hire.status = 'Approved'
    hire.save()

    # Mark worker as Hired
    hire.worker.availability = 'Hired'
    hire.worker.save(update_fields=['availability'])

    # Auto-generate digital contract
    # Use proposed salary if family suggested one, else worker's salary
    agreed_salary = hire.proposed_salary or hire.worker.salary
    if not hasattr(hire, 'contract'):
        Contract.objects.create(
            hiring_request=hire,
            start_date=datetime.date.today(),
            salary_agreed=agreed_salary,
        )

    messages.success(
        request,
        f"✅ Hire approved for {hire.worker.name}. "
        f"Contract generated with salary ৳{agreed_salary}."
    )
    return redirect('admin_dashboard')


# ─── REJECT HIRE ──────────────────────────────────────────────────────────────
@login_required
def reject_hire(request, hire_id):
    if not request.user.is_staff:
        return redirect('home')
    hire        = get_object_or_404(HiringRequest, pk=hire_id)
    hire.status = 'Rejected'
    hire.save()
    messages.warning(
        request,
        f"❌ Hiring request for {hire.worker.name} rejected."
    )
    return redirect('admin_dashboard')


# ─── RESOLVE REPLACEMENT ──────────────────────────────────────────────────────
@login_required
def resolve_replacement(request, rep_id):
    if not request.user.is_staff:
        return redirect('home')
    rep = get_object_or_404(ReplacementRequest, pk=rep_id)

    if request.method == 'POST':
        admin_note = request.POST.get('admin_note', '').strip()

        # Cancel old hire and free old worker
        old_hire                = rep.hiring_request
        old_hire.status         = 'Cancelled'
        old_hire.save()
        old_worker              = old_hire.worker
        old_worker.availability = 'Available'
        old_worker.save(update_fields=['availability'])

        rep.admin_note = admin_note
        rep.status     = 'Resolved'
        rep.save()

        messages.success(
            request,
            f"🔄 Replacement resolved. "
            f"{old_worker.name} is now available again."
        )
        return redirect('admin_dashboard')

    return render(request, 'dashboard/resolve_replacement.html',
                  {'rep': rep})