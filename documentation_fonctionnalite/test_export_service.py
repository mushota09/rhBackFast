"""Test script for export service"""
import asyncio
from pathlib import Path

# Test that the export service can be imported
try:
    from app.paie_app.services.export_service import ExportService
    print("✓ ExportService imported successfully")
except ImportError as e:
    print(f"✗ Failed to import ExportService: {e}")
    exit(1)

# Test that required libraries are available
try:
    import xlsxwriter
    print("✓ xlsxwriter library available")
except ImportError as e:
    print(f"✗ xlsxwriter not available: {e}")
    exit(1)

try:
    import openpyxl
    print("✓ openpyxl library available")
except ImportError as e:
    print(f"✗ openpyxl not available: {e}")
    exit(1)

# Test that the service has the expected methods
service_methods = [
    'export_periode_to_excel',
    'export_periode_to_csv',
    'export_all_periodes_to_excel',
    'export_retenues_to_csv'
]

for method in service_methods:
    if hasattr(ExportService, method):
        print(f"✓ ExportService.{method} exists")
    else:
        print(f"✗ ExportService.{method} not found")
        exit(1)

# Test that routes can be imported
try:
    from app.paie_app.routes import payroll_router
    print("✓ Payroll router imported successfully")
except ImportError as e:
    print(f"✗ Failed to import payroll router: {e}")
    exit(1)

print("\n✅ All export service tests passed!")
print("\nAvailable export endpoints:")
print("  - GET /payroll/export/periode/{periode_id}?export_format=excel|csv")
print("  - GET /payroll/export/all-periodes?annee={year}")
print("  - GET /payroll/export/retenues?employe_id={id}")
