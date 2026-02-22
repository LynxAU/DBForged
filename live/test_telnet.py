#!/usr/bin/env python
"""Simple telnet client test for Evennia server."""
import socket
import time
import sys

# Fix Windows console encoding for ANSI colors
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def test_telnet(host='localhost', port=4000, timeout=5):
    try:
        print(f"Connecting to {host}:{port}...")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(timeout)
        client.connect((host, port))
        
        # Wait for server greeting
        time.sleep(0.5)
        greeting = client.recv(4096).decode('utf-8', errors='replace')
        print(f"Server greeting: {greeting[:200]}")
        
        # Send test command
        print("Sending 'test' command...")
        client.send(b'test\r\n')
        
        time.sleep(0.5)
        response = client.recv(4096).decode('utf-8', errors='replace')
        print(f"Response: {response[:500]}")
        
        client.close()
        print("Connection closed successfully.")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    test_telnet()
