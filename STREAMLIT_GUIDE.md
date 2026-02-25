# Sahayak AI - Streamlit Dashboard

## 🎓 Overview

A comprehensive web-based dashboard for monitoring student focus during online classes. Administrators and teachers can:

- View all registered students
- Start monitoring sessions with custom duration and focus thresholds
- View detailed reports with statistics and visualizations
- Track attendance and focus percentage
- Detect mobile phone usage
- Delete old reports
- Configure system settings

## 🚀 Quick Start

### 1. Install Dependencies

Make sure you have installed all requirements:

```bash
pip install -r requirements.txt
```

### 2. Launch the Dashboard

Run the Streamlit app:

```bash
streamlit run streamlit_app.py
```

Or use the provided batch file (Windows):

```bash
launch_dashboard.bat
```

The dashboard will open in your default web browser at `http://localhost:8501`

## 📱 Dashboard Pages

### 🏠 Home
- Quick overview of the system
- Latest session statistics
- Focus distribution charts
- Quick action buttons

### 👥 Students
- View all registered students
- Search functionality
- Student list in table format
- Instructions for adding new students

### ▶️ Start Monitoring
- Configure class duration (minutes)
- Set focus threshold percentage
- Preview students to be monitored
- Generate config and start session
- Instructions for running the monitoring script

### 📈 View Reports
- Select and view past reports
- Comprehensive session summary including:
  - Duration and attendance
  - Average focus percentage
  - Pass/fail statistics
  - Mobile phone detections
- Individual student performance details
- Interactive charts and visualizations
- Delete reports functionality

### ⚙️ Settings
- Set default focus threshold
- View system configuration
- Manage reports (delete all, export)
- System information

## 📊 Key Features

### Attendance Tracking
The dashboard automatically calculates:
- **Total Registered Students**: From ZIP files in `sample_student_photos` folder
- **Students Present**: Detected during monitoring session
- **Attendance Rate**: Percentage of present vs registered students
- **Absent Students**: List of students who were not detected

### Focus Analysis
- **Average Focus**: Mean focus percentage across all present students
- **Threshold Comparison**: Students above vs below the threshold
- **Individual Performance**: Detailed breakdown per student
- **Focus Distribution**: Visual charts showing performance

### Mobile Detection
- **Mobile Alerts**: Highlighted warnings for students using phones
- **Detection Count**: Total mobile phone detections per student
- **Timestamps**: When mobile phones were detected
- **Priority Display**: Mobile alerts shown first in reports

### Reporting
- **JSON Format**: Reports saved as `focus_report_YYYYMMDD_HHMMSS.json`
- **Report Management**: Delete individual or all reports
- **Export Options**: Coming soon
- **Historical Data**: View all past sessions

## 🎯 Usage Workflow

### For Teachers/Admins:

1. **Setup Students** (One-time)
   - Create ZIP files for each student with their photos
   - Name files as: `studentname.zip`
   - Place in `sample_student_photos` folder

2. **Start a Session**
   - Go to "Start Monitoring" page
   - Set class duration (e.g., 45 minutes)
   - Set focus threshold (e.g., 60%)
   - Click "START MONITORING SESSION"
   - Run the monitoring command in terminal

3. **Monitor**
   - The camera will start
   - Students are detected and tracked
   - Focus and mobile usage monitored
   - Report generated automatically at end

4. **View Results**
   - Go to "View Reports" page
   - Select the latest report
   - Review attendance, focus, and mobile detections
   - Export or delete reports as needed

5. **Configure Settings**
   - Adjust default focus threshold
   - Manage old reports
   - View system status

## 🔧 Configuration

### Focus Threshold
The focus threshold determines the minimum percentage of time a student must be focused to "pass" the session. 

**Examples:**
- 50% = Student must be focused at least half the time
- 70% = Student must be focused 70% of the time
- 80% = High standard - very focused

**Recommendations:**
- Elementary: 40-50%
- Middle School: 50-60%
- High School: 60-70%
- College: 70-80%

### Session Duration
Set how long to monitor students:
- Short quiz: 5-15 minutes
- Regular class: 30-60 minutes
- Long session: 90-180 minutes

## 📈 Understanding Reports

### Student Performance Metrics

Each student gets:
- **Focus %**: Percentage of time looking at camera
- **Focused Count**: Number of "focused" checks
- **Unfocused Count**: Number of "unfocused" checks
- **Total Checks**: Total monitoring checks
- **Mobile Detected**: Number of times phone was detected
- **Status**: ✅ Pass or ❌ Fail (based on threshold)

### Session Summary Metrics

- **Duration**: Total monitoring time
- **Attendance**: Present/Total students with percentage
- **Average Focus**: Mean focus across all students
- **Passed**: Students above threshold
- **Mobile Use**: Total mobile detections

### Visualizations

1. **Focus Distribution Pie Chart**: Shows pass/fail ratio
2. **Attendance Pie Chart**: Present vs absent students
3. **Focus Bar Chart**: Individual student comparison
4. **Mobile Detection List**: Students with phone usage

## 🎨 Color Coding

- 🟢 **Green**: Good focus, above threshold
- 🔴 **Red**: Poor focus, below threshold
- 🔵 **Blue**: Present/attending
- ⚪ **Gray**: Absent
- ⚠️ **Yellow**: Mobile phone detected (warning)

## 💡 Tips

### For Best Results:

1. **Good Lighting**: Ensure room is well-lit for face detection
2. **Camera Angle**: Position camera at eye level facing students
3. **Clear Background**: Minimize visual distractions
4. **Test First**: Run a short test session before actual class
5. **Realistic Thresholds**: Don't set threshold too high initially

### Troubleshooting:

**No students detected:**
- Check ZIP files are in `sample_student_photos` folder
- Verify ZIP files are named correctly (studentname.zip)
- Ensure ZIP files contain photos of students

**Camera not working:**
- Check camera permissions
- Close other apps using the camera
- Try running as administrator

**Low focus percentages:**
- Adjust camera angle
- Improve lighting
- Verify eye detection is working
- Consider lowering threshold if realistic

## 📱 Mobile Detection

The system can detect mobile phone usage:

**Edge Detection Mode:**
- Uses edge detection
- Basic accuracy
- No additional files needed
- May have some false positives

## 🔒 Privacy & Security

- All processing is done locally - no data sent to cloud
- Reports stored locally on your computer
- Camera access required only during monitoring
- You can delete reports at any time
- No personal data shared externally

## 🆘 Support

For issues or questions:

1. Check QUICKSTART.md for setup help
2. Review USAGE_GUIDE.md for detailed instructions
3. See TROUBLESHOOTING section in README.md
4. Contact your system administrator

## 📄 License

This system is for educational use only.

---

**Made with ❤️ for Education**
