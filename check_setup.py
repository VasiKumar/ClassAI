"""
Quick System Check - Verify Student Monitoring System Setup
"""

import os
import sys

def check_system():
    """Check if the system is ready to run"""
    
    print("\n" + "="*70)
    print("STUDENT FOCUS MONITORING SYSTEM - SETUP CHECK")
    print("="*70 + "\n")
    
    all_good = True
    
    # Check 1: Python version
    print("1. Checking Python version...")
    if sys.version_info >= (3, 8):
        print("   ✓ Python version OK:", sys.version.split()[0])
    else:
        print("   ✗ Python version too old. Need 3.8 or higher")
        all_good = False
    
    # Check 2: Required files
    print("\n2. Checking required files...")
    required_files = [
        'student_monitor.py',
        'streamlit_app.py',
        'requirements.txt'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} - MISSING!")
            all_good = False
    
    # Check 3: Students folder
    print("\n3. Checking student photos folder...")
    if os.path.exists('sample_student_photos'):
        print("   ✓ sample_student_photos folder exists")
        
        # Check for ZIP files
        zip_files = [f for f in os.listdir('sample_student_photos') if f.endswith('.zip')]
        if zip_files:
            print(f"   ✓ Found {len(zip_files)} student ZIP files:")
            for zf in zip_files:
                student_name = os.path.splitext(zf)[0]
                print(f"      - {student_name}")
        else:
            print("   ⚠ No student ZIP files found!")
            print("     Add student ZIP files to start monitoring")
            all_good = False
    else:
        print("   ✗ sample_student_photos folder NOT FOUND")
        print("     Creating folder...")
        os.makedirs('sample_student_photos', exist_ok=True)
        print("   ✓ Folder created. Add student ZIP files here.")
        all_good = False
    
    # Check 4: Required packages
    print("\n4. Checking installed packages...")
    required_packages = [
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('PIL', 'Pillow'),
        ('streamlit', 'streamlit'),
        ('plotly', 'plotly'),
        ('pandas', 'pandas')
    ]
    
    missing_packages = []
    
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"   ✓ {package_name}")
        except ImportError:
            print(f"   ✗ {package_name} - NOT INSTALLED")
            missing_packages.append(package_name)
            all_good = False
    
    # Check 5: Optional packages
    print("\n5. Checking optional packages...")
    optional_packages = [
        ('face_recognition', 'face-recognition'),
        ('dlib', 'dlib')
    ]
    
    for module_name, package_name in optional_packages:
        try:
            __import__(module_name)
            print(f"   ✓ {package_name} (for ML-based detection)")
        except ImportError:
            print(f"   ⚠ {package_name} - Not installed (will use OpenCV fallback)")
    
    # Check 6: Camera
    print("\n6. Checking camera access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("   ✓ Camera is accessible")
            cap.release()
        else:
            print("   ✗ Cannot access camera")
            print("     Make sure no other app is using it")
            all_good = False
    except Exception as e:
        print(f"   ✗ Camera check failed: {e}")
        all_good = False
    
    # Final summary
    print("\n" + "="*70)
    if all_good:
        print("✅ SYSTEM READY!")
        print("="*70 + "\n")
        print("Next steps:")
        print("  1. Run: launch_dashboard.bat")
        print("  2. Or run: streamlit run streamlit_app.py")
        print("  3. Open dashboard in browser")
        print("  4. Start monitoring session")
        print("\nFor detailed instructions, see COMPLETE_GUIDE.md")
    else:
        print("⚠️  SETUP INCOMPLETE")
        print("="*70 + "\n")
        
        if missing_packages:
            print("Install missing packages:")
            print(f"  pip install {' '.join(missing_packages)}")
            print("\nOr install all requirements:")
            print("  pip install -r requirements.txt")
        
        print("\nFor setup help, see COMPLETE_GUIDE.md")
    
    print("\n" + "="*70 + "\n")
    
    return all_good

if __name__ == "__main__":
    check_system()
    input("\nPress Enter to exit...")
