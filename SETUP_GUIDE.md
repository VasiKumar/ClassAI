# 🎓 Student Focus Monitor - Quick Setup Guide

## 📦 How to Prepare Student Photos

The system uses **individual ZIP files** for each student. Each ZIP filename becomes the student's name!

### ✅ Correct Setup

Create one ZIP file per student, named after them:

```
Your Project Folder/
├── basistha.zip         ← Photos of Basistha
├── sarbeswar.zip        ← Photos of Sarbeswar
├── student3.zip         ← Photos of Student3
└── student_monitor.py   ← The main program
```

**Inside each ZIP:**
```
basistha.zip
├── photo1.jpg
├── photo2.jpg
└── photo3.png

sarbeswar.zip
├── image1.jpg
└── image2.png
```

### 🚀 That's It!

Just run:
```bash
python student_monitor.py
```

The system will:
1. ✅ Find all .zip files (basistha.zip, sarbeswar.zip)
2. ✅ Extract student name from filename (basistha, sarbeswar)
3. ✅ Train on photos inside each ZIP
4. ✅ **NO HARDCODED NAMES** - completely dynamic!

---

## 🎯 Three Ways to Organize

### Option 1: Current Directory (EASIEST) ⭐
Put ZIP files directly in project folder:
```
D:\educational website\
├── basistha.zip
├── sarbeswar.zip
└── student_monitor.py
```

**Code:** (already set up!)
```python
STUDENT_PHOTOS_PATH = "."  # Current directory
```

---

### Option 2: Subfolder
Put ZIP files in a subfolder:
```
D:\educational website\
├── students/
│   ├── basistha.zip
│   └── sarbeswar.zip
└── student_monitor.py
```

**Code:** Edit main():
```python
STUDENT_PHOTOS_PATH = "students"
```

---

### Option 3: Master ZIP (nested)
Create one ZIP containing all student ZIPs:
```
all_students.zip
├── basistha.zip
└── sarbeswar.zip
```

**Code:** Edit main():
```python
STUDENT_PHOTOS_PATH = "all_students.zip"
```

---

## 📸 Photo Tips

- **2-5 photos per student** for best accuracy
- **Clear, well-lit photos**
- **Face clearly visible**
- **Different angles** help recognition
- **JPG, PNG, or BMP** formats

---

## ▶️ Running the System

### 1. Make sure you have zip files:
```
basistha.zip
sarbeswar.zip
```

### 2. Run the system:
```bash
python student_monitor.py
```

### 3. You'll see:
```
======================================================================
TRAINING FACE RECOGNITION MODEL
======================================================================
📂 Scanning directory: .
📦 Found 2 student zip files
  📦 Extracting basistha.zip → basistha/
  📦 Extracting sarbeswar.zip → sarbeswar/

🔍 Scanning for student photos...
  ✓ Trained on: basistha (photo1.jpg)
  ✓ Trained on: basistha (photo2.jpg)
  ✓ Trained on: sarbeswar (image1.jpg)

======================================================================
✅ MODEL TRAINED SUCCESSFULLY
======================================================================
📊 Total students registered: 2
📸 Total photos processed: 3
```

### 4. Monitor Students:
- Watch the video feed
- System tracks focus automatically
- Press 'q' to stop

### 5. View Report (at end):
```
🚨 MOBILE PHONE USAGE REPORTS 🚨
======================================================================

⚠️  basistha REPORT!
   Mobile detected: 2 times
   Times detected:
      - 14:25:15
      - 14:27:42

======================================================================
📊 INDIVIDUAL STUDENT FOCUS REPORTS
======================================================================

✓ Student: basistha
   Focus Percentage: 68.5% ✓ GOOD FOCUS

✓ Student: sarbeswar
   Focus Percentage: 82.3% ✓ GOOD FOCUS
```

---

## ⚙️ Configuration

Edit these in `student_monitor.py`:

```python
# Where to find student ZIP files
STUDENT_PHOTOS_PATH = "."        # Current directory

# How long to monitor (in seconds)
CHECK_INTERVAL = 300             # 5 minutes

# Minimum focus required
FOCUS_THRESHOLD = 50             # 50%
```

---

## ❓ Common Questions

**Q: Do I need a file called "name.zip"?**  
A: NO! 😂 Use **basistha.zip**, **sarbeswar.zip**, etc.

**Q: Can the ZIP be called anything?**  
A: YES! The filename becomes the student name. `basistha.zip` → student "basistha"

**Q: Multiple photos per student?**  
A: YES! Put 2-5 photos inside each student's ZIP for better accuracy.

**Q: Can I add more students later?**  
A: YES! Just add new ZIP files and run again.

**Q: What if I don't have face_recognition installed?**  
A: No problem! System automatically uses OpenCV mode (still works great!)

---

## 🎉 Examples

### Example 1: Class with 3 students
```
project/
├── john.zip
├── mary.zip
├── peter.zip
└── student_monitor.py
```
Run: `python student_monitor.py`

### Example 2: Custom folder
```
project/
├── my_students/
│   ├── alice.zip
│   └── bob.zip
└── student_monitor.py
```
Edit code: `STUDENT_PHOTOS_PATH = "my_students"`

---

## 🚨 Troubleshooting

**No faces detected?**
- Ensure photos show faces clearly
- Check photo quality and lighting

**Student name wrong?**
- Check ZIP filename: `basistha.zip` → name is "basistha"
- Rename ZIP file to correct name

**System doesn't find ZIPs?**
- Ensure ZIPs are in the correct folder
- Check `STUDENT_PHOTOS_PATH` setting

---

**Ready to monitor? Just create your student ZIPs and run!** 🚀
