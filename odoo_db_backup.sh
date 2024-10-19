#!/bin/bash

# Odoo database backup script

# Configuration variables
ODOO_DB_NAME="appeul"
BACKUP_DIR="/home/odoo/backup"
BACKUP_FILENAME="odoo_backup_$(date +%Y%m%d_%H%M%S).sql"
PG_USER="odoo"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform database backup
sudo -u odoo pg_dump -F c -b -v -f "$BACKUP_DIR/$BACKUP_FILENAME" "$ODOO_DB_NAME"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_DIR/$BACKUP_FILENAME"
else
    echo "Backup failed"
    exit 1
fi

# Optional: Remove backups older than 30 days
find "$BACKUP_DIR" -name "odoo_backup_*.sql" -type f -mtime +30 -delete

# Optional: Compress the backup file
gzip "$BACKUP_DIR/$BACKUP_FILENAME"

echo "Backup process completed"
