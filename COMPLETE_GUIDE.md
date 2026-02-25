# 🎓 Student Focus Monitoring System - Complete Setup

## 📋 System Components

This system consists of two main parts:

1. **Monitoring System** (`student_monitor.py`)
   - Face recognition and detection
   - Focus tracking
   - Mobile phone detection
   - Report generation

2. **Web Dashboard** (`streamlit_app.py`)
   - Admin interface
   - View students and reports
   - Configure sessions
   - Manage reports

## 🚀 Quick Start Guide

### Step 1: Install Requirements

```bash
pip install -r requirements.txt
```

### Step 2: Setup Student Photos

1. Create a folder named `sample_student_photos` (if not exists)
2. For each student, create a ZIP file named `studentname.zip`
3. Add 5-10 photos of the student to their ZIP file
4. Place all ZIP files in the `sample_student_photos` folder

**Example structure:**
```
d:\educational website\
├── sample_student_photos\
│   ├── basistha.zip
│   ├── sarbeswar.zip
│   ├── john.zip
│   └── mary.zip
```

### Step 3: Launch the Dashboard

**Option A: Use Batch File (Windows)**
```bash
launch_dashboard.bat
```

**Option B: Command Line**
```bash
streamlit run streamlit_app.py
```

### Step 4: Start Monitoring

