# 📖 Complete Usage Guide - Student Focus Monitor with ML

## 🎯 Overview

This system uses **Machine Learning-based face recognition** to:
- **Train automatically** on student photos (NO hardcoded names)
- **Detect faces** and recognize students in real-time
- **Monitor focus** by tracking if students look at the camera
- **Track mobile usage** and report at END of session
- Support **nested zip files** (e.g., basistha.zip, sarbeswar.zip inside name.zip)

---

## 📦 Preparing Student Data

### Option 1: Single ZIP with Individual Photos
```
name.zip
├── basistha.jpg
├── sarbeswar.jpg
├── student1.jpg
└── student2.png
```

### Option 2: Nested ZIP Files (RECOMMENDED for multiple photos per student)
```
name.zip
├── basistha.zip
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── photo3.jpg
├── sarbeswar.zip
│   ├── image1.png
│   └── image2.jpg
└── otherstudent.jpg
```

**How it works:**
- The system automatically extracts all nested ZIPs
- Student name comes from the ZIP filename (e.g., `basistha.zip` → student: "basistha")
- Multiple photos per student improve recognition accuracy
- NO names are hardcoded - system learns from folder/file names

---

## 🚀 Installation

### Step 1: Install Dependencies

#### Full Installation (with ML face recognition - RECOMMENDED)
```bash
pip install -r requirements.txt
```

This installs:
- `opencv-python` - Computer vision
- `face-recognition` - ML-based face recognition
- `dlib` - Deep learning toolkit
- `numpy`, `Pillow` - Image processing

**Note:** `dlib` may require Visual C++ build tools on Windows. If installation fails:
```bash
# Install without dlib first
pip install opencv-python opencv-contrib-python numpy Pillow

# Then try face-recognition
pip install face-recognition
```

#### Minimal Installation (without ML - less accurate)
```bash
pip install opencv-python opencv-contrib-python numpy Pillow
```

The system will automatically use the best available method.

---

## 🎓 Training the Model

### Automatic Training Process

When you run the system, it automatically:

1. **Extracts all photos** from name.zip
2. **Detects faces** in each photo
3. **Learns face features** using ML (if available)
4. **Creates student profiles** dynamically
5. **NO hardcoded names** - learns from your data!

Example training output:
```
======================================================================
TRAINING FACE RECOGNITION MODEL
======================================================================
📂 Extracting name.zip...
  📦 Extracted nested zip: basistha.zip
  📦 Extracted nested zip: sarbeswar.zip

🔍 Scanning for student photos...
  ✓ Trained on: basistha (photo1.jpg)
  ✓ Trained on: basistha (photo2.jpg)
  ✓ Trained on: sarbeswar (image1.png)
  ✓ Trained on: sarbeswar (image2.jpg)

======================================================================
✅ MODEL TRAINED SUCCESSFULLY
======================================================================
📊 Total students registered: 2
📸 Total photos processed: 4
🤖 Recognition method: ML-based (face_recognition)
======================================================================
```

---

## 🎬 Running the System

### Basic Usage
```bash
python student_monitor.py
```

### Custom Configuration
Edit these lines in `student_monitor.py`:
```python
# Configuration
ZIP_FILE = "name.zip"          # Your ZIP file
CHECK_INTERVAL = 300           # Duration: 300 seconds = 5 minutes
FOCUS_THRESHOLD = 50           # 50% minimum focus required
```

### During Monitoring

**What you see:**
- **Green box** - Student is focused (looking at camera)
- **Orange box** - Student not focused (looking away)
- **Timer** - Shows elapsed time / total time

**What happens silently:**
- Mobile phone detection is logged
- All data is recorded
- NO immediate alerts shown during class

**Controls:**
- Press **'q'** to quit early and generate report
- Or wait for timer to complete automatically

---

## 📊 End-of-Session Report

### Mobile Phone Reports (First)

After monitoring ends, mobile usage is reported:

```
======================================================================
STUDENT FOCUS MONITORING REPORT - END OF SESSION
======================================================================
Generated: 2026-02-25 14:30:00
Monitoring Duration: 300 seconds
Focus Threshold: 50%
======================================================================

🚨 MOBILE PHONE USAGE REPORTS 🚨
======================================================================

⚠️  basistha REPORT!
   Mobile detected: 3 times
   Times detected:
      - 14:25:15
      - 14:27:42
      - 14:29:08

⚠️  sarbeswar REPORT!
   Mobile detected: 1 times
   Times detected:
      - 14:26:30
```

### Focus Reports (Second)

Then individual focus statistics:

```
======================================================================
📊 INDIVIDUAL STUDENT FOCUS REPORTS
======================================================================

✓ Student: basistha
   Focus Percentage: 68.5% ✓ GOOD FOCUS
   Focused Count: 137
   Unfocused Count: 63
   Total Checks: 200
   📱 Mobile Usage: 3 times

✓ Student: sarbeswar
   Focus Percentage: 82.3% ✓ GOOD FOCUS
   Focused Count: 165
   Unfocused Count: 35
   Total Checks: 200
   📱 Mobile Usage: 1 times
```

