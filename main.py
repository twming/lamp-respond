from treehole_m3_51 import process_once
from treehole_m4_5 import ResponseEngine

import time
import treehole_state
import sounddevice as sd
import pygame

from dataclasses import dataclass

@dataclass
class Utterance:
    accepted: bool
    emotion: str
    response: str

def build_utterance(label, emotion):
    if label != "VALID":
        return Utterance(False, "Normal", "Silence")

    emotion_to_response = {
        "Heavy": "Deep",
        "Joy": "Soft",
        "Agitated": "Brief",
        "Normal": "Soft",
    }

    response = emotion_to_response.get(emotion, "Soft")
    return Utterance(True, emotion, response)


def main():
    state = "SLEEP"
    engine = ResponseEngine()
    ambient_flag = None

    try:
        while True:
            label, emotion, ambient_flag = process_once(state)

            utterance = build_utterance(label, emotion)
            engine.respond_to_utterance(utterance)
            while treehole_state.is_playing:
                time.sleep(0.1)

            if ambient_flag == "NOISY":
                state = "SLEEP"
            elif label in ["VALID", "BACKGROUND", "SHORT", "EMPTY"]:
                state = "AWAKE"
            else: #NOISY Speech
                state = "SLEEP"
    
    except KeyboardInterrupt:
        print("\n[MAIN] Ctrl+C detected. Exit Tree-Hole...")

    finally:
        sd.stop()
        pygame.quit()
        print("[MAIN] Shutdown complete.")



if __name__ == "__main__":
    main()