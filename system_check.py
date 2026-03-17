"""
System Health Check Script
Verifies all components are properly configured
"""
import os
import sys

def check_file(path, description):
    """Check if a file exists"""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {path}")
    return exists

def check_directory(path, description):
    """Check if a directory exists"""
    exists = os.path.isdir(path)
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {path}")
    return exists

def check_python_package(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        print(f"  ✓ {package_name}")
        return True
    except ImportError:
        print(f"  ✗ {package_name} - NOT INSTALLED")
        return False

def main():
    print("=" * 80)
    print("VANET SYSTEM v3.0 - HEALTH CHECK")
    print("=" * 80)
    
    all_good = True
    
    # Check Backend Files
    print("\n📁 BACKEND FILES")
    all_good &= check_file("backend/main.py", "Main server")
    all_good &= check_file("backend/auth.py", "Authentication")
    all_good &= check_file("backend/attack_classifier.py", "Attack classifier")
    all_good &= check_file("backend/requirements.txt", "Requirements")
    all_good &= check_file("backend/.env", "Environment config")
    all_good &= check_file("backend/vanet_anomaly_detector.h5", "Trained model")
    
    # Check Frontend Files
    print("\n📁 FRONTEND FILES")
    all_good &= check_directory("client/src", "Source directory")
    all_good &= check_file("client/src/App.jsx", "Main app")
    all_good &= check_file("client/src/contexts/AuthContext.jsx", "Auth context")
    all_good &= check_file("client/src/components/DashboardPhase.jsx", "Dashboard")
    all_good &= check_file("client/src/components/AttackPanel.jsx", "Attack panel")
    all_good &= check_file("client/package.json", "Package config")
    
    # Check Documentation
    print("\n📚 DOCUMENTATION")
    all_good &= check_file("START_HERE.md", "Quick start guide")
    all_good &= check_file("README.md", "Project readme")
    all_good &= check_file("IMPROVEMENTS.md", "Feature documentation")
    all_good &= check_file("USER_MANAGEMENT_GUIDE.md", "User guide")
    all_good &= check_file("ATTACK_TYPES_GUIDE.md", "Attack guide")
    
    # Check Python Dependencies
    print("\n🐍 PYTHON PACKAGES")
    packages = [
        "fastapi",
        "uvicorn",
        "tensorflow",
        "numpy",
        "pandas",
        "bcrypt",
        "jose",
        "dotenv"
    ]
    
    for package in packages:
        pkg_name = package.replace("jose", "python-jose").replace("dotenv", "python-dotenv")
        all_good &= check_python_package(package)
    
    # Check Dataset
    print("\n📊 DATASET")
    all_good &= check_file("dataset_50k.csv", "Training dataset")
    
    # Summary
    print("\n" + "=" * 80)
    if all_good:
        print("✅ ALL CHECKS PASSED - SYSTEM READY!")
        print("\nNext steps:")
        print("  1. Start backend: cd backend && python -m uvicorn main:app --reload --port 8000")
        print("  2. Start frontend: cd client && npm run dev")
        print("  3. Open browser: http://localhost:5173")
        print("  4. Login with: admin / admin123")
    else:
        print("⚠️  SOME CHECKS FAILED - PLEASE REVIEW ABOVE")
        print("\nCommon fixes:")
        print("  - Install Python packages: cd backend && pip install -r requirements.txt")
        print("  - Install Node packages: cd client && npm install")
        print("  - Check file paths and names")
    print("=" * 80)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
