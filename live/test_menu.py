#!/usr/bin/env python
"""Test script to verify menu navigation works correctly."""
import socket
import time
import sys

# Fix Windows console encoding for ANSI colors
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


def send_command(sock, cmd):
    """Send a command and get response."""
    sock.send((cmd + "\r\n").encode('utf-8'))
    time.sleep(0.3)
    # Keep receiving until no more data
    response = b""
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
            # Small delay to allow more data to arrive
            time.sleep(0.1)
        except:
            break
    return response.decode('utf-8', errors='replace')


def test_menu_flow():
    host = 'localhost'
    port = 4000
    
    try:
        print("=" * 60)
        print("TESTING MENU SYSTEM")
        print("=" * 60)
        
        print("\n[1] Connecting to server...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        
        # Get initial greeting
        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                if b"Enter" in response or b"1" in response:
                    time.sleep(0.3)
                    chunk2 = sock.recv(4096)
                    if chunk2:
                        response += chunk2
                    break
            except:
                break
        greeting = response.decode('utf-8', errors='replace')
        print(f"Greeting received (first 300 chars):\n{greeting[:300]}...")
        
        print("\n[2] Testing main menu '1' - Enter Game...")
        response = send_command(sock, "1")
        print(f"Response (first 500 chars):\n{response[:500]}")
        
        # Check if we're in character selection
        if "ENTER GAME" in response or "character" in response.lower():
            print("   -> SUCCESS: Entered character selection mode")
        else:
            print("   -> FAILED: Did not enter character selection")
            
        print("\n[3] Testing 'back' command to return to main menu...")
        response = send_command(sock, "back")
        print(f"Response (first 500 chars):\n{response[:500]}")
        
        if "MAIN MENU" in response or "DragonballForged" in response:
            print("   -> SUCCESS: Returned to main menu")
        else:
            print("   -> FAILED: Did not return to main menu")
            
        print("\n[4] Testing main menu '2' - Create Character...")
        response = send_command(sock, "2")
        print(f"Response (first 800 chars):\n{response[:800]}")
        
        if "CHARACTER CREATION" in response or "Step" in response:
            print("   -> SUCCESS: Entered character creation")
        else:
            print("   -> FAILED: Did not enter character creation")
            
        print("\n[5] Testing 'back' command from character creation...")
        response = send_command(sock, "b")
        print(f"Response (first 500 chars):\n{response[:500]}")
        
        if "MAIN MENU" in response or "DragonballForged" in response:
            print("   -> SUCCESS: Returned to main menu from creation")
        else:
            print("   -> FAILED: Did not return to main menu")
            
        print("\n[6] Testing main menu '3' - Delete Character...")
        response = send_command(sock, "3")
        print(f"Response (first 500 chars):\n{response[:500]}")
        
        if "DELETE" in response:
            print("   -> SUCCESS: Entered delete character mode")
        else:
            print("   -> FAILED: Did not enter delete mode")
            
        print("\n[7] Testing 'back' command from delete...")
        response = send_command(sock, "back")
        print(f"Response (first 500 chars):\n{response[:500]}")
        
        if "MAIN MENU" in response or "DragonballForged" in response:
            print("   -> SUCCESS: Returned to main menu from delete")
        else:
            print("   -> FAILED: Did not return to main menu")
            
        print("\n[8] Testing main menu '4' - Exit...")
        response = send_command(sock, "4")
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
