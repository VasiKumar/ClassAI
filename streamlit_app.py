"""
Sahayak AI - Streamlit Dashboard
Admin interface for monitoring students and viewing reports
"""

import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import zipfile
import shutil
from pathlib import Path
import subprocess
import time
import threading

# Load .env (Gemini API key etc.)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; env vars must be set manually

import re
import io

# ── Gemini helper ─────────────────────────────────────────────────────────────
def _gemini_available():
    try:
        from google import genai  # noqa: F401
        key = os.getenv("GEMINI_API_KEY", "")
        return bool(key and key != "your_gemini_api_key_here")
    except ImportError:
        return False


# ── Text-to-Speech helper ──────────────────────────────────────────────────────
def _markdown_to_plain(md: str) -> str:
    """Strip Markdown syntax so TTS reads clean prose."""
    text = re.sub(r"#{1,6}\s*", "", md)          # headings
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)  # bold / italic
    text = re.sub(r"_{1,3}(.+?)_{1,3}", r"\1", text)    # underscore emphasis
    text = re.sub(r"`{1,3}[^`]*`{1,3}", "", text)       # inline code / code blocks
    text = re.sub(r"!?\[([^\]]*?)\]\([^)]*\)", r"\1", text)  # links / images
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)  # bullets
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)  # numbered lists
    text = re.sub(r"^\s*>+\s*", "", text, flags=re.MULTILINE)     # blockquotes
    text = re.sub(r"---+|===+", "", text)         # horizontal rules
    text = re.sub(r"\n{3,}", "\n\n", text)        # excess blank lines
    return text.strip()


def _tts_audio_bytes(text: str) -> bytes:
    """Convert plain text to MP3 bytes using gTTS."""
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text, lang="en", slow=False).write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        return b""


