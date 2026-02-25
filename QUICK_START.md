# 🚀 Quick Start - Student Focus Monitoring System

## ⚡ Fast Setup (5 Minutes)

### Step 1: Install Requirements
```bash
pip install -r requirements.txt
```

### Step 2: Add Student Photos
1. Put student ZIP files in `sample_student_photos` folder
2. Name each ZIP as: `studentname.zip` (e.g., `john.zip`, `mary.zip`)
3. Each ZIP should contain 5-10 photos of that student

### Step 3: Launch Dashboard
```bash
launch_dashboard.bat
```
Or:
```bash
streamlit run streamlit_app.py
```

### Step 4: Start Monitoring
1. Dashboard opens in browser at http://localhost:8501
2. Go to **"▶️ Start Monitoring"** page
3. Set class duration (e.g., 30 minutes)
4. Set focus threshold (e.g., 60%)
5. Click **"🚀 START MONITORING SESSION"**
6. **Monitoring starts automatically!** A new window opens with camera feed

### Step 5: During Monitoring
- The system tracks students automatically
- You can see status in the sidebar (🟢 Session Active)
- To end early, click **"🛑 END SESSION NOW"**
- Or press **Ctrl+C** in the monitoring window

### Step 6: View Results
1. When monitoring ends, go to **"📈 View Reports"** page
2. Select the latest report
3. See:
   - **Attendance**: How many students were present
   - **Focus percentage**: For each student and overall
   - **Pass/fail**: Based on your threshold
   - **Mobile detections**: If anyone used phone

---

## 📋 Dashboard Pages

### 🏠 Home
- System overview
- Latest session stats
- Monitoring status (active/inactive)
- Quick actions

### 👥 Students
- View all registered students
- Search students
- See total count

### ▶️ Start Monitoring
- **Configure session**:
  - Duration: 1-180 minutes
  - Threshold: 0-100%
- **Start button**: Automatically launches monitoring
- **End button**: Stop session early
- **Live progress**: See elapsed time and remaining time

### 📈 View Reports
- **Select any report** from dropdown
- **Detailed statistics**:
  - Attendance: Present/Total (%)
  - Average focus percentage
  - Students above/below threshold
  - Mobile phone detections
- **Charts**: Bar charts, pie charts, tables
- **Delete reports**: Remove old reports

### ⚙️ Settings
- Set default focus threshold
- View system info
- Delete all reports

---

## 🎯 Key Features

### ✅ Automatic Start
- **One-click start**: No terminal commands needed
- **New window opens**: Monitoring runs in separate window
- **Dashboard stays open**: Configure and view while monitoring

### 🛑 Easy Stop
- **End button**: Stop anytime from dashboard
- **Or Ctrl+C**: In monitoring window
- **Or wait**: Auto-stops after configured duration

### 📊 Real-Time Status
- **Sidebar indicator**: Shows if monitoring is active
- **Progress bar**: See elapsed and remaining time
- **Auto-detection**: Dashboard knows when monitoring ends

### 📈 Comprehensive Reports
- **Attendance tracking**: Present/Total students
- **Focus analysis**: Individual and average
- **Threshold comparison**: Pass/fail statistics
- **Mobile alerts**: Phone usage warnings
- **Visual charts**: Easy to understand graphs

---

## 💡 Usage Tips

### For Teachers:

**Starting a Class:**
1. Launch dashboard before class
2. Set duration to match class length (e.g., 45 min)
3. Set realistic threshold (start with 50-60%)
4. Click START when class begins
5. Minimize dashboard, teach normally

**During Class:**
- Dashboard shows session is active
- Students are tracked automatically
- No intervention needed

**After Class:**
- Session ends automatically
- Go to View Reports
- Review attendance and focus
- Check mobile detections
- Share or delete report

### For Admins:

**Setup:**
- Add all student ZIP files once
- System remembers them
- Auto-loads students each session

**Maintenance:**
- Check reports regularly
- Delete old reports periodically
- Adjust default threshold based on feedback

**Troubleshooting:**
- If camera fails, close other apps using it
- If students not detected, check lighting
- If low focus%, verify threshold isn't too high

---

## 🎨 Understanding the Interface

### Status Indicators
- 🟢 **Green**: Monitoring active
- 🔴 **Red**: Poor focus (below threshold)
- 🟢 **Green**: Good focus (above threshold)
- ⚪ **White**: No active session
- 📱 **Yellow**: Mobile detected

### Buttons
- **🚀 START**: Launch monitoring session
- **🛑 END**: Stop session early
- **🔄 Refresh**: Reload reports
- **🗑️ Delete**: Remove report

### Metrics
- **📚 Total Students**: All registered (ZIP files)
- **👥 Present**: Detected during session
- **📊 Avg Focus**: Mean focus percentage
- **✅ Passed**: Students above threshold
- **📱 Mobile Use**: Total detections

---

## 🔧 Troubleshooting

### Dashboard Won't Start
```bash
# Check Streamlit installed
pip install streamlit

# Try different port
streamlit run streamlit_app.py --server.port 8502
```

### Monitoring Won't Start
- **Camera in use**: Close other apps (Zoom, Teams, etc.)
- **No students**: Add ZIP files to `sample_student_photos`
- **Python error**: Check `python student_monitor.py` runs

### No Students Showing
- Check folder: `sample_student_photos` exists
- Check files: `*.zip` files present
- Check names: `studentname.zip` format
- Refresh dashboard (F5)

### Camera Not Working
1. Close browser
2. Close any app using camera
3. Relaunch dashboard
4. Try START again

### Low/Wrong Focus Results
- **Lighting**: Ensure good lighting on faces
- **Camera angle**: Point camera at students
- **Threshold**: Try lower threshold (40-50%)
- **Photos**: Add more training photos per student

---

## 📱 Using on Different Devices

### Desktop (Recommended)
- Best performance
- Reliable camera access
- Full features

### Laptop
- Good for mobile teaching
- Built-in webcam works well
- May need external camera for multiple students

### Tablet (Limited)
- Dashboard works
- Monitoring may have issues
- Not recommended for production use

---

## 🔐 Privacy & Data

- **All local**: No internet required
- **No cloud**: Data stays on your computer
- **You control**: Delete reports anytime
- **No tracking**: No telemetry or analytics
- **Open source**: Review the code yourself

---

## 📚 More Help

- **Full guide**: See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)
- **Dashboard details**: See [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)
- **Setup help**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Main readme**: See [README.md](README.md)

---

## 🎉 You're Ready!

1. ✅ Install requirements
2. ✅ Add student ZIPs
3. ✅ Launch dashboard
4. ✅ Click START
5. ✅ Monitor automatically
6. ✅ View reports

**That's it! Happy monitoring! 📊**

---

**Made with ❤️ for Education | No coding required to use!**
