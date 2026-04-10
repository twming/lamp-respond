
# Tree-Hole MVP
# Module 4.5 – Response Engine (Graphics Upgrade)

import time
import random
from dataclasses import dataclass
from pathlib import Path

import sounddevice as sd
import soundfile as sf
import numpy as np
import treehole_state
import os
import sys
import pygame

from sense_hat import SenseHat

# -------------------------------------------------
# Helper functions
# -------------------------------------------------

def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def smoothstep01(x):
    x = clamp(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


# -------------------------------------------------
# Response profile
# -------------------------------------------------

@dataclass(frozen=True)
class ResponseProfile:

    name: str

    glow_enabled: bool
    glow_total_s: float
    glow_attack_s: float
    glow_release_s: float
    glow_peak: float

    hum_enabled: bool

    glow_hold_s: float = 0.0
    residual_glow_s: float = 0.0

    glow_style: str = "breathe"
    glow_delay_s: float = 0.0
    glow_motion_amt: float = 0.03


# -------------------------------------------------
# Response profiles
# -------------------------------------------------

RESPONSE_PROFILES = {

    "Silence": ResponseProfile("Silence", False,0,0,0,0,False),

    "Glow": ResponseProfile("Glow", True,2.0,0.6,1.0,0.6,False,0.4),

    "Brief": ResponseProfile("Brief", True,1.8,0.3,0.8,0.65,True,0.4),

    "Soft": ResponseProfile("Soft", True,3.2,0.8,1.4,0.7,True,1.2),

    "Steady": ResponseProfile("Steady", True,5.0,1.0,1.6,0.75,True,2.0),

    "Deep": ResponseProfile("Deep", True,6.8,1.2,1.8,0.85,True,2.8),
}


# -------------------------------------------------
# Glow Engine (pygame)
# -------------------------------------------------

class GlowEngine1:
    def __init__(self):
        self.sense = SenseHat()

        r = (255,  0,  0)
        g = (  0,255,  0)
        bl = (  0,  0,255)
        w = (255,255,255)   
        b = (0  ,  0,  0)   

        self.pixels1 = [
                w,w,w,w,w,w,w,w,
                w,w,w,w,w,w,w,w,
                w,w,w,w,w,w,w,w,
                w,w,w,w,w,w,w,w,
                w,w,w,w,w,w,w,w,
                w,w,w,w,w,w,w,w,
                w,w,w,w,w,w,w,w,
                w,w,w,w,w,w,w,w
        ]
        self.pixels2 = [
                b,b,b,b,b,b,b,b,
                b,w,w,w,w,w,w,b,
                b,w,w,w,w,w,w,b,
                b,w,w,w,w,w,w,b,
                b,w,w,w,w,w,w,b,
                b,w,w,w,w,w,w,b,
                b,w,w,w,w,w,w,b,
                b,b,b,b,b,b,b,b
        ]
        self.pixels3 = [
                b,b,b,b,b,b,b,b,
                b,b,b,b,b,b,b,b,
                b,b,w,w,w,w,b,b,
                b,b,w,w,w,w,b,b,
                b,b,w,w,w,w,b,b,
                b,b,w,w,w,w,b,b,
                b,b,b,b,b,b,b,b,
                b,b,b,b,b,b,b,b
	]
        self.pixels4 = [
                b,b,b,b,b,b,b,b,
                b,b,b,b,b,b,b,b,
                b,b,b,b,b,b,b,b,
                b,b,b,w,w,b,b,b,
                b,b,b,w,w,b,b,b,
                b,b,b,b,b,b,b,b,
                b,b,b,b,b,b,b,b,
                b,b,b,b,b,b,b,b
        ]
        self.sense.set_pixels(self.pixels4)

    def run(self, profile):  
        self.sense.set_pixels(self.pixels4)
        time.sleep(0.8)
        self.sense.set_pixels(self.pixels3)
        time.sleep(0.6)
        self.sense.set_pixels(self.pixels2)
        time.sleep(0.3)
        self.sense.set_pixels(self.pixels1)
        time.sleep(0.1)
        self.sense.set_pixels(self.pixels2)
        time.sleep(0.3)
        self.sense.set_pixels(self.pixels4)
        time.sleep(0.5)

class GlowEngine:

    def __init__(self, width=300, height=300, fps=30):
        pygame.init()
        self.width = width
        self.height = height
        self.fps = fps

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Tree-Hole Glow")

        self.clock = pygame.time.Clock()

    def _brightness_at(self, t, profile):

        attack = profile.glow_attack_s
        hold = profile.glow_hold_s
        total = profile.glow_total_s
        peak = profile.glow_peak

        if t <= attack:
            p = smoothstep01(t / attack)
            return peak * (p ** 1.4)

        if t <= attack + hold:
            breathe = 0.035 * peak * np.sin(2 * np.pi * 0.32 * (t - attack))
            return peak + breathe

        fade_window = total - (attack + hold)
        p = 1 - smoothstep01((t - attack - hold) / fade_window)
        return peak * (p ** 1.3)

    def _draw_glow(self, brightness):

        self.screen.fill((10, 8, 6))
        center = (self.width // 2, self.height // 2)
        base_radius = 30 + int(brightness * 90)

        for i in range(6):
            alpha = int(80 * (1 - i / 6) * brightness)
            radius = int(base_radius * (1 + i * 0.25))

            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(
                surf,
                (255, 200, 120, alpha),
                center,
                radius
            )
            self.screen.blit(surf, (0, 0))

        pygame.draw.circle(
            self.screen,
            (255, 210, 140),
            center,
            int(base_radius * 0.6)
        )

    def run(self, profile):

        start = time.perf_counter()

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            elapsed = time.perf_counter() - start

            if elapsed >= profile.glow_total_s:
                break

            brightness = self._brightness_at(elapsed, profile)

            self._draw_glow(brightness)

            pygame.display.flip()
            self.clock.tick(self.fps)

        self.screen.fill((10, 8, 6))
        pygame.display.flip()


# -------------------------------------------------
# Hum Engine
# -------------------------------------------------

class HumSynth:

    def __init__(self, sound_dir="sounds"):
        import sys
        import os

        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        self.sound_dir = os.path.join(base_dir, sound_dir)

    
    def play(self, response_name, emotion):

        if emotion == "Joy":
            variant = 1
        elif emotion == "Heavy":
            variant = 3
        elif emotion == "Agitated":
            variant = 2
        else:
            variant = 2

        if random.random() < 0.25:
            variant = random.choice([1, 2, 3])

        filename = f"TreeHole_{response_name}_{variant}.wav"
        filepath = os.path.join(self.sound_dir, filename)

        data, samplerate = sf.read(filepath)
        sd.play(data, samplerate)
        sd.wait()


# -------------------------------------------------
# Expressive logic
# -------------------------------------------------

NORMAL_PROB = 0.5

VARIANT_WEIGHTS = [
    ("same_sound_diff_glow", 0.30),
    ("same_glow_diff_sound", 0.30),
    ("sound_only", 0.20),
    ("glow_only", 0.20),
]

NEIGHBOR_PROFILE = {
    "Brief": ["Glow", "Soft"],
    "Soft": ["Brief", "Steady"],
    "Steady": ["Soft", "Deep"],
    "Deep": ["Steady"],
    "Glow": ["Brief"],
}

def weighted_choice(weighted_items):
    items = [x[0] for x in weighted_items]
    weights = [x[1] for x in weighted_items]
    return random.choices(items, weights=weights, k=1)[0]


def choose_neighbor(response):
    neighbors = NEIGHBOR_PROFILE.get(response, [response])
    return random.choice(neighbors)


def expressive_decision(response):

    if random.random() < NORMAL_PROB:
        return {
            "mode": "normal",
            "sound_response": response,
            "glow_response": response,
            "sound_enabled": True,
            "glow_enabled": True
        }

    variant = weighted_choice(VARIANT_WEIGHTS)
    neighbor = choose_neighbor(response)

    if variant == "same_sound_diff_glow":
        return {
            "mode": variant,
            "sound_response": response,
            "glow_response": neighbor,
            "sound_enabled": True,
            "glow_enabled": True
        }

    if variant == "same_glow_diff_sound":
        return {
            "mode": variant,
            "sound_response": neighbor,
            "glow_response": response,
            "sound_enabled": True,
            "glow_enabled": True
        }

    if variant == "sound_only":
        return {
            "mode": variant,
            "sound_response": response,
            "glow_response": response,
            "sound_enabled": True,
            "glow_enabled": False
        }

    if variant == "glow_only":
        return {
            "mode": variant,
            "sound_response": response,
            "glow_response": response,
            "sound_enabled": False,
            "glow_enabled": True
        }


# -------------------------------------------------
# Response Engine
# -------------------------------------------------

class ResponseEngine:

    def __init__(self):
        #self.glow_engine = GlowEngine()
        self.glow_engine = GlowEngine1()
        self.hum_synth = HumSynth()

    def get_profile(self, name):
        return RESPONSE_PROFILES[name]

    def respond_to_utterance(self, utterance):

        if not utterance.accepted:
            print(" Ignored → no response")
            return

        response = utterance.response

        if response == "Silence":
            print(" Silence → no response")
            return

        self.execute(utterance)

    def execute(self, utterance):

        base_response = utterance.response
        emotion = utterance.emotion

        treehole_state.is_playing = True

        try:

            decision = expressive_decision(base_response)

            sound_response = decision["sound_response"]
            glow_response = decision["glow_response"]

            print("\n--- RESPONSE START ---")
            print(
                f" mode={decision['mode']} "
                f"sound={sound_response} glow={glow_response}"
            )

            # Glow
            if decision["glow_enabled"]:

                glow_profile = self.get_profile(glow_response)
                print(glow_profile)
                self.glow_engine.run(glow_profile)
                #if glow_profile.glow_enabled:
                #    input("\nDebug pause — review console, then press Enter for glow...")
                #    self.glow_engine.run(glow_profile)

            # Hum
            if decision["sound_enabled"]:

                sound_profile = self.get_profile(sound_response)

                if sound_profile.hum_enabled:
                    self.hum_synth.play(sound_profile.name, emotion)

            print("--- RESPONSE END ---\n")

        finally:
            treehole_state.is_playing = False
