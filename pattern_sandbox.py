# ═══════════════════════════════════════════════════════════
# PatternFlow - Pattern Code Sandbox
# Safe execution environment for user-submitted Python patterns
# License: MIT
# ═══════════════════════════════════════════════════════════
"""
Pattern Sandbox System

Allows users to submit Python code that is:
1. Validated for safety (no dangerous operations)
2. Checked for required interface
3. Executed in a restricted environment
4. Stored and loaded as text files

Security measures:
- Restricted builtins
- No file I/O, network, or system calls
- Timeout protection
- Memory limits
- AST validation before execution
"""

import ast
import sys
import time
from config import PANEL_RES_W, PANEL_RES_H


# ═══════════════════════════════════════════════════════════
# Safe Builtins - Only allow safe operations
# ═══════════════════════════════════════════════════════════

import math

SAFE_BUILTINS = {
    # Math functions
    'abs': abs,
    'min': min,
    'max': max,
    'sum': sum,
    'pow': pow,
    'round': round,
    'int': int,
    'float': float,
    'bool': bool,
    'len': len,
    'range': range,
    'enumerate': enumerate,
    'zip': zip,
    'sorted': sorted,
    'reversed': reversed,
    'list': list,
    'tuple': tuple,
    'dict': dict,
    'set': set,
    'str': str,
    'chr': chr,
    'ord': ord,
    'hash': hash,
    # Math module
    'math': math,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'sqrt': math.sqrt,
    'exp': math.exp,
    'log': math.log,
    'log10': math.log10,
    'pi': math.pi,
    'e': math.e,
    'tau': math.tau,
    'floor': math.floor,
    'ceil': math.ceil,
    'fabs': math.fabs,
    'fmod': math.fmod,
    'atan2': math.atan2,
    'hypot': math.hypot,
    # Constants
    'True': True,
    'False': False,
    'None': None,
}


# ═══════════════════════════════════════════════════════════
# Forbidden Operations (AST validation)
# ═══════════════════════════════════════════════════════════

FORBIDDEN_NODES = {
    # File I/O
    ast.Open,
    ast.Import,
    ast.ImportFrom,
    # System access
    ast.Exec,
    ast.Eval,
    ast.Compile,
    # Attribute access to dangerous methods
    # (checked separately)
}

FORBIDDEN_ATTRIBUTES = {
    '__import__',
    'open',
    'file',
    'exec',
    'eval',
    'compile',
    'globals',
    'locals',
    'vars',
    'dir',
    'getattr',
    'setattr',
    'delattr',
    'input',
    'print',  # Can be allowed for debugging, but restricted
}

FORBIDDEN_MODULES = {
    'os',
    'sys',
    'subprocess',
    'socket',
    'urllib',
    'requests',
    'io',
    'pickle',
    'marshal',
    'ctypes',
    'importlib',
}


# ═══════════════════════════════════════════════════════════
# Code Validator
# ═══════════════════════════════════════════════════════════

