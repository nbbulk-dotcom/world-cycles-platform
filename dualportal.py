"""
Version 1.3 — Dual Portal Interaction & Bridge Logic Module
Dual Portal Stargate Simulation System

Defines the DualPortal class and all logic for managing two linked resonance portals,
bidirectional transfer, bridge strength calculation, detune state, and cross-portal 
stability auditing. Each action is empirical, stateful, and transparently logged.
"""

import numpy as np
from portal import Portal
from config import SimulationConfig

class DualPortal:
    """
    Class to manage dual-portals, their bridge formation, resonance detuning,
    power transfer, stability, and audit trail for every transfer run.
    """

    def __init__(self, freq1=SimulationConfig["resonance_frequency"], 
                 detune=SimulationConfig["detune_default"],
                 power=SimulationConfig["energy_rate"]):
        self.portal1 = Portal(freq=freq1, power=power)
        self.portal2 = Portal(freq=freq1 + detune, power=power)
        self.detune = detune                         # Empirical detune (Hz)
        self.bridge_strength = 0.0                   # Bridge strength metric (0-1)
        self.transfer_energy = 0.0
        self.status_log = []
        self.run_id = None

    def initialize_run(self, payload_volume=None, payload_mass=None, 
                       floor_temp1=None, floor_contact1=None,
                       floor_temp2=None, floor_contact2=None):
        """
        Initializes both portals with payload and sensor readings.
        """
        self.portal1.reset()
        self.portal2.reset()
        self.portal1.sense_payload(volume=payload_volume, mass=payload_mass)
        self.portal2.sense_payload(volume=payload_volume, mass=payload_mass)
        self.portal1.floor_sensor(temp=floor_temp1, contact=floor_contact1)
        self.portal2.floor_sensor(temp=floor_temp2, contact=floor_contact2)
        self.status_log = []
        self.run_id = f"run_{np.random.randint(1e6)}"
        self.status_log.append(f"[INFO] Run {self.run_id} initialized.")

    def form_bridge(self, t, energy_input=None):
        """
        Forms a resonant bridge between portals if stability and energy conditions are met.
        Calculation uses direct energy delivery ratio and empirical detune.
        """
        if energy_input is None:
            energy_input = min(self.portal1.energy, self.portal2.energy)
        self.transfer_energy = energy_input
        min_energy = SimulationConfig["energy_rate"] * (1 + abs(self.detune) / SimulationConfig["resonance_frequency"])
        self.bridge_strength = max(0.0, min(1.0, energy_input / min_energy))
        if self.portal1.stability < 0.9 or self.portal2.stability < 0.9:
            self.bridge_strength *= 0.7
            self.status_log.append("[WARN] Portal stability below threshold—bridge degraded.")
        if not (self.portal1.safety_status and self.portal2.safety_status):
            self.bridge_strength = 0.0
            self.status_log.append("[ERROR] Safety failure—bridge formation blocked.")
        if self.bridge_strength >= 0.95:
            self.status_log.append("[INFO] Bridge formed at maximum strength.")
        else:
            self.status_log.append(f"[INFO] Bridge strength updated: {self.bridge_strength:.2f}")

    def transfer_payload(self):
        """
        Attempts a transfer across the bridge. Success/failure is calculated 
        empirically from bridge strength and portal stabilities.
        Returns True if transfer succeeds, or False if blocked/unstable.
        """
        if self.bridge_strength >= 0.98:
            self.status_log.append("[SUCCESS] Payload transferred—maximum bridge stability.")
            result = True
        elif self.bridge_strength >= 0.90:
            self.status_log.append("[SUCCESS] Payload transferred—acceptable bridge stability.")
            result = True
        else:
            self.status_log.append("[FAIL] Payload transfer blocked/unreliable (bridge too weak).")
            result = False
        return result

    def full_status(self):
        """
        Compiles full status report for both portals and bridge for display/log/audit.
        """
        report = [f"Run ID: {self.run_id}",
                  f"Portal 1 freq: {self.portal1.freq:.3f} Hz, stability: {self.portal1.stability:.2f}, safety: {self.portal1.safety_status}",
                  f"Portal 2 freq: {self.portal2.freq:.3f} Hz, stability: {self.portal2.stability:.2f}, safety: {self.portal2.safety_status}",
                  f"Detune: {self.detune:.3f} Hz",
                  f"Bridge strength: {self.bridge_strength:.2f}, transfer energy: {self.transfer_energy:.2f} J",
                  f"Status log:"]
        report += self.portal1.report_status()
        report += self.portal2.report_status()
        report += self.status_log
        return report

    def reset(self):
        """
        Resets bridge state, energy, and logs for next run.
        """
        self.portal1.reset()
        self.portal2.reset()
        self.bridge_strength = 0.0
        self.transfer_energy = 0.0
        self.status_log.clear()
        self.run_id = None

if __name__ == "__main__":
    dp = DualPortal()
    dp.initialize_run(payload_volume=0.1, payload_mass=75, 
                      floor_temp1=-196, floor_contact1=True, 
                      floor_temp2=-196, floor_contact2=True)
    dp.portal1.update_energy(dt=2.0)
    dp.portal2.update_energy(dt=2.0)
    dp.form_bridge(t=2.0)
    result = dp.transfer_payload()
    print("Bridge transfer result:", "Success" if result else "Fail")
    print("Full status report:")
    for line in dp.full_status():
        print(line)
    dp.reset()
    print("\nAfter reset:")
    for line in dp.full_status():
        print(line)
