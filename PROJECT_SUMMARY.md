# 📁 Project Structure & File Guide

## 📋 Complete File Listing

```
educational website/
├── 📄 student_monitor.py      # Main AI monitoring system (CORE FILE)
├── 📄 setup_test.py            # Setup verification and testing script
├── 📄 examples.py              # Example usage scenarios
├── 📄 requirements.txt         # Python dependencies
├── 📄 config.json              # Configuration settings
├── 📄 install.bat              # Windows installation script
├── 📘 README.md                # Complete documentation
├── 📘 QUICKSTART.md            # Quick start guide
├── 📘 PROJECT_SUMMARY.md       # This file
└── 📄 .gitignore               # Git ignore rules
```

---

## 📄 File Descriptions

### Core Application Files

#### **student_monitor.py** ⭐ MAIN FILE
The complete AI monitoring system that includes:
- Face detection and recognition
- Focus/gaze detection (looking at camera)
- Mobile phone detection
- Real-time monitoring with webcam
- Automatic report generation
- JSON data export

**Key Classes:**
- `StudentMonitor`: Main class handling all monitoring operations

**Key Methods:**
- `_load_student_photos()`: Loads faces from ZIP file
- `detect_gaze()`: Determines if student is looking at camera
- `detect_mobile()`: Detects mobile phone usage
- `match_face()`: Matches detected faces with known students
- `process_frame()`: Processes each video frame
- `generate_report()`: Creates detailed focus reports
- `start_monitoring()`: Begins the monitoring session

**How to Run:**
```bash
python student_monitor.py
```

---

#### **setup_test.py** 🔧
Verification script that checks:
- ✓ Python version compatibility
- ✓ Required dependencies installed
- ✓ Camera accessibility
- ✓ OpenCV cascade models
- ✓ Student data (name.zip) presence
- ✓ Runs optional camera test

**How to Run:**
```bash
python setup_test.py
```

---

#### **examples.py** 📚
Pre-configured scenarios for different use cases:
- Quick 1-minute test
- Full class monitoring (1 hour)
- Exam monitoring (2 hours, strict)
- External camera usage
- Custom scenarios (quiz/lecture/workshop/test)

**How to Run:**
```bash
python examples.py
```

---

### Configuration Files

#### **requirements.txt**
Python package dependencies:
- `opencv-python` - Computer vision library
- `opencv-contrib-python` - Additional CV modules
- `numpy` - Numerical computing
- `Pillow` - Image processing
- Optional: face-recognition, dlib, tensorflow, ultralytics

**Installation:**
```bash
pip install -r requirements.txt
```

---

#### **config.json**
JSON configuration file with customizable settings:
- ZIP file location
- Check interval duration
- Focus threshold percentage
- Camera index
- Detection parameters
- Mobile detection settings
- Report preferences

**Example Configuration:**
```json
{
    "zip_file": "name.zip",
    "check_interval_seconds": 300,
    "focus_threshold_percent": 50,
    "camera_index": 0
}
```

---

### Documentation Files

#### **README.md** 📖
Comprehensive documentation including:
- Features overview
- Installation instructions
- Detailed usage guide
- Configuration options
- Troubleshooting
- Examples and tips

---

#### **QUICKSTART.md** 🚀
Fast-track guide with:
- 5-step quick setup
- Common scenarios
- Keyboard controls
- Quick troubleshooting
- Duration examples

---

#### **PROJECT_SUMMARY.md** (this file) 📋
Complete project overview and file guide

---

### Utility Files

#### **install.bat** 💻
Windows batch script for automated installation:
- Checks Python installation
- Installs dependencies
- Runs setup verification

**How to Run:**
```bash
install.bat
```

---

#### **.gitignore**
Git ignore rules for:
- Python cache files
- Student photos and data
- Generated reports
- IDE settings
- OS-specific files

---

## 🎯 Key Features Breakdown

### 1. Face Detection & Recognition
- **Technology**: OpenCV Haar Cascades
- **Process**: Loads student photos from ZIP → Creates face database → Matches in real-time
- **Accuracy**: Histogram-based matching (can be upgraded to deep learning)

### 2. Focus Detection (Gaze Tracking)
- **Method**: Eye detection
- **Logic**: If both eyes visible → Student is focused
- **Tracking**: Counts focused vs unfocused instances

