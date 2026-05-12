# ═══════════════════════════════════════════════════════════
# PatternFlow - Code Editor Web Interface
# HTML/JavaScript for writing custom pattern code
# License: MIT
# ═══════════════════════════════════════════════════════════

CODE_EDITOR_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PatternFlow - Pattern Code Editor</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/theme/dracula.min.css">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #c9d1d9;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1600px; margin: 0 auto; }
        
        header {
            text-align: center;
            padding: 20px 0 30px;
            border-bottom: 1px solid #30363d;
            margin-bottom: 30px;
        }
        header h1 {
            font-size: 2rem;
            color: #58a6ff;
            margin-bottom: 10px;
        }
        header p { color: #8b949e; }
        
        .editor-layout {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 20px;
            height: calc(100vh - 200px);
            min-height: 600px;
        }
        
        .editor-panel {
            display: flex;
            flex-direction: column;
            background: #0d1117;
            border-radius: 8px;
            border: 1px solid #30363d;
            overflow: hidden;
        }
        
        .panel-header {
            padding: 12px 16px;
            background: #161b22;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .panel-header h2 {
            font-size: 0.9rem;
            color: #58a6ff;
            font-weight: 600;
        }
        
        .toolbar {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .btn-primary {
            background: #238636;
            color: #fff;
        }
        .btn-primary:hover { background: #2ea043; }
        .btn-secondary {
            background: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
        }
        .btn-secondary:hover { background: #30363d; }
        .btn-danger {
            background: #da3633;
            color: #fff;
        }
        .btn-danger:hover { background: #f85149; }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        #codeEditor {
            flex: 1;
            font-size: 14px;
        }
        .CodeMirror {
            height: 100% !important;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
            font-size: 14px;
        }
        
        .preview-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .preview-box {
            background: #0d1117;
            border-radius: 8px;
            border: 1px solid #30363d;
            overflow: hidden;
        }
        
        .matrix-preview {
            background: #000;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        #previewCanvas {
            width: 100%;
            max-width: 512px;
            aspect-ratio: 2/1;
            image-rendering: pixelated;
            border: 2px solid #30363d;
            border-radius: 4px;
        }
        
        .info-box {
            padding: 16px;
        }
        .info-box h3 {
            font-size: 0.85rem;
            color: #8b949e;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .pattern-info {
            background: #161b22;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 12px;
        }
        .pattern-info label {
            display: block;
            font-size: 0.8rem;
            color: #8b949e;
            margin-bottom: 4px;
        }
        .pattern-info input {
            width: 100%;
            padding: 8px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 4px;
            color: #c9d1d9;
            font-family: inherit;
            font-size: 0.9rem;
        }
        .pattern-info input:focus {
            outline: none;
            border-color: #58a6ff;
        }
        
        .knob-labels {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        .knob-labels input {
            font-size: 0.8rem;
            padding: 6px;
        }
        
        .console-output {
            background: #0d1117;
            border-radius: 6px;
            padding: 12px;
            font-family: 'SF Mono', monospace;
            font-size: 0.8rem;
            max-height: 200px;
            overflow-y: auto;
        }
        .console-line {
            padding: 2px 0;
            border-bottom: 1px solid #21262d;
        }
        .console-error { color: #ff7b72; }
        .console-success { color: #7ee787; }
        .console-info { color: #79c0ff; }
        
        .validation-status {
            padding: 12px 16px;
            border-radius: 6px;
            margin: 12px;
            font-size: 0.85rem;
        }
        .status-valid {
            background: rgba(46, 160, 67, 0.15);
            border: 1px solid #238636;
            color: #7ee787;
        }
        .status-error {
            background: rgba(218, 54, 51, 0.15);
            border: 1px solid #da3633;
            color: #ff7b72;
        }
        .status-pending {
            background: rgba(88, 166, 255, 0.15);
            border: 1px solid #58a6ff;
            color: #79c0ff;
        }
        
        .saved-list {
            max-height: 200px;
            overflow-y: auto;
        }
        .saved-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: #161b22;
            border-radius: 4px;
            margin-bottom: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .saved-item:hover { background: #21262d; }
        .saved-item-name {
            font-size: 0.85rem;
            color: #c9d1d9;
        }
        .saved-item-actions {
            display: flex;
            gap: 6px;
        }
        .saved-item-actions button {
            padding: 4px 8px;
            font-size: 0.75rem;
        }
        
        .examples-dropdown {
            margin: 12px;
        }
        .examples-dropdown select {
            width: 100%;
            padding: 8px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 4px;
            color: #c9d1d9;
            font-size: 0.85rem;
        }
        
        @media (max-width: 1200px) {
            .editor-layout {
                grid-template-columns: 1fr;
                height: auto;
            }
            .editor-panel {
                min-height: 500px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐍 Pattern Code Editor</h1>
            <p>Write custom Python patterns for your MatrixPortal M4</p>
        </header>
        
        <div class="editor-layout">
            <!-- Editor Panel -->
            <div class="editor-panel">
                <div class="panel-header">
                    <h2>pattern.py</h2>
                    <div class="toolbar">
                        <button class="btn btn-secondary" onclick="loadExample()">
                            📚 Load Example
                        </button>
                        <button class="btn btn-secondary" onclick="validateCode()">
                            ✓ Validate
                        </button>
                        <button class="btn btn-primary" onclick="applyPattern()">
                            ▶ Apply to Matrix
                        </button>
                        <button class="btn btn-secondary" onclick="savePattern()">
                            💾 Save
                        </button>
                    </div>
                </div>
                <textarea id="codeEditor"></textarea>
            </div>
            
            <!-- Preview Panel -->
            <div class="preview-panel">
                <!-- Preview Box -->
                <div class="preview-box">
                    <div class="panel-header">
                        <h2>Live Preview</h2>
                    </div>
                    <div class="matrix-preview">
                        <canvas id="previewCanvas" width="128" height="64"></canvas>
                    </div>
                    <div id="validationStatus" class="validation-status status-pending">
                        Ready to validate
                    </div>
                </div>
                
                <!-- Pattern Info -->
                <div class="preview-box">
                    <div class="panel-header">
                        <h2>Pattern Info</h2>
                    </div>
                    <div class="info-box">
                        <div class="pattern-info">
                            <label>Pattern Name</label>
                            <input type="text" id="patternName" placeholder="My Pattern" value="Custom Pattern">
                        </div>
                        <div class="pattern-info">
                            <label>Knob Labels (4 knobs)</label>
                            <div class="knob-labels">
                                <input type="text" id="knob0" placeholder="knob 0" value="param1">
                                <input type="text" id="knob1" placeholder="knob 1" value="param2">
                                <input type="text" id="knob2" placeholder="knob 2" value="param3">
                                <input type="text" id="knob3" placeholder="knob 3" value="param4">
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Console Output -->
                <div class="preview-box">
                    <div class="panel-header">
                        <h2>Output</h2>
                    </div>
                    <div class="info-box">
                        <div class="console-output" id="consoleOutput">
                            <div class="console-line console-info">Ready...</div>
                        </div>
                    </div>
                </div>
                
                <!-- Saved Patterns -->
                <div class="preview-box">
                    <div class="panel-header">
                        <h2>Saved Patterns</h2>
                    </div>
                    <div class="info-box">
                        <div class="saved-list" id="savedPatternsList">
                            <div class="console-line">Loading...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- CodeMirror -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/python/python.min.js"></script>
    
    <script>
        // Initialize CodeMirror editor
        let editor;
        let previewInterval = null;
        let time = 0;
        
        // Example patterns
        const EXAMPLES = {
            basic: `class BasicWavePattern:
    """Simple sine wave pattern."""
    
    KNOB_LABELS = ["frequency", "speed", "amplitude", "offset"]
    
    def setup(self):
        self.time = 0.0
        self.freq = 0.1
        self.speed = 1.0
        self.amplitude = 1.0
        
    def update(self, dt, knobs):
        self.time += dt * self.speed
        self.freq = knobs[0] * 0.01
        self.speed = knobs[1] * 0.1
        self.amplitude = knobs[2] * 0.02
        
    def draw(self):
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                value = sin(x * self.freq + self.time)
                value *= self.amplitude
                
                # Map to cyan color
                r = 0
                g = int(128 + value * 127)
                b = int(255 - value * 127)
                
                display.set_back_pixel(x, y, r, g, b)
`,
            plasma: `class PlasmaPattern:
    """Flowing plasma effect."""
    
    KNOB_LABELS = ["speed", "scale", "density", "hue_shift"]
    
    def setup(self):
        self.time = 0.0
        
    def update(self, dt, knobs):
        self.time += dt * (knobs[0] * 0.1 + 0.5)
        self.scale = knobs[1] * 0.001 + 0.01
        self.density = knobs[2] * 0.5 + 1.0
        self.hue_shift = knobs[3]
        
    def draw(self):
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                # Plasma calculation
                vx = x * self.scale
                vy = y * self.scale
                
                value = sin(vx + self.time)
                value += sin((vy + self.time) * self.density)
                value += sin((vx + vy + self.time) * 0.5)
                value += sin(sqrt(x*x + y*y) * self.scale + self.time)
                
                value = value / 4.0  # Normalize
                
                # HSV to RGB approximation
                h = (value + 1.0) * 0.5 + self.hue_shift
                h = h - int(h)  # Wrap to 0-1
                
                # Simple rainbow
                r = int(255 * max(0, sin(h * 2 * pi)))
                g = int(255 * max(0, sin((h - 0.33) * 2 * pi)))
                b = int(255 * max(0, sin((h - 0.66) * 2 * pi)))
                
                display.set_back_pixel(x, y, r, g, b)
`,
            mandelbrot: `class MiniMandelPattern:
    """Simplified Mandelbrot-like pattern."""
    
    KNOB_LABELS = ["zoom", "pan_x", "pan_y", "speed"]
    
    def setup(self):
        self.time = 0.0
        
    def update(self, dt, knobs):
        self.time += dt * knobs[3] * 0.1
        self.zoom = knobs[0] * 0.01 + 0.5
        self.pan_x = knobs[1] * 0.02 - 1.0
        self.pan_y = knobs[2] * 0.02 - 1.0
        
    def draw(self):
        for y in range(PANEL_RES_H):
            for x in range(PANEL_RES_W):
                # Map pixel to complex plane
                cx = (x - 64) / (64 * self.zoom) + self.pan_x
                cy = (y - 32) / (32 * self.zoom) + self.pan_y
                
                # Simple iteration
                zx = 0.0
                zy = 0.0
                iterations = 0
                
                for i in range(16):
                    zx2 = zx * zx
                    zy2 = zy * zy
                    if zx2 + zy2 > 4.0:
                        break
                    zy = 2 * zx * zy + cy * sin(self.time * 0.1)
                    zx = zx2 - zy2 + cx
                    iterations = i
                
                # Color based on iterations
                t = iterations / 16.0
                r = int(255 * t * sin(self.time * 0.5))
                g = int(255 * t * cos(self.time * 0.3))
                b = int(255 * t)
                
                display.set_back_pixel(x, y, r, g, b)
`,
        };
        
        function init() {
            // Initialize CodeMirror
            editor = CodeMirror.fromTextArea(
                document.getElementById("codeEditor"),
                {
                    mode: "python",
                    theme: "dracula",
                    lineNumbers: true,
                    indentUnit: 4,
                    tabSize: 4,
                    indentWithTabs: false,
                    matchBrackets: true,
                    autoCloseBrackets: true,
                    lineWrapping: false,
                }
            );
            
            // Load basic example
            editor.setValue(EXAMPLES.basic);
            
            // Start preview
            startPreview();
            
            // Load saved patterns
            loadSavedPatterns();
            
            log("Editor ready. Click 'Validate' to check your code.", "info");
        }
        
        // Validate code
        async function validateCode() {
            const code = editor.getValue();
            
            setStatus("pending", "Validating...");
            log("Sending code for validation...", "info");
            
            try {
                const response = await fetch("/api/pattern_code/validate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ code: code })
                });
                
                const result = await response.json();
                
                if (result.valid) {
                    setStatus("valid", "✓ Code is valid! Ready to apply.");
                    log("Validation successful!", "success");
                    if (result.warnings) {
                        result.warnings.forEach(w => log("Warning: " + w, "info"));
                    }
                    if (result.knob_labels) {
                        updateKnobLabels(result.knob_labels);
                    }
                } else {
                    setStatus("error", "✗ Validation failed: " + (result.errors[0] || "Unknown error"));
                    log("Validation errors:", "error");
                    result.errors.forEach(e => log("  • " + e, "error"));
                }
            } catch (err) {
                setStatus("error", "Connection error: " + err.message);
                log("Connection error: " + err.message, "error");
            }
        }
        
        // Apply pattern to matrix
        async function applyPattern() {
            const code = editor.getValue();
            const name = document.getElementById("patternName").value || "Custom";
            
            log("Applying pattern to matrix...", "info");
            
            try {
                const response = await fetch("/api/pattern_code/apply", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        code: code,
                        name: name
                    })
                });
                
                const result = await response.json();
                
                if (result.status === "ok") {
                    log("Pattern applied successfully!", "success");
                    setStatus("valid", "✓ Pattern running on matrix");
                } else {
                    log("Error: " + (result.error || "Unknown error"), "error");
                    setStatus("error", "✗ " + (result.error || "Failed to apply"));
                }
            } catch (err) {
                log("Connection error: " + err.message, "error");
                setStatus("error", "Connection error");
            }
        }
        
        // Save pattern
        async function savePattern() {
            const code = editor.getValue();
            const name = document.getElementById("patternName").value || "Custom";
            
            log("Saving pattern...", "info");
            
            try {
                const response = await fetch("/api/pattern_code/save", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        code: code,
                        name: name
                    })
                });
                
                const result = await response.json();
                
                if (result.status === "ok") {
                    log("Pattern saved as '" + name + "'", "success");
                    loadSavedPatterns();
                } else {
                    log("Error saving: " + (result.error || "Unknown error"), "error");
                }
            } catch (err) {
                log("Connection error: " + err.message, "error");
            }
        }
        
        // Load example
        function loadExample() {
            const examples = Object.keys(EXAMPLES);
            const current = examples.indexOf(
                Object.keys(EXAMPLES).find(k => 
                    editor.getValue().trim().startsWith(EXAMPLES[k].trim().substring(0, 20))
                )
            );
            const next = (current + 1) % examples.length;
            const name = examples[next];
            
            editor.setValue(EXAMPLES[name]);
            document.getElementById("patternName").value = name.charAt(0).toUpperCase() + name.slice(1);
            log("Loaded example: " + name, "info");
            validateCode();
        }
        
        // Load saved patterns
        async function loadSavedPatterns() {
            try {
                const response = await fetch("/api/pattern_code/list");
                const result = await response.json();
                
                const list = document.getElementById("savedPatternsList");
                list.innerHTML = "";
                
                if (!result.patterns || result.patterns.length === 0) {
                    list.innerHTML = '<div class="console-line">No saved patterns</div>';
                    return;
                }
                
                for (const name of result.patterns) {
                    const div = document.createElement("div");
                    div.className = "saved-item";
                    div.innerHTML = `
                        <span class="saved-item-name">${name}</span>
                        <div class="saved-item-actions">
                            <button class="btn btn-secondary" onclick="loadSavedPattern('${name}')">Load</button>
                            <button class="btn btn-danger" onclick="deletePattern('${name}')">×</button>
                        </div>
                    `;
                    list.appendChild(div);
                }
            } catch (err) {
                console.error("Error loading patterns:", err);
            }
        }
        
        // Load a saved pattern
        async function loadSavedPattern(name) {
            try {
                const response = await fetch(`/api/pattern_code/load/${name}`);
                const result = await response.json();
                
                if (result.code) {
                    editor.setValue(result.code);
                    document.getElementById("patternName").value = name;
                    log("Loaded pattern: " + name, "success");
                    validateCode();
                }
            } catch (err) {
                log("Error loading pattern: " + err.message, "error");
            }
        }
        
        // Delete a pattern
        async function deletePattern(name) {
            if (!confirm(`Delete "${name}"?`)) return;
            
            try {
                await fetch(`/api/pattern_code/delete/${name}`, { method: "DELETE" });
                log("Deleted pattern: " + name, "success");
                loadSavedPatterns();
            } catch (err) {
                log("Error deleting: " + err.message, "error");
            }
        }
        
        // Update knob labels from validation result
        function updateKnobLabels(labels) {
            if (labels && labels.length >= 4) {
                for (let i = 0; i < 4; i++) {
                    document.getElementById(`knob${i}`).value = labels[i];
                }
            }
        }
        
        // Set validation status
        function setStatus(type, message) {
            const el = document.getElementById("validationStatus");
            el.className = `validation-status status-${type}`;
            el.textContent = message;
        }
        
        // Log to console
        function log(message, type = "info") {
            const console = document.getElementById("consoleOutput");
            const line = document.createElement("div");
            line.className = `console-line console-${type}`;
            line.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            console.appendChild(line);
            console.scrollTop = console.scrollHeight;
            
            // Keep only last 50 lines
            while (console.children.length > 50) {
                console.removeChild(console.firstChild);
            }
        }
        
        // Preview rendering (simplified simulation)
        function startPreview() {
            const canvas = document.getElementById("previewCanvas");
            const ctx = canvas.getContext("2d");
            const imageData = ctx.createImageData(128, 64);
            
            function render() {
                time += 0.016;
                
                // Simulate wave pattern for preview
                const data = imageData.data;
                for (let y = 0; y < 64; y++) {
                    for (let x = 0; x < 128; x++) {
                        const value = Math.sin(x * 0.1 + time) * Math.cos(y * 0.05 - time * 0.5);
                        const t = (value + 1) * 0.5;
                        
                        const idx = (y * 128 + x) * 4;
                        data[idx] = 0;
                        data[idx + 1] = Math.floor(128 + t * 127);
                        data[idx + 2] = Math.floor(255 - t * 127);
                        data[idx + 3] = 255;
                    }
                }
                
                ctx.putImageData(imageData, 0, 0);
                requestAnimationFrame(render);
            }
            
            render();
        }
        
        // Start
        init();
    </script>
</body>
</html>
'''
