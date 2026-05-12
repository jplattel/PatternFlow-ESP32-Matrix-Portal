# ═══════════════════════════════════════════════════════════
# PatternFlow - Wave Saw Pattern
# CircuitPython implementation for MatrixPortal M4
# License: MIT
# ═══════════════════════════════════════════════════════════

import math
from config import PANEL_RES_W, PANEL_RES_H


class WaveSawPattern:
    """
    Wave Saw pattern - Vector-rotated saw wave with Perlin noise distortion.
    
    Knobs:
    - Knob 0: Angle (0-2π)
    - Knob 1: Scale (0.5-6.0)
    - Knob 2: Distortion (0.0-4.0)
    - Knob 3: Detail Scale (0.3-5.0)
    """
    
    NAME = "Wave Saw"
    KNOB_LABELS = ["angle", "scale", "dist", "dscale"]
    
    # Constants
    DETAIL_ROUGHNESS = 0.22
    DETAIL_OCTAVES = 2
    PHASE_PER_SEC = 2.4
    
    SCALE_MIN = 0.5
    SCALE_MAX = 6.0
    DIST_MIN = 0.0
    DIST_MAX = 4.0
    DSCALE_MIN = 0.3
    DSCALE_MAX = 5.0
    
    SIN_LUT_SIZE = 512
    
    # Permutation table for Perlin noise
    PERM = [
        151,160,137,91,90,15,131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,
        8,99,37,240,21,10,23,190,6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,
        35,11,32,57,177,33,88,237,149,56,87,174,20,125,136,171,168,68,175,74,165,71,
        134,139,48,27,166,77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,
        55,46,245,40,244,102,143,54,65,25,63,161,1,216,80,73,209,76,132,187,208,89,
        18,169,200,196,135,130,116,188,159,86,164,100,109,198,173,186,3,64,52,217,
        226,250,124,123,5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,
        17,182,189,28,42,223,183,170,213,119,248,152,2,44,154,163,70,221,153,101,
        155,167,43,172,9,129,22,39,253,19,98,108,110,79,113,224,232,178,185,112,
        104,218,246,97,228,251,34,242,193,238,210,144,12,191,179,162,241,81,51,145,
        235,249,14,239,107,49,192,214,31,181,199,106,157,184,84,204,176,115,121,50,
        45,127,4,150,254,138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,
        215,61,156,180,
    ] * 2  # Double for wrapping
    
    def __init__(self, display):
        self.display = display
        self.angle = 0.0
        self.scale = 3.0
        self.dist = 0.0
        self.d_scale = 1.0
        self.phase = 0.0
        self.sin_lut = []
        self.cos_lut = []
        
        # Build lookup tables
        self._build_trig_luts()
        
    def _build_trig_luts(self):
        """Build sine and cosine lookup tables."""
        self.sin_lut = []
        self.cos_lut = []
        for i in range(self.SIN_LUT_SIZE):
            angle = (i / self.SIN_LUT_SIZE) * 2.0 * math.pi
            self.sin_lut.append(math.sin(angle))
            self.cos_lut.append(math.cos(angle))
            
    def _fast_sin(self, x):
        """Fast sine using lookup table."""
        n = x * (1.0 / (2.0 * math.pi))
        n = n - math.floor(n)
        if n < 0:
            n += 1.0
        index = int(n * self.SIN_LUT_SIZE) & (self.SIN_LUT_SIZE - 1)
        return self.sin_lut[index]
        
    def _fast_cos(self, x):
        """Fast cosine using lookup table."""
        return self._fast_sin(x + math.pi * 0.5)
        
    def _fade(self, t):
        """Fade function for Perlin noise."""
        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)
        
    def _lerp(self, a, b, t):
        """Linear interpolation."""
        return a + t * (b - a)
        
    def _grad2(self, hash_val, x, y):
        """Gradient function for Perlin noise."""
        h = hash_val & 7
        u = x if h < 4 else y
        v = y if h < 4 else x
        return (-u if h & 1 else u) + (-2.0 * v if h & 2 else 2.0 * v)
        
    def _perlin_2d(self, x, y):
        """2D Perlin noise."""
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        x = x - math.floor(x)
        y = y - math.floor(y)
        
        u = self._fade(x)
        v = self._fade(y)
        
        A = self.PERM[X] + Y
        B = self.PERM[X + 1] + Y
        
        n00 = self._grad2(self.PERM[A], x, y)
        n10 = self._grad2(self.PERM[B], x - 1.0, y)
        n01 = self._grad2(self.PERM[A + 1], x, y - 1.0)
        n11 = self._grad2(self.PERM[B + 1], x - 1.0, y - 1.0)
        
        return self._lerp(self._lerp(n00, n10, u), self._lerp(n01, n11, u), v)
        
    def _fractal_noise(self, x, y, octaves, roughness):
        """Fractal noise with multiple octaves."""
        sum_val = 0.0
        amp = 1.0
        max_amp = 0.0
        freq = 1.0
        
        for i in range(octaves):
            sum_val += self._perlin_2d(x * freq, y * freq) * amp
            max_amp += amp
            amp *= roughness
            freq *= 2.0
            
        return sum_val / max_amp
        
    def _color_ramp_constant(self, t):
        """Constant 3-stop color ramp."""
        if t < 0.14:
            return (255, 255, 255)  # White
        elif t < 0.40:
            return (255, 0, 0)  # Red
        else:
            return (0, 0, 255)  # Blue
            
    def setup(self):
        """Initialize the pattern."""
        self.angle = 0.0
        self.scale = 3.0
        self.dist = 0.0
        self.d_scale = 1.0
        self.phase = 0.0
        
    def update(self, dt, knob_values, knob_deltas):
        """
        Update pattern state based on knob inputs.
        
        Args:
            dt: Delta time in seconds
            knob_values: List of 4 knob values
            knob_deltas: List of 4 knob deltas
        """
        # Knob 0: Angle
        if knob_deltas[0] != 0:
            self.angle += knob_deltas[0] * 0.1
            self.angle = self.angle % (2.0 * math.pi)
            if self.angle < 0:
                self.angle += 2.0 * math.pi
                
        # Knob 1: Scale
        if knob_deltas[1] != 0:
            self.scale = max(self.SCALE_MIN, min(self.SCALE_MAX, self.scale + knob_deltas[1] * 0.2))
            
        # Knob 2: Distortion
        if knob_deltas[2] != 0:
            self.dist = max(self.DIST_MIN, min(self.DIST_MAX, self.dist + knob_deltas[2] * 0.1))
            
        # Knob 3: Detail Scale
        if knob_deltas[3] != 0:
            self.d_scale = max(self.DSCALE_MIN, min(self.DSCALE_MAX, self.d_scale + knob_deltas[3] * 0.2))
            
        # Update phase
        self.phase += dt * self.PHASE_PER_SEC
        
    def draw(self):
        """Draw the pattern to the display."""
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        inv_two_pi = 1.0 / (2.0 * math.pi)
        
        for y in range(PANEL_RES_H):
            # y: -0.5 to +0.5 (aspect corrected)
            v = (y - (PANEL_RES_H / 2.0)) / PANEL_RES_H
            
            for x in range(PANEL_RES_W):
                # x: -1 to +1
                u = (x - (PANEL_RES_W / 2.0)) / (PANEL_RES_W / 2.0)
                
                # Vector rotate (Z axis)
                xr = u * cos_a - v * sin_a
                yr = u * sin_a + v * cos_a
                
                # Wave texture: bands along X
                n = xr * self.scale * 20.0 + self.phase
                
                # Distortion (noise-based)
                if self.dist > 0.01:
                    nz = self._fractal_noise(xr * self.d_scale, yr * self.d_scale, 
                                            self.DETAIL_OCTAVES, self.DETAIL_ROUGHNESS)
                    n += self.dist * nz
                    
                # Saw profile: n/(2π) - floor -> 0..1
                t = n * inv_two_pi
                t = t - math.floor(t)
                
                r, g, b = self._color_ramp_constant(t)
                self.display.set_back_pixel(x, y, r, g, b)
