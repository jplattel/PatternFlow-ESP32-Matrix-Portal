# Example Custom Patterns

Copy these patterns into the Code Editor (`http://<matrix-ip>/code`) to get started!

## 1. Simple Rainbow Wave

A basic sine wave with rainbow colors.

```python
class RainbowWavePattern:
    """Simple rainbow wave pattern."""
    
    KNOB_LABELS = ["frequency", "speed", "brightness", "offset"]
    
    def setup(self):
        self.time = 0.0
        
    def update(self, dt, knobs):
        self.time += dt * (knobs[1] * 0.5 + 0.5)
        self.freq = knobs[0] * 0.05
        self.brightness = knobs[2] * 0.5 + 0.5
        self.offset = knobs[3] * 0.1
        
    def draw(self):
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                value = sin(x * self.freq + self.time)
                value = value * self.brightness
                
                # Rainbow color
                hue = (value + 1) * 0.5 + self.offset
                r = int(255 * max(0, sin(hue * 2 * pi)))
                g = int(255 * max(0, sin((hue - 0.33) * 2 * pi)))
                b = int(255 * max(0, sin((hue - 0.66) * 2 * pi)))
                
                display.set_back_pixel(x, y, r, g, b)
```

## 2. Plasma Ball

Classic plasma effect with flowing colors.

```python
class PlasmaBallPattern:
    """Flowing plasma ball effect."""
    
    KNOB_LABELS = ["speed", "scale", "complexity", "hue"]
    
    def setup(self):
        self.time = 0.0
        
    def update(self, dt, knobs):
        self.time += dt * (knobs[0] + 0.5)
        self.scale = knobs[1] * 0.002 + 0.01
        self.complexity = knobs[2] * 2 + 1
        self.hue_shift = knobs[3]
        
    def draw(self):
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                # Center coordinates
                vx = (x - 64) * self.scale
                vy = (y - 32) * self.scale
                
                # Multiple sine waves
                value = sin(vx + self.time)
                value += sin((vy + self.time) * self.complexity)
                value += sin((vx + vy + self.time) * 0.5)
                
                # Distance from center
                dist = sqrt(vx * vx + vy * vy)
                value += sin(dist * 2 - self.time * 1.5)
                
                value = value / 4.0  # Normalize
                
                # HSV to RGB
                h = (value + 1) * 0.5 + self.hue_shift
                h = h - int(h)  # Wrap
                
                r = int(255 * max(0, sin(h * 2 * pi)))
                g = int(255 * max(0, sin((h - 0.33) * 2 * pi)))
                b = int(255 * max(0, sin((h - 0.66) * 2 * pi)))
                
                display.set_back_pixel(x, y, r, g, b)
```

## 3. Scrolling Grid

Retro scrolling grid pattern.

```python
class ScrollingGridPattern:
    """Retro scrolling grid pattern."""
    
    KNOB_LABELS = ["speed", "spacing", "thickness", "color"]
    
    def setup(self):
        self.offset_x = 0.0
        self.offset_y = 0.0
        
    def update(self, dt, knobs):
        speed = knobs[0] * 50 + 10
        self.offset_x += dt * speed
        self.offset_y += dt * speed * 0.7
        self.spacing = int(knobs[1] * 30 + 8)
        self.thickness = knobs[2] * 0.3 + 0.1
        self.color_idx = int(knobs[3] * 3)
        
    def draw(self):
        colors = [
            (0, 255, 128),   # Green
            (0, 128, 255),   # Blue
            (255, 0, 128),   # Pink
            (255, 128, 0),   # Orange
        ]
        base_color = colors[self.color_idx % len(colors)]
        
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                # Apply scrolling offset
                px = (x + self.offset_x) % (self.spacing * 4)
                py = (y + self.offset_y) % (self.spacing * 4)
                
                # Grid lines
                in_x = (px % self.spacing) / self.spacing
                in_y = (py % self.spacing) / self.spacing
                
                is_line = in_x < self.thickness or in_y < self.thickness
                
                if is_line:
                    r, g, b = base_color
                else:
                    r, g, b = 0, 0, 0
                    
                display.set_back_pixel(x, y, r, g, b)
```

## 4. Pulse Circle

Expanding circles from center.

```python
class PulseCirclePattern:
    """Expanding pulse circles from center."""
    
    KNOB_LABELS = ["speed", "spacing", "width", "color"]
    
    def setup(self):
        self.time = 0.0
        
    def update(self, dt, knobs):
        self.time += dt * (knobs[0] * 2 + 0.5)
        self.spacing = knobs[1] * 20 + 5
        self.width = knobs[2] * 5 + 1
        self.color_speed = knobs[3] * 0.1
        
    def draw(self):
        cx, cy = 64, 32  # Center
        
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                # Distance from center
                dx = x - cx
                dy = y - cy
                dist = sqrt(dx * dx + dy * dy)
                
                # Ring pattern
                ring_pos = (dist - self.time * self.spacing) % (self.spacing * 2)
                in_ring = abs(ring_pos - self.spacing) < self.width
                
                if in_ring:
                    # Rainbow based on distance
                    hue = (dist * 0.02 + self.time * self.color_speed) % 1.0
                    r = int(255 * max(0, sin(hue * 2 * pi)))
                    g = int(255 * max(0, sin((hue - 0.33) * 2 * pi)))
                    b = int(255 * max(0, sin((hue - 0.66) * 2 * pi)))
                else:
                    r, g, b = 0, 0, 0
                    
                display.set_back_pixel(x, y, r, g, b)
```

