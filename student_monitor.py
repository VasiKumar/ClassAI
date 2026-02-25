"""
AI-Based Sahayak AI with ML Face Recognition
Detects faces, monitors focus, and identifies mobile phone usage
Uses face_recognition library for accurate ML-based face detection
"""

import cv2
import numpy as np
import os
import zipfile
import time
from datetime import datetime
from pathlib import Path
import json
import shutil
import sys
import warnings
import signal
import atexit

# Suppress all warnings during face_recognition import
warnings.filterwarnings('ignore')

# Try to import face_recognition for ML-based recognition
FACE_RECOGNITION_AVAILABLE = False
face_recognition = None

# Redirect stdout/stderr to suppress error messages
class SuppressOutput:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

try:
    with SuppressOutput():
        import face_recognition
        # Test if it actually works
        test_array = np.zeros((100, 100, 3), dtype=np.uint8)
        _ = face_recognition.face_locations(test_array)
    
    FACE_RECOGNITION_AVAILABLE = True
    print("✓ Using ML-based face recognition (face_recognition library)")
except:
    FACE_RECOGNITION_AVAILABLE = False
    face_recognition = None
    print("⚠ Using OpenCV recognition mode (face_recognition not available)")
    print("  This is OK - the system will still work!")
    print("  OpenCV mode uses histogram matching for face recognition.")

