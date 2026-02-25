"""
Quick Demo Script - Test the ML Face Recognition System
This creates sample data and runs a quick test
"""

import os
import zipfile
from student_monitor import StudentMonitor

def create_demo_structure():
    """
    Create demo instructions for setting up student data
    """
    print("\n" + "="*70)
    print("DEMO SETUP INSTRUCTIONS")
    print("="*70)
    print("\nTo test the system with your students:")
    print("\n1. COLLECT STUDENT PHOTOS:")
    print("   - Take 1-3 clear photos of each student")
    print("   - Ensure good lighting and face is clearly visible")
    print()
    print("2. ORGANIZE PHOTOS:")
    print("\n   Option A - Individual Photos:")
    print("   name.zip")
    print("   ├── basistha.jpg")
    print("   ├── sarbeswar.jpg")
    print("   └── student3.jpg")
    print()
    print("   Option B - Nested ZIPs (RECOMMENDED):")
    print("   name.zip")
    print("   ├── basistha.zip")
    print("   │   ├── photo1.jpg")
    print("   │   └── photo2.jpg")
    print("   └── sarbeswar.zip")
    print("       ├── image1.png")
    print("       └── image2.jpg")
    print()
    print("3. SAVE AS:")
    print("   - Save the main ZIP file as: name.zip")
    print("   - Place it in the project folder")
    print()
    print("4. RUN THE SYSTEM:")
    print("   python student_monitor.py")
    print()
    print("="*70)
    print("\n📝 IMPORTANT NOTES:")
    print("   • NO names are hardcoded - system learns from your files")
    print("   • Student names come from ZIP filenames or photo filenames")
    print("   • Multiple photos per student improves accuracy")
    print("   • System trains automatically on first run")
    print("   • Mobile reports shown only at END of session")
    print()
    
    # Check if name.zip exists
    if os.path.exists("name.zip"):
        print("✓ Found name.zip - Ready to train!")
        print("\nRun: python student_monitor.py")
    else:
        print("⚠ name.zip not found - Please create it first")
        print("\nSteps:")
        print("1. Collect student photos")
        print("2. Create name.zip with the photos")
        print("3. Run: python student_monitor.py")
    
    print("\n" + "="*70)

def demo_quick_test():
    """
    Run a quick test if name.zip exists
    """
    if not os.path.exists("name.zip"):
        print("\n❌ Cannot run demo: name.zip not found")
        print("Please create name.zip with student photos first")
        return
    
    print("\n" + "="*70)
    print("STARTING QUICK DEMO TEST (30 seconds)")
    print("="*70)
    print("\nThis will:")
    print("  1. Train the ML model on your students")
    print("  2. Monitor for 30 seconds")
    print("  3. Generate end-of-session report")
    print("\nPress 'q' during monitoring to quit early")
    print("="*70 + "\n")
    
    response = input("Start demo? (y/n): ")
    
    if response.lower() == 'y':
        # Create monitor with short interval for demo
        monitor = StudentMonitor(
            zip_file_path="name.zip",
            check_interval=30,  # 30 seconds for quick test
            focus_threshold=50
        )
        
        # Start monitoring
        monitor.start_monitoring()
    else:
        print("Demo cancelled")

def show_system_info():
    """Show information about the ML system"""
    print("\n" + "="*70)
    print("SYSTEM INFORMATION")
    print("="*70)
    
    try:
        import face_recognition
        print("\n✅ ML Face Recognition: AVAILABLE")
        print("   • High accuracy face matching")
        print("   • Deep learning-based recognition")
        print("   • Robust to lighting/angle changes")
    except ImportError:
        print("\n⚠️  ML Face Recognition: NOT AVAILABLE")
        print("   • Using OpenCV histogram matching")
        print("   • Lower accuracy but still functional")
        print("   • Install for better results:")
        print("     pip install face-recognition dlib")
    
    try:
        import cv2
        print("\n✅ OpenCV: Available")
        print(f"   • Version: {cv2.__version__}")
    except ImportError:
        print("\n❌ OpenCV: NOT AVAILABLE")
        print("   • Install: pip install opencv-python")
    
    print("\n" + "="*70)
    print("FEATURES:")
    print("="*70)
    print("  ✓ NO hardcoded student names")
    print("  ✓ Automatic ML model training")
    print("  ✓ Nested ZIP file support")
    print("  ✓ Real-time face recognition")
    print("  ✓ Focus/attention tracking")
    print("  ✓ Mobile phone detection")
    print("  ✓ End-of-session mobile reports")
    print("  ✓ Threshold-based evaluation")
    print("  ✓ JSON export for analysis")
    print("="*70 + "\n")

def main():
    """Main demo function"""
    print("\n" + "="*70)
    print("STUDENT FOCUS MONITOR - ML DEMO & SETUP")
    print("="*70)
    print("\nOptions:")
    print("1. View setup instructions")
    print("2. Check system information")
    print("3. Run quick test (if name.zip exists)")
    print("4. Exit")
    print("="*70)
    
    choice = input("\nSelect option (1-4): ")
    
    if choice == '1':
        create_demo_structure()
    elif choice == '2':
        show_system_info()
    elif choice == '3':
        demo_quick_test()
    elif choice == '4':
        print("Goodbye!")
    else:
        print("Invalid option")
    
    print("\n")

if __name__ == "__main__":
    main()
