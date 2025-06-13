#!/usr/bin/env python3
"""
Once Noticias - Deployment Helper Script
Helps prepare and validate the app for deployment
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_git_status():
    """Check if git repository is clean and ready for deployment"""
    print("🔍 Checking Git status...")

    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True, check=True)

        if result.stdout.strip():
            print("⚠️  Warning: You have uncommitted changes:")
            print(result.stdout)
            return False
        else:
            print("✅ Git repository is clean")
            return True

    except subprocess.CalledProcessError:
        print("❌ Not in a git repository or git not available")
        return False

def check_required_files():
    """Check if all required deployment files exist"""
    print("\n📁 Checking required files...")

    required_files = [
        'src/interfaces/streamlit_app.py',
        'requirements_deploy.txt',
        'config/.streamlit/secrets.toml',
        '.streamlit/config.toml',
        'DEPLOYMENT.md'
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")

    if missing_files:
        print(f"\n❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False

    return True

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔑 Checking environment variables...")

    # Check secrets.toml file
    secrets_file = 'config/.streamlit/secrets.toml'
    if os.path.exists(secrets_file):
        with open(secrets_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content:
                print("✅ OpenAI API key found in secrets.toml")
            else:
                print("⚠️  OpenAI API key not found in secrets.toml")
                return False

    return True

def validate_app_structure():
    """Validate the application structure"""
    print("\n🏗️  Validating app structure...")

    required_dirs = [
        'src',
        'src/core',
        'src/interfaces',
        'src/utils',
        'config'
    ]

    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ Missing directory: {dir_path}")
            return False
        else:
            print(f"✅ {dir_path}")

    return True

def test_app_locally():
    """Test if the app can start locally"""
    print("\n🧪 Testing app locally...")

    try:
        # Try to import the main app
        sys.path.insert(0, 'src')
        from interfaces.streamlit_app import initialize_system

        # Test initialization
        prompt_system, qa_system = initialize_system()
        print("✅ App initialization successful")
        return True

    except Exception as e:
        print(f"❌ App initialization failed: {str(e)}")
        return False

def generate_deployment_summary():
    """Generate a summary of deployment options"""
    print("\n📋 Deployment Summary")
    print("=" * 50)

    print("\n🌐 Streamlit Cloud (Recommended):")
    print("   1. Push code to GitHub")
    print("   2. Go to share.streamlit.io")
    print("   3. Connect repository")
    print("   4. Set main file: src/interfaces/streamlit_app.py")
    print("   5. Configure secrets")

    print("\n🐳 Docker Deployment:")
    print("   1. docker build -t once-noticias .")
    print("   2. docker run -p 8501:8501 once-noticias")

    print("\n🔧 Heroku Deployment:")
    print("   1. heroku create your-app-name")
    print("   2. heroku config:set OPENAI_API_KEY=your-key")
    print("   3. git push heroku main")

    print("\n📊 Next Steps:")
    print("   - Review DEPLOYMENT.md for detailed instructions")
    print("   - Test all features after deployment")
    print("   - Monitor app performance and logs")

def main():
    """Main deployment check function"""
    print("🚀 Once Noticias - Deployment Checker")
    print("=" * 50)

    checks = [
        ("Git Status", check_git_status),
        ("Required Files", check_required_files),
        ("Environment Variables", check_environment_variables),
        ("App Structure", validate_app_structure),
        ("Local Testing", test_app_locally)
    ]

    all_passed = True

    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed: {str(e)}")
            all_passed = False

    print("\n" + "=" * 50)

    if all_passed:
        print("🎉 All checks passed! Your app is ready for deployment.")
        generate_deployment_summary()
    else:
        print("⚠️  Some checks failed. Please fix the issues before deploying.")
        print("\n📖 Check DEPLOYMENT.md for detailed instructions.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)