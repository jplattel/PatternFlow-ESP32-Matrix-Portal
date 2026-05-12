# ═══════════════════════════════════════════════════════════
# PatternFlow - WiFi Manager for MatrixPortal M4
# CircuitPython implementation using ESP32SPI
# License: MIT
# ═══════════════════════════════════════════════════════════

import socket
import board
import busio
from digitalio import DigitalInOut
import adafruit_connection_manager
import adafruit_esp32spi.adafruit_esp32spi_socketpool as socketpool
import adafruit_esp32spi.adafruit_esp32spi_wifimanager as wifimanager
from adafruit_esp32spi import adafruit_esp32spi

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add it!")
    secrets = {"ssid": "", "password": ""}


class WiFiManager:
    """WiFi connection manager for MatrixPortal M4."""
    
    def __init__(self):
        self.esp = None
        self.pool = None
        self.manager = None
        self.ip_address = None
        
    def init(self):
        """Initialize WiFi using ESP32 co-processor."""
        try:
            # Check for ESP32 co-processor
            esp32_cs = DigitalInOut(board.ESP_CS)
            esp32_ready = DigitalInOut(board.ESP_BUSY)
            esp32_reset = DigitalInOut(board.ESP_RESET)
            spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
            
            self.esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
            
            # Get pool and manager
            self.pool = socketpool.SocketPool(self.esp)
            self.manager = wifimanager.ESPSPI_WiFiManager(
                self.esp,
                secrets,
                timeout=10,
                retries=3,
            )
            
            self.ip_address = self.esp.ip_address
            print(f"Connected to WiFi, IP: {self.ip_address}")
            return True
            
        except Exception as e:
            print(f"WiFi initialization failed: {e}")
            print("Running in offline mode")
            return False
            
    def get_ip(self):
        """Get current IP address."""
        if self.esp:
            return self.esp.ip_address
        return None
        
    def is_connected(self):
        """Check if WiFi is connected."""
        if self.esp:
            return self.esp.is_connected
        return False
        
    def get_socket(self):
        """Get a socket from the pool."""
        if self.pool:
            return self.pool.socket()
        return socket.socket()


# Global WiFi manager instance
wifi_manager = None


def init_wifi():
    """Initialize and return the WiFi manager."""
    global wifi_manager
    wifi_manager = WiFiManager()
    wifi_manager.init()
    return wifi_manager
