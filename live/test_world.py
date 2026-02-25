#!/usr/bin/env python
"""Test script to interact with DBForged game server."""
import socket
import time
import sys
import codecs

# Fix Windows console encoding for UTF-8
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

def test_game_commands():
    host = 'localhost'
    port = 5203
    timeout = 10
    
    print(f"Connecting to {host}:{port}...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(timeout)
    client.connect((host, port))
    
    # Wait for greeting
    time.sleep(1)
    greeting = client.recv(8192).decode('utf-8', errors='replace')
    print(f"\n=== SERVER GREETING ===\n{greeting[:500]}")
    
    # Test help command
    print("\n=== TESTING 'help' COMMAND ===")
    client.send(b'help\r\n')
    time.sleep(0.5)
    response = client.recv(8192).decode('utf-8', errors='replace')
    print(response[:1000])
    
    # Create an account
    print("\n=== CREATING ACCOUNT 'testplayer' ===")
    client.send(b'create testplayer testpass123\r\n')
    time.sleep(0.5)
    response = client.recv(8192).decode('utf-8', errors='replace')
    print(response[:1000])
    
    # Answer Y to confirmation
    if 'Y' in response or 'y' in response:
        client.send(b'Y\r\n')
        time.sleep(1)
        response = client.recv(8192).decode('utf-8', errors='replace')
        print("After Y confirmation:", response[:1000])
    
    # Connect with the account
    print("\n=== CONNECTING WITH ACCOUNT ===")
    client.send(b'connect testplayer testpass123\r\n')
    time.sleep(1)
    response = client.recv(8192).decode('utf-8', errors='replace')
    print(response[:2000])
    
    # Select Create Character (option 2)
    print("\n=== SELECTING 'Create Character' ===")
    client.send(b'2\r\n')
    time.sleep(1)
    response = client.recv(8192).decode('utf-8', errors='replace')
    print(response[:3000])
    
    # Try Enter Game (option 1)
    print("\n=== SELECTING 'Enter Game' ===")
    client.send(b'1\r\n')
    time.sleep(1)
    response = client.recv(8192).decode('utf-8', errors='replace')
    print(response[:3000])
    
    # Test look command
    print("\n=== TESTING 'look' COMMAND ===")
    client.send(b'look\r\n')
    time.sleep(0.5)
    response = client.recv(8192).decode('utf-8', errors='replace')
    print(response[:1500])
    
    # Test who command
    print("\n=== TESTING 'who' COMMAND ===")
    client.send(b'who\r\n')
    time.sleep(0.5)
    response = client.recv(4096).decode('utf-8', errors='replace')
    print(response[:500])
    
    # Test techniques command
    print("\n=== TESTING 'techniques' COMMAND ===")
    client.send(b'techniques\r\n')
    time.sleep(0.5)
    response = client.recv(8192).decode('utf-8', errors='replace')
    print(response[:1500])
    
    # Test forms command
    print("\n=== TESTING 'forms' COMMAND ===")
    client.send(b'forms\r\n')
    time.sleep(0.5)
    response = client.recv(8192).decode('utf-8', errors='replace')
    print(response[:1500])
    
    # Test races command
    print("\n=== TESTING 'races' COMMAND ===")
    client.send(b'races\r\n')
    time.sleep(0.5)
    response = client.recv(4096).decode('utf-8', errors='replace')
    print(response[:1000])
    
    # Test quit
    print("\n=== TESTING 'quit' COMMAND ===")
    client.send(b'quit\r\n')
    time.sleep(0.5)
    
    client.close()
    print("\n=== CONNECTION CLOSED ===")
    return True

if __name__ == '__main__':
    try:
        test_game_commands()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