def generate_star_notes(raw_transcript: str) -> dict:
    """
    Call Gemini to produce organised notes + 3-5 questions from raw transcript.
    Returns dict with keys: 'notes' (str markdown) and 'questions' (list[str]).
    """
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)

    prompt = f"""You are an expert teacher's assistant. A class was recorded and the raw speech transcript is below.

Your task:
1. Rewrite the content as **clear, well-organised class notes** in Markdown format.
   - Use headings, bullet points, bold key terms.
   - Fix any transcription errors and make it readable.
   - Keep all important information — do NOT remove topics.
2. After the notes, generate exactly **3 to 5 questions** — a mix of real-life application questions and conceptual/critical-thinking questions — based on the content.
   - Number them 1 through 3-5.
   - Each question should make a student think, not just recall a fact.

Format your response EXACTLY like this (use these exact section markers):
---NOTES---
<your markdown notes here>
---QUESTIONS---
1. <question>
2. <question>
3. <question>
(4. <question>)
(5. <question>)

RAW TRANSCRIPT:
{raw_transcript}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    raw_output = response.text.strip()

    # Parse the two sections
    notes_part = ""
    questions_part = []

    if "---NOTES---" in raw_output and "---QUESTIONS---" in raw_output:
        after_notes = raw_output.split("---NOTES---", 1)[1]
        notes_raw, q_raw = after_notes.split("---QUESTIONS---", 1)
        notes_part = notes_raw.strip()
        for line in q_raw.strip().splitlines():
            line = line.strip()
            if line and line[0].isdigit():
                # Strip leading "1. ", "2. " etc.
                q_text = line.split(".", 1)[-1].strip() if "." in line else line
                questions_part.append(q_text)
    else:
        # Fallback: return raw output as notes
        notes_part = raw_output

    return {"notes": notes_part, "questions": questions_part}

# Page configuration
st.set_page_config(
    page_title="Student Focus Monitor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* ── Google Font ─────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
    }

    /* ── Page background ─────────────────────────────────────── */
    .stApp {
        background: linear-gradient(135deg, #f0f4ff 0%, #faf0ff 50%, #f0fff4 100%);
    }

    /* ── Main hero header ────────────────────────────────────── */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1.8rem;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 40%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
        padding: 0.4rem 0;
    }

    /* ── Section subheaders ──────────────────────────────────── */
    h2, h3 {
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        color: #3d3d6e !important;
        letter-spacing: -0.2px;
    }

    /* ── Generic card ────────────────────────────────────────── */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f3f4ff 100%);
        border: 1px solid #dde1ff;
        padding: 1.2rem 1.4rem;
        border-radius: 14px;
        margin: 0.6rem 0;
        box-shadow: 0 3px 12px rgba(102, 126, 234, 0.10);
        font-size: 1.05rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.18);
    }
    .metric-card h3 {
        color: #4a4aaa !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.3rem;
    }
    .metric-card p {
        color: #555577;
        font-size: 0.95rem;
        margin: 0;
    }

    /* ── Student present / absent pills ─────────────────────── */
    .student-present {
        background: linear-gradient(135deg, #d4edda, #a8f0be);
        border-left: 4px solid #28a745;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        font-size: 1rem;
        color: #155724;
        font-weight: 600;
    }
    .student-absent {
        background: linear-gradient(135deg, #f8d7da, #ffc0cb);
        border-left: 4px solid #dc3545;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        font-size: 1rem;
        color: #721c24;
        font-weight: 600;
    }

    /* ── Focus labels ────────────────────────────────────────── */
    .good-focus {
        color: #15803d;
        font-weight: 700;
        font-size: 1.05rem;
    }
    .poor-focus {
        color: #b91c1c;
        font-weight: 700;
        font-size: 1.05rem;
    }

    /* ── Streamlit metric widget ─────────────────────────────── */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff, #f0f4ff);
        border: 1px solid #d0d8ff;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 10px rgba(102,126,234,0.08);
    }
    [data-testid="metric-container"] label {
        font-size: 0.92rem !important;
        color: #6b7280 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #4338ca !important;
    }

    /* ── Buttons ─────────────────────────────────────────────── */
    .stButton > button {
        font-size: 1rem !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.4rem !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.2px;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(102, 126, 234, 0.45) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 7px 20px rgba(102, 126, 234, 0.55) !important;
    }
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #ff6b6b, #ee0979) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(238, 9, 121, 0.3) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 7px 20px rgba(238, 9, 121, 0.45) !important;
    }

    /* ── Sidebar ─────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a4e 0%, #2d2d7e 50%, #3d1a6e 100%) !important;
    }
    [data-testid="stSidebar"] * {
        color: #e8e8ff !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        padding: 0.35rem 0 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15) !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    [data-testid="stSidebar"] [data-testid="metric-container"] {
        background: rgba(255,255,255,0.1) !important;
        border-color: rgba(255,255,255,0.2) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #a5f3fc !important;
    }

    /* ── Alert / info boxes ──────────────────────────────────── */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }

    /* ── Dataframe / table ───────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden;
        font-size: 1rem !important;
    }

    /* ── Text inputs / selects ───────────────────────────────── */
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        font-size: 1rem !important;
        border-radius: 8px !important;
    }

    /* ── Progress bar ────────────────────────────────────────── */
    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #667eea, #f093fb) !important;
        border-radius: 999px !important;
    }

    /* ── Expander ────────────────────────────────────────────── */
    details summary {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    /* ── Footer ──────────────────────────────────────────────── */
    .footer-bar {
        text-align: center;
        padding: 0.8rem;
        font-size: 0.95rem;
        color: #6b7280;
        background: linear-gradient(135deg, #f0f4ff, #faf0ff);
        border-radius: 12px;
        margin-top: 1rem;
        border: 1px solid #e0e0ff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'monitoring_process' not in st.session_state:
    st.session_state.monitoring_process = None
if 'audio_process' not in st.session_state:
    st.session_state.audio_process = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'monitoring_start_time' not in st.session_state:
    st.session_state.monitoring_start_time = None
if 'focus_threshold' not in st.session_state:
    st.session_state.focus_threshold = 50
if 'class_duration' not in st.session_state:
    st.session_state.class_duration = 300

class StudentMonitorDashboard:
    def __init__(self):
        self.student_photos_path = "sample_student_photos"
        self.reports_dir = "."
        
    def get_registered_students(self):
        """Get list of all registered students from zip files"""
        students = []
        if os.path.exists(self.student_photos_path):
            for file in os.listdir(self.student_photos_path):
                if file.lower().endswith('.zip'):
                    student_name = os.path.splitext(file)[0]
                    students.append(student_name)
        return sorted(students)
    
    def get_all_reports(self):
        """Get all report files"""
        reports = []
        try:
            files = os.listdir(self.reports_dir)
            for file in files:
                if file.startswith('focus_report_') and file.endswith('.json'):
                    reports.append(file)
        except Exception as e:
            print(f"Error reading reports directory: {e}")
        return sorted(reports, reverse=True)
    
    def load_report(self, report_file):
        """Load a report JSON file"""
        try:
            with open(os.path.join(self.reports_dir, report_file), 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading report: {e}")
            return None
    
    def delete_report(self, report_file):
        """Delete a report file"""
        try:
            os.remove(os.path.join(self.reports_dir, report_file))
            return True
        except Exception as e:
            st.error(f"Error deleting report: {e}")
            return False
    
    def start_monitoring(self, duration, threshold):
        """Start the monitoring process"""
        # Update the student_monitor.py configuration
        config = {
            'duration': duration,
            'threshold': threshold
        }
        
        # Run the monitoring script
        cmd = f'python student_monitor.py'
        
        # This would ideally run in background
        # For now, we'll indicate it should be run
        return config

# Initialize dashboard
dashboard = StudentMonitorDashboard()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/fluency/96/000000/student-center.png", width=100)
st.sidebar.title("📊 Navigation")

# Monitoring Status in Sidebar
if st.session_state.monitoring_active:
    st.sidebar.success("🟢 **Session Active**")
    if st.session_state.monitoring_start_time:
        elapsed = (datetime.now() - st.session_state.monitoring_start_time).total_seconds()
        st.sidebar.metric("Time", f"{int(elapsed)}s")
else:
    st.sidebar.info("⚪ **No Active Session**")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Go to",
    ["🏠 Home", "👥 Students", "▶️ Start Monitoring", "📈 View Reports", "📝 Notes", "⚙️ Settings"]
)

# Main content based on selected page
if page == "🏠 Home":
    st.markdown('<div class="main-header">🎓 Sahayak AI</div>', unsafe_allow_html=True)
    
    # Check if monitoring process is still running
    if st.session_state.monitoring_active and st.session_state.monitoring_process:
        poll = st.session_state.monitoring_process.poll()
        if poll is not None:  # Process has ended
            st.session_state.monitoring_active = False
            st.session_state.monitoring_process = None
            st.success("✅ Monitoring session completed!")
            st.info("📊 Go to 'View Reports' to see the generated report.")
            st.session_state.monitoring_start_time = None
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_students = len(dashboard.get_registered_students())
        st.metric("📚 Total Registered Students", total_students)
    
    with col2:
        total_reports = len(dashboard.get_all_reports())
        st.metric("📄 Total Reports", total_reports)
    
    with col3:
        st.metric("⚙️ Focus Threshold", f"{st.session_state.focus_threshold}%")
    
    # Monitoring Status Indicator
    if st.session_state.monitoring_active:
        st.success("🟢 **Monitoring Session Active**")
        if st.session_state.monitoring_start_time:
            elapsed = (datetime.now() - st.session_state.monitoring_start_time).total_seconds()
            remaining = max(0, st.session_state.class_duration - elapsed)
            st.info(f"⏱️ Time Elapsed: {int(elapsed)}s | Remaining: {int(remaining)}s")
        
        col_end1, col_end2 = st.columns([3, 1])
        with col_end2:
            if st.button("🛑 End Session", key="home_end"):
                if st.session_state.monitoring_process:
                    try:
                        # Create stop signal file for Windows-compatible shutdown
                        with open('monitor_stop.signal', 'w') as f:
                            f.write('stop')
                        
                        # Wait a bit for graceful shutdown
                        time.sleep(3)
                        
                        # Then terminate if still running
                        st.session_state.monitoring_process.terminate()
                        st.session_state.monitoring_process.wait(timeout=5)
                    except:
                        try:
                            st.session_state.monitoring_process.kill()
                        except:
                            pass
                
                st.session_state.monitoring_active = False
                st.session_state.monitoring_process = None
                st.session_state.monitoring_start_time = None
                st.rerun()
    else:
        st.info("⚪ No active monitoring session")
    
    st.markdown("---")
    
    # Quick Stats from Latest Report
    st.subheader("📊 Latest Session Overview")
    
    reports = dashboard.get_all_reports()
    if reports:
        latest_report = dashboard.load_report(reports[0])
        
        if latest_report:
            col1, col2, col3, col4 = st.columns(4)
            
            students_data = latest_report.get('students', {})
            total_registered = len(dashboard.get_registered_students())
            students_present = len(students_data)
            
            avg_focus = sum(s['focus_percentage'] for s in students_data.values()) / len(students_data) if students_data else 0
            students_above_threshold = sum(1 for s in students_data.values() if s['focus_percentage'] >= latest_report.get('threshold', 50))
            
            with col1:
                st.metric("👥 Students Present", f"{students_present}/{total_registered}")
            
            with col2:
                st.metric("📊 Average Focus", f"{avg_focus:.1f}%")
            
            with col3:
                st.metric("✅ Above Threshold", students_above_threshold)
            
            with col4:
                if latest_report.get('mobile_detection_enabled', False):
                    total_mobile = sum(s['mobile_detected'] for s in students_data.values())
                    st.metric("📱 Mobile Detections", total_mobile)
                else:
                    st.metric("📱 Mobile Detection", "Disabled")
            
            # Focus Distribution Chart
            st.subheader("📈 Focus Distribution")
            
            # Build DataFrame based on whether mobile detection was enabled
            if latest_report.get('mobile_detection_enabled', False):
                focus_data = pd.DataFrame([
                    {
                        'Student': name,
                        'Focus %': data['focus_percentage'],
                        'Mobile Detected': data['mobile_detected']
                    }
                    for name, data in students_data.items()
                ])
            else:
                focus_data = pd.DataFrame([
                    {
                        'Student': name,
                        'Focus %': data['focus_percentage']
                    }
                    for name, data in students_data.items()
                ])
            
            fig = px.bar(
                focus_data,
                x='Student',
                y='Focus %',
                color='Focus %',
                color_continuous_scale=['red', 'yellow', 'green'],
                title='Student Focus Percentage'
            )
            fig.add_hline(y=latest_report.get('threshold', 50), line_dash="dash", 
                         line_color="red", annotation_text="Threshold")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 No reports available. Start a monitoring session to generate reports.")
    
    # Quick Actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Start New Session", type="primary", use_container_width=True, disabled=st.session_state.monitoring_active):
            st.info("➡️ Navigate to 'Start Monitoring' in the sidebar")
    
    with col2:
        if st.button("📊 View All Reports", use_container_width=True):
            st.info("➡️ Navigate to 'View Reports' in the sidebar")
    
    with col3:
        if st.button("⚙️ Configure Settings", use_container_width=True):
            st.info("➡️ Navigate to 'Settings' in the sidebar")

elif page == "👥 Students":
    st.markdown('<div class="main-header">👥 Registered Students</div>', unsafe_allow_html=True)
    
    students = dashboard.get_registered_students()
    
    st.subheader(f"📚 Total Students: {len(students)}")
    
    if students:
        # Search functionality
        search = st.text_input("🔍 Search Students", placeholder="Enter student name...")
        
        filtered_students = [s for s in students if search.lower() in s.lower()] if search else students
        
        # Display in columns
        cols_per_row = 3
        for i in range(0, len(filtered_students), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(filtered_students):
                    student = filtered_students[i + j]
                    with col:
                        with st.container():
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>👤 {student}</h3>
                                <p>📦 ZIP File: {student}.zip</p>
                            </div>
                            """, unsafe_allow_html=True)
        
        # Student List Table
        st.markdown("---")
        st.subheader("📋 Student List")
        
        df = pd.DataFrame({
            'Student Name': students,
            'ZIP File': [f"{s}.zip" for s in students],
            'Status': ['✅ Registered' for _ in students]
        })
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    else:
        st.warning("⚠️ No students registered. Please add student ZIP files to the 'sample_student_photos' folder.")
        st.info("""
        **How to add students:**
        1. Create a ZIP file for each student containing their photos
        2. Name the ZIP file as: `studentname.zip`
        3. Place it in the `sample_student_photos` folder
        4. Example: `basistha.zip`, `sarbeswar.zip`
        """)

