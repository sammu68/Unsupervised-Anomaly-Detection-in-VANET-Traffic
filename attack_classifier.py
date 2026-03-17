import numpy as np
from typing import Dict, List
from collections import deque

class AttackClassifier:
    """
    Classifies different types of VANET attacks based on vehicle behavior patterns.
    
    Attack Types:
    1. GPS Spoofing - Falsifying GPS coordinates (location manipulation)
    2. Position Falsification - Vehicle reports false position data
    3. Sybil Attack - Multiple fake identities from single vehicle
    4. DoS Attack - Flooding network with messages
    5. Message Tampering - Altering message content
    6. Replay Attack - Resending old messages
    """
    
    def __init__(self):
        self.vehicle_history = {}  # Track vehicle patterns
        self.message_counts = {}   # Track message frequency
        self.position_history = {} # Track position changes
        
    def classify_attack(self, vehicle_id: int, trajectory: np.ndarray, 
                       reconstruction_error: float, speed: float) -> Dict:
        """
        Classify the type of attack based on vehicle behavior.
        
        Args:
            vehicle_id: Vehicle identifier
            trajectory: Recent trajectory history (SEQUENCE_LENGTH x 4)
            reconstruction_error: MSE from autoencoder
            speed: Current vehicle speed
            
        Returns:
            Dictionary with attack classification and confidence
        """
        
        # Initialize tracking for new vehicles
        if vehicle_id not in self.vehicle_history:
            self.vehicle_history[vehicle_id] = deque(maxlen=50)
            self.message_counts[vehicle_id] = 0
            self.position_history[vehicle_id] = deque(maxlen=20)
        
        # Update tracking
        self.message_counts[vehicle_id] += 1
        self.position_history[vehicle_id].append(trajectory[-1][:2])  # x, y
        
        # Calculate behavior metrics
        metrics = self._calculate_metrics(vehicle_id, trajectory, speed)
        
        # Classify attack type
        attack_type = "NORMAL"
        confidence = 0.0
        details = {}
        
        if reconstruction_error > 0.1114:  # Anomaly detected
            attack_type, confidence, details = self._determine_attack_type(metrics)
        
        return {
            "attack_type": attack_type,
            "confidence": round(confidence, 2),
            "severity": self._calculate_severity(attack_type, confidence),
            "details": details
        }
    
    def _calculate_metrics(self, vehicle_id: int, trajectory: np.ndarray, speed: float) -> Dict:
        """Calculate behavioral metrics for classification"""
        
        metrics = {}
        
        # 1. Position Jump Detection (Position Falsification indicator)
        if len(trajectory) >= 2:
            position_changes = np.diff(trajectory[:, :2], axis=0)
            distances = np.sqrt(np.sum(position_changes**2, axis=1))
            metrics['max_jump'] = float(np.max(distances))
            metrics['avg_jump'] = float(np.mean(distances))
            metrics['jump_variance'] = float(np.var(distances))
        else:
            metrics['max_jump'] = 0.0
            metrics['avg_jump'] = 0.0
            metrics['jump_variance'] = 0.0
        
        # 2. Velocity Consistency (Tampering indicator)
        if len(trajectory) >= 3:
            velocities = trajectory[:, 2:4]
            velocity_changes = np.diff(velocities, axis=0)
            metrics['velocity_inconsistency'] = float(np.mean(np.abs(velocity_changes)))
        else:
            metrics['velocity_inconsistency'] = 0.0
        
        # 3. Trajectory Smoothness (Sybil/Replay indicator)
        if len(trajectory) >= 3:
            # Calculate jerk (rate of change of acceleration)
            velocities = trajectory[:, 2:4]
            accelerations = np.diff(velocities, axis=0)
            jerk = np.diff(accelerations, axis=0)
            metrics['jerk_magnitude'] = float(np.mean(np.sqrt(np.sum(jerk**2, axis=1))))
        else:
            metrics['jerk_magnitude'] = 0.0
        
        # 4. Message Frequency (DoS indicator)
        metrics['message_rate'] = self.message_counts[vehicle_id]
        
        # 5. Speed Anomaly
        metrics['speed'] = speed
        metrics['speed_anomaly'] = 1.0 if speed > 50 or speed < 0 else 0.0
        
        # 6. Position Clustering (Sybil indicator)
        if len(self.position_history[vehicle_id]) >= 5:
            positions = np.array(list(self.position_history[vehicle_id]))
            position_variance = np.var(positions, axis=0)
            metrics['position_clustering'] = float(np.mean(position_variance))
        else:
            metrics['position_clustering'] = 0.0
        
        return metrics
    
    def _determine_attack_type(self, metrics: Dict) -> tuple:
        """Determine the most likely attack type based on metrics"""
        
        scores = {
            "GPS Spoofing": 0.0,
            "Position Falsification": 0.0,
            "Sybil Attack": 0.0,
            "DoS Attack": 0.0,
            "Message Tampering": 0.0,
            "Replay Attack": 0.0
        }
        
        # GPS Spoofing: Sudden large jumps + high variance (teleportation-like behavior)
        if metrics['max_jump'] > 15:
            scores["GPS Spoofing"] += 0.5
        if metrics['jump_variance'] > 30:
            scores["GPS Spoofing"] += 0.4
        if metrics['avg_jump'] > 8:
            scores["GPS Spoofing"] += 0.3
        # GPS spoofing often shows impossible speed
        if metrics['speed_anomaly'] > 0 and metrics['max_jump'] > 10:
            scores["GPS Spoofing"] += 0.4
        
        # Position Falsification: Moderate position jumps (less extreme than GPS spoofing)
        if metrics['max_jump'] > 8 and metrics['max_jump'] <= 15:
            scores["Position Falsification"] += 0.4
        if metrics['avg_jump'] > 4 and metrics['avg_jump'] <= 8:
            scores["Position Falsification"] += 0.3
        if metrics['jump_variance'] > 15 and metrics['jump_variance'] <= 30:
            scores["Position Falsification"] += 0.3
        
        # Sybil Attack: Low position variance (multiple IDs, same location)
        if metrics['position_clustering'] < 5:
            scores["Sybil Attack"] += 0.5
        if metrics['jerk_magnitude'] < 0.1:
            scores["Sybil Attack"] += 0.3
        
        # DoS Attack: High message rate
        if metrics['message_rate'] > 100:
            scores["DoS Attack"] += 0.6
        if metrics['message_rate'] > 200:
            scores["DoS Attack"] += 0.4
        
        # Message Tampering: Velocity inconsistencies without extreme position jumps
        if metrics['velocity_inconsistency'] > 2 and metrics['max_jump'] < 10:
            scores["Message Tampering"] += 0.5
        if metrics['speed_anomaly'] > 0 and metrics['max_jump'] < 8:
            scores["Message Tampering"] += 0.3
        
        # Replay Attack: Repetitive patterns
        if metrics['jerk_magnitude'] < 0.05 and metrics['position_clustering'] < 10:
            scores["Replay Attack"] += 0.4
        if metrics['velocity_inconsistency'] < 0.5:
            scores["Replay Attack"] += 0.3
        
        # Find highest scoring attack
        attack_type = max(scores, key=scores.get)
        confidence = min(scores[attack_type], 1.0)
        
        # If confidence too low, mark as "Unknown Attack"
        if confidence < 0.3:
            attack_type = "Unknown Attack"
            confidence = 0.5
        
        # Build details
        details = {
            "primary_indicators": self._get_primary_indicators(attack_type, metrics),
            "all_scores": {k: round(v, 2) for k, v in scores.items()}
        }
        
        return attack_type, confidence, details
    
    def _get_primary_indicators(self, attack_type: str, metrics: Dict) -> List[str]:
        """Get human-readable indicators for the attack type"""
        indicators = []
        
        if attack_type == "GPS Spoofing":
            if metrics['max_jump'] > 15:
                indicators.append(f"Extreme position jump: {metrics['max_jump']:.1f} units")
            if metrics['jump_variance'] > 30:
                indicators.append("GPS coordinates highly erratic")
            if metrics['speed_anomaly'] > 0:
                indicators.append(f"Impossible speed detected: {metrics['speed']:.1f}")
            indicators.append("Location manipulation detected")
        
        elif attack_type == "Position Falsification":
            if metrics['max_jump'] > 8:
                indicators.append(f"Large position jump: {metrics['max_jump']:.1f} units")
            if metrics['jump_variance'] > 15:
                indicators.append("Erratic movement pattern")
            indicators.append("False position data reported")
        
        elif attack_type == "Sybil Attack":
            if metrics['position_clustering'] < 5:
                indicators.append("Multiple IDs at similar location")
            indicators.append("Suspicious identity behavior")
        
        elif attack_type == "DoS Attack":
            indicators.append(f"High message rate: {metrics['message_rate']} msgs")
            indicators.append("Network flooding detected")
        
        elif attack_type == "Message Tampering":
            if metrics['velocity_inconsistency'] > 2:
                indicators.append("Velocity data inconsistent")
            if metrics['speed_anomaly'] > 0:
                indicators.append(f"Impossible speed: {metrics['speed']:.1f}")
            indicators.append("Message content altered")
        
        elif attack_type == "Replay Attack":
            indicators.append("Repetitive message pattern")
            indicators.append("Stale data detected")
        
        return indicators if indicators else ["Anomalous behavior detected"]
    
    def _calculate_severity(self, attack_type: str, confidence: float) -> str:
        """Calculate attack severity level"""
        
        # Base severity by attack type
        severity_map = {
            "GPS Spoofing": 3,  # High severity - critical safety impact
            "Position Falsification": 2,
            "Sybil Attack": 3,
            "DoS Attack": 3,
            "Message Tampering": 2,
            "Replay Attack": 1,
            "Unknown Attack": 1,
            "NORMAL": 0
        }
        
        base_severity = severity_map.get(attack_type, 1)
        
        # Adjust by confidence
        if confidence > 0.8:
            base_severity = min(base_severity + 1, 3)
        elif confidence < 0.4:
            base_severity = max(base_severity - 1, 0)
        
        # Map to labels
        severity_labels = {
            0: "NONE",
            1: "LOW",
            2: "MEDIUM",
            3: "HIGH",
        }
        
        return severity_labels.get(base_severity, "LOW")
    
    def reset_vehicle(self, vehicle_id: int):
        """Reset tracking for a specific vehicle"""
        if vehicle_id in self.vehicle_history:
            del self.vehicle_history[vehicle_id]
            del self.message_counts[vehicle_id]
            del self.position_history[vehicle_id]
    
    def reset_all(self):
        """Reset all tracking data"""
        self.vehicle_history.clear()
        self.message_counts.clear()
        self.position_history.clear()
