"""
Example: Custom Configuration for Student Monitor
This file shows how to customize the monitoring system
"""

from student_monitor import StudentMonitor

# Example 1: Quick 1-minute test
def quick_test():
    """Run a quick 1-minute monitoring test"""
    print("Running 1-minute quick test...")
    
    monitor = StudentMonitor(
        zip_file_path="name.zip",
        check_interval=60,  # 1 minute
        focus_threshold=50  # 50% threshold
    )
    
    monitor.start_monitoring()

# Example 2: Full class monitoring (1 hour)
def full_class_monitoring():
    """Monitor an entire 1-hour class"""
    print("Starting full class monitoring (1 hour)...")
    
    monitor = StudentMonitor(
        zip_file_path="name.zip",
        check_interval=3600,  # 60 minutes
        focus_threshold=60  # 60% threshold (stricter)
    )
    
    monitor.start_monitoring()

# Example 3: Exam monitoring (2 hours, strict threshold)
def exam_monitoring():
    """Monitor a 2-hour exam with strict focus requirements"""
    print("Starting exam monitoring (2 hours, strict mode)...")
    
    monitor = StudentMonitor(
        zip_file_path="name.zip",
        check_interval=7200,  # 2 hours
        focus_threshold=75  # 75% threshold (very strict)
    )
    
    monitor.start_monitoring()

# Example 4: Use external camera
def external_camera_monitoring():
    """Use an external camera (camera index 1)"""
    print("Using external camera...")
    
    monitor = StudentMonitor(
        zip_file_path="name.zip",
        check_interval=300,  # 5 minutes
        focus_threshold=50
    )
    
    # Start with camera index 1 (external camera)
    monitor.start_monitoring(camera_index=1)

# Example 5: Custom reporting without video monitoring
def analyze_recorded_video():
    """
    Analyze a pre-recorded video file
    Note: This requires modifying the student_monitor.py to accept video files
    """
    print("This feature requires custom implementation")
    print("Modify start_monitoring() to accept video file path")

# Example 6: Get individual student report
def get_student_report(monitor, student_name):
    """Get detailed report for a specific student"""
    if student_name in monitor.student_data:
        data = monitor.student_data[student_name]
        focus_pct = monitor.calculate_focus_percentage(student_name)
        
        print(f"\n{'='*50}")
        print(f"Report for: {student_name}")
        print(f"{'='*50}")
        print(f"Focus Percentage: {focus_pct}%")
        print(f"Focused Count: {data['focused_count']}")
        print(f"Unfocused Count: {data['unfocused_count']}")
        print(f"Mobile Detected: {data['mobile_detected']} times")
        print(f"Total Checks: {data['total_checks']}")
        
        if data['alerts']:
            print(f"\nAlerts:")
            for alert in data['alerts']:
                print(f"  {alert['time']}: {alert['reason']}")
        print(f"{'='*50}\n")
    else:
        print(f"Student '{student_name}' not found in database")

# Example 7: Custom thresholds for different scenarios
def custom_scenarios():
    """Different monitoring scenarios"""
    
    scenarios = {
        'quiz': {
            'duration': 600,  # 10 minutes
            'threshold': 80,  # High focus required
            'description': 'Short quiz - high focus needed'
        },
        'lecture': {
            'duration': 2700,  # 45 minutes
            'threshold': 50,  # Moderate focus
            'description': 'Regular lecture - moderate focus'
        },
        'workshop': {
            'duration': 5400,  # 90 minutes
            'threshold': 40,  # Relaxed (hands-on work)
            'description': 'Workshop - students may look away'
        },
        'test': {
            'duration': 3600,  # 60 minutes
            'threshold': 85,  # Very high focus
            'description': 'Important test - very strict'
        }
    }
    
    print("\nAvailable scenarios:")
    for key, config in scenarios.items():
        print(f"  {key}: {config['description']}")
    
    scenario = input("\nSelect scenario (quiz/lecture/workshop/test): ").lower()
    
    if scenario in scenarios:
        config = scenarios[scenario]
        print(f"\nStarting {scenario} monitoring...")
        print(f"Duration: {config['duration']}s ({config['duration']//60} min)")
        print(f"Threshold: {config['threshold']}%")
        
        monitor = StudentMonitor(
            zip_file_path="name.zip",
            check_interval=config['duration'],
            focus_threshold=config['threshold']
        )
        
        monitor.start_monitoring()
    else:
        print("Invalid scenario selected")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("STUDENT MONITOR - EXAMPLE SCENARIOS")
    print("="*60)
    print("\nAvailable examples:")
    print("1. Quick 1-minute test")
    print("2. Full class monitoring (1 hour)")
    print("3. Exam monitoring (2 hours, strict)")
    print("4. Use external camera")
    print("5. Custom scenarios (quiz/lecture/workshop/test)")
    print("="*60)
    
    choice = input("\nSelect example (1-5): ")
    
    if choice == '1':
        quick_test()
    elif choice == '2':
        full_class_monitoring()
    elif choice == '3':
        exam_monitoring()
    elif choice == '4':
        external_camera_monitoring()
    elif choice == '5':
        custom_scenarios()
    else:
        print("Invalid choice")
