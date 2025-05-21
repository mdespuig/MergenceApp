"""
URL configuration for mergence project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from mergenceApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("mergenceApp.urls")),
    path('homepage/', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_user, name='logout_user'),
    path('registration/', views.registration, name='registration'),
    path('regForm/', views.regForm, name='regForm'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("", include('django.contrib.auth.urls')),
    path('report/', views.report, name='report'),
    path('become-partner/', views.become_partner, name='become_partner'),
    path('check-ticket/', views.check_ticket, name='check_ticket'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/partner-requests/', views.partner_requests, name='partner_requests'),
    path('admin-dashboard/manage-users/', views.manage_users, name='manage_users'),
    path('admin-dashboard/manage-hotlines/', views.manage_hotlines, name='manage_hotlines'),
    path('admin-dashboard/manage-tickets/', views.manage_tickets, name='manage_tickets'),
    path('update_partner_status/', views.update_partner_status, name='update_partner_status'),
    path('delete_users/', views.delete_users, name='delete_users'),
    path('save_user_roles/', views.save_user_roles, name='save_user_roles'),
    path('assign-responder/', views.assign_responder, name='assign_responder'),
    path('edit-timeline-entry/<int:entry_id>/', views.edit_timeline_entry, name='edit_timeline_entry'),
    path('bulk-delete-timeline-entries/', views.bulk_delete_timeline_entries, name='bulk_delete_timeline_entries'),
    path('bulk-delete-hotlines/', views.bulk_delete_hotlines, name='bulk_delete_hotlines'),
    path('view-profile/', views.view_profile, name='view_profile'),
    path('messenger/', views.messenger, name='messenger'),
    path('chat/<str:username>/', views.private_chat, name='private_chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
