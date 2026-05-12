# ═══════════════════════════════════════════════════════════
# PatternFlow for MatrixPortal M4
# CircuitPython Implementation
# License: MIT
# ═══════════════════════════════════════════════════════════
"""
PatternFlow - Generative LED Matrix Patterns with REST API Control

This is a CircuitPython port of the original PatternFlow firmware for the
MatrixPortal M4 board. Physical rotary encoders are replaced with REST API
endpoints for remote control.

Features:
- 3 generative patterns (Origin, Wave Saw, Liquid Plasma)
- REST API for knob control
- Web interface for pattern selection
- Real-time parameter adjustment
"""

import time
import board
import digitalio
from display_driver import init_display, DisplayDriver
from wifi_manager import init_wifi
from encoder_api import init_encoder_api
from patterns import OriginPattern, WaveSawPattern, LiquidPlasmaPattern
from pattern_sandbox import PatternSandbox
from config import KNOB_DEFAULTS

# ═══════════════════════════════════════════════════════════
# Pattern Registry
# ═══════════════════════════════════════════════════════════

PATTERNS = {
    "Origin": OriginPattern,
    "Wave Saw": WaveSawPattern,
    "Liquid Plasma": LiquidPlasmaPattern,
}

PATTERN_LIST = list(PATTERNS.keys())


class PatternRegistry:
    """Manages pattern selection and lifecycle."""
    
    def __init__(self, display, api):
        self.display = display
        self.api = api
        self.patterns = {}
        self.current_pattern_name = None
        self.current_pattern = None
        self.sandbox = PatternSandbox(display)
        self.using_custom = False
        
        # Initialize all patterns
        for name, pattern_class in PATTERNS.items():
            self.patterns[name] = pattern_class(display)
            
        # Set default pattern
        self.set_pattern("Origin")
        
    def set_pattern(self, name):
        """Set the current pattern by name."""
        if name in self.patterns:
            self.current_pattern_name = name
            self.current_pattern = self.patterns[name]
            self.current_pattern.setup()
            self.using_custom = False
            print(f"Pattern changed to: {name}")
            return True
        print(f"Unknown pattern: {name}")
        return False
        
    def set_custom_pattern(self, code, pattern_name="Custom"):
        """Load a custom pattern from code."""
        if self.sandbox.load_code(code, pattern_name):
            self.current_pattern_name = pattern_name
            self.using_custom = True
            print(f"Custom pattern loaded: {pattern_name}")
            return True
        print(f"Failed to load custom pattern")
        return False
        
    def get_pattern_names(self):
        """Get list of available pattern names."""
        return PATTERN_LIST
        
    def update(self, dt, knob_values, knob_deltas):
        """Update current pattern."""
        if self.using_custom:
            self.sandbox.update(dt, knob_values)
        elif self.current_pattern:
            self.current_pattern.update(dt, knob_values, knob_deltas)
            
    def draw(self):
        """Draw current pattern."""
        if self.using_custom:
            self.sandbox.draw()
        elif self.current_pattern:
            self.current_pattern.draw()


# ═══════════════════════════════════════════════════════════
# Main Application
# ═══════════════════════════════════════════════════════════

class PatternFlowApp:
    """Main application class."""
    
    def __init__(self):
        self.display = None
        self.wifi = None
        self.api = None
        self.registry = None
        self.last_time = 0
        self.running = True
        
        # Mode state (for pattern selection mode)
        self.mode = "running"  # "running" or "selecting"
        self.mode_hold_start = 0
        
    def init(self):
        """Initialize all components."""
        print("\n=== PatternFlow CircuitPython Booting ===\n")
        
        # Initialize display
        print("Initializing display...")
        self.display = init_display()
        self.display.clear()
        
        # Initialize WiFi
        print("Initializing WiFi...")
        self.wifi = init_wifi()
        
        # Initialize API server first (needed by registry)
        print("Initializing API server...")
        self.api = init_encoder_api(self.wifi, self.display)
        self.api.start_server(80)
        
        # Initialize pattern registry (with api reference)
        print("Initializing patterns...")
        self.registry = PatternRegistry(self.display, self.api)
        
        # Connect registry to API for custom pattern handling
        self.api.registry = self.registry
        
        print("\n=== Ready ===")
        ip = self.wifi.get_ip()
        if ip:
            print(f"Web Interface: http://{ip}")
            print(f"API Endpoints: http://{ip}/api/")
        else:
            print("WiFi not connected - API server running locally")
        print("\n")
        
        self.last_time = time.monotonic()
        
    def run(self):
        """Main application loop."""
        print("Starting main loop...\n")
        
        while self.running:
            try:
                current_time = time.monotonic()
                dt = current_time - self.last_time
                self.last_time = current_time
                
                # Poll API server for incoming requests
                self.api.poll()
                
                # Get knob values and deltas from API
                knob_values = self.api.get_knob_values()
                knob_deltas = self.api.get_knob_deltas()
                
                # Check for pattern change requests via API
                # (Pattern selection is done through API, not physical buttons)
                
                # Update and draw pattern
                self.registry.update(dt, knob_values, knob_deltas)
                self.registry.draw()
                
                # Flip buffer to show new frame
                self.display.flip()
                
                # Small delay to prevent CPU hogging
                time.sleep(0.01)
                
            except KeyboardInterrupt:
                print("\nShutting down...")
                self.running = False
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(0.1)
                
        # Cleanup
        self.cleanup()
        
    def cleanup(self):
        """Clean up resources."""
        if self.api:
            self.api.stop_server()
        self.display.clear()


# ═══════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════

# Built-in LED for status indication
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

app = None

try:
    app = PatternFlowApp()
    app.init()
    led.value = True  # Turn on LED when ready
    app.run()
except Exception as e:
    print(f"Fatal error: {e}")
    import traceback
    traceback.print_exception(e)
    led.value = False
finally:
    led.value = False
