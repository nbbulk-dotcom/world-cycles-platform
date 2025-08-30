"""
Version 1.2 — Portal & Resonance Model Module
Dual Portal Stargate Simulation System

Defines the Portal class, resonance oscillator, energy dynamics, payload sensing, 
floor sensor interaction, and stability metrics. Fully empirical, safety-aware, 
exception logged.
"""

import numpy as np
from config import SimulationConfig

def resonance_model(y, t, freq, damping=SimulationConfig["damping_min"]):
    """
    Second-order linear oscillator simulating portal resonance.
    y: [displacement, velocity]
    t: time (seconds)
    freq: resonance frequency (Hz)
    damping: damping/friction factor
    Returns the time derivative [velocity, acceleration]
    """
    omega2 = (2.0 * np.pi * freq) ** 2
    dydt = [y[1], -omega2 * y[0] - damping * y[1]]
    return dydt

class Portal:
    """
    Simulation class for a single quantum resonance portal.
    """
    def __init__(self, freq=SimulationConfig["resonance_frequency"], 
                 power=SimulationConfig["energy_rate"]):
        self.freq = freq                        # Resonance frequency (Hz)
        self.damping = SimulationConfig["damping_min"]  # Damping parameter
        self.power = power                      # Power input (W)
        self.stability = 1.0                    # System stability (0–1.0)
        self.energy = 0.0                       # Total energy delivered (Joules)
        self.payload_volume = SimulationConfig["subject_volume"]
        self.payload_mass = 75.0                # Default human mass (kg); overrideable
        self.floor_temp = SimulationConfig["floor_temp_threshold"]
        self.floor_contact = SimulationConfig["floor_temp_threshold"] < -100  # Assumes solid if cold enough
        self.safety_status = True               # All safety checks passed
        self.status_log = []

    def sense_payload(self, volume=None, mass=None):
        """
        Sets payload volume and mass, triggering auto-tuning of resonance frequency.
        """
        if volume:
            self.payload_volume = volume
        if mass:
            self.payload_mass = mass
        self.freq = min(SimulationConfig["resonance_frequency"], 
                        SimulationConfig["resonance_frequency"] / self.payload_volume ** (1/3))
        self.status_log.append(f"[INFO] Payload sensed: volume={self.payload_volume:.3f} m³, mass={self.payload_mass:.1f} kg. New freq={self.freq:.4f} Hz.")

    def update_energy(self, dt=1.0):
        """
        Updates cumulative energy delivered, based on current portal power and delta-t.
        """
        energy_add = self.power * dt
        self.energy += energy_add
        self.status_log.append(f"[INFO] Energy updated by {energy_add:.2f} J, total={self.energy:.2f} J.")

    def floor_sensor(self, temp=None, contact=None):
        """
        Receives input from coolant/floor sensors and updates safety status and stability.
        """
        if temp is not None:
            self.floor_temp = temp
        if contact is not None:
            self.floor_contact = contact
        if self.floor_temp > SimulationConfig["floor_temp_threshold"]:
            self.safety_status = False
            self.stability *= 0.7
            msg = f"[WARN] Floor temperature {self.floor_temp:.2f} °C exceeds safe threshold! Stability dropped to {self.stability:.2f}."
            self.status_log.append(msg)
        if not self.floor_contact:
            self.safety_status = False
            self.stability *= 0.8
            msg = f"[WARN] Floor contact lost; unsafe for transfer. Stability dropped to {self.stability:.2f}."
            self.status_log.append(msg)
        if self.safety_status:
            self.status_log.append("[INFO] Floor/coolant sensors OK.")

    def reset(self):
        """
        Resets energy, stability, safety status and sensor log for repeated runs.
        """
        self.energy = 0.0
        self.stability = 1.0
        self.safety_status = True
        self.status_log.clear()
        self.status_log.append("[INFO] Portal reset for new run.")

    def report_status(self):
        """
        Returns all logged status messages for review/audit.
        """
        return self.status_log.copy()

if __name__ == "__main__":
    portal = Portal()
    portal.sense_payload(volume=0.09, mass=80)
    portal.floor_sensor(temp=-196.0, contact=True)
    portal.update_energy(dt=2.0)
    print("Portal frequency:", portal.freq)
    print("Portal stability:", portal.stability)
    print("Portal energy:", portal.energy)
    print("Safety status:", portal.safety_status)
    print("Status log:")
    for log in portal.report_status():
        print(log)
    portal.reset()
    print("After reset:")
    for log in portal.report_status():
        print(log)
