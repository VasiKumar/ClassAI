# 🎓 AI Student Focus Monitoring System

An intelligent system that monitors student attention and engagement during online classes or exams using real-time face detection, gaze tracking, and mobile phone detection.

## ✨ Features

- **👤 Face Recognition**: Identifies students from a pre-loaded photo database
- **👁️ Focus Detection**: Monitors if students are looking at the camera (focused)
- **📱 Mobile Phone Detection**: Alerts when a student is using a mobile phone
- **📊 Detailed Reporting**: Generates comprehensive focus reports with statistics
- **⚠️ Real-time Alerts**: Displays instant alerts for mobile phone usage
- **📈 Threshold Analysis**: Evaluates if students meet the minimum focus threshold (default: 50%)

## 📋 Requirements

- Python 3.8 or higher
- Webcam/Camera
- Student photos in a ZIP file

## 🚀 Installation

1. **Clone or download this project**

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare student photos**:
   - Create a folder with student photos
   - Name each photo with the student's name (e.g., `Basistha.jpg`, `John.png`)
   - The name of the file will be used as the student's identifier
   - Compress the folder into a ZIP file named `name.zip`

## 📝 Usage

### Basic Usage

1. **Prepare your student photos ZIP file** (e.g., `name.zip`)
   ```
   name.zip
   ├── Basistha.jpg
   ├── Student1.jpg
   ├── Student2.jpg
   └── Student3.jpg
   ```

2. **Run the monitoring system**:
   ```bash
   python student_monitor.py
   ```

3. **Monitor your class**:
   - The system will start capturing video from your webcam
   - It will detect and recognize students in real-time
   - Press 'q' to quit or wait for the monitoring period to complete

4. **View the report**:
   - After monitoring ends, a detailed report will be displayed
   - A JSON file with the report will be saved automatically

### Custom Configuration

Edit the configuration in `student_monitor.py`:

```python
# Configuration
ZIP_FILE = "name.zip"          # Your zip file name
CHECK_INTERVAL = 300           # Duration in seconds (300 = 5 minutes)
FOCUS_THRESHOLD = 50           # Minimum focus percentage required (50%)
```

## 🎯 How It Works

### 1. **Face Detection & Recognition**
- Loads student photos from the ZIP file
- Creates a face database for each student
- Recognizes students during monitoring using face matching

### 2. **Focus Detection**
- Detects eyes to determine if student is looking at the camera
- If both eyes are visible, student is marked as "focused"
- Tracks focused vs unfocused counts for each student

### 3. **Mobile Phone Detection**
- Analyzes frames for mobile phone-like objects
- Triggers alert: `{Student Name} REPORT!`
- Records mobile usage incidents

### 4. **Reporting & Analysis**
- Calculates focus percentage for each student
- Compares against threshold (default: 50%)
- Generates detailed reports with:
  - Focus percentage
  - Focused/unfocused counts
  - Mobile detection incidents
  - Time-stamped alerts

## 📊 Report Format

### Console Output
```
======================================================================
STUDENT FOCUS MONITORING REPORT
======================================================================
Generated: 2026-02-25 10:30:45
Monitoring Duration: 300 seconds
Focus Threshold: 50%
======================================================================

✓ Student: Basistha
   Focus Percentage: 75.5% ✓ GOOD FOCUS
   Focused Count: 151
   Unfocused Count: 49
   Total Checks: 200
   
✗ Student: Student1
   Focus Percentage: 35.2% ✗ NEEDS IMPROVEMENT
   Focused Count: 70
   Unfocused Count: 129
   Total Checks: 199
   ⚠ Mobile Detected: 3 times
   Alerts:
      - 10:25:32: Mobile phone detected
      - 10:27:15: Mobile phone detected
```

### JSON Report
A detailed JSON report is saved with the filename format: `focus_report_YYYYMMDD_HHMMSS.json`

## 🎨 Visual Indicators

During monitoring, you'll see:
- **Green box + "Focused"**: Student is paying attention
- **Orange box + "Not Focused"**: Student is not looking at camera
- **Red box + "REPORT!"**: Mobile phone detected

## ⚙️ Advanced Configuration

### Change Monitoring Duration
```python
CHECK_INTERVAL = 600  # 10 minutes
```

### Adjust Focus Threshold
```python
FOCUS_THRESHOLD = 70  # Require 70% focus
```

### Use Different Camera
```python
monitor.start_monitoring(camera_index=1)  # Use second camera
```

## 🔧 Troubleshooting

### Camera Not Opening
- Check if another application is using the camera
- Try changing `camera_index` to 0, 1, or 2

### Poor Face Recognition
- Ensure student photos are clear and well-lit
- Photos should show faces clearly
- Avoid blurry or low-resolution images

### False Mobile Detection
- The system uses basic object detection for mobile phones
- For better accuracy, consider integrating a trained model

## 📈 Improving Accuracy

For better face recognition, install the `face-recognition` library:
```bash
pip install face-recognition
pip install dlib
```

Then modify the code to use `face_recognition` library's encodings instead of histogram comparison.

## 🤝 Example Workflow

1. **Before Class**:
   - Collect student photos
   - Create `name.zip`
   - Set monitoring duration and threshold

2. **During Class**:
   - Start the monitoring system
   - Let it run for the configured duration
   - System monitors focus and detects mobile usage

3. **After Class**:
   - Review the generated report
   - Identify students who need attention
   - Take necessary actions

## 📝 Notes

- The system requires good lighting for accurate detection
- Ensure students are visible to the camera
- Multiple students can be monitored simultaneously
- Reports are saved automatically for record-keeping

## 🔒 Privacy Considerations

- Inform students about monitoring
- Secure the stored photos and reports
- Use the system ethically and responsibly
- Follow your institution's privacy policies

## 📄 License

This project is provided as-is for educational purposes.

## 🆘 Support

For issues or questions, please check:
1. Camera is properly connected
2. All dependencies are installed
3. ZIP file is in the correct location
4. Student photos are properly named

---

**Made with ❤️ for better student engagement monitoring**
