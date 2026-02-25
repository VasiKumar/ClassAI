# 🔍 View Reports Troubleshooting Guide

## Problem: Reports Not Showing

If you don't see your reports in the "View Reports" page, follow these steps:

### Step 1: Check Debug Info

1. Go to **"📈 View Reports"** page
2. Expand the **"🔧 Debug Info"** section
3. Look at:
   - **Reports Directory**: Where reports should be saved
   - **Current Working Dir**: Where Streamlit is running from
   - **All JSON files found**: List of all JSON files

### Step 2: Verify Report Generation

Reports are named: `focus_report_YYYYMMDD_HHMMSS.json`

Example: `focus_report_20260225_192440.json`

**Check if:**
- The file exists in the Reports Directory shown
- The file starts with `focus_report_`
- The file ends with `.json`

### Step 3: Common Issues & Solutions

#### Issue 1: No Reports Found
**Symptoms:**
- "No reports available yet" message
- Empty reports list

**Solutions:**
1. **Complete a monitoring session first**:
   - Go to "Start Monitoring"
   - Click "START MONITORING SESSION"
   - Wait for session to end OR click "END SESSION NOW"
   - Check "View Reports" again

2. **Check if monitoring is still active**:
   - Look for 🟢 "Session Active" in sidebar
   - If active, wait for it to complete
   - Report generates AFTER session ends

3. **Create test report**:
   - In Debug Info section
   - Click "🧪 Create Test Report"
   - This creates a sample report
   - If test report appears, system is working

#### Issue 2: Report Was There, Now Gone
**Possible causes:**
1. **Accidentally deleted**
   - Reports can be deleted from dashboard
   - Check if you clicked "Delete Report" or "Delete All"

2. **Wrong directory**
   - Dashboard looking in different location
   - Check "Reports Directory" in Debug Info
   - Compare with where monitoring saved it

3. **File permissions**
   - Windows may block file access
   - Run dashboard as Administrator

#### Issue 3: Monitoring Completed But No Report
**Check:**
1. **Process actually completed?**
   - In Debug Info, check process status
   - Should say "ended with exit code"
   - If still "running", it didn't finish

2. **Report generation failed?**
   - Check the monitoring console window
   - Look for "✓ Report saved to:" message
   - See if any errors appeared

3. **Report in different location?**
   - The monitoring console shows full path
   - Compare with dashboard Reports Directory
   - They must match!

### Step 4: Manual Check

Open File Explorer and navigate to:
```
D:\educational website\
```

Look for files named: `focus_report_*.json`

**If you find reports:**
- They're in the right place
- Click "🔄 Refresh List" in dashboard
- Turn on "Auto" refresh checkbox

**If no reports found:**
- Monitoring didn't complete properly
- Or reports were deleted
- Run a new session

### Step 5: Test Report Generation

1. Go to "View Reports" page
2. Expand "Debug Info"
3. Click "🧪 Create Test Report"
4. A fake report will be created
5. It should appear in the list immediately

If test report appears: **System is working! Run real monitoring session.**

If test report doesn't appear: **File system issue - check permissions.**

## Quick Checklist

Before reporting an issue:

- [ ] Completed at least one full monitoring session
- [ ] Session ended (not still active)
- [ ] Checked Debug Info section
- [ ] Tried "Refresh List" button
- [ ] Tried creating test report
- [ ] Verified Reports Directory path
- [ ] Looked in File Explorer for JSON files
- [ ] Ran dashboard from correct directory

## How Reports Are Generated

1. **You start monitoring** → `python student_monitor.py` runs
2. **Session runs** → Tracks students
3. **Session ends** → Either:
   - Time expires
   - You click "END SESSION NOW"
   - You press Ctrl+C in console
   - You close monitoring window
4. **Report generates** → Saved as `focus_report_<timestamp>.json`
5. **Dashboard shows it** → In "View Reports" page

## Directory Structure

```
D:\educational website\
├── streamlit_app.py        <- Dashboard
├── student_monitor.py      <- Monitoring system
├── focus_report_*.json     <- Reports saved HERE
├── monitor_config.json     <- Configuration
└── sample_student_photos/  <- Student ZIPs
```

## Refresh Methods

**Manual Refresh:**
- Click "🔄 Refresh List" button

**Auto Refresh:**
- Check "Auto" checkbox
- Page refreshes every 5 seconds automatically

**Page Reload:**
- Press F5 in browser
- Or Ctrl+R

## Creating Reports Manually

If dashboard isn't showing reports, you can create one manually:

Run monitoring from terminal:
```bash
cd "D:\educational website"
python student_monitor.py --duration 10 --threshold 50
```

Wait for it to complete (10 seconds). Check for message:
```
✓ Report saved to: focus_report_20260225_HHMMSS.json
```

Then refresh dashboard.

## Still Having Issues?

1. **Close all terminals and dashboards**
2. **Relaunch dashboard**: `launch_dashboard.bat`
3. **Go to Start Monitoring**
4. **Set duration: 1 minute** (for testing)
5. **Click START**
6. **Wait 1 full minute** (don't close anything)
7. **Go to View Reports**
8. **Click Refresh**

The report should appear. If not:
- Check the monitoring console for errors
- Look at Debug Info for file paths
- Verify students are registered (ZIPs in folder)

## Contact Support

If none of this works, provide:
- Screenshot of Debug Info section
- Reports Directory path shown
- File Explorer screenshot of that directory
- Any error messages from console

---

**Quick Fix:** Click "🧪 Create Test Report" to verify system is working!
