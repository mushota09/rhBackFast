"""Test script for notification system"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.paie_app.services.notification_service import NotificationService


async def test_email_configuration():
    """Test if email is properly configured"""
    print("Testing Email Configuration...")
    print(f"SMTP Host: {getattr(settings, 'SMTP_HOST', 'Not configured')}")
    print(f"SMTP Port: {getattr(settings, 'SMTP_PORT', 'Not configured')}")
    print(f"SMTP User: {getattr(settings, 'SMTP_USER', 'Not configured')}")
    print(f"SMTP From: {getattr(settings, 'SMTP_FROM_EMAIL', 'Not configured')}")
    print(f"SMTP TLS: {getattr(settings, 'SMTP_TLS', 'Not configured')}")
    print(f"Notifications Enabled: {getattr(settings, 'NOTIFICATIONS_ENABLED', False)}")

    if not hasattr(settings, 'SMTP_HOST') or not settings.SMTP_HOST:
        print("\n⚠️  Email is not configured. Please set SMTP settings in .env file.")
        return False

    print("\n✓ Email configuration found")
    return True


async def test_send_test_email():
    """Send a test email"""
    if not await test_email_configuration():
        return

    # Create database session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        notification_service = NotificationService(session)

        # Get test email from settings or use a default
        test_email = getattr(settings, 'SMTP_USER', 'test@example.com')

        print(f"\nSending test email to: {test_email}")

        success = await notification_service.send_email(
            to_email=test_email,
            subject="Test Notification - RH Management System",
            body="""
This is a test email from the RH Management System notification service.

If you received this email, your notification system is working correctly!

Test Details:
- System: RH Management System
- Module: Payroll Notifications
- Date: 2024-02-17

---
RH Management System
            """,
            html_body="""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #28a745;">Test Notification</h2>
                <p>This is a test email from the RH Management System notification service.</p>
                <p>If you received this email, your notification system is working correctly!</p>

                <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-left: 4px solid #28a745;">
                    <h3>Test Details:</h3>
                    <ul>
                        <li><strong>System:</strong> RH Management System</li>
                        <li><strong>Module:</strong> Payroll Notifications</li>
                        <li><strong>Date:</strong> 2024-02-17</li>
                    </ul>
                </div>

                <hr>
                <p style="font-size: 12px; color: #6c757d;">
                    RH Management System - Automated Notification
                </p>
            </body>
            </html>
            """
        )

        if success:
            print("✓ Test email sent successfully!")
            print(f"  Check your inbox at: {test_email}")
        else:
            print("✗ Failed to send test email")
            print("  Check the logs for error details")


async def main():
    """Main test function"""
    print("=" * 60)
    print("RH Management System - Notification System Test")
    print("=" * 60)
    print()

    await test_send_test_email()

    print()
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