### 3. Mobile Phone Detection
- **Approach**: Object shape detection (rectangular objects with phone-like aspect ratio)
- **Alert**: Displays "{Name} REPORT!" when detected
- **Logging**: Records all mobile detection incidents

### 4. Reporting System
- **Console Report**: Detailed text output with statistics
- **JSON Export**: Machine-readable data for further analysis
- **Metrics**: Focus percentage, alert counts, timestamps

### 5. Threshold Analysis
- **Default**: 50% focus required
- **Configurable**: Adjust based on activity type
- **Visual Feedback**: ✓ GOOD FOCUS or ✗ NEEDS IMPROVEMENT

---

## 🔄 Typical Workflow

```
1. Prepare → Collect student photos → Create name.zip
           ↓
2. Install → Run install.bat or pip install -r requirements.txt
           ↓
3. Test → Run setup_test.py to verify everything works
           ↓
4. Configure → Edit settings in student_monitor.py (duration, threshold)
           ↓
5. Monitor → Run python student_monitor.py
           ↓
6. Review → Check console report and JSON file
           ↓
7. Action → Follow up with students who need attention
```

---

## ⚙️ Customization Quick Reference

### Change Monitoring Duration
**File**: `student_monitor.py`
```python
CHECK_INTERVAL = 600  # 10 minutes
```

### Change Focus Threshold
**File**: `student_monitor.py`
```python
FOCUS_THRESHOLD = 70  # 70% required
```

### Change ZIP File Name
**File**: `student_monitor.py`
```python
ZIP_FILE = "students_class_A.zip"
```

### Use Different Camera
**File**: `student_monitor.py`
```python
monitor.start_monitoring(camera_index=1)  # External camera
```

---

## 🎓 Use Case Examples

### Quiz (10 min, strict)
```python
StudentMonitor("name.zip", check_interval=600, focus_threshold=80)
```

### Lecture (45 min, moderate)
```python
StudentMonitor("name.zip", check_interval=2700, focus_threshold=50)
```

### Exam (2 hours, very strict)
```python
StudentMonitor("name.zip", check_interval=7200, focus_threshold=85)
```

### Workshop (1.5 hours, relaxed)
```python
StudentMonitor("name.zip", check_interval=5400, focus_threshold=40)
```

---

## 📊 Report Output Example

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

✗ Student: John
   Focus Percentage: 35.2% ✗ NEEDS IMPROVEMENT
   Focused Count: 70
   Unfocused Count: 129
   Total Checks: 199
   ⚠ Mobile Detected: 3 times
   Alerts:
      - 10:25:32: Mobile phone detected
```

---

## 🔧 Technical Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.8+ |
| Computer Vision | OpenCV (cv2) |
| Face Detection | Haar Cascade Classifiers |
| Eye Detection | Haar Cascade (for gaze) |
| Object Detection | Contour analysis |
| Data Format | JSON |
| Image Format | JPEG, PNG |
| Video Input | Webcam/Camera |

---

## 📈 Performance Tips

1. **Better Face Recognition**: Install `face-recognition` library
2. **Faster Processing**: Reduce `process_every_n_frames` in config
3. **Better Accuracy**: Use higher quality student photos
4. **GPU Acceleration**: Use OpenCV with CUDA support

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Camera not working | Try different camera_index (0, 1, 2) |
| Poor face recognition | Use clearer, well-lit photos |
| name.zip not found | Check file location and name |
| Dependencies error | Run `pip install -r requirements.txt` |
| False mobile detection | Adjust detection parameters in config |

---

## 📞 Support Resources

- **README.md**: Full documentation
- **QUICKSTART.md**: Quick setup guide
- **setup_test.py**: Diagnostic tool
- **examples.py**: Usage examples
- **config.json**: Settings reference

---

## 🔐 Privacy & Ethics

⚠️ **Important Reminders:**
- Inform students about monitoring
- Secure all photos and reports
- Follow institutional privacy policies
- Use responsibly and ethically
- Comply with data protection regulations

---

## 📝 Version Information

- **Project**: AI Student Focus Monitoring System
- **Created**: February 25, 2026
- **Platform**: Windows compatible
- **Python**: 3.8+ required

---

## 🎯 Next Steps

1. ✓ Review this summary
2. ✓ Read QUICKSTART.md
3. ✓ Run setup_test.py
4. ✓ Prepare name.zip
5. ✓ Start monitoring!

**Happy Monitoring! 📸👨‍🎓**
