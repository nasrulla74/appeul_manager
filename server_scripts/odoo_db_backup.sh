#!/bin/bash

# Odoo database backup script

# Configuration variables
DB_NAME="demo"
BACKUP_DIR="/odoo/bk"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILENAME="odoo_backup_${TIMESTAMP}.sql"

# Change to a directory where odoo_control has access
cd /tmp

# Perform the backup
sudo -u postgres pg_dump $DB_NAME > $BACKUP_DIR/$BACKUP_FILENAME

# Check if the backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_DIR/$BACKUP_FILENAME"
    # Optional: Compress the backup file
    gzip "$BACKUP_DIR/$BACKUP_FILENAME"
    echo "Backup compressed: $BACKUP_DIR/${BACKUP_FILENAME}.gz"
    
    # Optional: Remove backups older than 30 days
    find "$BACKUP_DIR" -name "odoo_backup_*.sql.gz" -type f -mtime +30 -delete
    
    exit 0
else
    echo "Backup failed"
    exit 1
fi
