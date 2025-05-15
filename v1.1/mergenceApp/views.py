from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from .models import EmergencyReport
from .models import TimelineUpdate, EmergencyReport
from django.shortcuts import get_object_or_404

def home(request):
    return render(request, "homepage.html")

def profile(request):
    return render(request, "profile.html")

def ticket(request):
    ticket_code = request.GET.get('code')
    updates = []

    if ticket_code:
        try:
            report = EmergencyReport.objects.get(ticket_id=ticket_code)
            updates = report.timeline_updates.order_by('-timestamp')  # newest first
        except EmergencyReport.DoesNotExist:
            report = None
            updates = []

    return render(request, 'ticket.html', {
        'ticket_code': ticket_code,
        'updates': updates,
    })

@login_required
def admin_ticket(request):
    ticket = None
    timeline_entries = []

    if request.method == 'GET':
        ticket_id = request.GET.get('code')
        if ticket_id:
            try:
                ticket = EmergencyReport.objects.get(ticket_id=ticket_id)
                timeline_entries = ticket.timeline_updates.order_by('-timestamp')
            except EmergencyReport.DoesNotExist:
                ticket = None
                timeline_entries = []

    elif request.method == 'POST':
        ticket_id = request.GET.get('code')
        ticket = EmergencyReport.objects.get(ticket_id=ticket_id)

        title = request.POST.get('title')
        responder = request.POST.get('responder') or None  # optional

        TimelineUpdate.objects.create(
            report=ticket,
            title=title,
            responder=responder,
        )

        timeline_entries = ticket.timeline_updates.order_by('-timestamp')

    return render(request, 'admin_ticket.html', {
        'ticket': ticket,
        'timeline_entries': timeline_entries,
    })


@login_required
def dashboard(request):
    return render(request, "dashboard.html")


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, "All fields are required.")
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')

    return render(request, 'login.html')

@require_POST
def logout_user(request):
    logout(request)
    return redirect('home')

def registration(request):
    return render(request, "registration.html")

def regForm(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm-password', '').strip()

        if not username or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, 'registrationForm.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'registrationForm.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'registrationForm.html')

        user = User.objects.create(
            username=username,
            password=make_password(password)
        )
        return redirect('login')

    return render(request, 'registrationForm.html')

@login_required
def report(request):
    latest_ticket_id = None

    if request.method == 'POST':
        report_instance = EmergencyReport(
            user=request.user,
            name=request.POST['name'],
            surname=request.POST['surname'],
            contact_number=request.POST['contact_number'],
            hotline_category=request.POST['hotline_category'],
            hotline_detail=request.POST['hotline_detail'],
        )
        report_instance.save()
        latest_ticket_id = report_instance.ticket_id

        TimelineUpdate.objects.create(
            report=report_instance,
            title="Report Created",
            responder=None
        )

        messages.success(request, 'Your emergency report has been submitted successfully!')

    return render(request, 'report.html', {
        'latest_ticket_id': latest_ticket_id
    })