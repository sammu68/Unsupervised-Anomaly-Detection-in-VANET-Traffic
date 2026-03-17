# Attack Types Detection Guide

## Overview
The VANET system can detect and classify 6 different types of attacks based on vehicle behavior patterns.

---

## 1. GPS Spoofing 📡

### Description
The most severe attack where vehicles falsify GPS coordinates with extreme position jumps, simulating teleportation-like behavior.

### Characteristics
- **Severity**: HIGH
- **Color Code**: Red (#dc2626)
- **Detection Threshold**: Position jump > 15 units

### Detection Indicators
- Extreme position jumps (>15 units)
- GPS coordinates highly erratic (variance >30)
- Impossible speed values
- Teleportation-like movement patterns

### Example Scenario
A vehicle suddenly appears 20 units away from its previous position, indicating GPS coordinate manipulation.

### Real-World Impact
- Causes traffic accidents
- Disrupts navigation systems
- Creates false traffic information
- Compromises safety-critical applications

---

## 2. Position Falsification 📍

### Description
Moderate false position reporting where vehicles report incorrect locations but with less extreme jumps than GPS spoofing.

### Characteristics
- **Severity**: MEDIUM
- **Color Code**: Orange (#ea580c)
- **Detection Threshold**: Position jump 8-15 units

### Detection Indicators
- Moderate position jumps (8-15 units)
- Erratic movement patterns
- False position data reported
- Jump variance 15-30

### Example Scenario
A vehicle reports being 10 units away from its actual position to avoid traffic or tolls.

### Real-World Impact
- Misleads traffic management systems
- Affects route optimization
- Compromises location-based services

---

## 3. Sybil Attack 👥

### Description
A single malicious vehicle creates multiple fake identities, appearing as multiple vehicles at the same or nearby locations.

### Characteristics
- **Severity**: HIGH
- **Color Code**: Fuchsia (#d946ef)
- **Detection Threshold**: Position clustering < 5

### Detection Indicators
- Multiple IDs at similar location
- Low position variance (<5)
- Suspicious identity behavior
- Low jerk magnitude (<0.1)

### Example Scenario
One physical vehicle broadcasts messages with 5 different vehicle IDs, all reporting similar positions.

### Real-World Impact
- Manipulates traffic density perception
- Affects voting-based protocols
- Compromises trust in network
- Enables other attacks

---

## 4. DoS Attack 💥

### Description
Denial of Service attack where malicious vehicles flood the network with excessive messages, overwhelming legitimate communication.

### Characteristics
- **Severity**: HIGH
- **Color Code**: Violet (#7c3aed)
- **Detection Threshold**: Message rate > 100

### Detection Indicators
- High message rate (>100 messages)
- Network flooding detected
- Excessive communication
- Message rate >200 for extreme cases

### Example Scenario
A vehicle sends 250 messages per second, consuming network bandwidth and preventing legitimate vehicles from communicating.

### Real-World Impact
- Network congestion
- Delayed safety messages
- Communication failures
- System unavailability

---

## 5. Message Tampering ✏️

### Description
Attackers intercept and modify message content, altering velocity, position, or other critical data without extreme position changes.

### Characteristics
- **Severity**: MEDIUM
- **Color Code**: Amber (#f59e0b)
- **Detection Threshold**: Velocity inconsistency > 2

### Detection Indicators
- Velocity data inconsistent
- Impossible speed values
- Message content altered
- Speed anomaly detected

### Example Scenario
A vehicle's speed is reported as 150 km/h when physically impossible, or velocity changes erratically without corresponding position changes.

### Real-World Impact
- False collision warnings
- Incorrect traffic predictions
- Compromised safety applications
- Misleading driver assistance

---

## 6. Replay Attack 🔁

### Description
Attackers capture legitimate messages and resend them later, creating stale or outdated information in the network.

### Characteristics
- **Severity**: LOW
- **Color Code**: Cyan (#06b6d4)
- **Detection Threshold**: Jerk magnitude < 0.05

### Detection Indicators
- Repetitive message patterns
- Stale data detected
- Low jerk magnitude (<0.05)
- Velocity inconsistency <0.5

### Example Scenario
An attacker records a vehicle's position messages and replays them 5 minutes later, making it appear the vehicle is still at that location.

### Real-World Impact
- Outdated traffic information
- False vehicle presence
- Timing-based protocol failures
- Reduced data freshness

---

## Detection Algorithm

### Behavioral Metrics Analyzed

1. **Position Jump Detection**
   - Calculates distance between consecutive positions
   - Identifies sudden teleportation-like movements
   - Threshold: 8-15 units (falsification), >15 units (spoofing)

2. **Velocity Consistency**
   - Monitors speed and acceleration patterns
   - Detects impossible velocity changes
   - Threshold: >2 for inconsistency

3. **Trajectory Smoothness**
   - Analyzes jerk (rate of change of acceleration)
   - Identifies erratic vs. smooth movement
   - Threshold: <0.05 for replay, <0.1 for Sybil

4. **Message Frequency**
   - Tracks communication rate per vehicle
   - Detects flooding patterns
   - Threshold: >100 messages for DoS

5. **Position Clustering**
   - Identifies multiple IDs at same location
   - Detects Sybil attack patterns
   - Threshold: <5 variance for clustering

### Classification Process

```
1. Detect Anomaly (MSE > 0.1114)
   ↓
2. Calculate Behavioral Metrics
   ↓
3. Score Each Attack Type (0-1)
   ↓
4. Select Highest Score
   ↓
5. Assign Confidence & Severity
   ↓
6. Generate Primary Indicators
```

---

## Confidence Scoring

### How It Works
Each attack type receives a score (0-1) based on how well the vehicle's behavior matches that attack pattern.

### Confidence Levels
- **High (>0.8)**: Very likely this attack type
- **Medium (0.4-0.8)**: Probable attack type
- **Low (<0.4)**: Uncertain, marked as "Unknown Attack"

### Example
```json
{
  "attack_type": "GPS Spoofing",
  "confidence": 0.87,
  "all_scores": {
    "GPS Spoofing": 0.87,
    "Position Falsification": 0.45,
    "Sybil Attack": 0.12,
    "DoS Attack": 0.05,
    "Message Tampering": 0.23,
    "Replay Attack": 0.08
  }
}
```

---

## Severity Calculation

### Base Severity by Type
- GPS Spoofing: 3 (HIGH)
- Sybil Attack: 3 (HIGH)
- DoS Attack: 3 (HIGH)
- Position Falsification: 2 (MEDIUM)
- Message Tampering: 2 (MEDIUM)
- Replay Attack: 1 (LOW)

### Confidence Adjustment
- Confidence >0.8: +1 severity level
- Confidence <0.4: -1 severity level

### Final Severity Labels
- 0: NONE
- 1: LOW (Yellow)
- 2: MEDIUM (Orange)
- 3: HIGH (Red)

---

### Visual Indicators

### Traffic Map Colors
- **Dark Green (#16a34a)**: Normal vehicle
- **Red (#dc2626)**: GPS Spoofing
- **Orange (#ea580c)**: Position Falsification
- **Fuchsia (#d946ef)**: Sybil Attack
- **Violet (#7c3aed)**: DoS Attack
- **Amber (#f59e0b)**: Message Tampering
- **Cyan (#06b6d4)**: Replay Attack

### Attack Panel Styling
- **Border Color**: Matches severity (yellow/orange/red)
- **Background**: Semi-transparent with severity color
- **Badge**: Shows severity level (LOW/MEDIUM/HIGH)
- **Icon**: Emoji representing attack type

---

## Testing Attack Detection

### Using Attack Injector (Recommended)
The system now uses a separate attack injector application for realistic testing:

```bash
# Basic 30-second test
python attack_injector.py

# Custom duration
python attack_injector.py --duration 60

# Continuous mode
python attack_injector.py --continuous --interval 5
```

**See [ATTACK_INJECTOR_GUIDE.md](ATTACK_INJECTOR_GUIDE.md) for complete guide.**

### What to Observe
1. Dashboard shows "⚠ SYSTEM UNDER ATTACK" banner
2. Vehicles appear with different colors (attack types)
3. Click AlertTriangle icon to open attack panel
4. View detailed threat information
5. Check attack statistics and severity levels

### Expected Results
- Multiple attack types detected simultaneously
- Color-coded vehicles on traffic map
- Attack panel shows detailed threat information
- Confidence scores between 0.3-1.0
- Severity levels assigned correctly
- Attack logs saved to database

---

## API Response Example

```json
{
  "id": 3,
  "x": 45.2,
  "y": 67.8,
  "speed": 35.5,
  "reconstruction_error": 0.2341,
  "is_anomaly": true,
  "attack_classification": {
    "attack_type": "GPS Spoofing",
    "confidence": 0.87,
    "severity": "HIGH",
    "details": {
      "primary_indicators": [
        "Extreme position jump: 18.5 units",
        "GPS coordinates highly erratic",
        "Impossible speed detected: 85.3",
        "Location manipulation detected"
      ],
      "all_scores": {
        "GPS Spoofing": 0.87,
        "Position Falsification": 0.45,
        "Sybil Attack": 0.12,
        "DoS Attack": 0.05,
        "Message Tampering": 0.23,
        "Replay Attack": 0.08
      }
    }
  }
}
```

---

## Best Practices

### For Operators
1. Use attack injector for testing: `python attack_injector.py`
2. Monitor attack panel during attack campaigns
3. Pay attention to HIGH severity attacks first
4. Check primary indicators for attack details
5. Review attack history for patterns
6. Report persistent attacks to administrators

### For Administrators
1. Use attack injector for training sessions
2. Review attack statistics regularly
3. Adjust detection thresholds if needed
4. Manage attack logs (delete old/all logs)
5. Monitor system performance during attacks
6. Update security policies based on attack patterns
7. Use continuous mode for stress testing

---

**Version**: 4.0.0 Enterprise Edition  
**Last Updated**: February 2026  
**Attack Types**: 6  
**Detection Accuracy**: 96.5%  
**Testing**: Separate attack injector application
