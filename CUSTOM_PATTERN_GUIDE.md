# Custom Pattern Code Editor - Implementation Guide

## Overview

The PatternFlow Code Editor allows you to write custom Python patterns directly in your web browser and run them on your MatrixPortal M4. No need to modify files on the device or re-upload code!

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Code Editor (CodeMirror)                             │  │
│  │  - Syntax highlighting                                │  │
│  │  - Live validation                                    │  │
│  │  - Pattern examples                                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  MatrixPortal M4                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  encoder_api.py                                       │  │
│  │  - /api/pattern_code/validate                         │  │
│  │  - /api/pattern_code/apply                            │  │
│  │  - /api/pattern_code/save                             │  │
│  │  - /api/pattern_code/list                             │  │
│  │  - /api/pattern_code/load/NAME                        │  │
│  │  - /api/pattern_code/delete/NAME                      │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  pattern_sandbox.py                                   │  │
│  │  - AST validation (security)                          │  │
│  │  - Safe builtins only                                 │  │
│  │  - Pattern interface checking                         │  │
│  │  - Sandboxed execution                                │  │
│  │  - Pattern storage (save/load/delete)                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  code.py (main loop)                                  │  │
│  │  - PatternRegistry with sandbox support               │  │
│  │  - Switches between built-in and custom patterns      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Files

### Core Implementation

| File | Purpose |
|------|---------|
| `pattern_sandbox.py` | Safe execution with AST validation, sandbox, storage |
| `web_code_editor.py` | CodeMirror-based web editor UI |
| `encoder_api.py` | REST API endpoints for pattern code |
| `code.py` | Main app with custom pattern support |

### Documentation

| File | Purpose |
|------|---------|
| `EXAMPLE_PATTERNS.md` | 6 ready-to-use pattern examples |
| `CUSTOM_PATTERN_GUIDE.md` | This implementation guide |
| `README.md` | API documentation |

## Security Features

### AST Validation

Before executing any user code, the system:

1. **Parses the AST** - Checks for syntax errors
2. **Blocks dangerous nodes**:
   - `ast.Open` - No file I/O
   - `ast.Import` - No imports
   - `ast.ImportFrom` - No module imports
   - `ast.Exec`, `ast.Eval` - No dynamic execution
3. **Blocks dangerous attributes**:
   - `__import__`, `open`, `file`
   - `exec`, `eval`, `compile`
   - `globals`, `locals`, `vars`
   - `getattr`, `setattr`, `delattr`
4. **Checks interface** - Ensures Pattern class with required methods
5. **Limits code size** - Max 10,000 characters

### Safe Builtins

Only these functions are available:

```python
# Math
abs, min, max, sum, pow, round
int, float, bool, len, range
sin, cos, tan, sqrt, exp, log
pi, e, tau, floor, ceil

# Data structures
list, tuple, dict, set
enumerate, zip, sorted, reversed

# Display & constants (injected)
display, PANEL_RES_W, PANEL_RES_H
```

### Pattern Interface Requirements

```python
class MyPattern:  # Name must end with 'Pattern'
    KNOB_LABELS = ["label0", "label1", "label2", "label3"]
    
    def setup(self):
        """Initialize pattern state"""
        pass
        
    def update(self, dt, knobs):
        """Update state
        dt: delta time in seconds
        knobs: [k0, k1, k2, k3]
        """
        pass
        
    def draw(self):
        """Render to display using:
        display.set_back_pixel(x, y, r, g, b)
        """
        pass
```

## Usage Flow

### 1. Access the Editor

Open `http://<matrix-ip>/code` in your browser

### 2. Write or Load Code

- Start with an example (click "Load Example")
- Modify parameters
- Write your own pattern from scratch

### 3. Validate

Click "✓ Validate" to check:
- Syntax errors
- Missing methods
- Dangerous operations
- Knob labels extracted automatically

### 4. Apply to Matrix

Click "▶ Apply to Matrix" to run your pattern live!

### 5. Save (Optional)

Click "💾 Save" to store on the device:
- Saved to `/custom_patterns/NAME.py`
- Load anytime from the saved patterns list
- Share code with others

## Example Pattern Walkthrough

Let's break down a simple pattern:

```python
class WavePattern:
    KNOB_LABELS = ["freq", "speed", "amp", "offset"]
    
    def setup(self):
        self.time = 0.0
        self.freq = 0.1
        self.speed = 1.0
        
    def update(self, dt, knobs):
        # Update time based on speed knob
        self.time += dt * self.speed
        
        # Read knob values
        self.freq = knobs[0] * 0.01
        self.speed = knobs[1] * 0.1
        
    def draw(self):
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                # Calculate wave value
                value = sin(x * self.freq + self.time)
                
                # Map to color (cyan gradient)
                r = 0
                g = int(128 + value * 127)
                b = int(255 - value * 127)
                
                display.set_back_pixel(x, y, r, g, b)
```

**Key points:**
- `setup()` runs once when pattern loads
- `update()` runs every frame with `dt` and knob values
- `draw()` renders to the back buffer
- Use `display.set_back_pixel()` to set colors
- Math functions like `sin()` are pre-imported

## Limitations

1. **No imports** - Cannot import modules (security)
2. **No file I/O** - Cannot read/write files
3. **No network** - Cannot make HTTP requests
4. **Limited memory** - CircuitPython memory constraints
5. **Performance** - Complex patterns may run slower

## Tips for Best Results

1. **Pre-calculate values** - Don't recalculate constants in draw()
2. **Use integer math** - Faster than float where possible
3. **Limit nested loops** - 128×64 = 8192 pixels per frame
4. **Test incrementally** - Validate often
5. **Save backups** - Copy code locally before major changes

## Troubleshooting

### "Validation failed: No Pattern class found"

- Make sure your class name ends with `Pattern`
- Example: `class MyWavePattern:` ✓
- Example: `class MyWave:` ✗

### "Pattern initialization error"

- Check that `setup()` doesn't raise exceptions
- Ensure all variables are initialized

### Pattern runs but looks wrong

- Check coordinate ranges (0-127 for x, 0-63 for y)
- Verify color values (0-255 for r, g, b)
- Add debug output to console

### "Failed to save pattern"

- Check storage is available
- Pattern name might be invalid
- Try a simpler name (alphanumeric + underscores)

## Future Enhancements

Potential improvements:

1. **Pattern sharing** - Export/import via JSON
2. **Collaborative editing** - Multiple users
3. **Pattern gallery** - Community patterns
4. **Advanced validation** - Type checking, performance hints
5. **Visual programming** - Block-based pattern builder
6. **Animation timeline** - Keyframe-based animation

## Contributing Patterns

Have a cool pattern? Share it!

1. Save your pattern on the device
2. Copy the code
3. Add to EXAMPLE_PATTERNS.md
4. Submit as a pattern contribution

## License

MIT License - Same as PatternFlow