1. Open dashboard in browser (http://localhost:8501)
2. Go to "Start Monitoring" page
3. Set class duration and focus threshold
4. Click "START MONITORING SESSION"
5. Open a terminal and run: `python student_monitor.py`
6. Monitor will run automatically
7. Report generated when session ends

### Step 5: View Results

1. Go to "View Reports" page in dashboard
2. Select the latest report
3. Review attendance, focus, and mobile detections

## 📊 Dashboard Features

### Home Page
- Quick overview of system status
- Latest session statistics
- Focus distribution charts
- Attendance summary

### Students Page
- View all registered students
- Search functionality
- Student information display

### Start Monitoring
- Configure session duration (1-180 minutes)
- Set focus threshold (0-100%)
- Preview students
- Generate config file
- Launch monitoring

### View Reports
- Browse all reports
- Detailed session analysis
- Attendance tracking (Present/Total)
- Focus statistics
- Mobile phone detections
- Individual student performance
- Delete reports

### Settings
- Configure default threshold
- System information
- Report management
- Delete all reports

## 🎯 Key Metrics Explained

### Attendance
- **Total Registered**: All students with ZIP files
- **Present**: Students detected during session
- **Absent**: Registered but not detected
- **Attendance %**: (Present/Total) × 100

### Focus
- **Focus %**: Time student looked at camera
- **Threshold**: Minimum % to pass
- **Passed**: Students above threshold
- **Failed**: Students below threshold

### Mobile Detection
- Warns when student uses phone
- Shows detection count and timestamps
- Flags student for report

## 🎨 Visual Features

### Color Coding
- 🟢 Green: Good focus (above threshold)
- 🔴 Red: Poor focus (below threshold)
- 🔵 Blue: Present student
- ⚪ Gray: Absent student
- ⚠️ Yellow: Mobile detected

### Charts
1. **Focus Bar Chart**: Compare all students
2. **Pass/Fail Pie**: Threshold distribution
3. **Attendance Pie**: Present vs absent
4. **Performance Table**: Detailed stats

## ⚙️ Configuration Options

### Session Duration
- Short: 5-15 minutes (quiz)
- Medium: 30-60 minutes (class)
- Long: 90-180 minutes (lecture)

### Focus Threshold
- 40-50%: Elementary
- 50-60%: Middle school
- 60-70%: High school
- 70-80%: College

### Mobile Detection
- **Edge Detection**: Basic accuracy (may have false positives)
- Disabled by default - enable only if needed

## 🔧 Advanced Usage

### Command Line Monitoring

You can run monitoring directly without the dashboard:

```bash
# Default settings (5 min, 50% threshold)
python student_monitor.py

# Custom duration and threshold
python student_monitor.py --duration 1800 --threshold 70

# With mobile detection enabled
python student_monitor.py --enable-mobile-detection
```

### Configuration File

The dashboard creates `monitor_config.json`:
```json
{
    "duration": 300,
    "threshold": 50,
    "enable_mobile_detection": false
}
```

You can edit this file manually before running.

### Report Format

Reports are saved as `focus_report_YYYYMMDD_HHMMSS.json`:

```json
{
    "timestamp": "2026-02-25T19:24:40",
    "duration": 300,
    "threshold": 50,
    "students": {
        "basistha": {
            "focus_percentage": 75.5,
            "focused_count": 151,
            "unfocused_count": 49,
            "total_checks": 200,
            "mobile_detected": 2,
            "mobile_times": ["19:25:30", "19:27:45"]
        }
    }
}
```

## 📱 Using the System

### Teacher Workflow

**Before Class:**
1. Launch dashboard
2. Configure session settings
3. Check all students are registered

**During Class:**
1. Start monitoring session
2. System tracks automatically
3. No intervention needed

**After Class:**
1. View report in dashboard
2. Review attendance and focus
3. Check mobile detections
4. Export or delete report

### Admin Workflow

**Setup:**
1. Install system
2. Add student photos
3. Configure default settings

**Maintenance:**
1. Add new students as needed
2. Delete old reports periodically
3. Adjust thresholds based on feedback

**Monitoring:**
1. Review reports regularly
2. Track trends over time
3. Identify struggling students

## 💡 Best Practices

### For Better Detection
1. ✅ Good lighting on student faces
2. ✅ Camera at eye level
3. ✅ Clear photos in ZIP files
4. ✅ 5-10 photos per student
5. ✅ Photos from different angles

### For Realistic Results
1. ✅ Start with lower threshold (50%)
2. ✅ Increase gradually based on results
3. ✅ Test with short sessions first
4. ✅ Consider student age/level
5. ✅ Account for technical issues

### For Privacy
1. ✅ Inform students about monitoring
2. ✅ Store reports securely
3. ✅ Delete old reports regularly
4. ✅ No cloud upload - all local
5. ✅ Respect student privacy

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check Streamlit installed
pip install streamlit

# Try different port
streamlit run streamlit_app.py --server.port 8502
```

### No students showing
- Check `sample_student_photos` folder exists
- Verify ZIP files are named correctly
- Ensure ZIP files contain images

### Camera not working
- Close other apps using camera
- Run as administrator
- Check camera permissions
- Test with webcam app first

### Low focus percentages
- Improve lighting
- Adjust camera angle
- Check eye detection working
- Consider lowering threshold

### Mobile detection not working
- Check lighting conditions
- Adjust detection parameters
- May have false positives - consider disabling

## 📞 Support Files

- **STREAMLIT_GUIDE.md**: Dashboard detailed guide
- **USAGE_GUIDE.md**: Monitoring system guide

- **SETUP_GUIDE.md**: Student photo setup
- **README.md**: General information

## 🔄 System Updates

### Adding Students
1. Create new `studentname.zip`
2. Place in `sample_student_photos`
3. Refresh dashboard
4. Student appears automatically

### Changing Threshold
1. Go to Settings page
2. Adjust slider
3. Save changes
4. Applies to next session

### Deleting Reports
1. Go to View Reports page
2. Select report
3. Click "Delete Report"
4. Or delete all in Settings

## 📊 Understanding Results

### Good Session Signs
- ✅ High attendance rate (>80%)
- ✅ Average focus above threshold
- ✅ Few mobile detections
- ✅ Most students passed

### Areas of Concern
- ⚠️ Low attendance (<70%)
- ⚠️ Low average focus
- ⚠️ Many mobile detections
- ⚠️ Few students passed

### What to Do Next
1. Review individual student data
2. Check if threshold too high
3. Verify technical setup
4. Consider student feedback
5. Adjust for next session

## 🎉 Success Tips

1. **Start Small**: Test with 2-3 students first
2. **Be Realistic**: Don't expect 100% focus
3. **Iterate**: Adjust settings based on results
4. **Communicate**: Tell students what you're monitoring
5. **Be Fair**: Account for technical issues

## 📈 Tracking Progress

Use the dashboard to:
- Compare sessions over time
- Track individual student improvement
- Identify patterns
- Adjust teaching strategies
- Celebrate improvements

## 🔐 Security Notes

- All data stored locally
- No internet connection required
- No third-party services
- You control all data
- Delete reports anytime

---

## 🆘 Quick Help

**Issue**: Dashboard won't open
**Solution**: Check port 8501 is free, try different port

**Issue**: Students not detected
**Solution**: Verify ZIP files in correct folder with photos

**Issue**: Camera error
**Solution**: Close other apps, check permissions

**Issue**: Report not generated
**Solution**: Wait for full session duration to complete

**Issue**: Low accuracy
**Solution**: Improve lighting, add more photos, adjust camera

---

**Ready to Start?**

1. Run: `launch_dashboard.bat`
2. Configure session
3. Start monitoring
4. View results

**Made with ❤️ for Better Education**
