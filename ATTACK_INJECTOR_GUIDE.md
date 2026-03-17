# Attack Injector Guide

## Overview
The Attack Injector is a separate application that simulates external attacks on the VANET system. This provides a realistic testing environment where the dashboard only monitors and detects attacks, not controls them.

---

## Architecture

```
┌─────────────────────────────┐
│   VANET Dashboard           │
│   (Monitor Only)            │
│   - View traffic            │
│   - Detect attacks          │
│   - Alert operators         │
│   - NO attack button        │
└─────────────────────────────┘
              ↑
              │ Detects
              │
┌─────────────────────────────┐
│   Backend API               │
│   - Process vehicle data    │
│   - Run ML detection        │
│   - Classify attacks        │
└─────────────────────────────┘
              ↑
              │ Injects
              │
┌─────────────────────────────┐
│   Attack Injector           │
│   (Separate Application)    │
│   - Simulates attacks       │
│   - External control        │
│   - Realistic testing       │
└─────────────────────────────┘
```

---

## Installation

### Prerequisites
- Python 3.9+
- Backend running on http://localhost:8000
- Valid admin credentials

### Setup
```bash
# No installation needed - uses standard libraries
# Just ensure requests library is installed
pip install requests
```

### Windows Quick Launch
For Windows users, use the batch file for easy access:
```bash
# Double-click or run from command prompt
run_attack_injector.bat

# Select from menu:
# 1. Quick Test (30 seconds)
# 2. Medium Test (60 seconds)
# 3. Long Test (120 seconds)
# 4. Continuous Mode
# 5. Custom Configuration
```

---

## Usage

### Basic Usage (30-second campaign)
```bash
python attack_injector.py
```

### Continuous Mode
```bash
python attack_injector.py --continuous
```

### Custom Duration
```bash
# Run for 60 seconds
python attack_injector.py --duration 60
```

### Custom Interval
```bash
# Attack every 3 seconds
python attack_injector.py --interval 3
```

### Custom Credentials
```bash
python attack_injector.py --username admin --password admin123
```

### Combined Options
```bash
# Continuous mode with 10-second intervals
python attack_injector.py --continuous --interval 10

# 2-minute campaign with 5-second intervals
python attack_injector.py --duration 120 --interval 5
```

---

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--continuous` | Run until Ctrl+C | Campaign mode |
| `--duration N` | Run for N seconds | 30 |
| `--interval N` | Wait N seconds between attacks | 5 |
| `--username USER` | Login username | admin |
| `--password PASS` | Login password | admin123 |
| `--help` | Show help message | - |

---

## Attack Types

The injector randomly selects from these attack types:

1. **GPS Spoofing** - Extreme position falsification
2. **Position Falsification** - False position reporting
3. **Sybil Attack** - Multiple fake identities
4. **DoS Attack** - Network flooding
5. **Message Tampering** - Altered messages
6. **Replay Attack** - Resending old messages

---

## Example Sessions

### Session 1: Quick Test
```bash
$ python attack_injector.py --duration 30 --interval 5

============================================================
🎯 VANET ATTACK INJECTOR
============================================================
Duration: 30 seconds
Interval: 5 seconds between attacks
Target: http://localhost:8000
============================================================

🔐 Logging in as admin...
✓ Login successful!
✓ Token: eyJhbGciOiJIUzI1NiIsInR5cCI6...
⚔️  Enabling attack mode...
✓ Attack mode enabled!
[10:30:15] 🚨 Attack #1: GPS Spoofing
⏳ Next attack in 5 seconds... (25s remaining)
[10:30:20] 🚨 Attack #2: DoS Attack
⏳ Next attack in 5 seconds... (20s remaining)
[10:30:25] 🚨 Attack #3: Sybil Attack
⏳ Next attack in 5 seconds... (15s remaining)
[10:30:30] 🚨 Attack #4: Position Falsification
⏳ Next attack in 5 seconds... (10s remaining)
[10:30:35] 🚨 Attack #5: Message Tampering
⏳ Next attack in 5 seconds... (5s remaining)
[10:30:40] 🚨 Attack #6: Replay Attack

============================================================
✓ Attack campaign completed!
✓ Total attacks injected: 6
============================================================

🛡️  Disabling attack mode...
✓ Attack mode disabled!
```

### Session 2: Continuous Mode
```bash
$ python attack_injector.py --continuous --interval 3

============================================================
🎯 VANET ATTACK INJECTOR - CONTINUOUS MODE
============================================================
Interval: 3 seconds between attacks
Target: http://localhost:8000
Press Ctrl+C to stop
============================================================

🔐 Logging in as admin...
✓ Login successful!
⚔️  Enabling attack mode...
✓ Attack mode enabled!
[10:35:00] 🚨 Attack #1: GPS Spoofing
⏳ Next attack in 3 seconds...
[10:35:03] 🚨 Attack #2: DoS Attack
⏳ Next attack in 3 seconds...
[10:35:06] 🚨 Attack #3: Sybil Attack
⏳ Next attack in 3 seconds...
^C

