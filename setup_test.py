"""
Setup and Test Script for Student Focus Monitor
Run this script to verify your setup and test the system
"""

import os
import sys
import cv2
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Please upgrade to Python 3.8+")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    required = {
        'cv2': 'opencv-python',
        'numpy': 'numpy'
    }
    
    all_ok = True
    for module, package in required.items():
        try:
            __import__(module)
            print(f"✓ {package} - Installed")
        except ImportError:
            print(f"✗ {package} - NOT installed")
            all_ok = False
    
    return all_ok

def check_camera():
    """Test if camera is accessible"""
    print("\nChecking camera...")
    cap = cv2.VideoCapture(0)
    
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        if ret:
            print("✓ Camera is working properly")
            return True
        else:
            print("✗ Camera opened but cannot capture frames")
            return False
    else:
        print("✗ Cannot access camera")
        return False

def check_cascades():
    """Check if Haar Cascades are available"""
    print("\nChecking detection models...")
    
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        if not face_cascade.empty() and not eye_cascade.empty():
            print("✓ Face detection models - OK")
            print("✓ Eye detection models - OK")
            return True
        else:
            print("✗ Detection models not loaded properly")
            return False
    except Exception as e:
        print(f"✗ Error loading detection models: {e}")
        return False

def check_zip_file():
    """Check if student photos ZIP file exists"""
    print("\nChecking student data...")
    zip_file = "name.zip"
    
    if os.path.exists(zip_file):
        print(f"✓ Found {zip_file}")
        return True
    else:
        print(f"✗ {zip_file} not found")
        print("\nPlease create a ZIP file with student photos:")
        print("  1. Create a folder with student photos")
        print("  2. Name each photo with student's name (e.g., Basistha.jpg)")
        print("  3. Compress the folder into name.zip")
        return False

def create_sample_structure():
    """Create sample directory structure"""
    print("\nCreating sample structure...")
    
    # Create a sample folder for instructions
    sample_dir = Path("sample_student_photos")
    sample_dir.mkdir(exist_ok=True)
    
    # Create a README in sample folder
    readme_path = sample_dir / "README.txt"
    with open(readme_path, 'w') as f:
        f.write("INSTRUCTIONS FOR STUDENT PHOTOS\n")
        f.write("="*50 + "\n\n")
        f.write("1. Place student photos in this folder\n")
        f.write("2. Name each photo with the student's name:\n")
        f.write("   - Basistha.jpg\n")
        f.write("   - Student1.png\n")
        f.write("   - Student2.jpg\n")
        f.write("   etc.\n\n")
        f.write("3. After adding all photos, compress this folder\n")
        f.write("4. Rename the ZIP file to 'name.zip'\n")
        f.write("5. Place 'name.zip' in the main project folder\n\n")
        f.write("Note: Photos should be clear, well-lit headshots\n")
    
    print(f"✓ Created {sample_dir} folder with instructions")

def run_quick_test():
    """Run a quick camera test"""
    print("\n" + "="*60)
    response = input("Would you like to run a quick camera test? (y/n): ")
    
    if response.lower() == 'y':
        print("\nStarting camera test...")
        print("Press 'q' to quit the test")
        
        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.putText(frame, "Press 'q' to quit", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Camera Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("✓ Camera test completed")

def main():
    """Main setup verification"""
    print("\n" + "="*60)
    print("STUDENT FOCUS MONITOR - SETUP VERIFICATION")
    print("="*60)
    
    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Camera': check_camera(),
        'Detection Models': check_cascades(),
        'Student Data': check_zip_file()
    }
    
    # Create sample structure
    create_sample_structure()
    
    # Summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    
    all_ok = True
    for check, status in results.items():
        status_text = "✓ OK" if status else "✗ NEEDS ATTENTION"
        print(f"{check:20s}: {status_text}")
        if not status:
            all_ok = False
    
    print("="*60)
    
    if all_ok:
        print("\n✓ All checks passed! You're ready to use the system.")
        print("\nTo start monitoring, run:")
        print("  python student_monitor.py")
        run_quick_test()
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
