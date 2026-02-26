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
import queue
import threading
from datetime import datetime
from pathlib import Path
import json
import shutil
import sys
import warnings
import signal
import atexit

# ── Whisper speech-to-text ──────────────────────────────────────────────────
WHISPER_AVAILABLE = False
_whisper_lib = None
try:
    import whisper as _whisper_lib
    WHISPER_AVAILABLE = True
except ImportError:
    pass

_AUDIO_AVAILABLE = False
try:
    import sounddevice as _sd
    _AUDIO_AVAILABLE = True
except ImportError:
    pass

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

# ── GPU face recognition via facenet-pytorch (primary) ─────────────────────
CUDA_AVAILABLE = False
FACE_RECOGNITION_MODEL = "hog"
FACENET_AVAILABLE = False
FACENET_DEVICE = None

try:
    import torch
    from facenet_pytorch import MTCNN, InceptionResnetV1
    FACENET_DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    CUDA_AVAILABLE = (FACENET_DEVICE.type == 'cuda')
    FACENET_AVAILABLE = True
    if CUDA_AVAILABLE:
        print(f"✓ GPU detected: {torch.cuda.get_device_name(0)} — face training & recognition on GPU")
        FACE_RECOGNITION_MODEL = "cnn"
    else:
        print("  facenet-pytorch loaded (CPU) — no CUDA GPU found")