### JSON Report File

A detailed JSON file is also saved:
```json
{
    "timestamp": "2026-02-25T14:30:00",
    "duration": 300,
    "threshold": 50,
    "students": {
        "basistha": {
            "focus_percentage": 68.5,
            "focused_count": 137,
            "unfocused_count": 63,
            "total_checks": 200,
            "mobile_detected": 3,
            "mobile_times": ["14:25:15", "14:27:42", "14:29:08"]
        },
        "sarbeswar": {
            "focus_percentage": 82.3,
            "focused_count": 165,
            "unfocused_count": 35,
            "total_checks": 200,
            "mobile_detected": 1,
            "mobile_times": ["14:26:30"]
        }
    }
}
```

---

## 🔧 Customization Examples

### Example 1: Quick 2-Minute Test
```python
monitor = StudentMonitor("name.zip", check_interval=120, focus_threshold=50)
monitor.start_monitoring()
```

### Example 2: 1-Hour Exam (Strict)
```python
monitor = StudentMonitor("name.zip", check_interval=3600, focus_threshold=80)
monitor.start_monitoring()
```

### Example 3: Multiple Students, Long Session
```python
# For a 90-minute workshop with 10+ students
monitor = StudentMonitor("name.zip", check_interval=5400, focus_threshold=45)
monitor.start_monitoring()
```

### Example 4: Use External Camera
```python
monitor = StudentMonitor("name.zip", check_interval=300, focus_threshold=50)
monitor.start_monitoring(camera_index=1)  # Use second camera
```

---

## 💡 Tips for Best Results

### Photo Preparation
1. **Clear photos** - Well-lit, sharp images
2. **Multiple angles** - 2-3 photos per student improves accuracy
3. **Different expressions** - Normal face, smiling, etc.
4. **Good quality** - At least 640x480 resolution
5. **Face visible** - Full face, no sunglasses/masks

### During Monitoring
1. **Good lighting** - Ensure room is well-lit
2. **Camera position** - Angle camera toward students
3. **Stable setup** - Keep camera steady
4. **Check first** - Run `setup_test.py` before actual session

### System Performance
- **ML method** (face_recognition) is more accurate but slower
- **OpenCV method** is faster but less accurate
- System automatically chooses best available method
- Process ~1 frame per second for real-time performance

---

## 🆘 Troubleshooting

### Issue: "face_recognition not available"
**Solution:** Install with:
```bash
pip install face-recognition dlib
```
Or continue with OpenCV method (system will work, just less accurate)

### Issue: Student not recognized
**Causes:**
- Poor lighting
- Face at different angle than training photos
- Low quality camera

**Solutions:**
- Add more training photos at different angles
- Improve lighting
- Use higher quality camera
- Lower matching threshold in code (see `match_face()`)

### Issue: False mobile detection
**Causes:**
- Reflective surfaces
- Other rectangular objects

**Solutions:**
- Adjust detection parameters in `detect_mobile()`
- Consider disabling mobile detection if too many false positives

### Issue: Camera not working
```bash
# Try different camera index
monitor.start_monitoring(camera_index=0)  # Built-in
monitor.start_monitoring(camera_index=1)  # External
```

---

## 📈 Understanding the Metrics

### Focus Percentage
- **80%+** - Excellent focus
- **60-79%** - Good focus
- **50-59%** - Acceptable (meets default threshold)
- **Below 50%** - Needs improvement

### Mobile Detection
- Counts number of times mobile was visible
- Shows exact times for accountability
- Reported only at end of session (not disruptive)

### Total Checks
- Number of times student's face was processed
- Higher number = more frames captured
- Typically ~1 check per second

---

## 🔐 Privacy & Ethics

**Important:**
- ✅ Inform students about monitoring
- ✅ Get consent before use
- ✅ Secure all data files
- ✅ Delete recordings after use
- ✅ Follow institutional policies
- ❌ Don't misuse data
- ❌ Don't share without permission

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Install dependencies | `pip install -r requirements.txt` |
| Test setup | `python setup_test.py` |
| Start monitoring | `python student_monitor.py` |
| Run examples | `python examples.py` |
| Quick test (1 min) | Edit `CHECK_INTERVAL = 60` |
| Quit early | Press 'q' during monitoring |

---

## 🎯 Summary

✅ **NO hardcoded student names** - learns from your data
✅ **Supports nested ZIPs** - basistha.zip, sarbeswar.zip, etc.
✅ **ML-based recognition** - High accuracy face matching
✅ **Automatic training** - Just provide photos
✅ **End-of-session reports** - Mobile usage reported after class
✅ **Focus tracking** - Real-time focus monitoring
✅ **Threshold analysis** - Shows who meets requirements
✅ **JSON export** - Machine-readable reports

**Ready to use! Just prepare your name.zip and run the system.**
