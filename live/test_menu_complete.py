#!/usr/bin/env python
"""Complete test of all menu options."""
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


def test_menu():
    host = 'localhost'
    port = 4000
    
    # Use same test account - check if it exists
    test_user = "testuser1258"  # from previous test
    test_pass = "testpass123"
    
    try:
        print("=" * 70)
        print("COMPLETE MENU SYSTEM TEST")
        print("=" * 70)
        
        # Connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        time.sleep(1)
        
        # Login
        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                if b"connect" in response.lower():
                    break
            except:
                break
        
        print("\n[LOGIN] Connecting with existing account...")
        response = send_command(sock, f"connect {test_user} {test_pass}", wait=1)
        
        if "MAIN MENU" in response or "DragonballForged" in response:
            print("   -> Logged in successfully!")
        else:
            print("   -> Login failed!")
            sock.close()
            return
            
        # ============================================================
        # TEST MAIN MENU
        # ============================================================
        print("\n" + "=" * 70)
        print("MAIN MENU TESTS")
        print("=" * 70)
        
        # Test menu command
        print("\n[MAIN] Testing 'menu' command...")
        response = send_command(sock, "menu", wait=0.5)
        if "MAIN MENU" in response:
            print("   -> PASS: menu command works")
        else:
            print("   -> FAIL: menu command not working")
            
        # Test look command  
        print("\n[MAIN] Testing 'look' command...")
        response = send_command(sock, "look", wait=0.5)
        if "MAIN MENU" in response or "DragonballForged" in response:
            print("   -> PASS: look command works")
        else:
            print("   -> FAIL: look command not working")
            
        # Test mainmenu command
        print("\n[MAIN] Testing 'mainmenu' command...")
        response = send_command(sock, "mainmenu", wait=0.5)
        if "MAIN MENU" in response:
            print("   -> PASS: mainmenu command works")
        else:
            print("   -> FAIL: mainmenu command not working")
            
        # ============================================================
        # TEST ENTER GAME (Option 1)
        # ============================================================
        print("\n" + "=" * 70)
        print("ENTER GAME (Option 1) TESTS")
        print("=" * 70)
        
        # Test '1'
        print("\n[ENTER] Testing '1'...")
        response = send_command(sock, "1", wait=0.5)
        if "ENTER GAME" in response or "character" in response.lower():
            print("   -> PASS: '1' shows character list")
        else:
            print("   -> FAIL: '1' not working")
            
        # Test 'back' from enter game
        print("\n[ENTER] Testing 'back'...")
        response = send_command(sock, "back", wait=0.5)
        if "MAIN MENU" in response:
            print("   -> PASS: 'back' returns to main menu")
        else:
            print("   -> FAIL: 'back' not working")
            
        # Test 'entergame' command
        print("\n[ENTER] Testing 'entergame'...")
        response = send_command(sock, "entergame", wait=0.5)
        if "ENTER GAME" in response or "character" in response.lower():
            print("   -> PASS: 'entergame' command works")
        else:
            print("   -> FAIL: 'entergame' not working")
            
        # Test 'b' from enter game
        print("\n[ENTER] Testing 'b' (back)...")
        response = send_command(sock, "b", wait=0.5)
        if "MAIN MENU" in response:
            print("   -> PASS: 'b' returns to main menu")
        else:
            print("   -> FAIL: 'b' not working")
            
        # ============================================================
        # TEST CREATE CHARACTER (Option 2)
        # ============================================================
        print("\n" + "=" * 70)
        print("CREATE CHARACTER (Option 2) TESTS")
        print("=" * 70)
        
        # Test '2'
        print("\n[CREATE] Testing '2'...")
        response = send_command(sock, "2", wait=0.5)
        if "CHARACTER CREATION" in response or "Step" in response:
            print("   -> PASS: '2' starts character creation")
        else:
            print("   -> FAIL: '2' not working")
            
        # Test 'back' from creation
        print("\n[CREATE] Testing 'back'...")
        response = send_command(sock, "back", wait=0.5)
        if "MAIN MENU" in response:
            print("   -> PASS: 'back' returns to main menu")
        else:
            print("   -> FAIL: 'back' not working from create")
            
        # Test 'createcharacter' command
        print("\n[CREATE] Testing 'createcharacter'...")
        response = send_command(sock, "createcharacter", wait=0.5)
        if "CHARACTER CREATION" in response or "Step" in response:
            print("   -> PASS: 'createcharacter' command works")
        else:
            print("   -> FAIL: 'createcharacter' not working")
            
        # Test 'b' from creation
        print("\n[CREATE] Testing 'b' (back)...")
        response = send_command(sock, "b", wait=0.5)
        if "MAIN MENU" in response:
            print("   -> PASS: 'b' returns to main menu")
        else:
            print("   -> FAIL: 'b' not working from create")
            
        # ============================================================
        # TEST DELETE CHARACTER (Option 3)
        # ============================================================
        print("\n" + "=" * 70)
        print("DELETE CHARACTER (Option 3) TESTS")
        print("=" * 70)
        
        # Test '3'
        print("\n[DELETE] Testing '3'...")
        response = send_command(sock, "3", wait=0.5)
        if "DELETE" in response:
            print("   -> PASS: '3' shows delete menu")
        else:
            print("   -> FAIL: '3' not working")
            
        # Test 'back' from delete
        print("\n[DELETE] Testing 'back'...")
        response = send_command(sock, "back", wait=0.5)
        if "MAIN MENU" in response:
            print("   -> PASS: 'back' returns to main menu")
        else:
            print("   -> FAIL: 'back' not working from delete")
            
        # Test 'deletecharacter' command
        print("\n[DELETE] Testing 'deletecharacter'...")
        response = send_command(sock, "deletecharacter", wait=0.5)
        if "DELETE" in response:
            print("   -> PASS: 'deletecharacter' command works")
        else:
            print("   -> FAIL: 'deletecharacter' not working")
            
        # Test 'b' from delete
        print("\n[DELETE] Testing 'b' (back)...")
        response = send_command(sock, "b", wait=0.5)
        if "MAIN MENU" in response:
            print("   -> PASS: 'b' returns to main menu")
        else:
            print("   -> FAIL: 'b' not working from delete")
            
        # ============================================================
        # TEST EXIT (Option 4)
        # ============================================================
        print("\n" + "=" * 70)
        print("EXIT (Option 4) TESTS")
        print("=" * 70)
        
        # Test '4' - should disconnect
        print("\n[EXIT] Testing '4'...")
        response = send_command(sock, "4", wait=1)
        # After quit, the connection should close
        print("   -> Connection should close (check manually)")
        
        # Test 'quit' command
        print("\n[EXIT] Note: 'quit', 'q', 'exit' also should work")
        
        print("\n" + "=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)
        
        sock.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_menu()
