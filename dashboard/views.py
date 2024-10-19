from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ServerStatus, BackupLog
import sys
print(sys.path)
import paramiko
from datetime import datetime
import logging
from paramiko.ssh_exception import SSHException
import socket

# Add this at the top of the file
logger = logging.getLogger(__name__)

ODOO_BIN_PATH = "/odoo/odoo-server/odoo-bin"
ODOO_CONF_PATH = "/etc/odoo-server.conf"
ODOO_DB_NAME = "demo"
BACKUP_DIR = "/odoo/bk"
backup_filename = "nbk"


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

@login_required
def backup_database(request):
    # SSH connection details
    hostname = '194.195.119.84'
    username = 'odoo_control'
    key_filename = '/home/nasru/.ssh/odoo_comm_odoo_contrr'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        logger.info("Attempting to connect to the server...")
        client.connect(hostname, username=username, key_filename=key_filename, timeout=10)
        logger.info("Successfully connected to the server.")
        
        # Command to run the backup script
        backup_command = "sudo ./odoo_db_backup.sh"
        
        logger.info(f"Executing backup command: {backup_command}")

        # Execute command with a timeout
        stdin, stdout, stderr = client.exec_command(backup_command, timeout=60)
        
        # Wait for the command to complete
        logger.info("Waiting for the backup command to complete...")
        exit_status = stdout.channel.recv_exit_status()
        logger.info(f"Backup command completed with exit status: {exit_status}")

        # Read the output and error streams
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        logger.info(f"Backup command output: {output}")
        if error:
            logger.error(f"Backup command error: {error}")

        success = exit_status == 0
        filename = ""
        file_location = ""
        if success:
            # Extract filename and location from the output
            for line in output.split('\n'):
                if line.startswith("Backup completed successfully:"):
                    file_location = line.split(": ", 1)[1].strip()
                    filename = file_location.split('/')[-1]
                elif line.startswith("Backup compressed:"):
                    file_location = line.split(": ", 1)[1].strip()
                    filename = file_location.split('/')[-1]
            logger.info(f"Backup file created successfully: {file_location}")
        else:
            logger.error("Backup file creation failed.")

        # Log the backup attempt
        BackupLog.objects.create(
            timestamp=datetime.now(),
            filename=filename,
            success=success,
            output=output,
            error=error
        )
        
        return render(request, 'dashboard/backup_result.html', {
            'output': output,
            'error': error,
            'filename': filename,
            'file_location': file_location,
            'success': success
        })
    except (paramiko.SSHException, socket.error, TimeoutError) as e:
        logger.exception("SSH connection error or timeout occurred")
        error_message = f"Connection error: {str(e)}"
        BackupLog.objects.create(
            timestamp=datetime.now(),
            filename="",
            success=False,
            output="",
            error=error_message
        )
        return render(request, 'dashboard/backup_result.html', {
            'output': '',
            'error': error_message,
            'filename': '',
            'file_location': '',
            'success': False
        })
    except Exception as e:
        logger.exception("An unexpected error occurred during backup")
        error_message = f"Unexpected error: {str(e)}"
        BackupLog.objects.create(
            timestamp=datetime.now(),
            filename="",
            success=False,
            output="",
            error=error_message
        )
        return render(request, 'dashboard/backup_result.html', {
            'output': '',
            'error': error_message,
            'filename': '',
            'file_location': '',
            'success': False
        })
    finally:
        client.close()
