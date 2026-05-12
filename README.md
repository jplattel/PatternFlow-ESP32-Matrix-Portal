# [PatternFlow](https://github.com/engmung/PatternFlow) for MatrixPortal M4

CircuitPython implementation of [PatternFlow](https://github.com/engmung/PatternFlow) for Adafruit MatrixPortal M4 with REST API endpoints for knob control.

> 🤖 Fully converted by clankers, sorry. Fully untested as well, don't have the time YET!

> ⚠️ Photosensitivity Warning Patternflow displays rapidly changing light patterns that may trigger seizures in people with photosensitive epilepsy. Viewer discretion is advised. If you experience any discomfort, stop use immediately.

## What Changed from Original

The original PatternFlow firmware used:
- ESP32-S3 with Arduino framework
- 4 physical rotary encoders
- Direct hardware pin control

This CircuitPython version uses:
- MatrixPortal M4 (SAMD51 + ESP32 co-processor)
- REST API endpoints instead of physical encoders
- Web interface for control
- Same generative patterns

## Hardware

- **Board:** Adafruit MatrixPortal M4 (SAMD51 with ESP32 WiFi co-processor)
- **Display:** 128x64 HUB75 LED Matrix (built-in)
- **Control:** REST API endpoints (knobs exposed as HTTP API)

## Features

- 3 generative patterns ported from original [PatternFlow](https://github.com/engmung/PatternFlow) firmware
- **Custom Pattern Code Editor** - Write Python patterns in your browser
- REST API endpoints for controlling all 4 knobs
- Pattern selection via API
- Real-time parameter adjustment
- Safe code execution with AST validation

## Custom Pattern Code Editor

Access the code editor at `http://<matrix-ip>/code` to write custom Python patterns directly in your browser!

### Pattern Interface

Your pattern must implement a class (name ending with `Pattern`) with:

```python
class MyPattern:
    KNOB_LABELS = ["param1", "param2", "param3", "param4"]
    
    def setup(self):
        # Initialize pattern state
        self.time = 0.0
        
    def update(self, dt, knobs):
        # Update state (dt = delta time, knobs = [k0, k1, k2, k3])
        self.time += dt
        
    def draw(self):
        # Render to display
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                # Calculate color
                r, g, b = 255, 0, 0
                display.set_back_pixel(x, y, r, g, b)
```

### Available Functions & Constants

**Constants:**
- `PANEL_RES_W` - Display width (128)
- `PANEL_RES_H` - Display height (64)

**Display:**
- `display.set_back_pixel(x, y, r, g, b)` - Set pixel in back buffer

**Math (from math module):**
- `sin()`, `cos()`, `tan()`, `sqrt()`, `exp()`, `log()`
- `pi`, `e`, `tau`
- `floor()`, `ceil()`, `abs()`, `min()`, `max()`
- And more...

### Pattern Code API Endpoints

```bash
# Validate pattern code
POST /api/pattern_code/validate
{"code": "class MyPattern: ..."}

# Apply pattern to matrix
POST /api/pattern_code/apply
{"code": "class MyPattern: ...", "name": "My Pattern"}

# Save pattern
POST /api/pattern_code/save
{"code": "class MyPattern: ...", "name": "My Pattern"}

# List saved patterns
GET /api/pattern_code/list

# Load saved pattern
GET /api/pattern_code/load/MyPattern

# Delete saved pattern
DELETE /api/pattern_code/delete/MyPattern
```

## Deployment

### Quick Deploy/sync to CIRCUITPY

```bash
# Make script executable (first time only)
chmod +x deploy.sh

# Deploy to MatrixPortal M4
./deploy.sh
```

The script will:
1. Find your CIRCUITPY drive automatically
2. Create required directories (`patterns/`, `custom_patterns/`)
3. Sync all necessary files
4. Skip files that haven't changed
5. Trigger auto-reload on the device

### Manual Deployment

Alternatively, copy these files to your CIRCUITPY drive:

**Required files:**
- `code.py`
- `config.py`
- `display_driver.py`
- `encoder_api.py`
- `pattern_sandbox.py`
- `web_code_editor.py`
- `wifi_manager.py`
- `patterns/` (entire directory)

**Create on device:**
- `secrets.py` - Your WiFi credentials
- `lib/` - CircuitPython libraries (from circuitpython.org/libraries)

### Required Libraries

Copy these from the [CircuitPython Library Bundle](https://circuitpython.org/libraries):

- `adafruit_esp32spi`
- `adafruit_display_shapes`
- `adafruit_display_text`
- `neopixel.mpy`

## REST API Endpoints

All endpoints respond with JSON.

### Get/Set Knob Values

```
GET/POST /api/knobs
```

Get current knob values:
```json
{
  "knob0": 0,
  "knob1": 0,
  "knob2": 0,
  "knob3": 0
}
```

Set knob values (POST with JSON body):
```json
{
  "knob0": 180,
  "knob1": 2.5,
  "knob2": 1,
  "knob3": 440
}
```

### Get/Set Individual Knob

```
GET/POST /api/knob/0
GET/POST /api/knob/1
GET/POST /api/knob/2
GET/POST /api/knob/3
```

### Get Pattern Info

```
GET /api/patterns
```

Returns list of available patterns:
```json
{
  "patterns": ["Origin", "Wave Saw", "Liquid Plasma"],
  "current": 0
}
```

### Change Pattern

```
POST /api/pattern
```

Body: `{"pattern": 1}` or `{"pattern": "Wave Saw"}`

### Reset Knobs

```
POST /api/knobs/reset
```

Reset all knobs to default values.

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed step-by-step instructions.

## Setup

### 1. Install CircuitPython

1. Download CircuitPython for MatrixPortal M4 from https://circuitpython.org/board/matrixportal_m4/
2. Hold the RESET button, press UF2, release RESET
3. Copy the `.uf2` file to the MATRIXPORTAL drive

### 2. Install Required Libraries

Download the CircuitPython library bundle from https://circuitpython.org/libraries and copy these to `lib/`:

- `adafruit_display_shapes`
- `adafruit_display_text`
- `adafruit_esp32spi`
- `adafruit_bus_device`
- `neopixel.mpy`

### 3. Configure WiFi

Edit `secrets.py` (not included in repo):

```python
secrets = {
    'ssid': 'your_wifi_name',
    'password': 'your_wifi_password',
    'ip': '192.168.1.100',  # Optional: static IP
}
```

### 4. Copy Files

Copy all files to the MATRIXPORTAL drive:
- `code.py`
- `config.py`
- `display_driver.py`
- `encoder_api.py`
- `patterns/` directory
- `lib/` directory

## Patterns

### Origin
Grid-based pattern with distance-based wave animation.
- **Knob 0:** Hue (0-360)
- **Knob 1:** Speed (0.0-5.0)
- **Knob 2:** Mode (0-4 presets)
- **Knob 3:** Frequency (0.1-1000)

### Wave Saw
Vector-rotated saw wave with Perlin noise distortion.
- **Knob 0:** Angle (0-2π)
- **Knob 1:** Scale (0.5-6.0)
- **Knob 2:** Distortion (0.0-4.0)
- **Knob 3:** Detail Scale (0.3-5.0)

### Liquid Plasma
Flowing plasma effect with HSV color mapping.
- **Knob 0:** Hue Base (0.0-1.0)
- **Knob 1:** Speed (0.0-5.0)
- **Knob 2:** Scale (0.02-0.2)
- **Knob 3:** Chaos (0.0-3.0)

## Hardware Notes

The original PatternFlow uses 4 physical rotary encoders. This CircuitPython version replaces them with REST API endpoints, allowing control from:
- Web interface
- Mobile app
- Home automation (Home Assistant, etc.)
- Custom scripts

## Project Structure

```
PatternFlow-ESP32-Matrix-Portal/
├── code.py              # Main application entry point
├── config.py            # Configuration constants
├── display_driver.py    # HUB75 display driver
├── encoder_api.py       # REST API server for knob control
├── wifi_manager.py      # WiFi connection manager
├── secrets.py           # WiFi credentials (create from template)
├── patterns/
│   ├── __init__.py
│   ├── pattern_origin.py
│   ├── pattern_wave_saw.py
│   └── pattern_liquid_plasma.py
├── README.md            # This file
├── QUICKSTART.md        # Quick start guide
└── lib/                 # CircuitPython libraries (copy from bundle)
```

## Development

### Adding New Patterns

1. Create a new file in `patterns/` directory
2. Implement the pattern interface:
   - `NAME` - Pattern name string
   - `KNOB_LABELS` - List of 4 knob label strings
   - `setup()` - Initialize pattern state
   - `update(dt, knob_values, knob_deltas)` - Update state
   - `draw()` - Render to display
3. Add to `patterns/__init__.py`
4. Add to `PATTERNS` dict in `code.py`

### API Development

The REST API is implemented in `encoder_api.py`. To add new endpoints:

1. Add route handler in `handle_api_request()`
2. Update web interface in `_get_main_page()`
3. Test with curl or browser

## Troubleshooting

### Common Issues

1. **Display not initializing**
   - Ensure you're using MatrixPortal M4 (not generic ESP32)
   - Check CircuitPython version is latest for MatrixPortal M4

2. **WiFi connection fails**
   - Verify 2.4GHz network (ESP32 doesn't support 5GHz)
   - Check credentials in `secrets.py`
   - Review serial console for error messages

3. **Patterns not rendering**
   - Check all pattern files are present in `patterns/`
   - Verify libraries are in `lib/` folder
   - Watch serial console for Python exceptions

## License

MIT
