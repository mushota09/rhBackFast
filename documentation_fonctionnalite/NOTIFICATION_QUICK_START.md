# Notification System - Quick Start Guide

## Setup (5 minutes)

### 1. Configure Email Settings

Add to your `.env` file:

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourcompany.com
SMTP_TLS=True
NOTIFICATIONS_ENABLED=True
```

### 2. Get Gmail App Password (if using Gmail)

1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Go to "App passwords"
4. Generate a new app password for "Mail"
5. Use this password in `SMTP_PASSWORD`

### 3. Test the Configuration

```bash
python test_notifications.py
```

## Usage

### Automatic Notifications

Notifications are sent automatically for:

- **Alert Creation** → Employees & HR managers
- **Deduction Creation** → Affected employee
- **Period Processing** → HR managers
- **Period Approval** → HR managers & Finance
- **Payslip Generation** → Employee

### Manual Notification

Send notification for a specific alert:

```bash
POST /alerts/{alert_id}/send-notification
```

## Troubleshooting

### Emails Not Sending?

1. Check `.env` file has correct settings
2. Verify `NOTIFICATIONS_ENABLED=True`
3. For Gmail, use app password (not regular password)
4. Check application logs for errors

### Test Email Connection

```python
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
server.quit()
print("✓ Connection successful!")
```

## Disable Notifications

Set in `.env`:
```bash
NOTIFICATIONS_ENABLED=False
```

The system will continue to work normally without sending emails.

## Full Documentation

See `NOTIFICATION_SYSTEM_GUIDE.md` for complete documentation.
