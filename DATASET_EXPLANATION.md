# Dataset Structure & Attack Types - Detailed Explanation

## Understanding Your Dataset

### What is VeReMi Dataset?

VeReMi (Vehicular Reference Misbehavior) is a **benchmark dataset** for testing misbehavior detection in vehicular networks. It contains simulated vehicle data with both normal and attack scenarios.

---

## Dataset Structure (Typical VeReMi)

### Columns You'll Find:

1. **sender** - Vehicle ID that sent the message
2. **messageID** - Unique message identifier
3. **rcvTime** - Time message was received
4. **type** - Message type (BSM = Basic Safety Message)
5. **pos_x** - X coordinate (position)
6. **pos_y** - Y coordinate (position)
7. **pos_z** - Z coordinate (altitude, often 0)
8. **spd_x** - Speed in X direction
9. **spd_y** - Speed in Y direction
10. **spd_z** - Speed in Z direction
11. **acl_x** - Acceleration in X direction
12. **acl_y** - Acceleration in Y direction
13. **acl_z** - Acceleration in Z direction
14. **heading** - Vehicle direction (degrees)
15. **attackerType** - Type of attack (0 = normal)

### Attack Types in VeReMi Dataset:

| attackerType | Attack Name | Description |
|--------------|-------------|-------------|
| 0 | Normal | Legitimate vehicle behavior |
| 1 | Constant Position | Reports same position repeatedly |
| 2 | Constant Offset | Adds fixed offset to real position |
| 3 | Random Position | Reports completely random positions |
| 4 | Random Offset | Adds random offset to real position |
| 5 | Eventual Stop | Gradually reduces speed to zero |
| 16 | Disruptive | Combination of multiple attacks |

---

## How Your System Uses This Data

### Training Phase (Already Done)

Your LSTM-Autoencoder was trained on **NORMAL data only** (attackerType = 0):

```python
# Training used only normal behavior
normal_data = dataset[dataset['attackerType'] == 0]

# Features used: [pos_x, pos_y, spd_x, spd_y]
# Sequence length: 10 timesteps
```

**Why only normal data?**
- Autoencoder learns "what normal looks like"
- Anything different = high reconstruction error = anomaly
- No need to show it attacks during training

### Detection Phase (Current System)

Your system detects anomalies by:

1. **Input**: Vehicle trajectory (10 timesteps of position + velocity)
2. **Process**: LSTM-Autoencoder tries to reconstruct it
3. **Output**: Reconstruction error (MSE)
4. **Decision**: 
   - MSE > 0.1114 → ANOMALY (attack)
   - MSE ≤ 0.1114 → NORMAL

### Classification Phase (Your New Feature)

After detecting anomaly, your `attack_classifier.py` classifies it into:

1. **GPS Spoofing** - Extreme position jumps
2. **Position Falsification** - Moderate false positions
3. **Sybil Attack** - Multiple IDs, same location
4. **DoS Attack** - High message rate
5. **Message Tampering** - Velocity inconsistencies
6. **Replay Attack** - Repetitive patterns

---

## Data Types Explained Simply

### 1. Position Data (pos_x, pos_y, pos_z)

**What it is**: Where the vehicle is located

```
Example:
pos_x = 450.5  (450.5 meters from origin in X direction)
pos_y = 320.8  (320.8 meters from origin in Y direction)
pos_z = 0.0    (ground level, usually 0)
```

**Data Type**: `float64` (decimal numbers)

**Why important**: 
- Sudden jumps = GPS spoofing
- Impossible positions = attack

### 2. Speed Data (spd_x, spd_y, spd_z)

**What it is**: How fast the vehicle is moving

```
Example:
spd_x = 15.5   (15.5 m/s in X direction)
spd_y = 2.3    (2.3 m/s in Y direction)
spd_z = 0.0    (not moving vertically)
```

**Data Type**: `float64` (decimal numbers)

**Why important**:
- Inconsistent with position = tampering
- Impossible speeds = attack

### 3. Acceleration Data (acl_x, acl_y, acl_z)

**What it is**: How quickly speed is changing

```
Example:
acl_x = 2.1    (accelerating at 2.1 m/s² in X)
acl_y = -0.5   (decelerating slightly in Y)
acl_z = 0.0    (no vertical acceleration)
```

**Data Type**: `float64` (decimal numbers)

**Why important**:
- Sudden changes = suspicious
- Physically impossible = attack

