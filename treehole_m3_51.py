
"""
Tree-Hole MVP
M3.5 Sound Features tunning
"""

import time
import random
import numpy as np
import sounddevice as sd
import soundfile as sf
import torch

torch.set_num_threads(1)

vad_model, vad_utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False
)

(get_speech_timestamps, _, _, _, _) = vad_utils


from dataclasses import dataclass

@dataclass
class EmotionFeatures:
    avg_rms: float
    rms_std: float
    pause_ratio: float
    zcr_mean: float
    zcr_std: float
    peak_to_avg: float
    jumpiness: float
    peak_density: float
    peak_gap_mean: float
    peak_width_mean: float

# =========================================================
# SLEEP
# =========================================================

# =========================================================
# Init

def init_parameters():
    print("\n[SLEEP] Initialising parameters...")

    return

# =========================================================
# SLEEP -main

def run_sleep():
    init_parameters()
    #input("[SLEEP] Press ENTER to wake Tree-Hole...睡眠中，回车启动 ")
    print(f"\nTree-Hole...睡眠中")
    return


# =========================================================
# AWAKE
# =========================================================

# =========================================================
# Capture 5s ambient

def frame_rms(frame):
    return np.sqrt(np.mean(frame ** 2))


def frame_zcr(frame):
    return np.mean(np.abs(np.diff(np.sign(frame)))) / 2.0


def capture_ambient_block(seconds=5, fs=16000):
    print(f"\n[AWAKE] Waiting for Quietness 我想静静 {seconds}s...")

    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()

    return audio.flatten()


# =========================================================
# Ambient suitability

def analyze_ambient(audio):
    avg_rms = frame_rms(audio)
    zcr = frame_zcr(audio)
    activity = np.mean(np.abs(audio) > 0.003)

    print(f"[AWAKE DEBUG] avg_rms={avg_rms:.6f} zcr={zcr:.3f} activity={activity:.3f}")

    if avg_rms >= 0.0060 and activity >= 0.30:
        return False

    return True

# =========================================================
# AWAKE -main
 
def run_awake(from_sleep):
    ambient_flag = None

    if from_sleep:    
        print("\n[AWAKE] Awakening ... 苏醒 ")
            
        audio = capture_ambient_block(5)
        suitable = analyze_ambient(audio)

        if suitable:
            sd.play(*sf.read("sounds/TreeHole_Awake.wav"))
            time.sleep(10)
            print("\n[AWAKE]Now Speak ...说吧 ")
            ambient_flag = "READY"
        else:
            print("[AWAKE] Ambient unsuitable, ...太吵了 ")
            ambient_flag= "NOISY"
            
    else:
        # Proceed to listen
        print("Continue ... 继续 ")

    return ambient_flag

# =========================================================
# LISTEN
# =========================================================

# =========================================================
# Read Block

