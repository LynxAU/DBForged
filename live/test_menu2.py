#!/usr/bin/env python
"""Test script to verify menu navigation - using full command names."""
import socket
import time
import sys

# Fix Windows console encoding for ANSI colors
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


def send_command(sock, cmd, wait=0.3):
    """Send a command and get response."""
    sock.send((cmd + "\r\n").encode('utf-8'))
    time.sleep(wait)
    # Keep receiving until no more data
    response = b""
    attempts = 0
    while attempts < 5:
        try:
            sock.setblocking(False)
            chunk = sock.recv(4096)
            if chunk:
                response += chunk
                time.sleep(0.1)
                attempts += 1
            else:
                break
        except BlockingIOError:
            break
        except Exception as e:
            break
    sock.setblocking(True)
    return response.decode('utf-8', errors='replace')


def test_menu_flow():
    host = 'localhost'
    port = 4000
    
    try:
        print("=" * 60)
        print("TESTING MENU SYSTEM - with full command names")
        print("=" * 60)
        
        print("\n[1] Connecting to server...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        
        # Get initial greeting - wait longer
        time.sleep(1)
        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                if b"Welcome" in response:
                    time.sleep(0.5)
                    more = sock.recv(4096)
                    if more:
                        response += more
                    break
            except:
                break
        
        greeting = response.decode('utf-8', errors='replace')
        print(f"Greeting received (first 500 chars):\n{greeting[:500]}")
        print(f"\n[1b] Does greeting contain 'MAIN MENU'? {'MAIN MENU' in greeting}")
        
        print("\n[2] Testing 'menu' command...")
        response = send_command(sock, "menu", wait=0.5)
        print(f"Response (first 800 chars):\n{response[:800]}")
        
        print("\n[3] Testing 'entergame' command...")
        response = send_command(sock, "entergame", wait=0.5)
        print(f"Response (first 800 chars):\n{response[:800]}")
        
        print("\n[4] Testing 'createcharacter' command...")
        response = send_command(sock, "createcharacter", wait=0.5)
        print(f"Response (first 800 chars):\n{response[:800]}")
        
        print("\n[5] Testing 'look' command...")
        response = send_command(sock, "look", wait=0.5)
        print(f"Response (first 800 chars):\n{response[:800]}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        
        sock.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_menu_flow()
