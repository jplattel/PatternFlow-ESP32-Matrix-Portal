# ═══════════════════════════════════════════════════════════
# PatternFlow - Hardware Configuration & Constants
# CircuitPython for MatrixPortal M4
# License: MIT
# ═══════════════════════════════════════════════════════════

# --- Display Specifications ---
PANEL_RES_W = 128
PANEL_RES_H = 64

# --- Hardware Settings ---
DEFAULT_BRIGHTNESS = 0.8  # 80% (0.0-1.0)

# --- Pattern Parameters Limits ---
MAX_HUE = 360
MAX_SPEED = 5.0
SPEED_STEP = 0.2
MAX_FREQ = 1000
FREQ_STEP = 50

# --- API Configuration ---
API_PORT = 80
MDNS_NAME = "patternflow"

# --- Knob Default Values per Pattern ---
# Each pattern defines its own defaults
KNOB_DEFAULTS = {
    "Origin": [0, 2.0, 0, 220.0],
    "Wave Saw": [0.0, 3.0, 0.0, 1.0],
    "Liquid Plasma": [0.5, 1.0, 0.1, 1.0],
}

# --- Knob Labels per Pattern ---
KNOB_LABELS = {
    "Origin": ["hue", "speed", "mode", "freq"],
    "Wave Saw": ["angle", "scale", "dist", "dscale"],
    "Liquid Plasma": ["hue", "speed", "scale", "chaos"],
}