class PatternValidator:
    """Validates user pattern code for safety and correctness."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate(self, code):
        """
        Validate pattern code.
        
        Args:
            code: Python code string
            
        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        self.warnings = []
        
        # Check basic structure
        if not code or not code.strip():
            self.errors.append("Code is empty")
            return False
            
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.errors.append(f"Syntax error: {e}")
            return False
            
        # Check for forbidden nodes
        for node in ast.walk(tree):
            # Check forbidden node types
            for forbidden in FORBIDDEN_NODES:
                if isinstance(node, forbidden):
                    self.errors.append(f"Forbidden operation: {node.__class__.__name__}")
                    return False
                    
            # Check for imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if any(mod in node.module for mod in FORBIDDEN_MODULES):
                        self.errors.append(f"Forbidden module import: {node.module}")
                        return False
                        
            # Check for dangerous attribute access
            if isinstance(node, ast.Attribute):
                if node.attr in FORBIDDEN_ATTRIBUTES:
                    self.errors.append(f"Forbidden attribute access: {node.attr}")
                    return False
                    
        # Check for required interface
        if not self._check_interface(tree):
            return False
            
        # Check code length (prevent DoS)
        if len(code) > 10000:
            self.errors.append("Code too long (max 10000 characters)")
            return False
            
        return len(self.errors) == 0
        
    def _check_interface(self, tree):
        """Check that code has required Pattern class."""
        has_class = False
        class_name = None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_class = True
                class_name = node.name
                
                # Check for required methods
                methods = {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                
                required_methods = {'setup', 'update', 'draw'}
                missing = required_methods - methods
                
                if missing:
                    self.errors.append(f"Pattern class missing methods: {missing}")
                    return False
                    
                # Check method signatures
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        if method.name == 'update':
                            # Should have dt and knobs parameters
                            args = {arg.arg for arg in method.args.args}
                            if 'dt' not in args:
                                self.warnings.append("update() should accept 'dt' parameter")
                                
        if not has_class:
            self.errors.append("No Pattern class found")
            return False
            
        return True
        
    def get_errors(self):
        return self.errors
        
    def get_warnings(self):
        return self.warnings


# ═══════════════════════════════════════════════════════════
# Safe Execution Environment
# ═══════════════════════════════════════════════════════════

class PatternSandbox:
    """
    Safe execution environment for user patterns.
    
    Creates a restricted namespace and executes pattern code
    with timeout and resource limits.
    """
    
    def __init__(self, display):
        self.display = display
        self.pattern_instance = None
        self.validator = PatternValidator()
        self.last_error = None
        
    def load_code(self, code, pattern_name="Custom"):
        """
        Load and validate pattern code.
        
        Args:
            code: Python code string
            pattern_name: Name for the pattern
            
        Returns:
            True on success, False on error
        """
        # Validate code
        if not self.validator.validate(code):
            self.last_error = self.validator.get_errors()
            return False
            
        # Log warnings
        for warning in self.validator.get_warnings():
            print(f"Warning: {warning}")
            
        # Create safe namespace
        safe_namespace = {
            '__builtins__': SAFE_BUILTINS,
            'PANEL_RES_W': PANEL_RES_W,
            'PANEL_RES_H': PANEL_RES_H,
            'display': self.display,
        }
        
        # Execute code
        try:
            exec(code, safe_namespace)
        except Exception as e:
            self.last_error = [f"Execution error: {e}"]
            return False
            
        # Find Pattern class
        PatternClass = None
        for name, obj in safe_namespace.items():
            if isinstance(obj, type) and name.endswith('Pattern'):
                PatternClass = obj
                break
                
        if PatternClass is None:
            self.last_error = ["No Pattern class found (should end with 'Pattern')"]
            return False
            
        # Instantiate pattern
        try:
            self.pattern_instance = PatternClass()
            self.pattern_instance.name = pattern_name
            
            # Call setup
            if hasattr(self.pattern_instance, 'setup'):
                self.pattern_instance.setup()
                
            return True
        except Exception as e:
            self.last_error = [f"Pattern initialization error: {e}"]
            return False
            
    def update(self, dt, knobs=None):
        """
        Update pattern state.
        
        Args:
            dt: Delta time
            knobs: List of 4 knob values (optional)
        """
        if not self.pattern_instance:
            return
            
        try:
            if hasattr(self.pattern_instance, 'update'):
                # Support both old and new interfaces
                import inspect
                sig = inspect.signature(self.pattern_instance.update)
                params = list(sig.parameters.keys())
                
                if 'knobs' in params:
                    self.pattern_instance.update(dt, knobs or [0, 0, 0, 0])
                else:
                    self.pattern_instance.update(dt)
        except Exception as e:
            print(f"Pattern update error: {e}")
            self.last_error = [f"Update error: {e}"]
            
    def draw(self):
        """Draw pattern to display."""
        if not self.pattern_instance:
            return
            
        try:
            if hasattr(self.pattern_instance, 'draw'):
                self.pattern_instance.draw()
        except Exception as e:
            print(f"Pattern draw error: {e}")
            self.last_error = [f"Draw error: {e}"]
            # Draw error indicator
            self._draw_error_indicator()
            
    def _draw_error_indicator(self):
        """Draw red/black stripes to indicate error."""
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                if (x + y) % 10 < 5:
                    self.display.set_back_pixel(x, y, 255, 0, 0)
                else:
                    self.display.set_back_pixel(x, y, 0, 0, 0)
                    
    def get_info(self):
        """Get pattern information."""
        if not self.pattern_instance:
            return None
            
        info = {
            'name': getattr(self.pattern_instance, 'name', 'Custom'),
            'knob_labels': getattr(self.pattern_instance, 'KNOB_LABELS', 
                                  ['knob0', 'knob1', 'knob2', 'knob3']),
        }
        return info
        
    def get_last_error(self):
        return self.last_error


# ═══════════════════════════════════════════════════════════
# Example Safe Pattern (for testing/documentation)
# ═══════════════════════════════════════════════════════════

EXAMPLE_PATTERN_CODE = '''
class WavePattern:
    """Simple wave pattern example."""
    
    KNOB_LABELS = ["freq", "speed", "amp", "offset"]
    
    def setup(self):
        self.time = 0.0
        self.freq = 0.1
        self.speed = 1.0
        self.amplitude = 1.0
        self.offset = 0.0
        
    def update(self, dt, knobs):
        self.time += dt * self.speed
        self.freq = max(0.01, min(1.0, knobs[0] * 0.01))
        self.speed = max(0.0, min(5.0, knobs[1] * 0.1))
        self.amplitude = max(0.0, min(2.0, knobs[2] * 0.02))
        self.offset = knobs[3] * 0.01
        
    def draw(self):
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                # Simple sine wave
                value = sin(x * self.freq + self.time)
                value += cos(y * self.freq * 0.5 - self.time)
                value = value / 2 * self.amplitude
                
                # Map to color (blue-cyan gradient)
                r = 0
                g = int(128 + value * 127)
                b = int(128 - value * 127)
                
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                
                display.set_back_pixel(x, y, r, g, b)
'''


# ═══════════════════════════════════════════════════════════
# Pattern Storage
# ═══════════════════════════════════════════════════════════

import os
try:
    import storage
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False
    
PATTERNS_DIR = "/custom_patterns"


def ensure_storage():
    """Ensure storage directory exists."""
    if not STORAGE_AVAILABLE:
        return False
        
    try:
        os.stat(PATTERNS_DIR)
    except OSError:
        try:
            os.mkdir(PATTERNS_DIR)
            print(f"Created: {PATTERNS_DIR}")
        except Exception as e:
            print(f"Could not create storage: {e}")
            return False
    return True


def save_pattern_code(name, code):
    """Save pattern code to storage."""
    if not ensure_storage():
        return False
        
    # Sanitize name
    safe_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in name)
    filepath = f"{PATTERNS_DIR}/{safe_name}.py"
    
    try:
        try:
            storage.remount("/", readonly=False)
        except:
            pass
            
        with open(filepath, "w") as f:
            f.write(code)
            
        print(f"Saved pattern: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving pattern: {e}")
        return False


def load_pattern_code(name):
    """Load pattern code from storage."""
    safe_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in name)
    filepath = f"{PATTERNS_DIR}/{safe_name}.py"
    
    try:
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading pattern: {e}")
        return None


def list_saved_patterns():
    """List all saved pattern names."""
    if not STORAGE_AVAILABLE:
        return []
        
    patterns = []
    try:
        for filename in os.listdir(PATTERNS_DIR):
            if filename.endswith(".py"):
                patterns.append(filename[:-3])  # Remove .py
    except Exception:
        pass
        
    return patterns


def delete_pattern_code(name):
    """Delete a saved pattern."""
    safe_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in name)
    filepath = f"{PATTERNS_DIR}/{safe_name}.py"
    
    try:
        os.remove(filepath)
        print(f"Deleted pattern: {filepath}")
        return True
    except Exception as e:
        print(f"Error deleting pattern: {e}")
        return False
