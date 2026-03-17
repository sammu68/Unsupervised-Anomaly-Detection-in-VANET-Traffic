#!/usr/bin/env python3
"""
Test script to verify continuous mode works correctly
"""

import sys

print("Testing argument parsing...")
print(f"Arguments received: {sys.argv}")

args = sys.argv[1:]
print(f"Args list: {args}")

continuous = "--continuous" in args
print(f"Continuous mode detected: {continuous}")

if continuous:
    print("✓ Continuous mode flag is working!")
    print("The attack injector should run in continuous mode.")
else:
    print("❌ Continuous mode flag NOT detected!")
    print("This might be why option 4 isn't working.")

print("\nTo test manually, run:")
print("python attack_injector.py --continuous --interval 5")
