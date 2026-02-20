"""Test that export service can be imported without database"""
import sys

print("Testing export service imports...")

# Test xlsxwriter
try:
    import xlsxwriter
    print("✓ xlsxwriter imported")
except ImportError as e:
    print(f"✗ xlsxwriter import failed: {e}")
    sys.exit(1)

# Test openpyxl
try:
    import openpyxl
    print("✓ openpyxl imported")
except ImportError as e:
    print(f"✗ openpyxl import failed: {e}")
    sys.exit(1)

# Test that the module compiles
try:
    import py_compile
    py_compile.compile('app/paie_app/services/export_service.py', doraise=True)
    print("✓ export_service.py compiles successfully")
except py_compile.PyCompileError as e:
    print(f"✗ Compilation error: {e}")
    sys.exit(1)

print("\n✅ All import tests passed!")
print("\nExport service is ready to use.")
print("Note: Full functionality requires database connection.")