⚠️  Attack injector stopped by user!
✓ Total attacks injected: 3
🛡️  Disabling attack mode...
✓ Attack mode disabled!
```

---

## How It Works

### 1. Login
- Connects to backend API
- Authenticates with admin credentials
- Receives JWT token

### 2. Enable Attack Mode
- Sends request to `/set-scenario` endpoint
- Backend switches to ATTACK mode
- Malicious vehicles start appearing

### 3. Inject Attacks
- Randomly selects attack type
- Backend generates malicious vehicle behavior
- Dashboard detects and displays attacks

### 4. Cleanup
- Disables attack mode on exit
- Backend returns to NORMAL mode
- Clean shutdown

---

## Integration with Dashboard

### What Dashboard Shows

**During Attack Campaign:**
- 🟢 Normal vehicles (dark green)
- 🔴 Attack vehicles (colored by type)
- 🚨 Attack alerts
- 📊 Attack statistics
- 📈 MSE graph showing anomalies

**Attack Panel:**
- List of detected attacks
- Attack types and severity
- Vehicle IDs and positions
- Timestamps

**System Status:**
- "⚠ SYSTEM UNDER ATTACK" banner
- Attack count in real-time
- Attack distribution by type

---

## Use Cases

### 1. Operator Training
```bash
# Run 5-minute training session
python attack_injector.py --duration 300 --interval 10
```

**Purpose:**
- Train operators to recognize attacks
- Practice incident response
- Familiarize with dashboard

### 2. System Testing
```bash
# Stress test with rapid attacks
python attack_injector.py --duration 60 --interval 2
```

**Purpose:**
- Test detection accuracy
- Verify alert system
- Check performance under load

### 3. Demonstrations
```bash
# Controlled demo with clear intervals
python attack_injector.py --duration 120 --interval 15
```

**Purpose:**
- Show stakeholders
- Demonstrate capabilities
- Explain attack types

### 4. Penetration Testing
```bash
# Continuous attacks to find weaknesses
python attack_injector.py --continuous --interval 5
```

**Purpose:**
- Test system resilience
- Find detection gaps
- Validate security

### 5. Research & Development
```bash
# Long-term data collection
python attack_injector.py --duration 3600 --interval 10
```

**Purpose:**
- Collect attack data
- Analyze patterns
- Improve ML model

---

## Troubleshooting

### Error: "Failed to login"
**Cause:** Backend not running or wrong credentials

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Verify credentials
python attack_injector.py --username admin --password admin123
```

### Error: "Connection refused"
**Cause:** Backend not accessible

**Solution:**
```bash
# Start backend
cd backend
python main.py

# Check port
netstat -an | grep 8000
```

### Error: "Failed to enable attack mode"
**Cause:** User doesn't have admin privileges

**Solution:**
- Use admin account
- Check user role in database

### No Attacks Appearing
**Cause:** Dashboard not refreshing or backend issue

**Solution:**
1. Refresh dashboard (F5)
2. Check backend logs
3. Verify attack mode enabled

### Continuous Mode Not Working
**See:** [ATTACK_INJECTOR_TROUBLESHOOTING.md](ATTACK_INJECTOR_TROUBLESHOOTING.md) for detailed solutions

**Quick fixes:**
1. Ensure backend is running first
2. Wait 5-10 seconds for login
3. Check for "🔄 Continuous mode detected" message
4. Try direct command: `python attack_injector.py --continuous --interval 5`

---

## Best Practices

### 1. Start Small
```bash
# Test with short duration first
python attack_injector.py --duration 10 --interval 5
```

### 2. Monitor Dashboard
- Keep dashboard open while running injector
- Watch for attack detection
- Verify alerts appear

### 3. Clean Shutdown
- Use Ctrl+C to stop gracefully
- Injector will disable attack mode
- System returns to normal

### 4. Log Results
```bash
# Save output to file
python attack_injector.py --duration 60 > attack_log.txt
```

### 5. Coordinate with Team
- Announce when starting attacks
- Inform operators it's a test
- Debrief after session

---

## Advanced Usage

### Custom Attack Patterns

Modify `attack_injector.py` to create custom patterns:

```python
# Focus on specific attack type
ATTACK_TYPES = ["GPS Spoofing"]  # Only GPS attacks

# Vary intensity
def variable_interval():
    return random.randint(2, 10)  # Random intervals
```

### Multiple Injectors

Run multiple injectors simultaneously:

```bash
# Terminal 1
python attack_injector.py --continuous --interval 5

# Terminal 2
python attack_injector.py --continuous --interval 7

# Creates overlapping attack patterns
```

### Scheduled Attacks

Use cron or Task Scheduler:

```bash
# Linux cron - attack every hour for 5 minutes
0 * * * * python /path/to/attack_injector.py --duration 300
```

---

## Comparison: Before vs After

### Before (Built-in Button)
- ❌ Dashboard controls attacks
- ❌ Not realistic
- ❌ Manual intervention
- ❌ Confusing for operators

### After (Separate Injector)
- ✅ External attack source
- ✅ Realistic scenario
- ✅ Automated testing
- ✅ Clear separation of concerns

---

## Security Notes

### Production Deployment

**DO NOT:**
- ❌ Deploy injector to production
- ❌ Leave injector running unattended
- ❌ Use in live VANET network

**DO:**
- ✅ Use only in test environment
- ✅ Coordinate with team
- ✅ Document test sessions
- ✅ Clean up after testing

### Access Control

- Requires admin credentials
- Logs all actions
- Audit trail maintained
- Can be disabled if needed

---

## Future Enhancements

### Possible Improvements

1. **GUI Interface**
   - Visual control panel
   - Real-time statistics
   - Attack scheduling

2. **Attack Profiles**
   - Predefined scenarios
   - Custom attack patterns
   - Intensity levels

3. **Network Simulation**
   - Multiple attacker nodes
   - Coordinated attacks
   - Geographic distribution

4. **Reporting**
   - Attack summary reports
   - Detection rate analysis
   - Performance metrics

---

## Summary

The Attack Injector provides:
- ✅ Realistic attack simulation
- ✅ External attack source
- ✅ Flexible testing options
- ✅ Easy to use
- ✅ Professional separation

**Result:** Dashboard becomes a pure monitoring and detection system, just like in real production!

---

**Created:** February 24, 2026  
**Version:** 4.0.0 Enterprise Edition  
**Status:** Production Ready
