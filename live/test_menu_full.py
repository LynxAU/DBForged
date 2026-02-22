#!/usr/bin/env python
"""Test script to verify menu navigation - login first."""
import socket
import time
import sys
import random
import string

# Fix Windows console encoding for ANSI colors
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


def send_command(sock, cmd, wait=0.5):
    """Send a command and get response."""
    sock.send((cmd + "\r\n").encode('utf-8'))
    time.sleep(wait)
    # Keep receiving until no more data
    response = b""
    attempts = 0
    while attempts < 10:
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
    
    # Generate random username/password for testing
    test_user = "testuser" + ''.join(random.choices(string.digits, k=4))
    test_pass = "testpass123"
    
    try:
        print("=" * 60)
        print("TESTING MENU SYSTEM - with login")
        print(f"Test account: {test_user}")
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
                if b"connect" in response.lower():
                    time.sleep(0.5)
                    more = sock.recv(4096)
                    if more:
                        response += more
                    break
            except:
                break
        
        greeting = response.decode('utf-8', errors='replace')
        print(f"Greeting received (first 400 chars):\n{greeting[:400]}")
        
        print(f"\n[2] Creating account: {test_user}...")
        response = send_command(sock, f"create {test_user} {test_pass}", wait=1)
        print(f"Create response (first 600 chars):\n{response[:600]}")
        
        # Handle confirmation prompt
        if "[Y]/N" in response or "Is this what you intended" in response:
            print("   -> Sending confirmation 'Y'...")
            response = send_command(sock, "Y", wait=1)
            print(f"Confirmation response (first 600 chars):\n{response[:600]}")
        
        # Now connect (login) with the account
        print(f"\n[3] Connecting (logging in) with account...")
        response = send_command(sock, f"connect {test_user} {test_pass}", wait=1)
        print(f"Connect response (first 1000 chars):\n{response[:1000]}")
        
        # Check if logged in (should see MAIN MENU now)
        if "MAIN MENU" in response or "DragonballForged" in response:
            print("\n-> SUCCESS: Logged in and seeing MAIN MENU")
        else:
            print("\n-> NOT showing MAIN MENU yet - checking response...")
            
        print("\n[4] Testing main menu '1' - Enter Game...")
        response = send_command(sock, "1", wait=0.5)
        print(f"Response (first 800 chars):\n{response[:800]}")
        
        if "ENTER GAME" in response or "character" in response.lower():
            print("   -> SUCCESS: Entered character selection mode")
        else:
            print("   -> ISSUE: Did not enter character selection")
            
        print("\n[5] Testing 'back' command...")
        response = send_command(sock, "b", wait=0.5)
        print(f"Response (first 500 chars):\n{response[:500]}")
        
        print("\n[6] Testing main menu '2' - Create Character...")
        response = send_command(sock, "2", wait=0.5)
        print(f"Response (first 800 chars):\n{response[:800]}")
        
        if "CHARACTER CREATION" in response or "Step" in response:
            print("   -> SUCCESS: Entered character creation")
        else:
            print("   -> ISSUE: Did not enter character creation")
            
        print("\n[7] Testing 'back' from creation...")
        response = send_command(sock, "b", wait=0.5)
        print(f"Response (first 500 chars):\n{response[:500]}")
        
        print("\n[8] Testing main menu '3' - Delete Character...")
        response = send_command(sock, "3", wait=0.5)
        print(f"Response (first 600 chars):\n{response[:600]}")
        
        print("\n[9] Testing 'back' from delete...")
        response = send_command(sock, "back", wait=0.5)
        print(f"Response (first 500 chars):\n{response[:500]}")
        
        print("\n[10] Testing main menu '4' - Exit...")
        response = send_command(sock, "4", wait=0.5)
        print(f"Response (first 300 chars):\n{response[:300]}")
        
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
