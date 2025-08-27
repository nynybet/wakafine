import subprocess
import sys
import os


def run_command(command):
    """Run a command and capture output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd="c:\\Users\\pateh\\Videos\\Dissertation\\wakafine\\wakafine",
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def test_django_functionality():
    """Test basic Django functionality"""

    print("🧪 Testing Django Functionality")
    print("=" * 40)

    # Test 1: Django check
    print("1. Testing Django configuration...")
    returncode, stdout, stderr = run_command("python manage.py check")
    if returncode == 0:
        print("   ✅ Django configuration OK")
    else:
        print(f"   ❌ Django check failed: {stderr}")
        return False

    # Test 2: Show migrations
    print("2. Checking migrations...")
    returncode, stdout, stderr = run_command("python manage.py showmigrations bookings")
    if returncode == 0:
        print("   ✅ Migrations check OK")
        if stdout.strip():
            print(f"   Migrations: {stdout.strip()}")
    else:
        print(f"   ❌ Migration check failed: {stderr}")

    # Test 3: Test round trip command
    print("3. Testing round trip booking...")
    returncode, stdout, stderr = run_command("python manage.py test_round_trip_booking")
    if returncode == 0:
        print("   ✅ Round trip test executed")
        if stdout.strip():
            print(f"   Output: {stdout.strip()}")
    else:
        print(f"   ❌ Round trip test failed: {stderr}")

    # Test 4: Test model import
    print("4. Testing model import...")
    test_import_command = '''python -c "import django; django.setup(); from bookings.models import Booking; print('Models imported successfully')"'''
    returncode, stdout, stderr = run_command(test_import_command)
    if returncode == 0:
        print("   ✅ Models can be imported")
        if stdout.strip():
            print(f"   Output: {stdout.strip()}")
    else:
        print(f"   ❌ Model import failed: {stderr}")

    return True


if __name__ == "__main__":
    test_django_functionality()
