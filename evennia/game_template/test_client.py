#!/usr/bin/env python
"""Simple telnet client to test Evennia."""
import socket
import sys
import time

def simple_telnet(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    
    # Read welcome message
    time.sleep(1)
    data = s.recv(4096)
    print("Welcome:", data.decode('utf-8', errors='ignore'))
    
    # Connect with credentials
    s.sendall(b"connect TestAdmin test123\r\n")
    time.sleep(1)
    data = s.recv(4096)
    print("Connected:", data.decode('utf-8', errors='ignore'))
    
    # Enter game as character
    s.sendall(b"ic\r\n")
    time.sleep(1)
    data = s.recv(4096)
    print("In game:", data.decode('utf-8', errors='ignore'))
    
    # Cancel character creation
    s.sendall(b"cancel\r\n")
    time.sleep(1)
    data = s.recv(4096)
    print("After cancel:", data.decode('utf-8', errors='ignore'))
    
    # Run world builder
    print("\\n=== Running Planet Vegeta Builder ===")
    s.sendall(b"@evennia call world.build_planet_vegeta\r\n")
    time.sleep(3)
    data = s.recv(8192)
    print("Builder output:", data.decode('utf-8', errors='ignore'))
    data = s.recv(4096)
    print("After password:", data.decode('utf-8', errors='ignore'))
    
    # Send look command
    s.sendall(b"look\r\n")
    time.sleep(0.5)
    data = s.recv(4096)
    print("Look:", data.decode('utf-8', errors='ignore'))
    
    s.close()

if __name__ == "__main__":
    simple_telnet("localhost", 5203)
