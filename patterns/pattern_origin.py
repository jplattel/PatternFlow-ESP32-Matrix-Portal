# ═══════════════════════════════════════════════════════════
# PatternFlow - Origin Pattern
# CircuitPython implementation for MatrixPortal M4
# License: MIT
# ═══════════════════════════════════════════════════════════

import math
from config import PANEL_RES_W, PANEL_RES_H


class OriginPattern:
    """
    Origin pattern - Grid-based pattern with distance-based wave animation.
    
    Knobs:
    - Knob 0: Hue (0-360)
    - Knob 1: Speed (0.0-5.0)
    - Knob 2: Mode (0-4 presets)
    - Knob 3: Frequency (0.1-1000)
    """
    
    NAME = "Origin"
    KNOB_LABELS = ["hue", "speed", "mode", "freq"]
    
    # Pattern presets
    PRESETS = [
        {"rows": 1, "cols": 2, "gap": 4, "tileSize": 56, "gridStep": 7, "gridCells": 8},
        {"rows": 2, "cols": 4, "gap": 3, "tileSize": 27, "gridStep": 3, "gridCells": 9},
        {"rows": 3, "cols": 6, "gap": 2, "tileSize": 18, "gridStep": 3, "gridCells": 6},
        {"rows": 3, "cols": 6, "gap": 2, "tileSize": 18, "gridStep": 2, "gridCells": 9},
        {"rows": 6, "cols": 12, "gap": 0, "tileSize": 10, "gridStep": 2, "gridCells": 5},
    ]
    
    # Color ramp stops
    COLOR_RAMP = [
        {"position": 0.000, "r": 0, "g": 0, "b": 0},
        {"position": 0.154, "r": 40, "g": 40, "b": 40},
        {"position": 0.556, "r": 255, "g": 255, "b": 255},  # Updated in update_color_ramp
        {"position": 0.816, "r": 255, "g": 255, "b": 255},
        {"position": 1.000, "r": 255, "g": 255, "b": 255},
    ]
    
    SIN_LUT_SIZE = 256
    
    def __init__(self, display):
        self.display = display
        self.params = {
            "hueDeg": 0,
            "speed": 2.0,
            "mode": 0,
            "freq": 220.0,
        }
        self.phase = 0.0
        self.cur_mode = -1
        self.total_w = 0
        self.total_h = 0
        self.offset_x = 0
        self.offset_y = 0
        self.dist_lut = []
        self.sin_lut = []
        
        # Build lookup tables
        self._build_sin_lut()
        
    def _build_sin_lut(self):
        """Build sine lookup table for fast trigonometry."""
        self.sin_lut = []
        for i in range(self.SIN_LUT_SIZE):
            self.sin_lut.append(math.sin((i / self.SIN_LUT_SIZE) * 2.0 * math.pi))
            
    def _fast_sin(self, x):
        """Fast sine using lookup table."""
        norm = x / (2.0 * math.pi)
        norm = norm - math.floor(norm)
        if norm < 0:
            norm += 1.0
        index = int(norm * self.SIN_LUT_SIZE) & (self.SIN_LUT_SIZE - 1)
        return self.sin_lut[index]
        
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB."""
        c = v * s
        x = c * (1.0 - abs((h * 6.0) % 2.0 - 1.0))
        m = v - c
        
        if h < 1/6:
            rf, gf, bf = c, x, 0
        elif h < 2/6:
            rf, gf, bf = x, c, 0
        elif h < 3/6:
            rf, gf, bf = 0, c, x
        elif h < 4/6:
            rf, gf, bf = 0, x, c
        elif h < 5/6:
            rf, gf, bf = x, 0, c
        else:
            rf, gf, bf = c, 0, x
            
        r = int((rf + m) * 255.0)
        g = int((gf + m) * 255.0)
        b = int((bf + m) * 255.0)
        return (r, g, b)
        
    def _update_color_ramp(self, hue):
        """Update color ramp based on hue."""
        hue_norm = hue / 360.0
        hr, hg, hb = self._hsv_to_rgb(hue_norm, 1.0, 1.0)
        self.COLOR_RAMP[2] = {"position": 0.556, "r": hr, "g": hg, "b": hb}
        
    def _sample_color_ramp(self, val):
        """Sample color from ramp."""
        t = (val + 1.0) * 0.5
        t = max(0.0, min(1.0, t))
        
        r, g, b = self.COLOR_RAMP[0]["r"], self.COLOR_RAMP[0]["g"], self.COLOR_RAMP[0]["b"]
        for stop in self.COLOR_RAMP:
            if t >= stop["position"]:
                r, g, b = stop["r"], stop["g"], stop["b"]
                
        return (r, g, b)
        
    def _apply_preset(self, idx):
        """Apply a preset configuration."""
        if idx >= len(self.PRESETS):
            idx = 0
        p = self.PRESETS[idx]
        
        self.total_w = p["cols"] * p["tileSize"] + (p["cols"] + 1) * p["gap"]
        self.total_h = p["rows"] * p["tileSize"] + (p["rows"] + 1) * p["gap"]
        self.offset_x = (PANEL_RES_W - self.total_w) // 2
        self.offset_y = (PANEL_RES_H - self.total_h) // 2
        
        # Build distance LUT
        self.dist_lut = []
        cx = p["tileSize"] / 2.0
        for gy in range(p["gridCells"]):
            row = []
            for gx in range(p["gridCells"]):
                dx = gx * p["gridStep"] + p["gridStep"] / 2.0 - cx
                dy = gy * p["gridStep"] + p["gridStep"] / 2.0 - cx
                row.append(math.sqrt(dx * dx + dy * dy))
            self.dist_lut.append(row)
            
        self.cur_mode = idx
        
    def setup(self):
        """Initialize the pattern."""
        self._apply_preset(0)
        self._update_color_ramp(0.0)
        self.phase = 0.0
        
    def update(self, dt, knob_values, knob_deltas):
        """
        Update pattern state based on knob inputs.
        
        Args:
            dt: Delta time in seconds
            knob_values: List of 4 knob values
            knob_deltas: List of 4 knob deltas
        """
        # Knob 0: Hue
        if knob_deltas[0] != 0:
            self.params["hueDeg"] = (self.params["hueDeg"] + int(knob_deltas[0] * 10)) % 360
            if self.params["hueDeg"] < 0:
                self.params["hueDeg"] += 360
                
        # Knob 1: Speed
        if knob_deltas[1] != 0:
            self.params["speed"] = max(0.0, min(5.0, self.params["speed"] + knob_deltas[1] * 0.1))
            
        # Knob 2: Mode
        if knob_deltas[2] != 0:
            self.params["mode"] = (self.params["mode"] + int(knob_deltas[2])) % len(self.PRESETS)
            if self.params["mode"] < 0:
                self.params["mode"] += len(self.PRESETS)
                
        # Knob 3: Frequency
        if knob_deltas[3] != 0:
            self.params["freq"] = max(0.1, min(1000.0, self.params["freq"] + knob_deltas[3] * 10.0))
            
        # Apply mode change
        if self.params["mode"] != self.cur_mode:
            self._apply_preset(self.params["mode"])
            
        # Update phase
        self.phase += dt * self.params["speed"] * 2.0
        self._update_color_ramp(self.params["hueDeg"])
        
    def draw(self):
        """Draw the pattern to the display."""
        p = self.PRESETS[self.cur_mode]
        brightness = 0.8
        cell_w = p["tileSize"] + p["gap"]
        cell_h = p["tileSize"] + p["gap"]
        cur_freq_base = self.params["freq"]
        cur_freq_var = self.params["freq"] * 0.9
        
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                lx = x - self.offset_x
                ly = y - self.offset_y
                
                ti = (lx - p["gap"]) // cell_w
                tj = (ly - p["gap"]) // cell_h
                
                # Check if outside tile grid
                if ti < 0 or ti >= p["cols"] or tj < 0 or tj >= p["rows"]:
                    self.display.set_back_pixel(x, y, 0, 0, 0)
                    continue
                    
                local_x = lx - (p["gap"] + ti * cell_w)
                local_y = ly - (p["gap"] + tj * cell_h)
                
                # Check if outside tile
                if local_x < 0 or local_x >= p["tileSize"] or local_y < 0 or local_y >= p["tileSize"]:
                    self.display.set_back_pixel(x, y, 0, 0, 0)
                    continue
                    
                gx = min(local_x // p["gridStep"], p["gridCells"] - 1)
                gy = min(local_y // p["gridStep"], p["gridCells"] - 1)
                
                dist = self.dist_lut[gy][gx]
                tile_freq = cur_freq_base + (tj * p["cols"] + ti) * cur_freq_var * 0.15
                wave = self._fast_sin(dist * tile_freq * 2.0 + self.phase)
                
                r, g, b = self._sample_color_ramp(wave * brightness)
                self.display.set_back_pixel(x, y, r, g, b)
