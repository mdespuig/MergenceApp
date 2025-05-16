from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models import OuterRef, Subquery
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from .models import EmergencyReport, PartnerApplication, Hotline, TimelineUpdates
import json

def home(request):
    return render(request, "homepage.html")

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
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
            else:
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
    hotlines = Hotline.objects.all()
    latest_ticket_id = None

    grouped_hotlines = {
        'paramedics': hotlines.filter(hotline_type='paramedics'),
        'fire': hotlines.filter(hotline_type='fire'),
        'law': hotlines.filter(hotline_type='law'),
        'utility': hotlines.filter(hotline_type='utility'),
    }

    if request.method == 'POST':
        report = EmergencyReport(
            user=request.user,
            name=request.POST['name'],
            surname=request.POST['surname'],
            contact_number=request.POST['contact_number'],
            hotline_category=request.POST['hotline_category'],
            hotline_detail=request.POST['hotline_detail'],
        )
        report.save()
        latest_ticket_id = report.ticket_id

        TimelineUpdates.objects.create(
            report=report,
            title="Report Created",
            responder=None
        )

        messages.success(request, 'Your emergency report has been submitted successfully!')

    return render(request, 'report.html', {
        'latest_ticket_id': latest_ticket_id,
        'grouped_hotlines': grouped_hotlines
    })

@login_required
def become_partner(request):
    submitted = False

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        hotline_number = request.POST.get('hotline_number', '').strip()
        hotline_category = request.POST.get('hotline_category', '').strip()

        if name and address and hotline_number and hotline_category:
            PartnerApplication.objects.create(
                user=request.user,
                organization_name=name,
                address=address,
                hotline_number=hotline_number,
                hotline_category=hotline_category
            )
            submitted = True
            messages.success(request, "Your partnership application has been submitted successfully!")
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'becomePartner.html', {
        'latest_ticket_id': submitted
    })

@login_required
def admin_dashboard(request):
    if request.user.is_superuser or request.user.is_staff:
        reports = EmergencyReport.objects.all()
        partner_applications = PartnerApplication.objects.all()
        return render(request, 'adminDashboard.html', {
            'reports': reports,
            'partner_applications': partner_applications
        })
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
@login_required
def partner_requests(request):
    if request.user.is_superuser:
        partner_applications = PartnerApplication.objects.all().order_by('date_submitted')
        return render(request, 'adminPartnership.html', {
            'partner_applications': partner_applications
        })
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

@csrf_exempt
def update_partner_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("DATA RECEIVED:", data)

        ids = data.get('ids', [])
        status = data.get('status', '')

        if not ids or status not in ['Approved', 'Rejected']:
            return JsonResponse({'success': False, 'error': 'Invalid data'})

        updated = PartnerApplication.objects.filter(id__in=ids).update(status=status)
        print("UPDATED ROWS:", updated)

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid method'})

@login_required
def manage_users(request):
    users_qs = User.objects.filter(is_superuser=False)
    
    users = []
    for user in users_qs:
        profile = getattr(user, 'profile', None)  
        address = profile.address if profile else ''
        contact_number = profile.contact_number if profile else ''
        
        user_type = "Partner" if user.is_staff else "Default"
        
        users.append({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'address': address,
            'contact_number': contact_number,
            'user_type': user_type,
        })
    
    return render(request, 'adminUser.html', {'users': users})

@login_required
@require_POST
def delete_users(request):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        ids_to_delete = data.get('ids', [])

        users_to_delete = User.objects.filter(id__in=ids_to_delete, is_superuser=False).exclude(id=request.user.id)

        deleted_count = users_to_delete.count()
        users_to_delete.delete()

        return JsonResponse({'success': True, 'deleted_count': deleted_count})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
@login_required
@require_POST
def save_user_roles(request):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        updates = data.get('updates', [])

        for update in updates:
            user_id = update.get('id')
            user_type = update.get('user_type')

            if user_type not in ['Default', 'Partner']:
                continue

            user = User.objects.get(id=user_id)
            if user.is_superuser:
                continue 

            user.is_staff = (user_type == 'Partner')
            user.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
