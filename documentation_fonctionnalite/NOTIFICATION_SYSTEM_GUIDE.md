# Notification System Guide

## Overview

The notification system provides automatic email notifications for key payroll events in the RH Management System. It integrates seamlessly with the existing payroll workflow and can be easily configured.

## Features

### Automatic Notifications

The system automatically sends email notifications for:

1. **Alert Creation** - When a new payroll alert is created
2. **Deduction Creation** - When a new salary deduction is added for an employee
3. **Period Processing** - When a payroll period is processed
4. **Period Approval** - When a payroll period is approved
5. **Payslip Generation** - When an employee's
sh
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=True
```
**Note**: For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833).

#### Office 365
```bash
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_TLS=True
```

#### SendGrid
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_TLS=True
```

#### Mailgun
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_TLS=True
```

#### Custom SMTP Server
```bash
SMTP_HOST=mail.yourcompany.com
SMTP_PORT=587
SMTP_TLS=True
```

### Enabling/Disabling Notifications

Set `NOTIFICATIONS_ENABLED=True` to enable automatic notifications.
Set `NOTIFICATIONS_ENABLED=False` to disable automatic notifications.

When disabled, the system will continue to function normally but won't send emails.

## Notification Types

### 1. Alert Notifications

**Triggered when**: A new alert is created
**Recipients**:
- Employee (if alert is employee-specific)
- HR/Payroll managers

**Content**:
- Alert title and severity
- Alert message and details
- Creation timestamp

**Example**:
```
Subject: [HIGH] Salary Calculation Error

Alert: Salary Calculation Error
Severity: HIGH
Type: CALCULATION_ERROR
Status: ACTIVE

Message:
Unable to calculate salary for employee due to missing contract data.

Details:
  employee_id: 123
  periode_id: 45
  error: Missing base salary

Created: 2024-02-17 10:30:00
```

### 2. Deduction Notifications

**Triggered when**: A new salary deduction is created
**Recipients**: The affected employee

**Content**:
- Deduction type and description
- Monthly and total amounts
- Start and end dates
- Bank details (if applicable)

**Example**:
```
Subject: New Salary Deduction

Dear Jean Dupont,

A new salary deduction has been added to your account.

Deduction Details:
- Type: LOAN
- Description: Personal loan repayment
- Monthly Amount: 50,000 FC
- Total Amount: 500,000 FC
- Start Date: 2024-03-01
- End Date: 2024-12-31

If you have any questions, please contact HR.
```

### 3. Period Processing Notifications

**Triggered when**: A payroll period is processed
**Recipients**: HR/Payroll managers

**Content**:
- Period details (month/year)
- Number of employees processed
- Total amounts (gross, net, contributions)
- Processing status

**Example**:
```
Subject: Payroll Period Processed: 2/2024

Payroll period has been processed successfully.

Period: 2/2024
Status: COMPLETED
Employees: 150
Total Net Payable: 45,000,000 FC

The period is now ready for review and approval.
```

### 4. Period Approval Notifications

**Triggered when**: A payroll period is approved
**Recipients**: HR/Payroll managers and Finance team

**Content**:
- Period details
- Approval timestamp
- Total amounts
- Payment instructions

**Example**:
```
Subject: Payroll Period Approved: 2/2024

Payroll period has been approved and is ready for payment.

Period: 2/2024
Status: APPROVED
Employees: 150
Total Net Payable: 45,000,000 FC
Approved: 2024-02-17 15:45:00

Please proceed with payment processing.
```

### 5. Payslip Generation Notifications

**Triggered when**: An employee's payslip is generated
**Recipients**: The employee

**Content**:
- Period details
- Gross and net salary
- Download instructions

**Example**:
```
Subject: Your Payslip - 2/2024

Dear Jean Dupont,

Your payslip for 2/2024 is now available.

Salary Details:
- Gross Salary: 500,000 FC
- Net Salary: 380,000 FC

