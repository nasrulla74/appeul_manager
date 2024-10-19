from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ServerStatus
import sys
print(sys.path)
import paramiko



@login_required
def dashboard(request):
    status = ServerStatus.objects.first()
    return render(request, 'dashboard/dashboard.html', {'status': status})

@login_required
def control_server(request, action):
    if action not in ['start', 'stop', 'status']:
        return redirect('dashboard')

    # SSH connection details
    hostname = '194.195.119.84'
    username = 'odoo_control'
    key_filename = '/home/nasru/.ssh/odoo_comm_odoo_contrr'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, key_filename=key_filename)
        stdin, stdout, stderr = client.exec_command(f'sudo ./odoo_control.sh {action}')
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        # Update server status
        status, created = ServerStatus.objects.get_or_create(pk=1)
        
        if action == 'start':
            if 'Odoo server started' in output:
                status.is_running = True
                status.save()
        elif action == 'stop':
            if 'Odoo server stopped' in output:
                status.is_running = False
                status.save()
        elif action == 'status':
            is_running = 'active (running)' in output
            status.is_running = is_running
            status.save()
        
        return render(request, 'dashboard/control_result.html', {
            'output': output,
            'error': error,
            'action': action,
            'status': status
        })
    except Exception as e:
        return render(request, 'dashboard/control_result.html', {
            'output': '',
            'error': str(e),
            'action': action,
            'status': status
        })
    finally:
        client.close()
