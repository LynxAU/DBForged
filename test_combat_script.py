#!/usr/bin/env python
"""
Interactive combat test script - connects to the Evennia server
and tests combat functionality.
"""

import socket
import time
import threading
import sys
import io

HOST = 'localhost'
PORT = 5153

# Set up UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def recv_all(sock, timeout=1.0):
    """Receive all available data from socket."""
    sock.setblocking(False)
    data = b""
    start = time.time()
    while time.time() - start < timeout:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        except BlockingIOError:
            break
    return data.decode('utf-8', errors='replace')

def send_command(sock, cmd):
    """Send a command and receive response."""
    print(f"\n>>> {cmd}")
    try:
        sock.sendall(f"{cmd}\n".encode('utf-8'))
    except Exception as e:
        print(f"Send error: {e}")
        return ""
    time.sleep(0.5)
    try:
        response = recv_all(sock, timeout=2.0)
        return response
    except Exception as e:
        print(f"Recv error: {e}")
        return ""

def main():
    print("Connecting to DBForged combat server...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        sock.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}")
        
        # Receive welcome message
        welcome = recv_all(sock, timeout=3.0)
        print(welcome)
        
        # Send a test command to see what happens
        # Try to get help
        response = send_command(sock, "help")
        print(response)
        
        # Try looking around
        response = send_command(sock, "look")
        print(response)
        
        # Try stats
        response = send_command(sock, "+stats")
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
        print("\nDisconnected.")

if __name__ == "__main__":
    main()
