"""
Quick Fix for face_recognition_models issue
This script helps diagnose and fix the face_recognition installation
"""

import sys
import subprocess

def check_imports():
    """Check if packages can be imported"""
    print("\n" + "="*70)
    print("CHECKING FACE RECOGNITION INSTALLATION")
    print("="*70)
    
    # Check face_recognition
    try:
        import face_recognition
        print("✓ face_recognition package: FOUND")
        fr_available = True
    except ImportError as e:
        print(f"✗ face_recognition package: NOT FOUND")
        print(f"  Error: {e}")
        fr_available = False
    
    # Check face_recognition_models
    try:
        import face_recognition_models
        print("✓ face_recognition_models package: FOUND")
        frm_available = True
    except ImportError as e:
        print(f"✗ face_recognition_models package: NOT FOUND")
        print(f"  Error: {e}")
        frm_available = False
    
    # Try to actually use face_recognition
    if fr_available:
        try:
            import numpy as np
            # Create a dummy image
            dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
            _ = face_recognition.face_encodings(dummy_image)
            print("✓ face_recognition functionality: WORKING")
            print("\n✅ ALL CHECKS PASSED - face_recognition is ready!")
            return True
        except Exception as e:
            print(f"✗ face_recognition functionality: ERROR")
            print(f"  Error: {e}")
            if "face_recognition_models" in str(e):
                print("\n⚠ face_recognition_models is not properly configured")
    
    return False

def fix_installation():
    """Attempt to fix the installation"""
    print("\n" + "="*70)
    print("ATTEMPTING TO FIX INSTALLATION")
    print("="*70)
    
    commands = [
        ("Clearing pip cache", [sys.executable, "-m", "pip", "cache", "purge"]),
        ("Uninstalling face-recognition", [sys.executable, "-m", "pip", "uninstall", "-y", "face-recognition", "face-recognition-models"]),
        ("Installing face-recognition", [sys.executable, "-m", "pip", "install", "face-recognition"]),
        ("Installing face-recognition-models", [sys.executable, "-m", "pip", "install", "git+https://github.com/ageitgey/face_recognition_models"])
    ]
    
    for desc, cmd in commands:
        print(f"\n{desc}...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✓ Success")
            else:
                print(f"  ⚠ Warning: {result.stderr[:100]}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "="*70)
    print("RETESTING...")
    print("="*70)
    
    # Need to restart Python for changes to take effect
    print("\n⚠ Please RESTART your terminal and run this script again to verify")

def main():
    print("\n" + "="*70)
    print("FACE RECOGNITION TROUBLESHOOTER")
    print("="*70)
    
    is_working = check_imports()
    
    if is_working:
        print("\n✅ Everything is working! You can now run:")
        print("   python student_monitor.py")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("OPTIONS:")
        print("="*70)
        print("\nOption 1: Try automatic fix")
        print("Option 2: Use OpenCV fallback (no face_recognition)")
        print("Option 3: Manual installation steps")
        print("\n" + "="*70)
        
        choice = input("\nSelect option (1/2/3): ").strip()
        
        if choice == "1":
            fix_installation()
        elif choice == "2":
            print("\n✓ Using OpenCV fallback mode")
            print("\nThe system will work without face_recognition.")
            print("It will use OpenCV's histogram matching instead (slightly less accurate)")
            print("\nJust run: python student_monitor.py")
            print("\nThe system will automatically detect and use OpenCV mode.")
        elif choice == "3":
            print("\n" + "="*70)
            print("MANUAL INSTALLATION STEPS")
            print("="*70)
            print("\n1. Close this terminal completely")
            print("\n2. Open a NEW terminal (Run as Administrator if on Windows)")
            print("\n3. Run these commands ONE BY ONE:\n")
            print("   pip cache purge")
            print("   pip uninstall -y face-recognition face-recognition-models")
            print("   pip install --no-cache-dir face-recognition")
            print("   pip install --no-cache-dir git+https://github.com/ageitgey/face_recognition_models")
            print("\n4. Close terminal and open a NEW one")
            print("\n5. Run: python student_monitor.py")
            print("\n" + "="*70)
            
            print("\n📝 ALTERNATIVE: Use OpenCV mode (no ML)")
            print("   The system works fine without face_recognition!")
            print("   Just run: python student_monitor.py")
            print("   It will automatically use OpenCV fallback mode.")
            print("="*70)
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