elif page == "▶️ Start Monitoring":
    st.markdown('<div class="main-header">▶️ Start Monitoring Session</div>', unsafe_allow_html=True)
    
    # Check if monitoring process is still running
    if st.session_state.monitoring_active and st.session_state.monitoring_process:
        poll = st.session_state.monitoring_process.poll()
        if poll is not None:  # Process has ended
            st.session_state.monitoring_active = False
            st.session_state.monitoring_process = None
            st.success("✅ Monitoring session completed!")
            st.info("📊 Go to 'View Reports' to see the generated report.")
            st.session_state.monitoring_start_time = None
    
    students = dashboard.get_registered_students()
    
    if not students:
        st.error("❌ No students registered! Please add student ZIP files first.")
        st.stop()
    
    # Configuration
    st.subheader("⚙️ Session Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duration_minutes = st.number_input(
            "⏱️ Class Duration (minutes)",
            min_value=1,
            max_value=180,
            value=5,
            step=1,
            help="How long to monitor students"
        )
        duration_seconds = duration_minutes * 60
    
    with col2:
        threshold = st.slider(
            "📊 Focus Threshold (%)",
            min_value=0,
            max_value=100,
            value=st.session_state.focus_threshold,
            step=5,
            help="Minimum focus percentage required"
        )
    
    # Mobile Detection Option
    st.markdown("---")
    st.subheader("📱 Mobile Phone Detection (Optional)")
    
    enable_mobile = st.checkbox(
        "Enable Mobile Phone Detection",
        value=False,
        help="Uses edge detection to identify rectangular mobile phone shapes. May have false positives."
    )
    
    if enable_mobile:
        st.warning("""
        **Detection Method:**
        - Edge detection algorithm
        - Detects rectangular shapes
        - Shows RED rectangles around detected phones
        - May have some false positives
        """)
    
    # Save to session state
    st.session_state.class_duration = duration_seconds
    st.session_state.focus_threshold = threshold
    
    # Student Preview
    st.markdown("---")
    st.subheader(f"👥 Students to Monitor ({len(students)})")
    
    cols = st.columns(min(5, len(students)))
    for i, student in enumerate(students[:5]):
        with cols[i]:
            st.info(f"👤 {student}")
    
    if len(students) > 5:
        st.caption(f"... and {len(students) - 5} more students")
    
    # Start Button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.monitoring_active:
            if st.button("🚀 START MONITORING SESSION", type="primary", use_container_width=True):
                with st.spinner("🔄 Starting monitoring session..."):
                    # Clean up any old signal files
                    for _sig_file in ('monitor_stop.signal', 'camera_ready.signal'):
                        if os.path.exists(_sig_file):
                            try:
                                os.remove(_sig_file)
                            except:
                                pass
                    
                    # Save config file for student_monitor.py
                    config = {
                        'duration': duration_seconds,
                        'threshold': threshold,
                        'enable_mobile_detection': enable_mobile
                    }
                    
                    with open('monitor_config.json', 'w') as f:
                        json.dump(config, f, indent=4)
                    
                    # Start monitoring process
                    try:
                        import sys
                        python_executable = sys.executable
                        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.session_state.session_id = session_id
                        process = subprocess.Popen(
                            [python_executable, 'student_monitor.py'],
                            cwd=os.getcwd(),
                            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                        )
                        
                        # Start audio recorder alongside the monitoring session
                        try:
                            audio_process = subprocess.Popen(
                                [python_executable, 'audio_recorder.py', '--session-id', session_id],
                                cwd=os.getcwd(),
                                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                            )
                            st.session_state.audio_process = audio_process
                        except Exception as ae:
                            st.warning(f"⚠️ Audio recorder could not start: {ae}")
                            st.session_state.audio_process = None
                        
                        st.session_state.monitoring_process = process
                        st.session_state.monitoring_active = True
                        st.session_state.monitoring_start_time = datetime.now()
                        st.session_state.class_duration = duration_seconds
                        st.session_state.focus_threshold = threshold
                        
                        time.sleep(2)  # Give process time to start
                        
                        st.success("✅ Monitoring session started successfully!")
                        audio_status = "🎙️ Audio recording active" if st.session_state.audio_process else "⚠️ Audio recorder not started"
                        st.info(f"""
                        **Session Details:**
                        - Duration: {duration_minutes} minutes ({duration_seconds} seconds)
                        - Threshold: {threshold}%
                        - Students: {len(students)}
                        - Session ID: `{session_id}`
                        
                        **A new window has opened for monitoring.**
                        - The camera will track student focus automatically
                        - Report will be generated when session ends
                        - {audio_status} — view transcript in **📝 Notes**
                        - You can end the session early using the button below
                        """)
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error starting monitoring: {e}")
                        st.info("You can still run manually: `python student_monitor.py`")
        else:
            # Monitoring is active
            st.info("📹 **Monitoring Session Active**")
            
            if st.session_state.monitoring_start_time:
                elapsed = (datetime.now() - st.session_state.monitoring_start_time).total_seconds()
                remaining = max(0, st.session_state.class_duration - elapsed)
                progress = min(1.0, elapsed / st.session_state.class_duration)
                
                st.progress(progress, text=f"Time Elapsed: {int(elapsed)}s / {st.session_state.class_duration}s")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Elapsed", f"{int(elapsed)}s")
                with col_b:
                    st.metric("Remaining", f"{int(remaining)}s")
                with col_c:
                    st.metric("Threshold", f"{st.session_state.focus_threshold}%")
            
            st.warning("⚠️ A monitoring window is open. Check that window for live tracking.")
            
            if st.button("🛑 END SESSION NOW", type="secondary", use_container_width=True):
                with st.spinner("⏳ Ending session and generating report..."):
                    if st.session_state.monitoring_process:
                        try:
                            # Create stop signal file for Windows-compatible shutdown
                            with open('monitor_stop.signal', 'w') as f:
                                f.write('stop')
                            
                            st.info("⏳ Waiting for report generation...")
                            
                            # Wait for graceful shutdown (the script will detect the file)
                            time.sleep(5)
                            
                            # Check if process has ended
                            poll_result = st.session_state.monitoring_process.poll()
                            if poll_result is None:
                                # Still running, send terminate signal
                                st.session_state.monitoring_process.terminate()
                                
                                # Wait up to 10 more seconds
                                try:
                                    st.session_state.monitoring_process.wait(timeout=10)
                                    st.success("✅ Session ended gracefully!")
                                except subprocess.TimeoutExpired:
                                    st.warning("⚠️ Process taking too long, forcing shutdown...")
                                    st.session_state.monitoring_process.kill()
                                    st.session_state.monitoring_process.wait(timeout=5)
                                    st.warning("⚠️ Session force-stopped. Report may not be generated.")
                            else:
                                st.success("✅ Session ended gracefully!")
                                
                        except Exception as e:
                            st.error(f"❌ Error stopping session: {e}")
                            try:
                                st.session_state.monitoring_process.kill()
                            except:
                                pass
                    
                    # Small delay to ensure report file is written
                    time.sleep(3)
                    
                    # Also stop audio recorder if still running
                    if st.session_state.audio_process:
                        try:
                            if st.session_state.audio_process.poll() is None:
                                st.session_state.audio_process.terminate()
                                st.session_state.audio_process.wait(timeout=15)
                        except Exception:
                            try:
                                st.session_state.audio_process.kill()
                            except Exception:
                                pass
                    
                    st.session_state.monitoring_active = False
                    st.session_state.monitoring_process = None
                    st.session_state.audio_process = None
                    st.session_state.monitoring_start_time = None
                    
                    st.success("✅ Session ended!")
                    st.info("📊 Check 'View Reports' page for the generated report.")
                    time.sleep(2)
                st.rerun()

