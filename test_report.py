"""
Test Report Generation
Quick test to verify that report generation works
"""

import os
import json
from datetime import datetime

def create_test_report():
    """Create a test report to verify the system is working"""
    
    print("Creating test report...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'duration': 60,
        'threshold': 50,
        'students': {
            'test_student_1': {
                'focus_percentage': 75.5,
                'focused_count': 15,
                'unfocused_count': 5,
                'total_checks': 20,
                'mobile_detected': 1,
                'mobile_times': ['12:30:45'],
                'alerts': ['12:30:45 - Mobile phone detected']
            },
            'test_student_2': {
                'focus_percentage': 90.0,
                'focused_count': 18,
                'unfocused_count': 2,
                'total_checks': 20,
                'mobile_detected': 0,
                'mobile_times': [],
                'alerts': []
            }
        }
    }
    
    filename = f"focus_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.abspath(filename)
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=4)
    
    print(f"✅ Test report created successfully!")
    print(f"   File: {filename}")
    print(f"   Path: {filepath}")
    print(f"\nOpen the dashboard and check 'View Reports' page.")
    
    return filename

if __name__ == "__main__":
    create_test_report()