### 4. Heading

**What it is**: Direction vehicle is facing (0-360 degrees)

```
Example:
heading = 45.0   (facing northeast)
heading = 180.0  (facing south)
heading = 270.0  (facing west)
```

**Data Type**: `float64` (decimal number)

**Why important**:
- Should match movement direction
- Mismatch = possible attack

### 5. Time (rcvTime)

**What it is**: When the message was received

```
Example:
rcvTime = 10.5  (10.5 seconds into simulation)
```

**Data Type**: `float64` (decimal number)

**Why important**:
- Creates time sequences
- Detects replay attacks

### 6. IDs (sender, messageID)

**What it is**: Identifiers for vehicles and messages

```
Example:
sender = 42        (Vehicle #42)
messageID = 15023  (Message #15023)
```

**Data Type**: `int64` (whole numbers)

**Why important**:
- Track individual vehicles
- Detect Sybil attacks (multiple IDs, same location)

### 7. Attack Label (attackerType)

**What it is**: Ground truth - what attack is happening

```
Example:
attackerType = 0   (Normal - no attack)
attackerType = 1   (Constant Position attack)
attackerType = 3   (Random Position attack)
```

**Data Type**: `int64` (whole number)

**Why important**:
- Used for training evaluation
- Calculate accuracy
- Validate detection

---

## Simple Analogy

Think of the dataset like a **GPS tracking log**:

```
Time | Vehicle | Location (X,Y) | Speed (X,Y) | Attack?
-----|---------|----------------|-------------|--------
1.0  | Car#1   | (100, 200)     | (10, 5)     | No
1.1  | Car#1   | (101, 200.5)   | (10, 5)     | No
1.2  | Car#1   | (102, 201)     | (10, 5)     | No
1.3  | Car#1   | (500, 800)     | (10, 5)     | YES! (jumped)
```

In row 4, the car "teleported" from (102, 201) to (500, 800) - **GPS Spoofing!**

---

## How to Check Your Dataset

Run this command:

```bash
python quick_check.py
```

This will show you:
1. Column names in your dataset
2. First row of data
3. Data types for each column

---

## Common Questions

### Q: Why so many columns?
**A**: Vehicles broadcast lots of information for safety - position, speed, acceleration, direction, etc.

### Q: What's the difference between pos_x and spd_x?
**A**: 
- `pos_x` = WHERE you are (position)
- `spd_x` = HOW FAST you're moving (speed)

### Q: Why are there X, Y, Z versions?
**A**: 3D space:
- X = East-West
- Y = North-South  
- Z = Up-Down (usually 0 for ground vehicles)

### Q: What does float64 mean?
**A**: A decimal number with high precision (64 bits)
- Can store: 123.456789
- Range: Very large positive/negative numbers

### Q: What does int64 mean?
**A**: A whole number (no decimals) with 64 bits
- Can store: 1, 2, 3, 100, -50
- Range: -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807

---

## Your System's Data Flow

```
1. Dataset (50,000 samples)
   ↓
2. Extract features: [pos_x, pos_y, spd_x, spd_y]
   ↓
3. Create sequences: 10 timesteps per vehicle
   ↓
4. Normalize: Scale to 0-1 range
   ↓
5. Feed to LSTM-Autoencoder
   ↓
6. Get reconstruction error (MSE)
   ↓
7. Compare to threshold (0.1114)
   ↓
8. If anomaly → Classify attack type
   ↓
9. Display on dashboard
```

---

## Verification Steps

To verify your dataset is correct:

1. **Check it exists**:
   ```bash
   ls -l dataset_50k.csv
   ```

2. **Check structure**:
   ```bash
   python quick_check.py
   ```

3. **Verify it has**:
   - Position columns (pos_x, pos_y)
   - Speed columns (spd_x, spd_y)
   - Attack labels (attackerType)
   - ~50,000 rows

4. **Check attack distribution**:
   - Should have both normal (0) and attacks (1-16)
   - Typical: 70-80% normal, 20-30% attacks

---

## If Dataset Structure is Different

If your dataset has different column names, update:

1. **In `calculate_accuracy.py`**: Adjust column names
2. **In `main.py`**: Update feature extraction
3. **In documentation**: Update column references

---

**Need to see your actual dataset structure?** Run:
```bash
python quick_check.py
```

Then share the output and I'll help you understand it!
