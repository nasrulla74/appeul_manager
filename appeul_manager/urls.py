from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from dashboard import views
from dashboard.auth import CustomLoginView

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')

urlpatterns = [
    path('', root_redirect, name='root'),
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('', include('django.contrib.auth.urls')),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('control/<str:action>/', login_required(views.control_server), name='control_server'),
    path('backup/', login_required(views.backup_database), name='backup_database'),


]
