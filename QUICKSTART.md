# 🚀 QUICK START GUIDE

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Prepare Student Photos

1. Collect clear photos of all students (one photo per student)
2. Name each photo with the student's name:
   - `Basistha.jpg`
   - `Student1.png`
   - `Student2.jpg`
   
3. Put all photos in a folder
4. Compress the folder to create `name.zip`
5. Place `name.zip` in the project root directory

## Step 3: Test Your Setup
```bash
python setup_test.py
```

This will verify:
- Python version
- Dependencies
- Camera access
- Detection models
- Student data file

## Step 4: Start Monitoring

### Default Configuration (5 minutes, 50% threshold)
```bash
python student_monitor.py
```

### Quick Test (1 minute)
```bash
python examples.py
# Select option 1
```

### Custom Duration
Edit `student_monitor.py` and change:
```python
CHECK_INTERVAL = 300  # Change to your desired duration in seconds
```

### Custom Threshold
Edit `student_monitor.py` and change:
```python
FOCUS_THRESHOLD = 50  # Change to your desired percentage
```

## Step 5: View Reports

After monitoring completes, you'll see:
1. Console output with detailed statistics
2. A JSON file: `focus_report_YYYYMMDD_HHMMSS.json`

## Common Durations

- **Quiz**: 600 seconds (10 minutes)
- **Lecture**: 2700 seconds (45 minutes)
- **Class**: 3600 seconds (1 hour)
- **Exam**: 7200 seconds (2 hours)

## Quick Example Scenarios

### Scenario 1: 10-minute Quiz (Strict)
```python
monitor = StudentMonitor("name.zip", check_interval=600, focus_threshold=80)
monitor.start_monitoring()
```

### Scenario 2: 1-hour Exam (Very Strict)
```python
monitor = StudentMonitor("name.zip", check_interval=3600, focus_threshold=85)
monitor.start_monitoring()
```

### Scenario 3: 45-minute Lecture (Moderate)
```python
monitor = StudentMonitor("name.zip", check_interval=2700, focus_threshold=50)
monitor.start_monitoring()
```

## Keyboard Controls

- **'q'**: Quit monitoring and generate report immediately

## Understanding the Output

### During Monitoring:
- **Green box**: Student is focused
- **Orange box**: Student is not focused
- **Red box + "REPORT!"**: Mobile phone detected

### Report Interpretation:
- **✓ GOOD FOCUS**: Focus percentage >= threshold
- **✗ NEEDS IMPROVEMENT**: Focus percentage < threshold
- **Mobile Detected**: Number of times mobile phone was detected

## Tips for Best Results

1. **Good Lighting**: Ensure adequate lighting for face detection
2. **Camera Position**: Position camera to capture all students
3. **Clear Photos**: Use high-quality, clear photos for training
4. **Stable Connection**: Ensure stable camera connection
5. **Test First**: Always run `setup_test.py` before actual monitoring

## Troubleshooting

### Camera not working?
```bash
# Try different camera index
monitor.start_monitoring(camera_index=1)  # or 2, 3, etc.
```

### Poor face recognition?
- Use clearer student photos
- Ensure good lighting during monitoring
- Photos should show full face clearly

### "name.zip not found"?
- Verify the file is in the project root
- Check the filename is exactly `name.zip`
- Or change ZIP_FILE in the code to your filename

## Next Steps

✓ Test the system with `setup_test.py`
✓ Run a quick 1-minute test with `examples.py`
✓ Adjust settings for your needs
✓ Start monitoring your class!

---

**For more details, see [README.md](README.md)**