elif page == "📈 View Reports":
    st.markdown('<div class="main-header">📈 View Reports</div>', unsafe_allow_html=True)
    
    # Show reports directory for debugging
    reports_path = os.path.abspath(dashboard.reports_dir)
    with st.expander("🔧 Debug Info", expanded=False):
        st.code(f"Reports Directory: {reports_path}")
        st.code(f"Current Working Dir: {os.getcwd()}")
        
        # List all JSON files for debugging
        all_json_files = [f for f in os.listdir(dashboard.reports_dir) if f.endswith('.json')]
        st.write(f"All JSON files found: {len(all_json_files)}")
        for jf in all_json_files:
            st.text(f"  - {jf}")
        
        # Check if monitoring is still active
        if st.session_state.monitoring_active:
            st.warning("⚠️ Monitoring session is still ACTIVE. Report will generate when it ends.")
            if st.session_state.monitoring_process:
                poll = st.session_state.monitoring_process.poll()
                if poll is None:
                    st.info("✓ Monitoring process is running")
                else:
                    st.info(f"✓ Monitoring process ended (exit code: {poll})")
        
        # Create test report button
        if st.button("🧪 Create Test Report"):
            test_report = {
                "timestamp": datetime.now().isoformat(),
                "duration": 60,
                "threshold": 50,
                "students": {
                    "test_student": {
                        "focus_percentage": 75.0,
                        "focused_count": 15,
                        "unfocused_count": 5,
                        "total_checks": 20,
                        "mobile_detected": 0,
                        "mobile_times": [],
                        "alerts": []
                    }
                }
            }
            test_filename = f"focus_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(test_filename, 'w') as f:
                json.dump(test_report, f, indent=4)
            st.success(f"✅ Test report created: {test_filename}")
            time.sleep(1)
            st.rerun()
    
    reports = dashboard.get_all_reports()
    
    if not reports:
        st.warning("📭 No reports available yet.")
        st.info(f"""
        **Reports are saved in:** `{reports_path}`
        
        **To generate a report:**
        1. Go to "Start Monitoring" page
        2. Click "START MONITORING SESSION"
        3. Wait for the session to complete (or end it manually)
        4. The report will appear here automatically
        
        **Note:** Reports are named `focus_report_YYYYMMDD_HHMMSS.json`
        """)
        
        # Check if there are any JSON files that might be reports
        all_json = [f for f in os.listdir(dashboard.reports_dir) if f.endswith('.json')]
        if all_json:
            st.write("**Other JSON files found:**")
            for jf in all_json:
                st.text(f"  • {jf}")
        
        st.stop()
    
    # Report Selection
    st.subheader("📄 Select Report")
    
    # Refresh button at top
    col_ref1, col_ref2, col_ref3 = st.columns([4, 1, 1])
    with col_ref2:
        if st.button("🔄 Refresh List", use_container_width=True):
            st.rerun()
    with col_ref3:
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto", help="Auto-refresh every 5 seconds")
    
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    report_options = {}
    for report in reports:
        try:
            data = dashboard.load_report(report)
            if data:
                timestamp = data.get('timestamp', report)
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted = dt.strftime("%B %d, %Y at %I:%M %p")
                report_options[f"{formatted} ({report})"] = report
        except:
            report_options[report] = report
    
    selected_display = st.selectbox("Choose a report:", list(report_options.keys()))
    selected_report = report_options[selected_display]
    
    # Load selected report
    report_data = dashboard.load_report(selected_report)
    
    if not report_data:
        st.error("❌ Error loading report")
        st.stop()
    
    # Report Actions
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("🗑️ Delete Report", type="secondary", use_container_width=True):
            if dashboard.delete_report(selected_report):
                st.success("✅ Report deleted successfully!")
                time.sleep(1)
                st.rerun()
    
    st.markdown("---")
    
    # Report Summary
    students_data = report_data.get('students', {})
    threshold = report_data.get('threshold', 50)
    duration = report_data.get('duration', 0)
    
    # Key Metrics
    st.subheader("📊 Session Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_registered = len(dashboard.get_registered_students())
    students_present = len(students_data)
    attendance_rate = (students_present / total_registered * 100) if total_registered > 0 else 0
    
    avg_focus = sum(s['focus_percentage'] for s in students_data.values()) / len(students_data) if students_data else 0
    students_above = sum(1 for s in students_data.values() if s['focus_percentage'] >= threshold)
    students_below = len(students_data) - students_above
    
    mobile_enabled = report_data.get('mobile_detection_enabled', False)
    total_mobile = sum(s['mobile_detected'] for s in students_data.values()) if mobile_enabled else 0
    
    with col1:
        st.metric("⏱️ Duration", f"{duration // 60} min")
    
    with col2:
        st.metric("👥 Attendance", f"{students_present}/{total_registered}", 
                 delta=f"{attendance_rate:.0f}%")
    
    with col3:
        st.metric("📊 Avg Focus", f"{avg_focus:.1f}%",
                 delta="Good" if avg_focus >= threshold else "Low")
    
    with col4:
        st.metric("✅ Passed", students_above, 
                 delta=f"{(students_above/max(1,students_present)*100):.0f}%")
    
    with col5:
        if mobile_enabled:
            st.metric("📱 Mobile Use", total_mobile,
                     delta="None" if total_mobile == 0 else "Detected", delta_color="inverse")
        else:
            st.metric("📱 Mobile Detection", "Disabled")
    
    # Detailed Statistics
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Focus Performance")
        
        # Focus distribution pie chart
        pass_fail = pd.DataFrame({
            'Category': ['Above Threshold', 'Below Threshold'],
            'Count': [students_above, students_below]
        })
        
        fig = px.pie(pass_fail, values='Count', names='Category',
                    color='Category',
                    color_discrete_map={'Above Threshold': 'green', 'Below Threshold': 'red'},
                    title=f'Students vs {threshold}% Threshold')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👥 Attendance Overview")
        
        # Attendance pie chart
        attendance_data = pd.DataFrame({
            'Status': ['Present', 'Absent'],
            'Count': [students_present, total_registered - students_present]
        })
        
        fig = px.pie(attendance_data, values='Count', names='Status',
                    color='Status',
                    color_discrete_map={'Present': 'lightblue', 'Absent': 'lightgray'},
                    title='Attendance Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Student-wise Details
    st.markdown("---")
    st.subheader("👤 Individual Student Performance")
    
    # Create DataFrame
    if mobile_enabled:
        student_df = pd.DataFrame([
            {
                'Student': name,
                'Focus %': f"{data['focus_percentage']:.1f}%",
                'Focused': data['focused_count'],
                'Unfocused': data['unfocused_count'],
                'Total Checks': data['total_checks'],
                'Mobile Detected': data['mobile_detected'],
                'Status': '✅ Pass' if data['focus_percentage'] >= threshold else '❌ Fail'
            }
            for name, data in students_data.items()
        ])
    else:
        student_df = pd.DataFrame([
            {
                'Student': name,
                'Focus %': f"{data['focus_percentage']:.1f}%",
                'Focused': data['focused_count'],
                'Unfocused': data['unfocused_count'],
                'Total Checks': data['total_checks'],
                'Status': '✅ Pass' if data['focus_percentage'] >= threshold else '❌ Fail'
            }
            for name, data in students_data.items()
        ])
    
    # Sort by focus percentage
    student_df = student_df.sort_values('Focus %', ascending=False)
    
    st.dataframe(student_df, use_container_width=True, hide_index=True)
    
    # Focus Bar Chart
    st.subheader("📊 Focus Comparison")
    
    focus_chart_data = pd.DataFrame([
        {
            'Student': name,
            'Focus Percentage': data['focus_percentage']
        }
        for name, data in students_data.items()
    ]).sort_values('Focus Percentage', ascending=False)
    
    fig = px.bar(
        focus_chart_data,
        x='Student',
        y='Focus Percentage',
        color='Focus Percentage',
        color_continuous_scale=['red', 'yellow', 'green'],
        title='Student Focus Percentage Comparison'
    )
    fig.add_hline(y=threshold, line_dash="dash", line_color="red", 
                 annotation_text=f"Threshold ({threshold}%)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Mobile Phone Usage (only show if feature was enabled)
    if report_data.get('mobile_detection_enabled', False):
        if total_mobile > 0:
            st.markdown("---")
            st.subheader("📱 Mobile Phone Detections")
            
            mobile_students = [(name, data) for name, data in students_data.items() 
                              if data['mobile_detected'] > 0]
            
            for student_name, data in mobile_students:
                with st.expander(f"⚠️ {student_name} - {data['mobile_detected']} detections"):
                    st.warning(f"**{student_name} REPORT!**")
                    st.write(f"Total mobile detections: {data['mobile_detected']}")
                    st.write("Detection times:")
                    for time_str in data.get('mobile_times', []):
                        st.text(f"  • {time_str}")
    
    # Absent Students
    all_students = set(dashboard.get_registered_students())
    present_students = set(students_data.keys())
    absent_students = all_students - present_students
    
    if absent_students:
        st.markdown("---")
        st.subheader("🚫 Absent Students")
        
        absent_cols = st.columns(min(5, len(absent_students)))
        for i, student in enumerate(sorted(absent_students)):
            with absent_cols[i % len(absent_cols)]:
                st.error(f"❌ {student}")

# ─────────────────────────────────────────────────────────────────────────────
elif page == "📝 Notes":
    st.markdown('<div class="main-header">📝 Class Notes</div>', unsafe_allow_html=True)
    st.caption("Audio transcriptions captured by Whisper base model during live sessions.")

    # ── Collect all notes files ───────────────────────────────────────────────
    notes_files = sorted(
        [f for f in os.listdir(".") if f.startswith("class_notes_") and f.endswith(".json")],
        reverse=True,
    )

    if not notes_files:
        st.warning("📭 No class notes found yet.")
        st.info(
            "Notes are recorded automatically when you start a monitoring session.\n\n"
            "Make sure your microphone is accessible and start a new session from "
            "**▶️ Start Monitoring**."
        )
        # Show live recording indicator if session is active
        if st.session_state.monitoring_active and st.session_state.session_id:
            live_file = f"class_notes_{st.session_state.session_id}.json"
            st.success(f"🔴 **Recording in progress** — notes will appear here as `{live_file}` once the session ends.")
            if st.button("🔄 Refresh"):
                st.rerun()
    else:
        # ── Session selector ─────────────────────────────────────────────────
        col_sel, col_ref = st.columns([5, 1])
        with col_ref:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

        # Build display labels from filename timestamps
        notes_options = {}
        for nf in notes_files:
            try:
                session_ts = nf.replace("class_notes_", "").replace(".json", "")
                dt = datetime.strptime(session_ts, "%Y%m%d_%H%M%S")
                label = dt.strftime("%B %d, %Y at %I:%M %p")
            except Exception:
                label = nf
            notes_options[f"{label}  ({nf})"] = nf

        with col_sel:
            selected_label = st.selectbox("Select session:", list(notes_options.keys()))

        selected_notes_file = notes_options[selected_label]

        # Show live badge if this is the active session
        if (
            st.session_state.monitoring_active
            and st.session_state.session_id
            and selected_notes_file == f"class_notes_{st.session_state.session_id}.json"
        ):
            st.success("🔴 **Live — recording in progress.** Refresh to see new segments.")

        # ── Load notes data ───────────────────────────────────────────────────
        try:
            with open(selected_notes_file, "r", encoding="utf-8") as f:
                notes_data = json.load(f)
        except Exception as e:
            st.error(f"❌ Could not load {selected_notes_file}: {e}")
            st.stop()

        full_transcript = notes_data.get("full_transcript", "").strip()
        segments        = notes_data.get("segments", [])
        saved_at        = notes_data.get("timestamp", "")

        if saved_at:
            try:
                dt_saved = datetime.fromisoformat(saved_at)
                st.caption(f"Last updated: {dt_saved.strftime('%B %d, %Y at %I:%M:%S %p')}")
            except Exception:
                pass

        # ── Metrics row ───────────────────────────────────────────────────────
        word_count = len(full_transcript.split()) if full_transcript else 0
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("🎙️ Segments", len(segments))
        col_m2.metric("📝 Total Words", word_count)
        col_m3.metric("⏱️ Duration covered", f"{len(segments) * 30}s" if segments else "—")

        st.markdown("---")

        # ── Tabs ──────────────────────────────────────────────────────────────
        tab_raw, tab_segments, tab_star = st.tabs(["📄 Raw", "🕐 By Segment", "⭐ Star Notes"])

        with tab_raw:
            st.subheader("Raw Transcript")
            if full_transcript:
                st.text_area(
                    label="All spoken text (full session)",
                    value=full_transcript,
                    height=500,
                    key="raw_transcript_area",
                )
                # Download button
                st.download_button(
                    label="⬇️ Download transcript (.txt)",
                    data=full_transcript,
                    file_name=selected_notes_file.replace(".json", ".txt"),
                    mime="text/plain",
                )
            else:
                st.info("No speech detected yet in this session.")

        with tab_segments:
            st.subheader("Transcript by Segment")
            if segments:
                for seg in segments:
                    with st.expander(f"🕐 {seg.get('time', '?')}"):
                        st.write(seg.get("text", ""))
            else:
                st.info("No segments recorded yet.")

        with tab_star:
            st.subheader("⭐ Star Notes — AI-Generated")
            st.caption("Organised notes and conceptual questions generated by Google Gemini from the raw transcript.")

            if not full_transcript:
                st.info("No transcript available yet. Star Notes will appear once the session is recorded.")
            elif not _gemini_available():
                st.error("❌ Gemini API key not configured.")
                st.info(
                    "Open the `.env` file in the project root and replace `your_gemini_api_key_here` "
                    "with your key from https://aistudio.google.com/app/apikey, then restart the app."
                )
            else:
                # Cache key: hash of transcript so re-generating only happens when content changes
                star_cache_key = f"star_notes_{selected_notes_file}"
                star_transcript_key = f"star_transcript_{selected_notes_file}"

                cached_star = st.session_state.get(star_cache_key)
                cached_for_transcript = st.session_state.get(star_transcript_key, "")

                # If we have cached notes for this exact transcript, show them directly
                if cached_star and cached_for_transcript == full_transcript:
                    star_data = cached_star
                else:
                    # Check if star notes are already saved in the JSON file
                    star_data = notes_data.get("star_notes")
                    if star_data and notes_data.get("star_transcript") == full_transcript:
                        st.session_state[star_cache_key] = star_data
                        st.session_state[star_transcript_key] = full_transcript
                    else:
                        star_data = None

                col_gen1, col_gen2 = st.columns([3, 1])
                with col_gen2:
                    regen = st.button("🔄 Re-generate", use_container_width=True, key="regen_star")

                if star_data is None or regen:
                    with col_gen1:
                        st.info("Click **Generate ⭐ Star Notes** to process this transcript with Gemini.")
                    if st.button("✨ Generate ⭐ Star Notes", type="primary", use_container_width=True, key="gen_star") or regen:
                        with st.spinner("Gemini is reading the transcript and writing notes…"):
                            try:
                                star_data = generate_star_notes(full_transcript)
                                # Persist into the JSON file so it survives page reloads
                                notes_data["star_notes"] = star_data
                                notes_data["star_transcript"] = full_transcript
                                with open(selected_notes_file, "w", encoding="utf-8") as f:
                                    json.dump(notes_data, f, indent=4, ensure_ascii=False)
                                st.session_state[star_cache_key] = star_data
                                st.session_state[star_transcript_key] = full_transcript
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Gemini error: {e}")

                if star_data:
                    # ── Organised Notes ───────────────────────────────────────
                    st.markdown("### 📚 Organised Notes")
                    notes_md = star_data.get("notes", "")
                    if notes_md:
                        st.markdown(notes_md)

                        # ── Action buttons row ────────────────────────────────
                        btn_dl, btn_listen = st.columns([2, 1])
                        with btn_dl:
                            st.download_button(
                                label="⬇️ Download Star Notes (.md)",
                                data=notes_md,
                                file_name=selected_notes_file.replace(".json", "_star_notes.md"),
                                mime="text/markdown",
                                use_container_width=True,
                            )
                        with btn_listen:
                            if st.button("🔊 Listen to Notes", use_container_width=True, key="listen_star"):
                                st.session_state["play_star_audio"] = True

                        # ── Audio player (shown once Listen is clicked) ────────
                        if st.session_state.get("play_star_audio"):
                            with st.spinner("Generating audio…"):
                                plain_text = _markdown_to_plain(notes_md)
                                audio_bytes = _tts_audio_bytes(plain_text)
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                                if st.button("⏹ Stop / Hide Player", key="stop_star_audio"):
                                    st.session_state["play_star_audio"] = False
                                    st.rerun()
                            else:
                                st.error("⚠️ Could not generate audio. Make sure `gTTS` is installed: `pip install gTTS`")
                                st.session_state["play_star_audio"] = False
                    else:
                        st.warning("No notes were generated.")

                    # ── Questions ─────────────────────────────────────────────
                    questions = star_data.get("questions", [])
                    if questions:
                        st.markdown("---")
                        st.markdown("### 🤔 Practice Questions")
                        for i, q in enumerate(questions, 1):
                            st.markdown(f"**Q{i}.** {q}")

# ─────────────────────────────────────────────────────────────────────────────
elif page == "⚙️ Settings":
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    st.subheader("📊 Focus Monitoring Settings")
    
    # Focus Threshold
    threshold = st.slider(
        "🎯 Default Focus Threshold (%)",
        min_value=0,
        max_value=100,
        value=st.session_state.focus_threshold,
        step=5,
        help="Minimum focus percentage required for students to pass"
    )
    
    if st.button("💾 Save Threshold"):
        st.session_state.focus_threshold = threshold
        st.success(f"✅ Focus threshold updated to {threshold}%")
    
    st.markdown("---")
    
    # System Configuration
    st.subheader("🔧 System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Student Photos Path:**
        `{dashboard.student_photos_path}`
        
        **Total Students:**
        {len(dashboard.get_registered_students())}
        """)
    
    with col2:
        st.info(f"""
        **Reports Directory:**
        `{dashboard.reports_dir}`
        
        **Total Reports:**
        {len(dashboard.get_all_reports())}
        """)
    
    st.markdown("---")
    
    # Report Management
    st.subheader("🗂️ Report Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Delete All Reports", type="secondary"):
            confirm = st.checkbox("⚠️ Confirm deletion of all reports")
            if confirm:
                reports = dashboard.get_all_reports()
                for report in reports:
                    dashboard.delete_report(report)
                st.success(f"✅ Deleted {len(reports)} reports")
                st.rerun()
    
    with col2:
        if st.button("📥 Export All Reports"):
            st.info("📦 Export functionality - Coming soon!")
    
    st.markdown("---")
    
    # About
    st.subheader("ℹ️ About")
    
    st.info("""
    **Sahayak AI**
    
    Version: 1.0.0
    
    Features:
    - Real-time face recognition
    - Focus tracking
    - Mobile phone detection
    - Attendance monitoring
    - Comprehensive reporting
    
    For support, contact your system administrator.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div class='footer-bar'>
    🎓 <strong>Sahayak AI</strong> &nbsp;|&nbsp; Made with ❤️ using Streamlit &nbsp;|&nbsp; v1.0.0
</div>
""", unsafe_allow_html=True)