except Exception as _fe:
    FACENET_AVAILABLE = False
    FACENET_DEVICE = None
    # Fallback: try dlib CUDA
    try:
        import dlib
        CUDA_AVAILABLE = dlib.DLIB_USE_CUDA
        FACE_RECOGNITION_MODEL = "cnn" if CUDA_AVAILABLE else "hog"
        if CUDA_AVAILABLE:
            print("✓ GPU (dlib CUDA) — using CNN face model")
    except Exception:
        pass

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
        self.facenet_embeddings = {}   # GPU embeddings keyed by student name
        self.face_cascade = None
        self.eye_cascade = None
        self.mtcnn = None              # facenet-pytorch face detector
        self.resnet = None             # facenet-pytorch encoder (GPU)
        self.start_time = None
        self.should_stop = False
        self._report_generated = False
        self.enable_mobile_detection = enable_mobile_detection
        self.mobile_detection_boxes = []
        self.stop_file = "monitor_stop.signal"
        self.yolo_model = None
        # Whisper / audio transcription
        self.whisper_model = None
        self._audio_stop_event = None
        self._audio_thread = None
        self._whisper_session_id = None
        
        # Clean up old stop file
        if os.path.exists(self.stop_file):
            try:
                os.remove(self.stop_file)
            except:
                pass
        
        # Initialize detection models
        self._load_cascades()
        self._load_yolov8()
        self._load_facenet()  # GPU face recognition model
        
        # Load and train on student photos from zip files
        print("\n" + "="*70)
        print("TRAINING FACE RECOGNITION MODEL")
        print("="*70)
        self._load_student_photos()
    
    # ── Whisper helpers ────────────────────────────────────────────────────
    def _load_whisper(self):
        """Load Whisper base model on GPU right when the camera opens."""
        if not WHISPER_AVAILABLE:
            print("⚠ Whisper not available — pip install openai-whisper sounddevice")
            return
        if not _AUDIO_AVAILABLE:
            print("⚠ sounddevice not available — pip install sounddevice")
            return
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            gpu_label = f"GPU ({torch.cuda.get_device_name(0)})" if device == "cuda" else "CPU"
            print(f"⏳ Loading Whisper base model on {gpu_label}...")
            self.whisper_model = _whisper_lib.load_model("base", device=device)
            print(f"✓ Whisper base model loaded on {gpu_label}")
        except Exception as e:
            print(f"⚠ Whisper load failed: {e}")
            self.whisper_model = None

    def _run_audio_transcription(self, session_id: str):
        """
        Background thread: records audio in 30-second chunks and
        transcribes each chunk with Whisper, saving results to
        class_notes_<session_id>.json
        """
        SAMPLE_RATE = 16000
        CHUNK_SECONDS = 30
        notes_file = f"class_notes_{session_id}.json"
        segments = []
        full_parts = []
        session_start = time.time()
        audio_q = queue.Queue()
        stop_ev = self._audio_stop_event

        def _recording_loop():
            chunk_samples = int(CHUNK_SECONDS * SAMPLE_RATE)
            while not stop_ev.is_set():
                try:
                    chunk = _sd.rec(chunk_samples, samplerate=SAMPLE_RATE,
                                    channels=1, dtype="float32")
                    for _ in range(CHUNK_SECONDS):
                        if stop_ev.is_set():
                            _sd.stop()
                            break
                        time.sleep(1)
                    else:
                        _sd.wait()
                    audio_q.put(chunk.copy())
                except Exception as rec_err:
                    print(f"  [Audio] Recording error: {rec_err}")
                    time.sleep(1)

        rec_thread = threading.Thread(target=_recording_loop, daemon=True)
        rec_thread.start()
        print("🎤 Audio transcription started (Whisper base)")

        try:
            while not stop_ev.is_set():
                try:
                    audio_chunk = audio_q.get(timeout=2)
                except queue.Empty:
                    continue
                elapsed = time.time() - session_start
                t_label = f"{int(elapsed)//60}:{int(elapsed)%60:02d}"
                try:
                    af = audio_chunk.astype(np.float32)
                    if af.ndim > 1:
                        af = af.mean(axis=1)
                    mx = np.abs(af).max()
                    if mx > 0:
                        af = af / mx
                    result = self.whisper_model.transcribe(af, language="en", fp16=False)
                    text = result.get("text", "").strip()
                except Exception as tr_err:
                    print(f"  [Whisper] Transcription error: {tr_err}")
                    text = ""
                if text:
                    segments.append({"time": t_label, "text": text})
                    full_parts.append(text)
                    print(f"  📝 [{t_label}] {text[:80]}{'...' if len(text)>80 else ''}")
                # Drain any remaining in queue after stop
                while not audio_q.empty():
                    try:
                        extra = audio_q.get_nowait()
                        af = extra.astype(np.float32)
                        if af.ndim > 1:
                            af = af.mean(axis=1)
                        mx = np.abs(af).max()
                        if mx > 0:
                            af = af / mx
                        res2 = self.whisper_model.transcribe(af, language="en", fp16=False)
                        t2 = res2.get("text", "").strip()
                        if t2:
                            segments.append({"time": t_label, "text": t2})
                            full_parts.append(t2)
                    except Exception:
                        break
        finally:
            stop_ev.set()
            rec_thread.join(timeout=5)
            data = {
                "timestamp": datetime.now().isoformat(),
                "segments": segments,
                "full_transcript": " ".join(full_parts),
            }
            tmp = notes_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            os.replace(tmp, notes_file)
            print(f"✅ Transcript saved → {notes_file} ({len(segments)} segments)")

    def _load_facenet(self):
        """Load MTCNN + InceptionResnetV1 on GPU for fast, accurate face recognition"""
        if not FACENET_AVAILABLE:
            return
        try:
            from facenet_pytorch import MTCNN, InceptionResnetV1
            # MTCNN: detects & aligns faces to 160×160 before encoding
            self.mtcnn = MTCNN(
                image_size=160,
                margin=20,
                keep_all=True,       # return all faces in frame
                device=FACENET_DEVICE,
                post_process=True,   # normalize to [-1, 1]
            )
            # InceptionResnetV1 pretrained on VGGFace2 (very good for ID)
            self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(FACENET_DEVICE)
            device_label = f"GPU ({FACENET_DEVICE})" if CUDA_AVAILABLE else "CPU"
            print(f"✓ facenet-pytorch loaded on {device_label}")
        except Exception as e:
            print(f"⚠ Could not load facenet-pytorch: {e}")
            self.mtcnn = None
            self.resnet = None

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
            import torch
            from ultralytics import YOLO
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yolov8l.pt')
            if not os.path.exists(model_path):
                model_path = 'yolov8l.pt'  # Try relative path
            self.yolo_model = YOLO(model_path)
            # Force YOLO onto GPU if available
            self._yolo_device = 0 if torch.cuda.is_available() else 'cpu'
            if torch.cuda.is_available():
                self.yolo_model.to('cuda')
                print(f"\u2713 YOLOv8l loaded on GPU ({torch.cuda.get_device_name(0)}) for mobile phone detection")
            else:
                print("\u2713 YOLOv8l loaded for mobile phone detection (CPU)")
        except Exception as e:
            print(f"\u26a0 Could not load YOLOv8l: {e}")
            print("  Mobile detection will use basic edge detection as fallback")
            self.yolo_model = None
            self._yolo_device = 'cpu'
    
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
            
            if FACENET_AVAILABLE and self.facenet_embeddings:
                import torch
                total_students = len(self.facenet_embeddings)
                gpu_name = torch.cuda.get_device_name(0) if CUDA_AVAILABLE else "CPU"
                method = f"facenet-pytorch {'GPU (' + gpu_name + ')' if CUDA_AVAILABLE else 'CPU'} — 512-d embeddings"
            elif FACE_RECOGNITION_AVAILABLE and self.known_face_encodings:
                total_students = len(self.known_face_encodings)
                method = "face_recognition (dlib, CPU) — 128-d embeddings"
            else:
                total_students = len(self.known_faces)
                method = "OpenCV histogram (CPU fallback)"
            print(f"\n{'='*70}")
            print(f"✅ MODEL TRAINED SUCCESSFULLY")
            print(f"{'='*70}")
            print(f"📊 Total students registered: {total_students}")
            print(f"📸 Total photos processed: {students_trained}")
            print(f"🤖 Recognition method: {method}")
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
            # ── Path 1: facenet-pytorch on GPU (fastest & most accurate) ──────
            if FACENET_AVAILABLE and self.mtcnn is not None and self.resnet is not None:
                try:
                    import torch
                    from PIL import Image as PILImage
                    img_pil = PILImage.open(img_path).convert('RGB')
                    # MTCNN detects, aligns, and crops face to 160×160
                    face_tensor = self.mtcnn(img_pil)   # shape: (N, 3, 160, 160) or None
                    if face_tensor is not None:
                        # Take first face only (training images should have one face)
                        if face_tensor.dim() == 4:
                            face_tensor = face_tensor[0].unsqueeze(0)
                        face_tensor = face_tensor.to(FACENET_DEVICE)
                        with torch.no_grad():
                            embedding = self.resnet(face_tensor).cpu().numpy()[0]  # 512-d
                        if student_name not in self.facenet_embeddings:
                            self.facenet_embeddings[student_name] = []
                            self._initialize_student_data(student_name)
                        self.facenet_embeddings[student_name].append(embedding)
                        print(f"  ✓ [GPU] Trained on: {student_name} ({os.path.basename(img_path)})")
                        return True
                    else:
                        print(f"  ⚠ No face detected in: {os.path.basename(img_path)}")
                        return False
                except Exception as fe_err:
                    print(f"  ⚠ facenet GPU training failed, falling back: {fe_err}")
                    # fall through to face_recognition below

            # ── Path 2: face_recognition (dlib, CPU) ─────────────────────────
            if FACE_RECOGNITION_AVAILABLE:
                try:
                    image = face_recognition.load_image_file(img_path)
                    face_locations = face_recognition.face_locations(image, model=FACE_RECOGNITION_MODEL)
                    face_encodings = face_recognition.face_encodings(
                        image, known_face_locations=face_locations, num_jitters=10
                    )
                    if len(face_encodings) > 0:
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
                    print(f"  ⚠ ML method failed, using OpenCV for: {os.path.basename(img_path)}")
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
            device = getattr(self, '_yolo_device', 0)
            results = self.yolo_model(frame, verbose=False, conf=0.25, device=device)
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
    
    def _facenet_embed(self, face_bgr_img):
        """Get 512-d facenet embedding for a BGR face crop. Returns None on failure."""
        try:
            import torch
            from PIL import Image as PILImage
            face_rgb = cv2.cvtColor(face_bgr_img, cv2.COLOR_BGR2RGB)
            img_pil = PILImage.fromarray(face_rgb)
            face_tensor = self.mtcnn(img_pil)
            if face_tensor is None:
                return None
            if face_tensor.dim() == 4:
                face_tensor = face_tensor[0].unsqueeze(0)
            face_tensor = face_tensor.to(FACENET_DEVICE)
            with torch.no_grad():
                embedding = self.resnet(face_tensor).cpu().numpy()[0]
            return embedding
        except Exception:
            return None

    def match_face(self, face_img, face_location=None):
        """
        Match detected face with known student faces using ML

        Priority: facenet-pytorch GPU → face_recognition CPU → OpenCV histogram
        """
        # ── Path 1: facenet-pytorch GPU matching ─────────────────────────────
        if FACENET_AVAILABLE and self.mtcnn is not None and self.resnet is not None and self.facenet_embeddings:
            try:
                import numpy as np
                probe = self._facenet_embed(face_img)
                if probe is not None:
                    best_match = "Unknown"
                    best_dist = 0.75  # L2 distance threshold (≤0.75 = same person; family ~0.85+)
                    for student_name, embeddings in self.facenet_embeddings.items():
                        for known_emb in embeddings:
                            dist = float(np.linalg.norm(probe - known_emb))
                            if dist < best_dist:
                                best_dist = dist
                                best_match = student_name
                    return best_match
            except Exception as e:
                pass  # fall through

        # ── Path 2: face_recognition (dlib) ──────────────────────────────────
        if FACE_RECOGNITION_AVAILABLE and face_location is not None and self.known_face_encodings:
            try:
                rgb_frame = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB) if len(face_img.shape) == 3 else face_img
                face_encodings = face_recognition.face_encodings(rgb_frame, [face_location])
                if len(face_encodings) == 0:
                    return "Unknown"
                face_encoding = face_encodings[0]
                best_match = "Unknown"
                best_distance = 0.40
                for student_name, known_encodings in self.known_face_encodings.items():
                    distances = face_recognition.face_distance(known_encodings, face_encoding)
                    min_distance = min(distances) if len(distances) > 0 else 1.0
                    if min_distance < best_distance:
                        best_distance = min_distance
                        best_match = student_name
                return best_match
            except Exception as e:
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
        if FACENET_AVAILABLE and self.mtcnn is not None and self.resnet is not None:
            # ── GPU path: MTCNN detects faces, InceptionResnetV1 encodes ─────
            import torch
            from PIL import Image as PILImage
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = PILImage.fromarray(rgb_frame)
            boxes, _ = self.mtcnn.detect(img_pil)  # detect without cropping
            if boxes is None:
                boxes = []
            for box in boxes:
                left, top, right, bottom = [max(0, int(v)) for v in box]
                face_region = frame[top:bottom, left:right]
                if face_region.size == 0:
                    continue
                student_name = self.match_face(face_region)
                if student_name != "Unknown" and student_name in self.student_data:
                    is_focused = self.detect_gaze(face_region)
                    self.student_data[student_name]['total_checks'] += 1
                    if is_focused:
                        self.student_data[student_name]['focused_count'] += 1
                        status_text = f"{student_name}: Focused"
                        color = (0, 255, 0)
                    else:
                        self.student_data[student_name]['unfocused_count'] += 1
                        status_text = f"{student_name}: Not Focused"
                        color = (0, 165, 255)
                    if mobile_detected_in_frame:
                        self.student_data[student_name]['mobile_detected'] += 1
                        current_time = datetime.now().strftime("%H:%M:%S")
                        self.student_data[student_name]['mobile_times'].append(current_time)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
                    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    cv2.rectangle(frame, (left, top - text_size[1] - 10),
                                (left + text_size[0], top), color, -1)
                    cv2.putText(frame, status_text, (left, top - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                else:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    status_text = "Unknown"
                    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    cv2.rectangle(frame, (left, top - text_size[1] - 10),
                                (left + text_size[0], top), (0, 0, 255), -1)
                    cv2.putText(frame, status_text, (left, top - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        elif FACE_RECOGNITION_AVAILABLE:
            # ── CPU fallback: dlib face_recognition ──────────────────────────
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame, model=FACE_RECOGNITION_MODEL)
            
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
                    # Draw RED rectangle for unrecognized / unknown face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    status_text = "Unknown"
                    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    cv2.rectangle(frame, (left, top - text_size[1] - 10),
                                (left + text_size[0], top), (0, 0, 255), -1)
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
                else:
                    # Draw RED rectangle for unrecognized / unknown face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    status_text = "Unknown"
                    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    cv2.rectangle(frame, (x, y - text_size[1] - 10),
                                (x + text_size[0], y), (0, 0, 255), -1)
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

        # ── Load Whisper now that camera is confirmed open ────────────────────
        self._load_whisper()
        if self.whisper_model is not None and _AUDIO_AVAILABLE:
            self._whisper_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._audio_stop_event = threading.Event()
            self._audio_thread = threading.Thread(
                target=self._run_audio_transcription,
                args=(self._whisper_session_id,),
                daemon=True,
            )
            self._audio_thread.start()
        
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
            # Stop audio transcription thread
            if self._audio_stop_event is not None:
                self._audio_stop_event.set()
            if self._audio_thread is not None and self._audio_thread.is_alive():
                print("⏳ Waiting for Whisper to finish last chunk...")
                self._audio_thread.join(timeout=15)
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
