#!/usr/bin/env python3
"""
VANET Attack Injector
Simulates external attacks on the VANET system for testing purposes.
This runs separately from the main dashboard to simulate realistic attack scenarios.
"""

import requests
import random
import time
import sys
from datetime import datetime
from typing import List, Dict

# Configuration
API_URL = "http://localhost:8000"
ATTACK_INTERVAL = 5  # Seconds between attacks
ATTACK_DURATION = 30  # Seconds to run attacks before stopping

# Attack types to simulate
ATTACK_TYPES = [
    "GPS Spoofing",
    "Position Falsification",
    "Sybil Attack",
    "DoS Attack",
    "Message Tampering",
    "Replay Attack"
]

class AttackInjector:
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
        self.token = None
        self.attack_count = 0
        self.running = False
        
    def login(self, username: str = "admin", password: str = "admin123") -> bool:
        """Login to get authentication token"""
        try:
            print(f"🔐 Logging in as {username}...")
            response = requests.post(
                f"{self.api_url}/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print(f"✓ Login successful!")
                print(f"✓ Token: {self.token[:30]}...")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def enable_attack_mode(self) -> bool:
        """Enable attack mode on the backend"""
        try:
            print("⚔️  Enabling attack mode...")
            response = requests.post(
                f"{self.api_url}/set-scenario",
                json={"scenario": "ATTACK"},
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                print("✓ Attack mode enabled!")
                return True
            else:
                print(f"❌ Failed to enable attack mode: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error enabling attack mode: {e}")
            return False
    
    def disable_attack_mode(self) -> bool:
        """Disable attack mode on the backend"""
        try:
            print("🛡️  Disabling attack mode...")
            response = requests.post(
                f"{self.api_url}/set-scenario",
                json={"scenario": "NORMAL"},
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                print("✓ Attack mode disabled!")
                return True
            else:
                print(f"❌ Failed to disable attack mode: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error disabling attack mode: {e}")
            return False
    
    def inject_attack(self, attack_type: str = None) -> bool:
        """Inject a single attack"""
        if not attack_type:
            attack_type = random.choice(ATTACK_TYPES)
        
        try:
            # Enable attack mode (backend will generate malicious vehicles)
            if not self.running:
                self.enable_attack_mode()
                self.running = True
            
            self.attack_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 🚨 Attack #{self.attack_count}: {attack_type}")
            
            return True
        except Exception as e:
            print(f"❌ Error injecting attack: {e}")
            return False
    
    def run_attack_campaign(self, duration: int = ATTACK_DURATION, interval: int = ATTACK_INTERVAL):
        """Run a campaign of attacks for specified duration"""
        print("\n" + "="*60)
        print("🎯 VANET ATTACK INJECTOR")
        print("="*60)
        print(f"Duration: {duration} seconds")
        print(f"Interval: {interval} seconds between attacks")
        print(f"Target: {self.api_url}")
        print("="*60 + "\n")
        
        start_time = time.time()
        
        try:
            while (time.time() - start_time) < duration:
                attack_type = random.choice(ATTACK_TYPES)
                self.inject_attack(attack_type)
                
                remaining = duration - (time.time() - start_time)
                if remaining > 0:
                    print(f"⏳ Next attack in {interval} seconds... ({int(remaining)}s remaining)")
                    time.sleep(interval)
            
            print("\n" + "="*60)
            print(f"✓ Attack campaign completed!")
            print(f"✓ Total attacks injected: {self.attack_count}")
            print("="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Attack campaign interrupted by user!")
            print(f"✓ Total attacks injected: {self.attack_count}")
        finally:
            # Disable attack mode
            self.disable_attack_mode()
            self.running = False
    
    def run_continuous(self, interval: int = ATTACK_INTERVAL):
        """Run attacks continuously until stopped"""
        print("\n" + "="*60)
        print("🎯 VANET ATTACK INJECTOR - CONTINUOUS MODE")
        print("="*60)
        print(f"Interval: {interval} seconds between attacks")
        print(f"Target: {self.api_url}")
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        print("⏳ Starting continuous attack mode...")
        print("   Attacks will begin shortly...\n")
        
        try:
            while True:
                attack_type = random.choice(ATTACK_TYPES)
                self.inject_attack(attack_type)
                print(f"⏳ Next attack in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Attack injector stopped by user!")
            print(f"✓ Total attacks injected: {self.attack_count}")
        finally:
            # Disable attack mode
            self.disable_attack_mode()
            self.running = False


def print_usage():
    """Print usage instructions"""
    print("""
VANET Attack Injector - Usage
==============================

This tool simulates external attacks on the VANET system for testing.

Modes:
------
1. Campaign Mode (default): Run attacks for specified duration
   python attack_injector.py

2. Continuous Mode: Run attacks until manually stopped
   python attack_injector.py --continuous

3. Custom Duration: Specify attack duration
   python attack_injector.py --duration 60

4. Custom Interval: Specify time between attacks
   python attack_injector.py --interval 10

Options:
--------
--continuous        Run continuously until Ctrl+C
--duration N        Run for N seconds (default: 30)
--interval N        Wait N seconds between attacks (default: 5)
--username USER     Login username (default: admin)
--password PASS     Login password (default: admin123)
--help              Show this help message

Examples:
---------
# Run 60-second attack campaign
python attack_injector.py --duration 60

# Run continuous attacks every 3 seconds
python attack_injector.py --continuous --interval 3

# Use custom credentials
python attack_injector.py --username operator --password pass123

Notes:
------
- Requires backend to be running on http://localhost:8000
- Requires valid admin credentials
- Dashboard will detect and display attacks in real-time
- Press Ctrl+C to stop at any time
""")


def main():
    """Main entry point"""
    # Parse command line arguments
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print_usage()
        return
    
    # Configuration
    continuous = "--continuous" in args
    duration = ATTACK_DURATION
    interval = ATTACK_INTERVAL
    username = "admin"
    password = "admin123"
    
    # Debug: Show what mode was detected
    if continuous:
        print("🔄 Continuous mode detected")
    else:
        print(f"⏱️  Campaign mode detected (duration: {duration}s)")
    
    # Parse duration
    if "--duration" in args:
        try:
            idx = args.index("--duration")
            duration = int(args[idx + 1])
        except (IndexError, ValueError):
            print("❌ Invalid duration value")
            return
    
    # Parse interval
    if "--interval" in args:
        try:
            idx = args.index("--interval")
            interval = int(args[idx + 1])
        except (IndexError, ValueError):
            print("❌ Invalid interval value")
            return
    
    # Parse username
    if "--username" in args:
        try:
            idx = args.index("--username")
            username = args[idx + 1]
        except IndexError:
            print("❌ Invalid username value")
            return
    
    # Parse password
    if "--password" in args:
        try:
            idx = args.index("--password")
            password = args[idx + 1]
        except IndexError:
            print("❌ Invalid password value")
            return
    
    # Create injector
    injector = AttackInjector()
    
    # Login
    if not injector.login(username, password):
        print("\n❌ Failed to login. Please check:")
        print("   1. Backend is running on http://localhost:8000")
        print("   2. Credentials are correct")
        print("   3. User has admin privileges")
        return
    
    # Run attacks
    if continuous:
        injector.run_continuous(interval)
    else:
        injector.run_attack_campaign(duration, interval)


if __name__ == "__main__":
    main()