Please log in to the system to download your payslip.
```

## API Endpoints

### Manual Notification Trigger

```http
POST /alerts/{alert_id}/send-notification
```

**Description**: Manually send or resend notification for a specific alert

**Authentication**: Required (alert.update permission)

**Response**:
```json
{
  "message": "Notification sent successfully"
}
```

## Email Templates

All notifications support both plain text and HTML formats:

- **Plain Text**: Simple, readable format for email clients that don't support HTML
- **HTML**: Rich, formatted emails with colors, tables, and styling

### HTML Email Features

- Color-coded severity levels (alerts)
- Professional table layouts
- Responsive design
- Company branding footer

## Recipient Logic

### Alert Notifications
1. If alert is employee-specific → Send to employee's email
2. Always send to HR/Payroll managers

### Deduction Notifications
- Send to the affected employee only

### Period Notifications
- Send to all HR/Payroll managers
- Managers are identified by `is_superuser` or `is_staff` flags

### Payslip Notifications
- Send to the employee only

## Email Preferences

Employees receive emails at:
1. Professional email (if available)
2. Personal email (fallback)

## Error Handling

The notification system is designed to fail gracefully:

- If email is not configured, notifications are skipped with a warning log
- If an email fails to send, the error is logged but doesn't block the operation
- Failed notifications don't affect the core payroll functionality

## Logging

All notification activities are logged:

```python
logger.info(f"Email sent successfully to {to_email}")
logger.error(f"Failed to send email to {to_email}: {error}")
logger.warning("Email not configured. Skipping email notification.")
```

## Testing

### Test Email Configuration

To test your email configuration:

1. Create a test alert:
```bash
POST /alerts
{
  "alert_type": "TEST",
  "severity": "LOW",
  "status": "ACTIVE",
  "title": "Test Alert",
  "message": "This is a test notification"
}
```

2. Check the logs for email sending status

3. Verify the email was received

### Development Mode

During development, you can:
- Set `NOTIFICATIONS_ENABLED=False` to disable emails
- Use a test SMTP service like [Mailtrap](https://mailtrap.io/)
- Use Gmail with an app password

## Security Considerations

1. **Never commit credentials**: Keep SMTP credentials in `.env` file
2. **Use app passwords**: For Gmail, use app-specific passwords
3. **Enable TLS**: Always use `SMTP_TLS=True` for secure connections
4. **Restrict permissions**: Only authorized users can trigger notifications
5. **Audit logging**: All notification actions are logged in the audit system

## Troubleshooting

### Emails Not Sending

1. **Check configuration**:
   ```bash
   # Verify .env file has correct SMTP settings
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_FROM_EMAIL=noreply@company.com
   SMTP_TLS=True
   NOTIFICATIONS_ENABLED=True
   ```

2. **Check logs**:
   ```bash
   # Look for error messages in application logs
   tail -f logs/app.log | grep -i email
   ```

3. **Test SMTP connection**:
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-app-password')
   server.quit()
   ```

### Gmail-Specific Issues

- **"Less secure app access"**: Use an [App Password](https://support.google.com/accounts/answer/185833)
- **2FA required**: Enable 2-factor authentication before creating app password
- **Blocked sign-in**: Check Gmail security settings

### Common Errors

**Error**: `SMTPAuthenticationError`
**Solution**: Check username and password, use app password for Gmail

**Error**: `SMTPConnectError`
**Solution**: Check SMTP host and port, verify firewall settings

**Error**: `SMTPServerDisconnected`
**Solution**: Enable TLS/SSL, check network connectivity

## Best Practices

1. **Use a dedicated email account** for sending notifications
2. **Monitor email delivery** through SMTP provider dashboard
3. **Keep email content concise** and professional
4. **Test notifications** in staging before production
5. **Set up email bounce handling** for invalid addresses
6. **Respect email frequency** to avoid spam filters
7. **Provide unsubscribe options** for non-critical notifications

## Future Enhancements

Potential improvements for the notification system:

- [ ] SMS notifications via Twilio/AWS SNS
- [ ] In-app notifications
- [ ] Notification preferences per user
- [ ] Email templates customization
- [ ] Batch email sending for bulk operations
- [ ] Email queue with retry mechanism
- [ ] Notification history tracking
- [ ] Multi-language support
- [ ] Rich text editor for custom messages
- [ ] Scheduled notifications

## Support

For issues or questions about the notification system:
1. Check the logs for error messages
2. Verify email configuration
3. Test with a simple alert
4. Contact system administrator

---

**Last Updated**: 2024-02-17
**Version**: 1.0.0