def read_five_seconds(fs=16000):
    block = sd.rec(int(fs * 5.0), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    return block.flatten()

# =========================================================
# Check end of speech

def has_speech_vad(block, fs=16000, min_speech_ratio=0.10):
    wav = torch.from_numpy(block)
    speech_segments = get_speech_timestamps(wav, vad_model, sampling_rate=fs)

    speech_samples = sum(seg["end"] - seg["start"] for seg in speech_segments)
    speech_ratio = speech_samples / len(block)

    print(f"[VAD DEBUG] speech_ratio={speech_ratio:.3f}")

    return speech_ratio >= min_speech_ratio

# =========================================================
# LISTEN -main

def run_listen():
    speech_blocks = []

    while True:
        five_sec_block = read_five_seconds()

        if has_speech_vad(five_sec_block):
            speech_blocks.append(five_sec_block)
        else:
            print(" end_of_speech ")
            break

    return speech_blocks

# =========================================================
# CLASSIFY
# =========================================================

# =========================================================
# FEATURE EXTRACTION (unchanged)

def envelope_peak_features(frame, sr=16000):
    x = np.abs(frame).astype(np.float32)

    if len(x) == 0:
        return 0.0, 0.0, 0.0

    win = max(1, int(0.02 * sr))  # 20 ms smoothing
    kernel = np.ones(win, dtype=np.float32) / win
    env = np.convolve(x, kernel, mode="same")

    thr = max(0.001, 0.35 * float(np.max(env)))
    above = env > thr

    segments = []
    start = None
    for i, flag in enumerate(above):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            segments.append((start, i))
            start = None
    if start is not None:
        segments.append((start, len(above)))

    if not segments:
        return 0.0, 0.0, 0.0

    peak_count = len(segments)
    duration_s = len(frame) / sr
    peak_density = peak_count / duration_s if duration_s > 0 else 0.0

    widths = [(b - a) / sr for a, b in segments]
    peak_width_mean = float(np.mean(widths)) if widths else 0.0

    if len(segments) > 1:
        gaps = [(segments[i][0] - segments[i - 1][1]) / sr for i in range(1, len(segments))]
        peak_gap_mean = float(np.mean(gaps)) if gaps else 0.0
    else:
        peak_gap_mean = duration_s

    return peak_density, peak_gap_mean, peak_width_mean


def extract_emotion_features(frames, sr=16000):
    rms_values = np.array([frame_rms(f) for f in frames], dtype=np.float32)
    zcr_values = np.array([frame_zcr(f) for f in frames], dtype=np.float32)
    
    peak_feats = [envelope_peak_features(f, sr=sr) for f in frames]
    peak_density_values = np.array([p[0] for p in peak_feats], dtype=np.float32) if peak_feats else np.array([], dtype=np.float32)
    peak_gap_values = np.array([p[1] for p in peak_feats], dtype=np.float32) if peak_feats else np.array([], dtype=np.float32)
    peak_width_values = np.array([p[2] for p in peak_feats], dtype=np.float32) if peak_feats else np.array([], dtype=np.float32)

    if len(rms_values) > 0:
        avg_rms = float(np.mean(rms_values))
        rms_std = float(np.std(rms_values))
        peak_rms = float(np.max(rms_values))
        peak_to_avg = peak_rms / (avg_rms + 1e-6)
    else:
        avg_rms = 0.0
        rms_std = 0.0
        peak_to_avg = 0.0

    if len(rms_values) > 1:
        jumpiness = float(np.mean(np.abs(np.diff(rms_values))))
    else:
        jumpiness = 0.0

    return EmotionFeatures(
        avg_rms=avg_rms,
        rms_std=rms_std,
        pause_ratio=0.0,
        zcr_mean=float(np.mean(zcr_values)) if len(zcr_values) else 0.0,
        zcr_std=float(np.std(zcr_values)) if len(zcr_values) else 0.0,
        peak_to_avg=peak_to_avg,
        jumpiness=jumpiness,
        peak_density=float(np.mean(peak_density_values)) if len(peak_density_values) else 0.0,
        peak_gap_mean=float(np.mean(peak_gap_values)) if len(peak_gap_values) else 0.0,
        peak_width_mean=float(np.mean(peak_width_values)) if len(peak_width_values) else 0.0,
    )


# =========================================================
# Feature ENTRY POINT

def compute_features(speech_blocks):
      
    return extract_emotion_features(speech_blocks)


# =========================================================
# CLASSIFY FILTER (now uses features — no duplication)

def run_classify_filter(speech_blocks, features):
    n = len(speech_blocks)

    if n == 0:
        return "EMPTY"

    if n < 3:
        return "SHORT"

    return "VALID"


# =========================================================
# CLASSIFY EMOTION (unchanged)

def run_classify_emotion(features):
    avg_rms = features.avg_rms
    peak_to_avg = features.peak_to_avg
    jumpiness = features.jumpiness
    zcr_mean = features.zcr_mean

    peak_density = features.peak_density
    peak_gap_mean = features.peak_gap_mean
    peak_width_mean = features.peak_width_mean

    print("peak_density ", peak_density)
    print("peak_gap_mean ", peak_gap_mean)
    print("peak_width_mean ", peak_width_mean)
    print("jumpiness ", jumpiness)
    print("Peak_to_avg ", peak_to_avg)
    
    # --- 1) NORMAL as anchor ---
    # --- 1) NORMAL as anchor ---
    if (
        0.1 <= peak_gap_mean < 0.40
        and 2.5 <= peak_density <= 5 
        and jumpiness < 0.004
    ):
        return "Normal"

    # --- 2) Wider gaps than Normal -> Heavy ---
    if (
        (jumpiness < 0.006 and peak_density < 2.5) or peak_gap_mean >= 0.40
    ):
        return "Heavy"

    # --- 3) Narrower gaps than Normal -> Joy / Agitated candidate ---
    if (
        (peak_gap_mean < 0.3
        and peak_density > 3.0)
        or jumpiness >= 0.004
    ):
        # Agitated = spikier / jaggier / narrower envelope
        if (
            jumpiness >= 0.007
            and peak_to_avg >= 1
            and peak_width_mean < 0.04
        ):
            return "Agitated"

        # Joy = smoother / wider envelope
        else: 
            return "Joy"

    return "Unknown"

def process_once(state):
    label = ""
    emotion = "unknown"
    ambient_flag = None

    # --- SLEEP / AWAKE ---
    if state == "SLEEP": 
        run_sleep()
        ambient_flag = run_awake(True)  # 5s Ambient Check needed
    else:
        ambient_flag = run_awake(False) # Quick ambient check

    if ambient_flag == "NOISY":
        return label, emotion, ambient_flag
    # --- LISTEN ---
    speech_blocks = run_listen()

    # --- COMPUTE FEATURES (ONCE) ---
    features = compute_features(speech_blocks)
    
    # --- FILTER ---
    label = run_classify_filter(speech_blocks, features)

    print(f"[MAIN] label={label}")

          
    # VALID → EMOTION
    if label == "VALID":
        emotion = run_classify_emotion(features)
        print("emotion =", emotion)

    return label, emotion, ambient_flag


def main():
    process_once("SLEEP")

if __name__ == "__main__":
        main()

