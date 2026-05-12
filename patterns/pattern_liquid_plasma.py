# ═══════════════════════════════════════════════════════════
# PatternFlow - Liquid Plasma Pattern
# CircuitPython implementation for MatrixPortal M4
# License: MIT
# ═══════════════════════════════════════════════════════════

import math
from config import PANEL_RES_W, PANEL_RES_H


class LiquidPlasmaPattern:
    """
    Liquid Plasma pattern - Flowing plasma effect with HSV color mapping.
    
    Knobs:
    - Knob 0: Hue Base (0.0-1.0)
    - Knob 1: Speed (0.0-5.0)
    - Knob 2: Scale (0.02-0.2)
    - Knob 3: Chaos (0.0-3.0)
    """
    
    NAME = "Liquid Plasma"
    KNOB_LABELS = ["hue", "speed", "scale", "chaos"]
    
    # Step sizes for knob adjustments
    HUE_STEP = 0.05
    SPEED_STEP = 0.05
    SCALE_STEP = 0.01
    CHAOS_STEP = 0.1
    
    def __init__(self, display):
        self.display = display
        self.params = {
            "hue_base": 0.5,
            "speed": 1.0,
            "scale": 0.1,
            "chaos": 1.0,
            "time_acc": 0.0,
        }
        
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB."""
        h = h % 1.0
        if h < 0.0:
            h += 1.0
            
        i = int(math.floor(h * 6.0))
        f = h * 6.0 - float(i)
        p = v * (1.0 - s)
        q = v * (1.0 - f * s)
        t = v * (1.0 - (1.0 - f) * s)
        
        if i % 6 == 0:
            r, g, b = v, t, p
        elif i % 6 == 1:
            r, g, b = q, v, p
        elif i % 6 == 2:
            r, g, b = p, v, t
        elif i % 6 == 3:
            r, g, b = p, q, v
        elif i % 6 == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
            
        return (
            int(round(r * 255.0)),
            int(round(g * 255.0)),
            int(round(b * 255.0))
        )
        
    def setup(self):
        """Initialize the pattern."""
        self.params = {
            "hue_base": 0.5,
            "speed": 1.0,
            "scale": 0.1,
            "chaos": 1.0,
            "time_acc": 0.0,
        }
        
    def update(self, dt, knob_values, knob_deltas):
        """
        Update pattern state based on knob inputs.
        
        Args:
            dt: Delta time in seconds
            knob_values: List of 4 knob values
            knob_deltas: List of 4 knob deltas
        """
        # Knob 0: Hue Base
        self.params["hue_base"] = (self.params["hue_base"] + knob_deltas[0] * self.HUE_STEP) % 1.0
        if self.params["hue_base"] < 0.0:
            self.params["hue_base"] += 1.0
            
        # Knob 1: Speed
        self.params["speed"] = self.params["speed"] + knob_deltas[1] * self.SPEED_STEP
        if self.params["speed"] < 0.0:
            self.params["speed"] = 0.0
            
        # Knob 2: Scale
        self.params["scale"] = max(0.02, min(0.2, self.params["scale"] + knob_deltas[2] * self.SCALE_STEP))
        
        # Knob 3: Chaos
        self.params["chaos"] = max(0.0, min(3.0, self.params["chaos"] + knob_deltas[3] * self.CHAOS_STEP))
        
        # Update time accumulator
        self.params["time_acc"] += dt * self.params["speed"]
        
    def draw(self):
        """Draw the pattern to the display."""
        t = self.params["time_acc"]
        s = self.params["scale"]
        c = self.params["chaos"]
        
        # Precompute row and column values to eliminate inner-loop trig functions
        # Using angle addition identities for optimization
        
        v1_arr = []
        nx_arr = []
        sin_a_arr = []
        cos_a_arr = []
        sin_d_arr = []
        cos_d_arr = []
        
        for x in range(PANEL_RES_W):
            nx = x * s
            nx_arr.append(nx)
            v1_arr.append(math.sin(nx + t))
            
            warp_y = math.cos(nx * 2.0 - t * 1.2) * c
            A = nx * 1.5 + t * 1.5
            sin_a_arr.append(math.sin(A))
            cos_a_arr.append(math.cos(A))
            
            D = warp_y * 1.5
            sin_d_arr.append(math.sin(D))
            cos_d_arr.append(math.cos(D))
            
        v2_arr = []
        ny_arr = []
        sin_b_arr = []
        cos_b_arr = []
        sin_c_arr = []
        cos_c_arr = []
        
        for y in range(PANEL_RES_H):
            ny = y * s
            ny_arr.append(ny)
            v2_arr.append(math.cos(ny - t * 0.8))
            
            warp_x = math.sin(ny * 2.0 + t) * c
            B = warp_x * 1.5
            sin_b_arr.append(math.sin(B))
            cos_b_arr.append(math.cos(B))
            
            C = ny * 1.5 - t
            sin_c_arr.append(math.sin(C))
            cos_c_arr.append(math.cos(C))
            
        # Draw pixels
        for y in range(PANEL_RES_H):
            v2 = v2_arr[y]
            sin_b = sin_b_arr[y]
            cos_b = cos_b_arr[y]
            sin_c = sin_c_arr[y]
            cos_c = cos_c_arr[y]
            ny = ny_arr[y]
            
            for x in range(PANEL_RES_W):
                v1 = v1_arr[x]
                
                # Reconstruct nested sine/cosine without inner-loop trig calls
                v3 = sin_a_arr[x] * cos_b + cos_a_arr[x] * sin_b
                v4 = cos_c * cos_d_arr[x] - sin_c * sin_d_arr[x]
                
                field = abs(v1 + v2 + v3 + v4)
                
                val = 1.0 - (field * 0.5)
                val = max(0.0, min(1.0, val))
                
                # Fast cubic curve (replace pow(val, 3.0))
                val = val * val * val
                
                val = max(0.0, min(1.0, val * 2.5))
                
                hue = self.params["hue_base"] + nx_arr[x] * 0.1 + ny * 0.1 + field * 0.05
                
                r, g, b = self._hsv_to_rgb(hue, 1.0 - val * 0.2, val)
                self.display.set_back_pixel(x, y, r, g, b)