class StudentMonitor:
    def __init__(self, student_photos_path=".", check_interval=60, focus_threshold=50, enable_mobile_detection=False):
        """
        Initialize the Student Monitor
        
        Args:
            student_photos_path: Path to student zip files
            check_interval: Monitoring duration in seconds (default: 60)
            focus_threshold: Minimum focus percentage (default: 50%)
            enable_mobile_detection: Enable mobile detection (default: False)
        """
        self.student_photos_path = student_photos_path
        self.check_interval = check_interval
        self.focus_threshold = focus_threshold
        self.student_data = {}
        self.known_faces = {}
        self.known_face_encodings = {}
        self.face_cascade = None
        self.eye_cascade = None
        self.start_time = None
        self.should_stop = False
        self._report_generated = False
        self.enable_mobile_detection = enable_mobile_detection
        self.mobile_detection_boxes = []
        self.stop_file = "monitor_stop.signal"
        self.yolo_model = None
        
        # Clean up old stop file
        if os.path.exists(self.stop_file):
            try:
                os.remove(self.stop_file)
            except:
                pass
        
        # Initialize detection models
        self._load_cascades()
        self._load_yolov8()
        
        # Load and train on student photos from zip files
        print("\n" + "="*70)
        print("TRAINING FACE RECOGNITION MODEL")
        print("="*70)
        self._load_student_photos()
    
    def _load_cascades(self):
        """Load OpenCV cascade classifiers"""
        try:
            # Load Haar Cascade for face detection
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Load Haar Cascade for eye detection (to determine gaze)
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )
            
            print("✓ Successfully loaded detection models")
        except Exception as e:
            print(f"Error loading cascades: {e}")
    
    def _load_yolov8(self):
        """Load YOLOv8l model for mobile phone detection"""
        try:
            from ultralytics import YOLO
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yolov8l.pt')
            if not os.path.exists(model_path):
                model_path = 'yolov8l.pt'  # Try relative path
            self.yolo_model = YOLO(model_path)
            print("\u2713 YOLOv8l loaded for mobile phone detection")
        except Exception as e:
            print(f"\u26a0 Could not load YOLOv8l: {e}")
            print("  Mobile detection will use basic edge detection as fallback")
            self.yolo_model = None
    
    def _extract_nested_zips(self, extract_path):
        """Recursively extract nested zip files (e.g., basistha.zip, sarbeswar.zip)"""
        for item in os.listdir(extract_path):
            item_path = os.path.join(extract_path, item)
            
            # Check if item is a zip file
            if item.lower().endswith('.zip'):
                # Extract student name from zip filename
                student_name = os.path.splitext(item)[0]
                student_folder = os.path.join(extract_path, student_name)
                os.makedirs(student_folder, exist_ok=True)
                
                try:
                    with zipfile.ZipFile(item_path, 'r') as nested_zip:
                        nested_zip.extractall(student_folder)
                    print(f"  📦 Extracted nested zip: {item}")
                except Exception as e:
                    print(f"  ⚠ Could not extract {item}: {e}")
    
    def _load_student_photos(self):
        """
        Extract and load student photos from zip files
        Supports: basistha.zip, sarbeswar.zip, etc. (student name = zip filename)
        Trains ML model on student faces - NO HARDCODED NAMES
        """
        # Create temporary directory for extracted photos
        extract_path = "student_photos_temp"
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path, exist_ok=True)
        
        try:
            # Determine if path is a directory or a file
            if os.path.isdir(self.student_photos_path):
                # Directory: load all .zip files in it
                print(f"📂 Scanning directory: {self.student_photos_path}")
                zip_files = [f for f in os.listdir(self.student_photos_path) if f.lower().endswith('.zip')]
                
                if not zip_files:
                    print(f"❌ Error: No .zip files found in {self.student_photos_path}")
                    print("\nPlease create student zip files like:")
                    print("  - basistha.zip (containing photos of Basistha)")
                    print("  - sarbeswar.zip (containing photos of Sarbeswar)")
                    print("  - etc.")
                    return
                
                print(f"📦 Found {len(zip_files)} student zip files")
                
                # Extract each student's zip file
                for zip_file in zip_files:
                    student_name = os.path.splitext(zip_file)[0]
                    zip_path = os.path.join(self.student_photos_path, zip_file)
                    student_folder = os.path.join(extract_path, student_name)
                    os.makedirs(student_folder, exist_ok=True)
                    
                    print(f"  📦 Extracting {zip_file} → {student_name}/")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(student_folder)
            
            elif os.path.isfile(self.student_photos_path) and self.student_photos_path.lower().endswith('.zip'):
                # Single zip file: extract and check for nested zips
                print(f"📂 Extracting {self.student_photos_path}...")
                with zipfile.ZipFile(self.student_photos_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                
                # Handle nested zip files
                self._extract_nested_zips(extract_path)
            else:
                print(f"❌ Error: {self.student_photos_path} is not a valid directory or zip file!")
                return
            
            # Recursively find all image files
            print("\n🔍 Scanning for student photos...")
            students_trained = 0
            
            for root, dirs, files in os.walk(extract_path):
                for filename in files:
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                        # Determine student name from folder or filename
                        img_path = os.path.join(root, filename)
                        
                        # Try to get student name from parent folder
                        parent_folder = os.path.basename(root)
                        if parent_folder == "student_photos_temp":
                            # Use filename if directly in temp folder
                            student_name = os.path.splitext(filename)[0]
                        else:
                            # Use folder name (for nested zips like basistha.zip)
                            student_name = parent_folder
                        
                        # Load and train on this image
                        success = self._train_on_image(img_path, student_name)
                        if success:
                            students_trained += 1
            
            total_students = len(self.known_face_encodings) if FACE_RECOGNITION_AVAILABLE else len(self.known_faces)
            print(f"\n{'='*70}")
            print(f"✅ MODEL TRAINED SUCCESSFULLY")
            print(f"{'='*70}")
            print(f"📊 Total students registered: {total_students}")
            print(f"📸 Total photos processed: {students_trained}")
            print(f"🤖 Recognition method: {'ML-based (face_recognition)' if FACE_RECOGNITION_AVAILABLE else 'OpenCV histogram'}")
            print(f"{'='*70}\n")
        
        except Exception as e:
            print(f"❌ Error loading student photos: {e}")
    
    def _train_on_image(self, img_path, student_name):
        """
        Train the model on a single image
        
        Args:
            img_path: Path to image file
            student_name: Name of the student (from folder/filename)
        
        Returns:
            Boolean indicating success
        """
        try:
            if FACE_RECOGNITION_AVAILABLE:
                # Use ML-based face recognition
                try:
                    image = face_recognition.load_image_file(img_path)
                    face_encodings = face_recognition.face_encodings(image)
                    
                    if len(face_encodings) > 0:
                        # Store the first face encoding found
                        if student_name not in self.known_face_encodings:
                            self.known_face_encodings[student_name] = []
                            self._initialize_student_data(student_name)
                        
                        self.known_face_encodings[student_name].append(face_encodings[0])
                        print(f"  ✓ Trained on: {student_name} ({os.path.basename(img_path)})")
                        return True
                    else:
                        print(f"  ⚠ No face detected in: {os.path.basename(img_path)}")
                        return False
                except Exception as fr_error:
                    # If face_recognition fails, fall back to OpenCV
                    print(f"  ⚠ ML method failed, using OpenCV for: {os.path.basename(img_path)}")
                    if "face_recognition_models" in str(fr_error):
                        print("  Note: face_recognition_models issue detected, using OpenCV mode for this session")
                    # Fall through to OpenCV method below
            
            # OpenCV fallback method
            img = cv2.imread(img_path)
            if img is not None:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    face_img = img[y:y+h, x:x+w]
                    
                    if student_name not in self.known_faces:
                        self.known_faces[student_name] = []
                        self._initialize_student_data(student_name)
                    
                    self.known_faces[student_name].append(face_img)
                    print(f"  ✓ Trained on: {student_name} ({os.path.basename(img_path)})")
                    return True
                return False
        except Exception as e:
            print(f"  ⚠ Error processing {os.path.basename(img_path)}: {e}")
            return False
    
    def _initialize_student_data(self, student_name):
        """Initialize tracking data for a student"""
        self.student_data[student_name] = {
            'focused_count': 0,
            'unfocused_count': 0,
            'mobile_detected': 0,
            'mobile_times': [],  # Track when mobile was detected
            'total_checks': 0,
            'alerts': []
        }
    
    def detect_gaze(self, face_region):
        """
        Detect if person is looking at camera by detecting eyes
        
        Args:
            face_region: Cropped face image region
        
        Returns:
            Boolean indicating if person is focused (looking at camera)
        """
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray_face, 1.1, 5)
        
        # If both eyes are visible, person is likely looking at camera
        if len(eyes) >= 2:
            return True
        return False
    
    def detect_mobile(self, frame):
        """
        Detect mobile phone in frame using YOLOv8l.
        Falls back to basic edge detection if YOLOv8l is unavailable.
        
        Args:
            frame: Video frame to analyze
        
        Returns:
            Boolean indicating if mobile phone detected
        """
        if not self.enable_mobile_detection:
            return False
        if self.yolo_model is not None:
            return self._detect_mobile_yolov8(frame)
        return self._detect_mobile_basic(frame)
    
    def _detect_mobile_yolov8(self, frame):
        """Detect mobile phone using YOLOv8l (COCO class 67: cell phone)"""
        try:
            self.mobile_detection_boxes = []
            results = self.yolo_model(frame, verbose=False, conf=0.25)
            detected = False
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    if cls_id == 67:  # COCO class 67 = cell phone
                        detected = True
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        self.mobile_detection_boxes.append({
                            'box': (x1, y1, x2 - x1, y2 - y1),
                            'confidence': confidence,
                            'class': 'cell phone'
                        })
                        print(f"\U0001f4f1 MOBILE DETECTED (YOLOv8l)! Confidence: {confidence:.2f}")
            return detected
        except Exception as e:
            print(f"YOLOv8l detection error: {e}")
            return self._detect_mobile_basic(frame)
    
    def _detect_mobile_basic(self, frame):
        """Basic mobile phone detection using edge detection (fallback)"""
        # NOTE: Basic detection has high false positive rate
        # It can detect books, bottles, hands, etc. as phones
        # Used only as fallback when YOLOv8l is unavailable
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply blur to reduce noise
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detect rectangular objects that might be phones
        edges = cv2.Canny(gray, 100, 200)  # Higher thresholds to reduce false positives
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        phone_candidates = 0
        for contour in contours:
            # Filter small contours
            if cv2.contourArea(contour) < 2000:  # Minimum area threshold
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = h / float(w) if w > 0 else 0
            
            # Stricter phone-like aspect ratio and size
            # Phones are typically 1.6-2.2 aspect ratio
            if 1.6 < aspect_ratio < 2.2 and 60 < w < 150 and 120 < h < 350:
                phone_candidates += 1
        
        # Only return True if multiple candidates detected (reduces single-object false positives)
        return phone_candidates >= 2
    
    def match_face(self, face_img, face_location=None):
        """
        Match detected face with known student faces using ML
        
        Args:
            face_img: Detected face image (for OpenCV method)
            face_location: Face location tuple (for face_recognition method)
        
        Returns:
            Student name if matched, else "Unknown"
        """
        if FACE_RECOGNITION_AVAILABLE and face_location is not None:
            # Use ML-based face recognition (more accurate)
            try:
                # Get encoding for this face
                rgb_frame = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB) if len(face_img.shape) == 3 else face_img
                face_encodings = face_recognition.face_encodings(rgb_frame, [face_location])
                
                if len(face_encodings) == 0:
                    return "Unknown"
                
                face_encoding = face_encodings[0]
                
                # Compare with all known students
                best_match = "Unknown"
                best_distance = 0.6  # Threshold for matching (lower is stricter)
                
                for student_name, known_encodings in self.known_face_encodings.items():
                    # Compare with all training images of this student
                    distances = face_recognition.face_distance(known_encodings, face_encoding)
                    min_distance = min(distances) if len(distances) > 0 else 1.0
                    
                    if min_distance < best_distance:
                        best_distance = min_distance
                        best_match = student_name
                
                return best_match
            except Exception as e:
                print(f"  ⚠ Face matching error: {e}")
                return "Unknown"
        else:
            # Fallback to OpenCV histogram method
            best_match = "Unknown"
            best_score = float('inf')
            
            face_resized = cv2.resize(face_img, (100, 100))
            
            for student_name, known_faces in self.known_faces.items():
                for known_face in known_faces:
                    known_resized = cv2.resize(known_face, (100, 100))
                    
                    # Calculate similarity using histogram comparison
                    hist_face = cv2.calcHist([face_resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    hist_known = cv2.calcHist([known_resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    
                    hist_face = cv2.normalize(hist_face, hist_face).flatten()
                    hist_known = cv2.normalize(hist_known, hist_known).flatten()
                    
                    score = cv2.compareHist(hist_face, hist_known, cv2.HISTCMP_CHISQR)
                    
                    if score < best_score:
                        best_score = score
                        best_match = student_name
            
            # Threshold for matching
            if best_score < 500:
                return best_match
            return "Unknown"
    
    def process_frame(self, frame):
        """
        Process video frame: detect faces, check focus, detect mobile phones
        Shows rectangles for both faces and phones
        """
        # STEP 1: Detect mobile phones in entire frame (if enabled)
        mobile_detected_in_frame = False
        if self.enable_mobile_detection:
            mobile_detected_in_frame = self.detect_mobile(frame)
            
            # Draw rectangles around detected phones
            if mobile_detected_in_frame and hasattr(self, 'mobile_detection_boxes'):
                for detection in self.mobile_detection_boxes:
                    x, y, w, h = detection['box']
                    confidence = detection['confidence']
                    
                    # Draw RED rectangle around phone
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 4)
                    
                    # Add label
                    label = f"MOBILE {confidence:.2f}"
                    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                    cv2.rectangle(frame, (x, y - text_size[1] - 10), 
                                (x + text_size[0], y), (0, 0, 255), -1)
                    cv2.putText(frame, label, (x, y - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # STEP 2: Detect and track student faces
        if FACE_RECOGNITION_AVAILABLE:
            # ML-based face recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            
            for face_location in face_locations:
                top, right, bottom, left = face_location
                face_region = frame[top:bottom, left:right]
                
                # Match student
                student_name = self.match_face(rgb_frame, face_location)
                
                if student_name != "Unknown" and student_name in self.student_data:
                    # Check focus
                    is_focused = self.detect_gaze(face_region)
                    
                    # Update stats
                    self.student_data[student_name]['total_checks'] += 1
                    
                    if is_focused:
                        self.student_data[student_name]['focused_count'] += 1
                        status_text = f"{student_name}: Focused"
                        color = (0, 255, 0)  # Green
                    else:
                        self.student_data[student_name]['unfocused_count'] += 1
                        status_text = f"{student_name}: Not Focused"
                        color = (0, 165, 255)  # Orange
                    
                    # If mobile detected in frame, add to this student's record
                    if mobile_detected_in_frame:
                        self.student_data[student_name]['mobile_detected'] += 1
                        current_time = datetime.now().strftime("%H:%M:%S")
                        self.student_data[student_name]['mobile_times'].append(current_time)
                    
                    # Draw GREEN/ORANGE rectangle around face
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
                    
                    # Draw label
                    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    cv2.rectangle(frame, (left, top - text_size[1] - 10), 
                                (left + text_size[0], top), color, -1)
                    cv2.putText(frame, status_text, (left, top - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            # OpenCV face detection (fallback)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                face_region = frame[y:y+h, x:x+w]
                student_name = self.match_face(face_region)
                
                if student_name != "Unknown" and student_name in self.student_data:
                    # Check focus
                    is_focused = self.detect_gaze(face_region)
                    
                    # Update stats
                    self.student_data[student_name]['total_checks'] += 1
                    
                    if is_focused:
                        self.student_data[student_name]['focused_count'] += 1
                        status_text = f"{student_name}: Focused"
                        color = (0, 255, 0)  # Green
                    else:
                        self.student_data[student_name]['unfocused_count'] += 1
                        status_text = f"{student_name}: Not Focused"
                        color = (0, 165, 255)  # Orange
                    
                    # If mobile detected in frame, add to this student's record
                    if mobile_detected_in_frame:
                        self.student_data[student_name]['mobile_detected'] += 1
                        current_time = datetime.now().strftime("%H:%M:%S")
                        self.student_data[student_name]['mobile_times'].append(current_time)
                    
                    # Draw GREEN/ORANGE rectangle around face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
                    
                    # Draw label
                    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    cv2.rectangle(frame, (x, y - text_size[1] - 10), 
                                (x + text_size[0], y), color, -1)
                    cv2.putText(frame, status_text, (x, y - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # STEP 3: Display timer
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            time_text = f"Time: {elapsed}s / {self.check_interval}s"
            cv2.rectangle(frame, (5, 5), (350, 45), (0, 0, 0), -1)
            cv2.putText(frame, time_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        return frame
    
    def calculate_focus_percentage(self, student_name):
        """Calculate focus percentage for a student"""
        data = self.student_data[student_name]
        total = data['total_checks']
        
        if total == 0:
            return 0
        
        focus_percentage = (data['focused_count'] / total) * 100
        return round(focus_percentage, 2)
    
    def generate_report(self):
        """
        Generate comprehensive focus report for all students
        MOBILE REPORTS shown here at END OF SESSION (if enabled)
        """
        print("\n" + "="*70)
        print("STUDENT FOCUS MONITORING REPORT - END OF SESSION")
        print("="*70)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Monitoring Duration: {self.check_interval} seconds")
        print(f"Focus Threshold: {self.focus_threshold}%")
        print(f"Mobile Detection: {'Enabled' if self.enable_mobile_detection else 'Disabled'}")
        print("="*70)
        
        # Show mobile phone reports only if feature is enabled
        if self.enable_mobile_detection:
            print("\n" + "🚨 MOBILE PHONE USAGE REPORTS 🚨")
            print("="*70)
            mobile_reports = []
            for student_name, data in self.student_data.items():
                if data['mobile_detected'] > 0:
                    mobile_reports.append((student_name, data))
            
            if mobile_reports:
                for student_name, data in mobile_reports:
                    print(f"\n⚠️  {student_name} REPORT!")
                    print(f"   Mobile detected: {data['mobile_detected']} times")
                    print(f"   Times detected:")
                    for time_detected in data['mobile_times']:
                        print(f"      - {time_detected}")
            else:
                print("\n✓ No mobile phone usage detected during session")
        
        print("\n" + "="*70)
        print("📊 INDIVIDUAL STUDENT FOCUS REPORTS")
        print("="*70)
        
        for student_name, data in self.student_data.items():
            focus_percentage = self.calculate_focus_percentage(student_name)
            
            # Determine status based on threshold
            if focus_percentage >= self.focus_threshold:
                status = "✓ GOOD FOCUS"
                status_symbol = "✓"
            else:
                status = "✗ NEEDS IMPROVEMENT"
                status_symbol = "✗"
            
            print(f"\n{status_symbol} Student: {student_name}")
            print(f"   Focus Percentage: {focus_percentage}% {status}")
            print(f"   Focused Count: {data['focused_count']}")
            print(f"   Unfocused Count: {data['unfocused_count']}")
            print(f"   Total Checks: {data['total_checks']}")
            
            if self.enable_mobile_detection and data['mobile_detected'] > 0:
                print(f"   📱 Mobile Usage: {data['mobile_detected']} times")
        
        print("\n" + "="*70)
        
        # Save report to file
        self._save_report()
        self._report_generated = True  # Mark that report was generated
    
    def _save_report(self):
        """Save report to JSON file"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'duration': self.check_interval,
                'threshold': self.focus_threshold,
                'mobile_detection_enabled': self.enable_mobile_detection,
                'students': {}
            }
            
            for student_name, data in self.student_data.items():
                try:
                    report['students'][student_name] = {
                        'focus_percentage': self.calculate_focus_percentage(student_name),
                        'focused_count': data['focused_count'],
                        'unfocused_count': data['unfocused_count'],
                        'total_checks': data['total_checks'],
                        'mobile_detected': data['mobile_detected'],
                        'mobile_times': data['mobile_times'],
                        'alerts': data['alerts']
                    }
                except Exception as e:
                    print(f"⚠️  Error processing student {student_name}: {e}")
                    # Add minimal data
                    report['students'][student_name] = {
                        'focus_percentage': 0.0,
                        'focused_count': 0,
                        'unfocused_count': 0,
                        'total_checks': 0,
                        'mobile_detected': 0,
                        'mobile_times': [],
                        'alerts': []
                    }
            
            report_filename = f"focus_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path = os.path.abspath(report_filename)
            
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=4)
            
            print(f"\n✅ Report saved successfully!")
            print(f"   File: {report_filename}")
            print(f"   Path: {report_path}")
            print(f"   Students: {len(report['students'])}")
            
            return report_filename
            
        except Exception as e:
            print(f"\n❌ ERROR saving report: {e}")
            print(f"   Attempted path: {os.getcwd()}")
            
            # Try to save to a backup location
            try:
                backup_filename = f"focus_report_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                import tempfile
                backup_path = os.path.join(tempfile.gettempdir(), backup_filename)
                with open(backup_path, 'w') as f:
                    json.dump(report, f, indent=4)
                print(f"⚠️  Backup report saved to: {backup_path}")
                return backup_path
            except Exception as backup_error:
                print(f"❌ Backup save also failed: {backup_error}")
                return None
    
    def signal_handler(self, signum, frame):
        """Handle termination signals gracefully"""
        print(f"\n\n⚠️  Received termination signal ({signum}). Generating report...")
        self.should_stop = True
    
    def _check_stop_signal(self):
        """Check if stop signal file exists (Windows-compatible shutdown)"""
        if os.path.exists(self.stop_file):
            try:
                os.remove(self.stop_file)
            except:
                pass
            return True
        return False
    
    def start_monitoring(self, camera_index=0):
        """
        Start real-time monitoring using webcam
        
        Args:
            camera_index: Camera device index (default: 0 for primary webcam)
        """
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Register cleanup function to run on exit
        atexit.register(self._cleanup_and_report)
        
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        print("\n" + "="*70)
        print("STARTING STUDENT FOCUS MONITOR")
        print("="*70)
        print(f"Monitoring {len(self.known_faces)} students")
        print(f"Check interval: {self.check_interval} seconds")
        print(f"Focus threshold: {self.focus_threshold}%")
        if self.enable_mobile_detection:
            if self.yolo_model is not None:
                print(f"Mobile Detection: YOLOv8l (confidence > 0.25)")
            else:
                print(f"Mobile Detection: Basic edge detection (YOLOv8l unavailable)")
        else:
            print(f"Mobile Detection: Disabled")
        print("\nPress 'q' to quit and generate report")
        print("="*70 + "\n")
        
        self.start_time = time.time()
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("Error: Failed to capture frame")
                    break
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Display frame
                cv2.imshow('Student Focus Monitor', processed_frame)
                
                frame_count += 1
                
                # Check if monitoring duration elapsed
                elapsed_time = time.time() - self.start_time
                if elapsed_time >= self.check_interval:
                    print("\n✓ Monitoring period completed!")
                    break
                
                # Check for quit command
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n✓ Monitoring stopped by user (Q pressed)")
                    break
                
                # Check for file-based stop signal (Windows-compatible)
                if self._check_stop_signal():
                    print("\n✓ Monitoring stopped by dashboard request")
                    self.should_stop = True
                    break
                
                # Check if external stop requested
                if self.should_stop:
                    print("\n✓ Monitoring stopped by external signal")
                    break
        
        finally:
            print("\n🔄 Cleaning up and generating report...")
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()
            
            # Generate report
            self.generate_report()
            print("✅ Cleanup completed!")
    
    def _cleanup_and_report(self):
        """Ensure report is generated on exit"""
        if hasattr(self, 'student_data') and self.student_data and hasattr(self, '_report_generated') and not self._report_generated:
            print("\n📊 Emergency cleanup: Generating final report...")
            try:
                self.generate_report()
                self._report_generated = True
            except Exception as e:
                print(f"⚠️  Error generating emergency report: {e}")
                import traceback
                traceback.print_exc()


def main():
    """Main function to run the student monitor"""
    import argparse
    import json
    
    print("\n" + "="*70)
    print("Sahayak AI")
    print("="*70)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Sahayak AI')
    parser.add_argument('--duration', type=int, help='Monitoring duration in seconds')
    parser.add_argument('--threshold', type=int, help='Focus threshold percentage')
    parser.add_argument('--enable-mobile-detection', action='store_true', help='Enable mobile phone detection')
    args = parser.parse_args()
    
    # Try to load config from Streamlit app
    config_file = 'monitor_config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                print(f"\n✓ Loaded configuration from {config_file}")
        except:
            config = {}
    else:
        config = {}
    
    # Configuration (priority: CLI args > config file > defaults)
    STUDENT_PHOTOS_PATH = "sample_student_photos"  # Folder containing student zip files
    CHECK_INTERVAL = args.duration if args.duration else config.get('duration', 300)  # Default: 5 minutes
    FOCUS_THRESHOLD = args.threshold if args.threshold else config.get('threshold', 50)  # Default: 50%
    ENABLE_MOBILE_DETECTION = args.enable_mobile_detection if args.enable_mobile_detection else config.get('enable_mobile_detection', False)
    
    # Create monitor instance
    monitor = StudentMonitor(
        student_photos_path=STUDENT_PHOTOS_PATH,
        check_interval=CHECK_INTERVAL,
        focus_threshold=FOCUS_THRESHOLD,
        enable_mobile_detection=ENABLE_MOBILE_DETECTION
    )
    
    # Start monitoring
    monitor.start_monitoring()


if __name__ == "__main__":
    main()
