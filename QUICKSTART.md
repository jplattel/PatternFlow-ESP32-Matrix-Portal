# Quick Start Guide

## Step 1: Install CircuitPython

1. Download the latest CircuitPython UF2 for MatrixPortal M4:
   - https://circuitpython.org/board/matrixportal_m4/

2. Put the board in bootloader mode:
   - Hold the RESET button
   - Press the UF2 button (next to RESET)
   - Release RESET
   - Release UF2

3. A drive called `MATRIXPORTAL` should appear on your computer

4. Copy the `.uf2` file to the drive
   - The board will reset and CircuitPython will start

## Step 2: Install Libraries

1. Download the CircuitPython library bundle:
   - https://circuitpython.org/libraries

2. Extract the zip file

3. Copy these folders/files to the `lib` folder on MATRIXPORTAL:
   - `adafruit_display_shapes/`
   - `adafruit_display_text/`
   - `adafruit_esp32spi/`
   - `adafruit_bus_device/`
   - `neopixel.mpy`

## Step 3: Configure WiFi

1. Create a file called `secrets.py` on the MATRIXPORTAL drive

2. Add your WiFi credentials:
```python
secrets = {
    'ssid': 'your_wifi_name',
    'password': 'your_wifi_password',
}
```

## Step 4: Copy PatternFlow Files

Copy these files to the MATRIXPORTAL drive:
- `code.py`
- `config.py`
- `display_driver.py`
- `encoder_api.py`
- `wifi_manager.py`
- `patterns/` folder (with all pattern files)

## Step 5: Access the Interface

1. After copying files, the board will reset automatically

2. Open the Serial Console (baud rate doesn't matter for USB CDC)
   - You should see: `Web Interface: http://192.168.x.x`

3. Open that IP address in your browser

4. You'll see the PatternFlow control interface with:
   - Knob sliders
   - Pattern selection buttons
   - Real-time preview on the LED matrix

## API Endpoints

### Get/Set All Knobs
```bash
# Get current values
curl http://192.168.x.x/api/knobs

# Set all values
curl -X POST http://192.168.x.x/api/knobs \
  -H "Content-Type: application/json" \
  -d '{"knob0": 180, "knob1": 2.5, "knob2": 1, "knob3": 440}'
```

### Get/Set Individual Knob
```bash
curl http://192.168.x.x/api/knob/0
curl -X POST http://192.168.x.x/api/knob/0 \
  -H "Content-Type: application/json" \
  -d '{"value": 90}'
```

### Pattern Control
```bash
# List patterns
curl http://192.168.x.x/api/patterns

# Change pattern
curl -X POST http://192.168.x.x/api/pattern \
  -H "Content-Type: application/json" \
  -d '{"pattern": "Wave Saw"}'
```

## Troubleshooting

### Display not working
- Make sure you have the MatrixPortal M4 (not just any ESP32)
- Check that the HUB75 matrix is properly connected

### WiFi not connecting
- Verify your WiFi credentials in `secrets.py`
- Check that your network is 2.4GHz (ESP32 doesn't support 5GHz)
- Look at the serial console for error messages

### Patterns not showing
- Check the serial console for Python errors
- Make sure all pattern files are in the `patterns/` folder
- Try resetting the board (press RESET twice)

## Home Assistant Integration

Add this to your `configuration.yaml`:

```yaml
rest_command:
  patternflow_knob0:
    url: "http://PATTERNFLOW_IP/api/knob/0"
    method: POST
    headers:
      content-type: application/json
    payload: '{"value": "{{ value }}"}'
    
  patternflow_pattern:
    url: "http://PATTERNFLOW_IP/api/pattern"
    method: POST
    headers:
      content-type: application/json
    payload: '{"pattern": "{{ pattern }}"}'
```

Then create sliders and selectors in your dashboard!
