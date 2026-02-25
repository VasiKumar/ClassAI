"""
Test script to verify report generation on end session
"""

import subprocess
import time
import os
import sys
import json

def test_end_session():
    """Test that ending a session generates a report"""
    print("\n" + "="*70)
    print("TESTING END SESSION REPORT GENERATION")
    print("="*70)
    
    # Clean up old files
    if os.path.exists('monitor_stop.signal'):
        os.remove('monitor_stop.signal')
        print("✓ Cleaned old stop signal")
    
    # Remove old test reports
    test_reports = [f for f in os.listdir('.') if f.startswith('focus_report_') and f.endswith('.json')]
    for report in test_reports:
        try:
            os.remove(report)
            print(f"✓ Removed old test report: {report}")
        except:
            pass
    
    # Create config for 30-second test
    config = {
        'duration': 30,  # 30 seconds
        'threshold': 50,
        'enable_mobile_detection': False
    }
    
    with open('monitor_config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    print("\n✓ Created test configuration (30 seconds)")
    
    # Start monitoring process
    print("\n🚀 Starting monitoring process...")
    print("   (A camera window should open)")
    
    try:
        process = subprocess.Popen(
            [sys.executable, 'student_monitor.py'],
            cwd=os.getcwd(),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        print("✓ Process started (PID: {})".format(process.pid))
        
        # Wait 10 seconds
        print("\n⏳ Waiting 10 seconds...")
        for i in range(10, 0, -1):
            print(f"   {i}...", end='\r')
            time.sleep(1)
        
        print("\n\n🛑 Sending stop signal...")
        
        # Create stop signal file
        with open('monitor_stop.signal', 'w') as f:
            f.write('stop')
        print("✓ Stop signal file created")
        
        # Wait for graceful shutdown
        print("\n⏳ Waiting for process to generate report and exit...")
        try:
            process.wait(timeout=15)
            print("✓ Process ended gracefully")
        except subprocess.TimeoutExpired:
            print("⚠️  Process didn't exit in time, forcing...")
            process.kill()
            process.wait()
        
        # Wait a bit more for file I/O
        time.sleep(2)
        
        # Check for report
        print("\n" + "="*70)
        print("CHECKING FOR REPORTS")
        print("="*70)
        
        reports = [f for f in os.listdir('.') if f.startswith('focus_report_') and f.endswith('.json')]
        
        if reports:
            print(f"\n✅ SUCCESS! Found {len(reports)} report(s):")
            for report in reports:
                file_size = os.path.getsize(report)
                print(f"   ✓ {report} ({file_size} bytes)")
                
                # Show report contents
                try:
                    with open(report, 'r') as f:
                        data = json.load(f)
                    print(f"      - Timestamp: {data.get('timestamp', 'N/A')}")
                    print(f"      - Students: {len(data.get('students', {}))}")
                    print(f"      - Duration: {data.get('duration', 'N/A')}s")
                except Exception as e:
                    print(f"      ⚠️  Error reading report: {e}")
            
            print("\n" + "="*70)
            print("✅ TEST PASSED! Reports are being generated correctly!")
            print("="*70)
            return True
        else:
            print("\n❌ TEST FAILED! No reports found.")
            print("\nChecking for issues...")
            print(f"   - Current directory: {os.getcwd()}")
            print(f"   - Monitor stopped: {process.poll() is not None}")
            
            # List all JSON files
            all_json = [f for f in os.listdir('.') if f.endswith('.json')]
            print(f"   - All JSON files: {all_json}")
            
            print("\n" + "="*70)
            print("❌ TEST FAILED!")
            print("="*70)
            return False
            
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Make sure your camera is connected!")
    print("⚠️  A camera window will open for 10 seconds.")
    print("\nPress Enter to continue, or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)
    
    success = test_end_session()
    
    if success:
        print("\n🎉 Your system is working correctly!")
        print("📊 Reports will now generate when you click 'End Session' in the dashboard.")
    else:
        print("\n⚠️  There may be an issue. Check the error messages above.")
    
    print("\nPress Enter to exit...")
    try:
        input()
    except:
        pass
