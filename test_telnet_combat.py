#!/usr/bin/env python
"""
Telnet test script using telnetlib for better handling.
"""

import telnetlib
import time
import sys

HOST = 'localhost'
PORT = 5153

def main():
    print(f"Connecting to {HOST}:{PORT}...")
    
    try:
        tn = telnetlib.Telnet(HOST, PORT, 5)
        
        # Read initial welcome
        print("Reading welcome...")
        time.sleep(2)
        data = tn.read_very_eager().decode('utf-8', errors='replace')
        print(data[:1000])
        
        # Try to look around
        print("\n--- Looking around ---")
        tn.write(b"look\n")
        time.sleep(1)
        data = tn.read_very_eager().decode('utf-8', errors='replace')
        print(data)
        
        # Try stats
        print("\n--- Stats ---")
        tn.write(b"+stats\n")
        time.sleep(1)
        data = tn.read_very_eager().decode('utf-8', errors='replace')
        print(data)
        
        # Try techniques list
        print("\n--- Techniques ---")
        tn.write(b"+tech\n")
        time.sleep(1)
        data = tn.read_very_eager().decode('utf-8', errors='replace')
        print(data)
        
        # Close
        tn.close()
        print("\nDone!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
