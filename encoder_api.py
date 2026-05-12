# ═══════════════════════════════════════════════════════════
# PatternFlow - Encoder API with REST Endpoints
# CircuitPython implementation for MatrixPortal M4
# License: MIT
# ═══════════════════════════════════════════════════════════

import json
import socket
from config import KNOB_DEFAULTS, KNOB_LABELS
from pattern_sandbox import (
    PatternSandbox, PatternValidator, EXAMPLE_PATTERN_CODE,
    save_pattern_code, load_pattern_code, list_saved_patterns, delete_pattern_code
)
from web_code_editor import CODE_EDITOR_HTML


class EncoderAPI:
    """
    REST API server for controlling virtual encoder knobs.
    Replaces physical rotary encoders with HTTP endpoints.
    """
    
    def __init__(self, wifi_manager, display=None, registry=None):
        self.wifi_manager = wifi_manager
        self.display = display
        self.registry = registry
        self.server_socket = None
        self.knob_values = [0, 0, 0, 0]  # knob0, knob1, knob2, knob3
        self.knob_deltas = [0, 0, 0, 0]  # Changes since last read
        self.current_pattern = "Origin"
        self.sandbox = None
        self.custom_pattern_active = False
        if display:
            self.sandbox = PatternSandbox(display)
        
    def set_pattern(self, pattern_name):
        """Set current pattern and reset knobs to defaults."""
        if pattern_name in KNOB_DEFAULTS:
            self.current_pattern = pattern_name
            self.knob_values = list(KNOB_DEFAULTS[pattern_name])
            self.knob_deltas = [0, 0, 0, 0]
            self.custom_pattern_active = False
            return True
        return False
        
    def set_custom_pattern(self, code, name="Custom"):
        """Load and activate a custom pattern from code."""
        # Try registry first (if available)
        if self.registry and hasattr(self.registry, 'set_custom_pattern'):
            if self.registry.set_custom_pattern(code, name):
                self.custom_pattern_active = True
                self.current_pattern = name
                return True
            return False
            
        # Fallback to local sandbox
        if self.sandbox:
            if self.sandbox.load_code(code, name):
                self.custom_pattern_active = True
                self.current_pattern = name
                info = self.sandbox.get_info()
                if info and 'knob_labels' in info:
                    KNOB_LABELS[name] = info['knob_labels']
                return True
        return False
        
    def get_custom_pattern_info(self):
        """Get info about active custom pattern."""
        if self.sandbox and self.custom_pattern_active:
            return self.sandbox.get_info()
        return None
        
    def get_knob_values(self):
        """Get current knob values."""
        return list(self.knob_values)
    
    def get_knob_deltas(self):
        """Get and reset knob deltas."""
        deltas = list(self.knob_deltas)
        self.knob_deltas = [0, 0, 0, 0]
        return deltas
    
    def set_knob(self, index, value):
        """Set a knob value and update delta."""
        if 0 <= index < 4:
            old_value = self.knob_values[index]
            self.knob_values[index] = value
            self.knob_deltas[index] = value - old_value
            return True
        return False
        
    def adjust_knob(self, index, delta):
        """Adjust a knob by a delta value."""
        if 0 <= index < 4:
            self.knob_values[index] += delta
            self.knob_deltas[index] += delta
            return True
        return False
        
    def reset_knobs(self):
        """Reset all knobs to pattern defaults."""
        if self.current_pattern in KNOB_DEFAULTS:
            self.knob_values = list(KNOB_DEFAULTS[self.current_pattern])
            self.knob_deltas = [0, 0, 0, 0]
            
    def parse_request(self, request_data):
        """Parse HTTP request and return method, path, and body."""
        try:
            lines = request_data.split('\r\n')
            if not lines:
                return None, None, None
                
            request_line = lines[0]
            parts = request_line.split(' ')
            if len(parts) < 2:
                return None, None, None
                
            method = parts[0]
            path = parts[1]
            
            # Find body (after empty line)
            body = None
            for i, line in enumerate(lines):
                if line == '':
                    if i + 1 < len(lines):
                        body = '\r\n'.join(lines[i+1:])
                    break
                    
            return method, path, body
        except Exception as e:
            print(f"Error parsing request: {e}")
            return None, None, None
            
    def handle_api_request(self, method, path, body):
        """Handle API request and return response."""
        response_data = None
        status = "200 OK"
        
        try:
            # GET /api/knobs - Get all knob values
            if path == '/api/knobs' and method == 'GET':
                response_data = {
                    "knob0": self.knob_values[0],
                    "knob1": self.knob_values[1],
                    "knob2": self.knob_values[2],
                    "knob3": self.knob_values[3],
                    "labels": KNOB_LABELS.get(self.current_pattern, ["", "", "", ""])
                }
                
            # POST /api/knobs - Set all knob values
            elif path == '/api/knobs' and method == 'POST':
                if body:
                    data = json.loads(body)
                    for i in range(4):
                        key = f"knob{i}"
                        if key in data:
                            self.set_knob(i, float(data[key]))
                    response_data = {"status": "ok", "knobs": self.knob_values}
                    
            # POST /api/knobs/reset - Reset knobs
            elif path == '/api/knobs/reset' and method == 'POST':
                self.reset_knobs()
                response_data = {"status": "ok", "knobs": self.knob_values}
                
            # GET /api/knob/N - Get individual knob
            elif path.startswith('/api/knob/') and method == 'GET':
                try:
                    index = int(path.split('/')[-1])
                    if 0 <= index < 4:
                        response_data = {
                            "knob": index,
                            "value": self.knob_values[index],
                            "label": KNOB_LABELS.get(self.current_pattern, ["", "", "", ""])[index]
                        }
                    else:
                        status = "400 Bad Request"
                        response_data = {"error": "Invalid knob index"}
                except ValueError:
                    status = "400 Bad Request"
                    response_data = {"error": "Invalid knob index"}
                    
            # POST /api/knob/N - Set individual knob
            elif path.startswith('/api/knob/') and method == 'POST':
                try:
                    index = int(path.split('/')[-1])
                    if 0 <= index < 4 and body:
                        data = json.loads(body)
                        value = float(data.get('value', 0))
                        self.set_knob(index, value)
                        response_data = {
                            "status": "ok",
                            "knob": index,
                            "value": self.knob_values[index]
                        }
                    else:
                        status = "400 Bad Request"
                        response_data = {"error": "Invalid knob index"}
                except ValueError:
                    status = "400 Bad Request"
                    response_data = {"error": "Invalid knob index"}
                    
            # GET /api/patterns - Get pattern list
            elif path == '/api/patterns' and method == 'GET':
                response_data = {
                    "patterns": list(KNOB_DEFAULTS.keys()),
                    "current": self.current_pattern
                }
                
            # POST /api/pattern - Change pattern
            elif path == '/api/pattern' and method == 'POST':
                if body:
                    data = json.loads(body)
                    pattern = data.get('pattern')
                    if isinstance(pattern, int):
                        pattern_names = list(KNOB_DEFAULTS.keys())
                        if 0 <= pattern < len(pattern_names):
                            self.set_pattern(pattern_names[pattern])
                            response_data = {"status": "ok", "pattern": self.current_pattern}
                        else:
                            status = "400 Bad Request"
                            response_data = {"error": "Invalid pattern index"}
                    elif isinstance(pattern, str):
                        if self.set_pattern(pattern):
                            response_data = {"status": "ok", "pattern": self.current_pattern}
                        else:
                            status = "400 Bad Request"
                            response_data = {"error": "Unknown pattern"}
                    else:
                        status = "400 Bad Request"
                        response_data = {"error": "Invalid pattern format"}
                        
            # GET / - Main page
            elif path == '/' and method == 'GET':
                response_data = self._get_main_page()
                content_type = "text/html"
                return self._build_response(status, response_data, content_type)
                
            # GET /code - Pattern code editor
            elif path == '/code' and method == 'GET':
                response_data = CODE_EDITOR_HTML
                content_type = "text/html"
                return self._build_response(status, response_data, content_type)
                
            # POST /api/pattern_code/validate - Validate pattern code
            elif path == '/api/pattern_code/validate' and method == 'POST':
                if body:
                    data = json.loads(body)
                    code = data.get('code', '')
                    validator = PatternValidator()
                    valid = validator.validate(code)
                    response_data = {
                        "valid": valid,
                        "errors": validator.get_errors() if not valid else [],
                        "warnings": validator.get_warnings(),
                    }
                    # Try to extract knob labels from code
                    if valid:
                        labels = self._extract_knob_labels(code)
                        if labels:
                            response_data["knob_labels"] = labels
                else:
                    status = "400 Bad Request"
                    response_data = {"error": "No code provided"}
                    
            # POST /api/pattern_code/apply - Apply pattern code to matrix
            elif path == '/api/pattern_code/apply' and method == 'POST':
                if body:
                    data = json.loads(body)
                    code = data.get('code', '')
                    name = data.get('name', 'Custom')
                    
                    if self.set_custom_pattern(code, name):
                        response_data = {"status": "ok", "pattern": name}
                    else:
                        status = "400 Bad Request"
                        errors = self.sandbox.get_last_error() if self.sandbox else ["Sandbox not initialized"]
                        response_data = {"error": errors[0] if errors else "Failed to load pattern"}
                else:
                    status = "400 Bad Request"
                    response_data = {"error": "No code provided"}
                    
            # POST /api/pattern_code/save - Save pattern code
            elif path == '/api/pattern_code/save' and method == 'POST':
                if body:
                    data = json.loads(body)
                    code = data.get('code', '')
                    name = data.get('name', 'Custom')
                    
                    if save_pattern_code(name, code):
                        response_data = {"status": "ok", "name": name}
                    else:
                        status = "500 Internal Server Error"
                        response_data = {"error": "Failed to save pattern"}
                else:
                    status = "400 Bad Request"
                    response_data = {"error": "No code provided"}
                    
            # GET /api/pattern_code/list - List saved patterns
            elif path == '/api/pattern_code/list' and method == 'GET':
                patterns = list_saved_patterns()
                response_data = {"patterns": patterns}
                
            # GET /api/pattern_code/load/NAME - Load saved pattern code
            elif path.startswith('/api/pattern_code/load/') and method == 'GET':
                name = path.split('/')[-1]
                code = load_pattern_code(name)
                if code:
                    response_data = {"name": name, "code": code}
                else:
                    status = "404 Not Found"
                    response_data = {"error": "Pattern not found"}
                    
            # DELETE /api/pattern_code/delete/NAME - Delete saved pattern
            elif path.startswith('/api/pattern_code/delete/') and method == 'DELETE':
                name = path.split('/')[-1]
                if delete_pattern_code(name):
                    response_data = {"status": "ok"}
                else:
                    status = "500 Internal Server Error"
                    response_data = {"error": "Failed to delete pattern"}
                    
            # GET /api/pattern_code/example - Get example pattern code
            elif path == '/api/pattern_code/example' and method == 'GET':
                response_data = {"code": EXAMPLE_PATTERN_CODE}
                
            else:
                status = "404 Not Found"
                response_data = {"error": "Not Found"}
                
            content_type = "application/json"
            return self._build_response(status, response_data, content_type)
            
        except json.JSONDecodeError:
            status = "400 Bad Request"
            response_data = {"error": "Invalid JSON"}
            return self._build_response(status, response_data, "application/json")
        except Exception as e:
            status = "500 Internal Server Error"
            response_data = {"error": str(e)}
            return self._build_response(status, response_data, "application/json")
            
    def _build_response(self, status, data, content_type="application/json"):
        """Build HTTP response."""
        if content_type == "application/json":
            body = json.dumps(data)
        else:
            body = data
            
        response = f"HTTP/1.1 {status}\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        response += body
        
        return response.encode('utf-8')
        
    def _extract_knob_labels(self, code):
        """Extract KNOB_LABELS from pattern code."""
        import re
        # Look for KNOB_LABELS = [...]
        match = re.search(r'KNOB_LABELS\s*=\s*\[([^\]]+)\]', code)
        if match:
            labels_str = match.group(1)
            # Extract strings from the list
            labels = re.findall(r'["\']([^"\']+)["\']', labels_str)
            if len(labels) >= 4:
                return labels[:4]
        return None
        
    def _get_main_page(self):
        """Return simple HTML main page."""
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>PatternFlow - {self.current_pattern}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial; max-width: 600px; margin: 20px auto; padding: 20px; }}
        h1 {{ color: #333; }}
        .knob {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
        .knob label {{ display: inline-block; width: 100px; }}
        .knob input {{ width: 200px; }}
        button {{ padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }}
        button:hover {{ background: #0056b3; }}
        #status {{ margin-top: 20px; padding: 10px; background: #e7f3ff; border-radius: 5px; }}
        .nav {{ margin-bottom: 20px; }}
        .nav a {{ text-decoration: none; color: #007bff; margin-right: 15px; }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Controls</a>
        <a href="/code">Code Editor</a>
    </div>
    <h1>PatternFlow Control</h1>
    <p>Current Pattern: <strong>{self.current_pattern}</strong></p>
    
    <h2>Knob Controls</h2>
    <div id="knobs">
        <div class="knob">
            <label>Knob 0:</label>
            <input type="range" id="k0" min="0" max="360" value="{int(self.knob_values[0])}" oninput="updateKnob(0, this.value)">
            <span id="v0">{int(self.knob_values[0])}</span>
        </div>
        <div class="knob">
            <label>Knob 1:</label>
            <input type="range" id="k1" min="0" max="5" step="0.1" value="{self.knob_values[1]}" oninput="updateKnob(1, this.value)">
            <span id="v1">{self.knob_values[1]}</span>
        </div>
        <div class="knob">
            <label>Knob 2:</label>
            <input type="range" id="k2" min="0" max="4" step="1" value="{int(self.knob_values[2])}" oninput="updateKnob(2, this.value)">
            <span id="v2">{int(self.knob_values[2])}</span>
        </div>
        <div class="knob">
            <label>Knob 3:</label>
            <input type="range" id="k3" min="0" max="1000" value="{int(self.knob_values[3])}" oninput="updateKnob(3, this.value)">
            <span id="v3">{int(self.knob_values[3])}</span>
        </div>
    </div>
    
    <h2>Pattern Selection</h2>
    <button onclick="setPattern('Origin')">Origin</button>
    <button onclick="setPattern('Wave Saw')">Wave Saw</button>
    <button onclick="setPattern('Liquid Plasma')">Liquid Plasma</button>
    
    <div id="status"></div>
    
    <script>
        async function updateKnob(index, value) {{
            document.getElementById('v' + index).textContent = value;
            const response = await fetch('/api/knob/' + index, {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{value: parseFloat(value)}})
            }});
            const data = await response.json();
            document.getElementById('status').textContent = 'Knob ' + index + ' updated';
        }}
        
        async function setPattern(name) {{
            const response = await fetch('/api/pattern', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{pattern: name}})
            }});
            const data = await response.json();
            if (data.status === 'ok') {{
                location.reload();
            }}
        }}
    </script>
</body>
</html>'''
        
    def start_server(self, port=80):
        """Start the HTTP server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', port))
        self.server_socket.listen(1)
        self.server_socket.settimeout(1.0)  # 1 second timeout
        print(f"API server listening on port {port}")
        
    def stop_server(self):
        """Stop the HTTP server."""
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            
    def poll(self):
        """Poll for incoming connections and handle requests."""
        if not self.server_socket:
            return
            
        try:
            client_socket, addr = self.server_socket.accept()
            try:
                request = client_socket.recv(4096).decode('utf-8')
                if request:
                    method, path, body = self.parse_request(request)
                    if method and path:
                        response = self.handle_api_request(method, path, body)
                        client_socket.send(response)
            except Exception as e:
                print(f"Error handling client: {e}")
            finally:
                client_socket.close()
        except OSError:
            # Timeout, no client
            pass
        except Exception as e:
            print(f"Server error: {e}")


# Global API instance
encoder_api = None


def init_encoder_api(wifi_manager):
    """Initialize and return the encoder API."""
    global encoder_api
    encoder_api = EncoderAPI(wifi_manager)
    return encoder_api
