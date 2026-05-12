#!/bin/bash
# ═══════════════════════════════════════════════════════════
# PatternFlow - Deploy Script for CircuitPython
# Syncs files to CIRCUITPY drive
# License: MIT
# ═══════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════

# Files to deploy
FILES_TO_DEPLOY=(
    "code.py"
    "config.py"
    "display_driver.py"
    "encoder_api.py"
    "pattern_sandbox.py"
    "web_code_editor.py"
    "wifi_manager.py"
    "patterns/__init__.py"
    "patterns/pattern_origin.py"
    "patterns/pattern_wave_saw.py"
    "patterns/pattern_liquid_plasma.py"
)

# Directories to create on device
DIRS_TO_CREATE=(
    "patterns"
    "custom_patterns"
)

# Files to skip
FILES_TO_SKIP=(
    "secrets.py"
    "deploy.sh"
    "README.md"
    "QUICKSTART.md"
    "EXAMPLE_PATTERNS.md"
    "CUSTOM_PATTERN_GUIDE.md"
)

# ═══════════════════════════════════════════════════════════
# Functions
# ═══════════════════════════════════════════════════════════

print_header() {
    echo -e "\n${BOLD}${CYAN}============================================================${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

find_circuitpy() {
    # Search for CIRCUITPY drive
    local circuitpy_path=""
    
    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [[ -d "/Volumes/CIRCUITPY" ]]; then
            circuitpy_path="/Volumes/CIRCUITPY"
        else
            # Search all volumes for boot_out.txt
            for vol in /Volumes/*; do
                if [[ -f "$vol/boot_out.txt" ]]; then
                    circuitpy_path="$vol"
                    break
                fi
            done
        fi
    # Linux
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -d "/media/$USER/CIRCUITPY" ]]; then
            circuitpy_path="/media/$USER/CIRCUITPY"
        elif [[ -d "/mnt/CIRCUITPY" ]]; then
            circuitpy_path="/mnt/CIRCUITPY"
        else
            # Search for boot_out.txt
            for path in /media/*/* /run/media/*/*; do
                if [[ -f "$path/boot_out.txt" ]]; then
                    circuitpy_path="$path"
                    break
                fi
            done
        fi
    # Windows (Git Bash)
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        for drive in D E F G H I J K L M N O P Q R S T U V W X Y Z; do
            if [[ -f "${drive}:/boot_out.txt" ]]; then
                circuitpy_path="${drive}:"
                break
            fi
        done
    fi
    
    echo "$circuitpy_path"
}

check_secrets() {
    local drive_path="$1"
    
    if [[ ! -f "$drive_path/secrets.py" ]]; then
        print_warning "\nsecrets.py not found on device!"
        echo -e "${BLUE}Create secrets.py on the CIRCUITPY drive with:${NC}"
        echo ""
        echo "  secrets = {"
        echo "      'ssid': 'your_wifi_name',"
        echo "      'password': 'your_wifi_password',"
        echo "  }"
        echo ""
        return 1
    else
        print_success "secrets.py found on device"
        return 0
    fi
}

check_libraries() {
    local drive_path="$1"
    local lib_path="$drive_path/lib"
    
    if [[ ! -d "$lib_path" ]]; then
        print_warning "\nlib/ directory not found!"
        print_info "Copy required libraries from CircuitPython bundle:"
        print_info "https://circuitpython.org/libraries"
        return 1
    fi
    
    # Check for key libraries
    local missing=()
    
    if ! ls "$lib_path" | grep -q "adafruit_esp32spi"; then
        missing+=("adafruit_esp32spi")
    fi
    
    if ! ls "$lib_path" | grep -q "adafruit_display_shapes"; then
        missing+=("adafruit_display_shapes")
    fi
    
    if ! ls "$lib_path" | grep -q "adafruit_display_text"; then
        missing+=("adafruit_display_text")
    fi
    
    if ! ls "$lib_path" | grep -q "neopixel"; then
        missing+=("neopixel")
    fi
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        print_warning "\nMissing libraries: ${missing[*]}"
        print_info "Copy these from the CircuitPython library bundle"
        return 1
    else
        print_success "Required libraries found"
        return 0
    fi
}

get_device_info() {
    local drive_path="$1"
    local boot_file="$drive_path/boot_out.txt"
    
    if [[ -f "$boot_file" ]]; then
        print_info "Device Information:"
        head -n 5 "$boot_file" | while read -r line; do
            echo -e "  ${CYAN}$line${NC}"
        done
    fi
}

# ═══════════════════════════════════════════════════════════
# Main Script
# ═══════════════════════════════════════════════════════════

print_header "PatternFlow Deploy"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Find CIRCUITPY drive
print_info "Searching for CIRCUITPY drive..."
CIRCUITPY=$(find_circuitpy)

if [[ -z "$CIRCUITPY" ]]; then
    print_error "CIRCUITPY drive not found!"
    echo ""
    print_info "Troubleshooting:"
    echo "  1. Connect MatrixPortal M4 via USB"
    echo "  2. Ensure CircuitPython is installed"
    echo "  3. Wait for CIRCUITPY drive to appear"
    echo "  4. Try again"
    exit 1
fi

print_success "Found CIRCUITPY at: $CIRCUITPY"

# Check if writable
if [[ ! -w "$CIRCUITPY" ]]; then
    print_error "Drive is not writable!"
    print_info "Make sure the device is not in boot mode"
    exit 1
fi

# Get device info
get_device_info "$CIRCUITPY"

# Create directories
print_info "Creating directories..."
for dir in "${DIRS_TO_CREATE[@]}"; do
    if [[ ! -d "$CIRCUITPY/$dir" ]]; then
        mkdir -p "$CIRCUITPY/$dir"
        print_success "Created: $dir/"
    else
        print_info "Exists: $dir/"
    fi
done

# Deploy files
print_info "Deploying files..."
deployed=0
skipped=0

for file in "${FILES_TO_DEPLOY[@]}"; do
    src="$SCRIPT_DIR/$file"
    dst="$CIRCUITPY/$file"
    
    if [[ ! -f "$src" ]]; then
        print_warning "Source not found: $file"
        continue
    fi
    
    # Create parent directory if needed
    dst_dir=$(dirname "$dst")
    if [[ "$dst_dir" != "$CIRCUITPY" ]] && [[ ! -d "$dst_dir" ]]; then
        mkdir -p "$dst_dir"
    fi
    
    # Check if file needs updating
    if [[ -f "$dst" ]]; then
        if cmp -s "$src" "$dst"; then
            print_info "Unchanged: $(basename "$file")"
            ((skipped++))
            continue
        fi
    fi
    
    # Copy file
    cp "$src" "$dst"
    print_success "Deployed: $(basename "$file")"
    ((deployed++))
done

# Summary
echo ""
print_header "Deployment Summary"
print_success "Deployed: $deployed files"
if [[ $skipped -gt 0 ]]; then
    print_info "Skipped: $skipped unchanged files"
fi

# Check prerequisites
echo ""
print_header "Checking Prerequisites"
check_secrets "$CIRCUITPY" || true
check_libraries "$CIRCUITPY" || true

# Trigger reload
echo ""
print_header "Finalizing"
if [[ -f "$CIRCUITPY/boot_out.txt" ]]; then
    touch "$CIRCUITPY/boot_out.txt"
    print_success "Device will auto-reload"
fi

echo ""
print_success "✓ Deployment Complete!"
echo ""
print_info "The device will reload automatically."
print_info "Watch the serial console for output."
print_info "Then open http://<device-ip> in your browser."
echo ""

exit 0