def manage_hotlines(request):
    username_error = None

    if request.method == 'POST':
        organization_name = request.POST.get('organization_name', '').strip()
        hotline_type = request.POST.get('hotline_type', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        hotline_number = request.POST.get('hotline_number', '').strip()
        username = request.POST.get('username', '').strip()

        if not all([organization_name, hotline_type, email, address, hotline_number]):
            messages.error(request, "All fields except Username are required.")
        else:
            hotline = Hotline(
                organization_name=organization_name,
                hotline_type=hotline_type,
                email=email,
                address=address,
                hotline_number=hotline_number
            )

            if username:
                try:
                    user = User.objects.get(username=username)
                    hotline.user = user
                except User.DoesNotExist:
                    username_error = f"No user found with username '{username}'"
            if not username_error:
                hotline.save()
                messages.success(request, "Hotline added successfully!")
                return redirect('manage_hotlines')

    hotlines = Hotline.objects.all()
    return render(request, "adminHotline.html", {
        'hotlines': hotlines,
        'username_error': username_error
    })

@login_required
def manage_tickets(request):
    ticket = None
    timeline_entries = []

    if request.method == 'GET':
        ticket_id = request.GET.get('code')
        if ticket_id:
            try:
                ticket = EmergencyReport.objects.get(ticket_id=ticket_id)
                timeline_entries = ticket.timeline_updates.order_by('timestamp')
            except EmergencyReport.DoesNotExist:
                ticket = None
                timeline_entries = []

    elif request.method == 'POST':
        ticket_id = request.GET.get('code')
        ticket = EmergencyReport.objects.get(ticket_id=ticket_id)

        title = request.POST.get('title')
        responder = request.POST.get('responder') or None

        if not title or title.strip() == "":
            title = "(No title provided)"

        TimelineUpdates.objects.create(
            report=ticket,
            title=title,
            responder=responder,
        )

        timeline_entries = ticket.timeline_updates.order_by('timestamp')

    return render(request, 'adminTicket.html', {
        'ticket': ticket,
        'timeline_entries': timeline_entries,
    })

def ticket(request):
    ticket_code = request.GET.get('code')
    updates = []

    if ticket_code:
        try:
            report = EmergencyReport.objects.get(ticket_id=ticket_code)
            updates = report.timeline_updates.order_by('timestamp')
        except EmergencyReport.DoesNotExist:
            report = None
            updates = []

    return render(request, 'ticket.html', {
        'ticket_code': ticket_code,
        'updates': updates,
    })

def assign_responder(request):
    if request.method == 'POST':
        responder_username = request.POST.get('responder_username')
        ticket_id = request.POST.get('ticket_id')

        if not responder_username or not ticket_id:
            return JsonResponse({'status': 'error', 'message': 'Missing data.'})

        try:
            user = User.objects.get(username=responder_username)
            updated = TimelineUpdates.objects.filter(id=ticket_id).update(responder=user)

            if updated == 0:
                return JsonResponse({'status': 'error', 'message': 'Timeline update not found.'})

            return JsonResponse({'status': 'success', 'message': 'Responder assigned.'})

        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Responder not found.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@csrf_exempt
@login_required
def edit_timeline_entry(request, entry_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_title = data.get('title')
            update = TimelineUpdates.objects.get(id=entry_id)
            update.title = new_title
            update.save()
            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'invalid'})

@csrf_exempt
@login_required
def bulk_delete_timeline_entries(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids = data.get('ids', [])
            TimelineUpdates.objects.filter(id__in=ids).delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid'})

@login_required
@require_POST
def bulk_delete_hotlines(request):
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        if not isinstance(ids, list):
            return JsonResponse({'status': 'error', 'message': 'Invalid data format.'}, status=400)

        deleted_count, _ = Hotline.objects.filter(id__in=ids).delete()

        if deleted_count > 0:
            return JsonResponse({'status': 'success', 'deleted_count': deleted_count})
        else:
            return JsonResponse({'status': 'error', 'message': 'No hotlines deleted.'}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@login_required
def check_ticket(request):
    ticket = None
    timeline_entries = []

    if request.method == 'GET' and 'code' in request.GET:
        code = request.GET.get('code').strip()
        try:
            ticket = EmergencyReport.objects.get(ticket_id=code)
            
            org_subquery = PartnerApplication.objects.filter(
                user=OuterRef('responder_id')
            ).values('organization_name')[:1]
            
            timeline_entries = TimelineUpdates.objects.filter(report=ticket).annotate(
                organization_name=Subquery(org_subquery)
            ).order_by('timestamp')
            
        except EmergencyReport.DoesNotExist:
            ticket = None

    context = {
        'ticket': ticket,
        'timeline_entries': timeline_entries,
    }
    return render(request, "checkTicket.html", context)