## 5. Noise Terrain

Pseudo-noise terrain effect.

```python
class NoiseTerrainPattern:
    """Pseudo-noise terrain pattern."""
    
    KNOB_LABELS = ["speed", "scale", "height", "water"]
    
    def setup(self):
        self.time = 0.0
        # Simple permutation table
        self.perm = [(i * 7 + 13) % 256 for i in range(256)] * 2
        
    def _hash(self, x, y):
        h = self.perm[int(x) & 255] + self.perm[int(y) & 255]
        return self.perm[h & 255] / 256.0
        
    def update(self, dt, knobs):
        self.time += dt * (knobs[0] + 0.2)
        self.scale = knobs[1] * 0.1 + 0.05
        self.height = knobs[2] * 2 + 1
        self.water_level = knobs[3] * 0.5
        
    def draw(self):
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                # Simple noise
                nx = x * self.scale + self.time
                ny = y * self.scale
                
                gx = int(nx)
                gy = int(ny)
                lx = nx - gx
                ly = ny - gy
                
                # Smooth interpolation
                sx = lx * lx * (3 - 2 * lx)
                sy = ly * ly * (3 - 2 * ly)
                
                n00 = self._hash(gx, gy)
                n10 = self._hash(gx + 1, gy)
                n01 = self._hash(gx, gy + 1)
                n11 = self._hash(gx + 1, gy + 1)
                
                nx_val = n00 * (1 - sx) + n10 * sx
                ny_val = n01 * (1 - sx) + n11 * sx
                value = nx_val * (1 - sy) + ny_val * sy
                
                value = value * self.height
                
                # Color based on height
                if value < self.water_level:
                    # Water (blue)
                    r, g, b = 0, 64, 192
                elif value < self.water_level + 0.2:
                    # Sand (yellow)
                    r, g, b = 194, 178, 128
                elif value < self.water_level + 0.5:
                    # Grass (green)
                    r, g, b = 0, 128, 0
                else:
                    # Mountain (white/gray)
                    brightness = int(128 + value * 127)
                    r, g, b = brightness, brightness, brightness
                    
                display.set_back_pixel(x, y, r, g, b)
```

## 6. Matrix Rain

Falling characters effect (simplified).

```python
class MatrixRainPattern:
    """Matrix-style falling rain effect."""
    
    KNOB_LABELS = ["speed", "density", "brightness", "color"]
    
    def setup(self):
        self.drops = [0] * (PANEL_RES_W // 2)  # One drop per 2 columns
        self.time = 0.0
        
    def update(self, dt, knobs):
        self.speed = knobs[0] * 30 + 10
        self.density = knobs[1] * 0.5 + 0.3
        self.brightness = knobs[2] * 0.8 + 0.2
        self.color_idx = int(knobs[3] * 3)
        
        # Update drops
        for i in range(len(self.drops)):
            self.drops[i] += self.speed * dt
            if self.drops[i] > PANEL_RES_H:
                self.drops[i] = 0
                
    def draw(self):
        colors = [
            (0, 255, 128),   # Green
            (0, 192, 255),   # Cyan
            (255, 0, 128),   # Pink
            (128, 0, 255),   # Purple
        ]
        base_color = colors[self.color_idx % len(colors)]
        
        # Clear to black
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                display.set_back_pixel(x, y, 0, 0, 0)
        
        # Draw drops
        for i, drop_y in enumerate(self.drops):
            x = i * 2
            # Draw trail
            trail_len = int(8 * self.density)
            for j in range(trail_len):
                y = int(drop_y) - j
                if 0 <= y < PANEL_RES_H:
                    brightness = int(255 * self.brightness * (1 - j / trail_len))
                    r = int(base_color[0] * brightness / 255)
                    g = int(base_color[1] * brightness / 255)
                    b = int(base_color[2] * brightness / 255)
                    if x < PANEL_RES_W:
                        display.set_back_pixel(x, y, r, g, b)
```

## Tips for Writing Patterns

1. **Keep it efficient** - The display is only 128x64, but nested loops still add up
2. **Use math functions** - `sin()`, `cos()`, `sqrt()` create smooth animations
3. **Experiment with knobs** - Map knob values to interesting parameters
4. **Test incrementally** - Use Validate before Apply to catch syntax errors
5. **Save your work** - Use Save to store patterns on the device

## Security Notes

The code editor runs in a **sandboxed environment**:
- No file I/O access
- No network access
- No system calls
- Limited to safe math and display functions
- Code is validated before execution

This protects your device while still allowing creative pattern creation!
