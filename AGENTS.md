# PatternFlow - Agent Development Guide

## Project Overview

PatternFlow is a CircuitPython implementation for the Adafruit MatrixPortal M4 that displays generative LED matrix patterns with REST API control. Users can write custom Python patterns through a web-based code editor.

**Hardware:** Adafruit MatrixPortal M4 (SAMD51 + ESP32 WiFi co-processor)
**Display:** 128x64 HUB75 LED Matrix
**Control:** REST API endpoints + Web-based code editor

## Architecture

```
code.py (main loop)
    ├── display_driver.py (HUB75 control)
    ├── wifi_manager.py (WiFi connection)
    ├── encoder_api.py (REST API server)
    │   └── pattern_sandbox.py (safe code execution)
    └── patterns/
        ├── pattern_origin.py
        ├── pattern_wave_saw.py
        └── pattern_liquid_plasma.py
```

## Key Files

| File | Purpose | Agent Notes |
|------|---------|-------------|
| `code.py` | Main application loop | Entry point, initializes all components |
| `encoder_api.py` | REST API server | Handles HTTP requests, serves web UI |
| `pattern_sandbox.py` | Safe code execution | AST validation, restricted builtins |
| `web_code_editor.py` | Web UI for patterns | CodeMirror-based editor |
| `display_driver.py` | HUB75 display control | Low-level display operations |
| `config.py` | Configuration constants | Display dimensions, knob defaults |

## Development Guidelines

### 1. CircuitPython Constraints

- **Memory is limited** - SAMD51 has ~256KB RAM
- **No threading** - Single-threaded cooperative multitasking
- **No standard library** - Only CircuitPython modules available
- **File I/O is slow** - Minimize reads/writes during runtime
- **Avoid `time.sleep()` in main loop** - Use `time.monotonic()` for timing

### 2. Pattern Interface

All patterns must implement:

```python
class MyPattern:
    def setup(self):
        """Called once when pattern loads"""
        pass
        
    def update(self, dt, knobs):
        """Called every frame
        dt: delta time in seconds
        knobs: [k0, k1, k2, k3]
        """
        pass
        
    def draw(self):
        """Render to display
        Use: display.set_back_pixel(x, y, r, g, b)
        """
        pass
```

### 3. Security (Custom Patterns)

When modifying `pattern_sandbox.py`:

- **Never remove AST validation** - Blocks dangerous operations
- **Keep FORBIDDEN_NODES comprehensive** - Import, Open, Exec, etc.
- **Keep SAFE_BUILTINS minimal** - Only math and display functions
- **Test sandbox escapes** - Try to break out before merging changes

### 4. REST API Design

- All endpoints return JSON
- Use standard HTTP methods (GET/POST/DELETE)
- Include error messages in response body
- Keep responses small (memory constraints)

### 5. Testing Strategy

**Unit Tests (on host):**
- Test pattern_sandbox.py validation logic
- Test pattern_sandbox.py storage functions
- Test encoder_api.py request routing

**Integration Tests (on device):**
- Manual testing via serial console
- Watch for crashes in main loop
- Verify WiFi connectivity

**Pattern Testing:**
- Use EXAMPLE_PATTERNS.md as test cases
- Validate each pattern through web editor
- Check memory usage over time

## Common Tasks

### Adding a New Pattern

1. Create file in `patterns/` directory
2. Implement Pattern class with setup/update/draw
3. Add to PATTERNS dict in `code.py`
4. Test on device

### Modifying the API

1. Update `encoder_api.py` request handler
2. Add route to `_handle_request()` method
3. Test with curl or web browser
4. Update README.md documentation

### Changing the Web UI

1. Edit `web_code_editor.py` (CODE_EDITOR_HTML constant)
2. Deploy to device
3. Test in browser
4. Check console for JavaScript errors

### Debugging

**Serial Console:**
```python
# Add debug output
print(f"Debug: value = {value}")
```

**Error Display:**
- Pattern crashes show red/black stripes on display
- Check `boot_out.txt` for startup errors
- Watch serial console for exceptions

**Common Issues:**
- `ImportError` - Missing library in `lib/`
- `OSError` - File I/O on read-only filesystem
- `MemoryError` - Too much allocation
- `NameError` - Typo in variable name

## Deployment

```bash
# Quick deploy
./deploy.sh

# Manual deploy
# Copy files to CIRCUITPY drive
# Create secrets.py with WiFi credentials
```

## Libraries Required

Download from [CircuitPython Bundle](https://circuitpython.org/libraries):

- `adafruit_esp32spi` - WiFi control
- `adafruit_display_shapes` - Drawing primitives
- `adafruit_display_text` - Text rendering
- `neopixel.mpy` - Status LED

## Configuration

### secrets.py (create on device)

```python
secrets = {
    'ssid': 'your_wifi_name',
    'password': 'your_wifi_password',
}
```

### config.py (edit as needed)

```python
PANEL_RES_W = 128  # Display width
PANEL_RES_H = 64   # Display height
KNOB_DEFAULTS = [0, 0, 0, 0]  # Default knob values
```

## Performance Tips

1. **Pre-calculate constants** - Don't recalculate in draw()
2. **Use integer math** - Faster than float where possible
3. **Limit nested loops** - 128×64 = 8192 pixels per frame
4. **Avoid allocations in hot paths** - Reuse objects
5. **Use local variables** - Faster than global lookups

## Security Considerations

### Custom Pattern Sandbox

The sandbox prevents:
- File I/O (`open()`, file operations)
- Network access (socket, requests)
- System calls (os, sys modules)
- Dynamic execution (`exec()`, `eval()`)
- Import statements

**When reviewing sandbox changes:**
- Verify AST validation is comprehensive
- Check for bypass vectors
- Test with malicious code examples
- Ensure error handling doesn't leak privileges

### Web Interface

- Served over HTTP (no HTTPS on device)
- No authentication (local network only)
- Input validation on all API endpoints
- Size limits on code submissions

## Troubleshooting

### Device Not Connecting to WiFi

1. Check secrets.py syntax
2. Verify SSID/password are correct
3. Check WiFi signal strength
4. Try 2.4GHz network (no 5GHz support)

### Patterns Not Loading

1. Check for syntax errors in pattern code
2. Verify pattern class name ends with "Pattern"
3. Ensure setup/update/draw methods exist
4. Check serial console for errors

### Web Editor Not Working

1. Verify device has IP address
2. Check browser console for errors
3. Try different browser (Chrome/Firefox)
4. Clear browser cache

### Deployment Issues

1. Ensure CIRCUITPY drive is mounted
2. Check device not in boot mode
3. Try different USB cable
4. Reset device and retry

## Agent Workflow

### Before Making Changes

1. Read relevant files completely
2. Understand existing patterns
3. Check for similar implementations
4. Consider CircuitPython constraints

### When Implementing Features

1. Start with interface design
2. Add validation/error handling
3. Test incrementally
4. Update documentation

### When Debugging Issues

1. Reproduce the issue
2. Check serial console output
3. Add targeted debug statements
4. Verify fix doesn't break other features

### Before Claiming Completion

1. Run deployment script
2. Test on actual device (if available)
3. Verify all endpoints work
4. Check memory usage
5. Update README.md if needed

## Resources

- [CircuitPython Documentation](https://docs.circuitpython.org/)
- [MatrixPortal M4 Guide](https://learn.adafruit.com/adafruit-matrixportal-m4)
- [CircuitPython Libraries](https://circuitpython.org/libraries)
- [HUB75 Matrix Guide](https://learn.adafruit.com/adafruit-hub75-matrix-panel)

## License

MIT License - See LICENSE file for details
