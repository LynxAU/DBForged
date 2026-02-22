#!/usr/bin/env python
"""Simple test to check character creation input"""
import socket
import time

def send_command(sock, cmd, wait=0.5):
    """Send a command and return response"""
    sock.sendall((cmd + "\r\n").encode('utf-8'))
    time.sleep(wait)
    
    # Read all available data
    data = b""
    sock.setblocking(False)
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        except BlockingIOError:
            break
    
    return data.decode('utf-8', errors='replace')

def main():
    test_user = "testuser1258"
    test_pass = "testpass123"
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 4000))
    sock.setblocking(True)
    
    # Wait for welcome screen
    time.sleep(1)
    response = sock.recv(8192).decode('utf-8', errors='replace')
    print("=== Welcome screen received ===")
    
    # Login with existing account (using connect command)
    print("\n=== Logging in ===")
    response = send_command(sock, f"connect {test_user} {test_pass}", wait=1)
    print(f"Login response contains MAIN MENU: {'MAIN MENU' in response}")
    
    # Check we're at main menu
    response = send_command(sock, "menu", wait=0.5)
    print(f"Main menu response: {'MAIN MENU' in response}")
    
    # Start character creation with '2'
    print("\n=== Starting character creation ===")
    response = send_command(sock, "2", wait=0.5)
    print(f"Character creation started: {'CHARACTER CREATION' in response or 'Step' in response}")
    
    # Try entering a character name
    print("\n=== Entering character name 'Harath' ===")
    response = send_command(sock, "Harath", wait=0.5)
    print(f"Response contains 'MAIN MENU': {'MAIN MENU' in response}")
    print(f"Response contains 'not available': {'not available' in response}")
    print(f"Response preview:\n{response[:500]}")
    
    sock.close()

if __name__ == "__main__":
    main()
