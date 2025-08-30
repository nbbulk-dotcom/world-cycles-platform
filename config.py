"""
Version 1.1 — Imports, Physical Constants, and Configuration
Dual Portal Stargate Simulation System

This module sets up all core scientific and hardware parameters for the simulation, 
and initializes the configuration structure for subsequent modules. Designed for full 
transparency, empirical accuracy, and real-world hardware extension.
"""

import numpy as np                  # Core numerical operations
from scipy.integrate import odeint  # Scientific ODE solver, for resonance dynamics
import matplotlib.pyplot as plt     # Full-featured plotting/display library

RES_FREQ = 32.0            # Hz (Bio-safe resonance frequency, main portal drive band)
ENERGY_RATE = 13500.0      # Watts (Tesla Powerwall peak, main supply per portal)
V_HUMAN = 0.1              # m³ (Default human subject volume, overrideable per run)
FLOOR_TEMP_THRESH = -195.8 # °C (Liquid nitrogen phase threshold, critical for safety)
FLOOR_SOLID_CONTACT = True # Boolean default; True if physical floor sensor reads contact

TESLA_BATTERY_CAPACITY = 13.5     # kWh, each main power module
FAILSAFE_BLOCKS = 2               # Number of independent physical failsafe backups

DETUNE_DEFAULT = 0.08             # Hz, recommended initial detuning for bridge regime

DAMPING_MIN = 0.02                # Minimum physical damping to avoid ringing
DAMPING_MAX = 0.12                # Maximum damping before coherence drops

MONITOR_COUNT = 3                 # System runs on 3 physical/logical monitors

LOG_FILENAME = "stargate_datalog.csv"
AUDIT_FILENAME = "stargate_auditlog.json"

SimulationConfig = {
    "resonance_frequency": RES_FREQ,
    "energy_rate": ENERGY_RATE,
    "subject_volume": V_HUMAN,
    "floor_temp_threshold": FLOOR_TEMP_THRESH,
    "tesla_battery_capacity": TESLA_BATTERY_CAPACITY,
    "failsafe_blocks": FAILSAFE_BLOCKS,
    "detune_default": DETUNE_DEFAULT,
    "damping_min": DAMPING_MIN,
    "damping_max": DAMPING_MAX,
    "monitor_count": MONITOR_COUNT,
    "log_filename": LOG_FILENAME,
    "audit_filename": AUDIT_FILENAME
}

def load_simulation_config(filepath=None):
    """
    Loads and validates a configuration dict.
    If filepath is provided, overrides baseline defaults.
    """
    import json, os
    cfg = SimulationConfig.copy()
    if filepath and os.path.exists(filepath):
        with open(filepath, "r") as f:
            user_cfg = json.load(f)
        for k, v in user_cfg.items():
            if k in cfg:
                cfg[k] = v
    return cfg

def validate_config(cfg):
    """
    Checks all critical parameters, prints warning and raises error if critical bounds are violated.
    """
    if cfg["resonance_frequency"] < 1 or cfg["resonance_frequency"] > 100:
        raise ValueError("Resonance frequency must be within 1–100 Hz (bio-safe/engineering bounds).")
    if not (0 < cfg["subject_volume"] < 10):
        raise ValueError("Subject volume unreasonably outside bounds: 0 < volume (m³) < 10.")
    if cfg["floor_temp_threshold"] > -100:
        raise ValueError("Floor temp threshold must be below -100°C for LN2 systems.")
    if cfg["monitor_count"] != 3:
        print("Warning: Non-standard monitor count—system expects three for full visibility.")
    return True

if __name__ == "__main__":
    cfg = load_simulation_config()
    try:
        validate_config(cfg)
        print("Configuration loaded and validated successfully:")
        from pprint import pprint
        pprint(cfg)
    except Exception as e:
        print("Critical configuration error:", str(e))
