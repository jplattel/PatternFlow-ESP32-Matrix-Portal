# ═══════════════════════════════════════════════════════════
# PatternFlow - Display Driver for MatrixPortal M4
# CircuitPython implementation
# License: MIT
# ═══════════════════════════════════════════════════════════

import board
import displayio
import rgbmatrix
import framebufferio
from config import PANEL_RES_W, PANEL_RES_H, DEFAULT_BRIGHTNESS


class DisplayDriver:
    """Display driver for MatrixPortal M4 HUB75 matrix."""
    
    def __init__(self):
        self.width = PANEL_RES_W
        self.height = PANEL_RES_H
        self.brightness = DEFAULT_BRIGHTNESS
        
        # MatrixPortal M4 uses built-in HUB75 pins
        # Create the RGB matrix
        self.matrix = rgbmatrix.RGBMatrix(
            width=self.width,
            height=self.height,
            bit_depth=6,
            rgb_pins=(
                board.MTX_R1,
                board.MTX_G1,
                board.MTX_B1,
                board.MTX_R2,
                board.MTX_G2,
                board.MTX_B2,
            ),
            addr_pins=(
                board.MTX_ADDRA,
                board.MTX_ADDRB,
                board.MTX_ADDRC,
                board.MTX_ADDRD,
                board.MTX_ADDRE,
            ),
            clock_pin=board.MTX_CLK,
            latch_pin=board.MTX_LAT,
            output_enable_pin=board.MTX_OE,
            tile=1,
        )
        
        # Create framebuffer
        self.framebuffer = framebufferio.Framebuffer(self.matrix)
        
        # Create display
        self.display = displayio.Display(
            self.framebuffer,
            displayio.Colorspace.RGB565,
            rotation=0,
        )
        
        # Create main group
        self.root_group = displayio.Group()
        self.display.root_group = self.root_group
        
        # Create bitmap for direct pixel manipulation
        self.bitmap = displayio.Bitmap(self.width, self.height, 65536)
        self.tile_grid = displayio.TileGrid(
            self.bitmap,
            pixel_shader=displayio.ColorConverter(),
        )
        self.root_group.append(self.tile_grid)
        
        # Double buffer for smooth updates
        self.back_bitmap = displayio.Bitmap(self.width, self.height, 65536)
        
    def set_brightness(self, value):
        """Set display brightness (0.0-1.0)."""
        self.brightness = max(0.0, min(1.0, value))
        self.display.brightness = self.brightness
        
    def clear(self):
        """Clear the display to black."""
        for y in range(self.height):
            for x in range(self.width):
                self.bitmap[x, y] = 0
                
    def draw_pixel(self, x, y, r, g, b):
        """Draw a single pixel with RGB888 values."""
        if 0 <= x < self.width and 0 <= y < self.height:
            # Convert RGB888 to RGB565
            r5 = r >> 3
            g6 = g >> 2
            b5 = b >> 3
            color = (r5 << 11) | (g6 << 5) | b5
            self.bitmap[x, y] = color
            
    def draw_pixel_rgb565(self, x, y, color):
        """Draw a single pixel with RGB565 color value."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.bitmap[x, y] = color
            
    def fill_screen(self, color=0):
        """Fill the screen with a single color."""
        for y in range(self.height):
            for x in range(self.width):
                self.bitmap[x, y] = color
                
    def swap_buffers(self):
        """Swap front and back buffers for double buffering."""
        # Copy back buffer to front
        for y in range(self.height):
            for x in range(self.width):
                self.bitmap[x, y] = self.back_bitmap[x, y]
                
    def get_back_buffer(self):
        """Get the back buffer for drawing."""
        return self.back_bitmap
        
    def set_back_pixel(self, x, y, r, g, b):
        """Set a pixel in the back buffer."""
        if 0 <= x < self.width and 0 <= y < self.height:
            r5 = r >> 3
            g6 = g >> 2
            b5 = b >> 3
            color = (r5 << 11) | (g6 << 5) | b5
            self.back_bitmap[x, y] = color
            
    def flip(self):
        """Flip the buffer (swap and show)."""
        self.swap_buffers()
        
    def set_rotation(self, rotation):
        """Set display rotation (0, 90, 180, 270)."""
        self.display.rotation = rotation


# Global display instance
display_driver = None


def init_display():
    """Initialize and return the display driver."""
    global display_driver
    display_driver = DisplayDriver()
    return display_driver
