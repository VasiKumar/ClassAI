"""
Audio Recorder & Transcriber
Records classroom audio and transcribes with Whisper base model.
Saves transcription as class_notes_<session_id>.json
Run alongside student_monitor.py during a class session.

Design: a dedicated recording thread fills a queue with audio chunks
while the main thread drains the queue and transcribes — no gaps.
"""

import os
import sys
import json
import time
import queue
import threading
import argparse
from datetime import datetime

# ─── Audio & Whisper ──────────────────────────────────────────────────────────
try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠ sounddevice not available. Install: pip install sounddevice")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠ openai-whisper not available. Install: pip install openai-whisper")

# ─── Constants ────────────────────────────────────────────────────────────────
SAMPLE_RATE   = 16000   # Whisper expects 16 kHz
CHUNK_SECONDS = 30      # Each audio chunk length in seconds
STOP_FILE     = "monitor_stop.signal"
NOTES_DIR     = "."


# ─── Helpers ──────────────────────────────────────────────────────────────────
def transcribe_chunk(model, audio_data: "np.ndarray") -> str:
    """Transcribe a numpy float32 mono array with Whisper base."""
    try:
        audio_float = audio_data.astype(np.float32)
        if audio_float.ndim > 1:
            audio_float = audio_float.mean(axis=1)
        max_val = np.abs(audio_float).max()
        if max_val > 0:
            audio_float = audio_float / max_val
        result = model.transcribe(audio_float, language="en", fp16=False)
        return result.get("text", "").strip()
    except Exception as e:
        print(f"  Transcription error: {e}")
        return ""


def save_notes(notes_file: str, segments: list, full_transcript: str):
    """Write current transcript state to disk atomically."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "segments": segments,
        "full_transcript": full_transcript,
    }
    tmp = notes_file + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(tmp, notes_file)


# ─── Recording thread ─────────────────────────────────────────────────────────
def recording_thread(audio_queue: queue.Queue, stop_event: threading.Event):
    """
    Continuously records CHUNK_SECONDS of audio and puts each chunk
    onto audio_queue.  Runs until stop_event is set.
    """
    chunk_samples = int(CHUNK_SECONDS * SAMPLE_RATE)
    print("🎤 Recording thread started.")
    while not stop_event.is_set():
        try:
            chunk = sd.rec(
                chunk_samples,
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32",
            )
            # Poll stop_event every second while recording so we can stop quickly
            for _ in range(CHUNK_SECONDS):
                if stop_event.is_set():
                    sd.stop()
                    break
                time.sleep(1)
            else:
                sd.wait()  # make sure recording finished if not stopped early

            audio_queue.put(chunk.copy())
        except Exception as e:
            print(f"  Recording error: {e}")
            time.sleep(1)

    print("🎤 Recording thread stopped.")


# ─── Main transcription loop ──────────────────────────────────────────────────
def record_and_transcribe(session_id: str):
    if not AUDIO_AVAILABLE or not WHISPER_AVAILABLE:
        print("❌ Required packages missing. Exiting audio recorder.")
        return

    notes_file = os.path.join(NOTES_DIR, f"class_notes_{session_id}.json")
    print(f"\n{'='*60}")
    print("CLASSROOM AUDIO RECORDER")
    print(f"{'='*60}")
    print(f"• Whisper model : base")
    print(f"• Sample rate   : {SAMPLE_RATE} Hz")
    print(f"• Chunk size    : {CHUNK_SECONDS}s")
    print(f"• Notes file    : {notes_file}")
    print(f"{'='*60}\n")

    print("⏳ Loading Whisper base model...")
    try:
        model = whisper.load_model("base")
        print("✓ Whisper base model loaded\n")
    except Exception as e:
        print(f"❌ Failed to load Whisper: {e}")
        return

    segments: list = []
    full_transcript_parts: list = []
    session_start = time.time()

    audio_queue: queue.Queue = queue.Queue()
    stop_event = threading.Event()

    # Start the dedicated recording thread
    rec_thread = threading.Thread(
        target=recording_thread,
        args=(audio_queue, stop_event),
        daemon=True,
    )
    rec_thread.start()

    print("Running — transcribing every chunk as it arrives...\n")

    try:
        while True:
            # ── Check stop signal from dashboard ─────────────────────────────
            if os.path.exists(STOP_FILE):
                print("\n🛑 Stop signal received. Finishing current chunk then saving...")
                stop_event.set()
                break

            # ── Wait for the next recorded chunk (timeout so we can re-check stop) ──
            try:
                audio_chunk = audio_queue.get(timeout=2)
            except queue.Empty:
                continue

            chunk_elapsed = time.time() - session_start - CHUNK_SECONDS
            mm = int(max(0, chunk_elapsed)) // 60
            ss = int(max(0, chunk_elapsed)) % 60
            time_label = f"{mm}:{ss:02d}"

            print(f"📝 Transcribing chunk [{time_label}]...")
            text = transcribe_chunk(model, audio_chunk)

            if text:
                segments.append({"time": time_label, "text": text})
                full_transcript_parts.append(text)
                save_notes(notes_file, segments, " ".join(full_transcript_parts))
                print(f"  ✓ [{time_label}] {text[:90]}{'...' if len(text) > 90 else ''}")
            else:
                print(f"  [{time_label}] (silence / no speech)")

    except KeyboardInterrupt:
        print("\n⌨ Interrupted by user.")
        stop_event.set()

    # ── Drain any remaining chunks already in the queue ───────────────────────
    stop_event.set()
    rec_thread.join(timeout=5)

    remaining = 0
    while not audio_queue.empty():
        try:
            audio_chunk = audio_queue.get_nowait()
            chunk_elapsed = time.time() - session_start
            mm = int(chunk_elapsed) // 60
            ss = int(chunk_elapsed) % 60
            time_label = f"{mm}:{ss:02d}"
            print(f"📝 Transcribing final chunk [{time_label}]...")
            text = transcribe_chunk(model, audio_chunk)
            if text:
                segments.append({"time": time_label, "text": text})
                full_transcript_parts.append(text)
            remaining += 1
        except queue.Empty:
            break

    save_notes(notes_file, segments, " ".join(full_transcript_parts))
    total = time.time() - session_start
    print(f"\n✅ Done. {len(segments)} segments transcribed over {total:.0f}s.")
    print(f"   Notes saved → {notes_file}")


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classroom audio recorder — Whisper base")
    parser.add_argument(
        "--session-id",
        type=str,
        default=datetime.now().strftime("%Y%m%d_%H%M%S"),
        help="Session ID matching the monitoring report",
    )
    args = parser.parse_args()
    record_and_transcribe(args.session_id)

