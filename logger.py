"""
Version 1.6 — Data Logging, Export, and Audit Module
Dual Portal Stargate Simulation System

Provides full logging of all portal/bridge actions, simulation parameters, state changes, 
transfers, warnings, and failures. Supports export to CSV and JSON for compliance, audit, 
and peer review. Logging is modular and can be attached to all simulation orchestration scripts.
"""

import json
import csv
import os
import time
from datetime import datetime

def make_log_entry(timestamp, event, run_id, portal1, portal2, bridge_strength, transfer_result=None, extra=None):
    """Create a unified log dictionary for all major simulation events."""
    entry = {
        "timestamp": timestamp,
        "event": event,
        "run_id": run_id,
        "portal1_freq": portal1.freq,
        "portal1_stab": portal1.stability,
        "portal1_energy": portal1.energy,
        "portal1_safety": portal1.safety_status,
        "portal2_freq": portal2.freq,
        "portal2_stab": portal2.stability,
        "portal2_energy": portal2.energy,
        "portal2_safety": portal2.safety_status,
        "bridge_strength": bridge_strength,
        "transfer_result": transfer_result,
        "extra": extra if extra is not None else ""
    }
    return entry

class SimulationLogger:
    """
    Handles the collection, buffering, and export of all simulation event records.
    """
    def __init__(self, csv_filename="stargate_datalog.csv", json_filename="stargate_auditlog.json"):
        self.records = []
        self.csv_filename = csv_filename
        self.json_filename = json_filename

    def log_event(self, event, run_id, portal1, portal2, bridge_strength, transfer_result=None, extra=None):
        timestamp = datetime.utcnow().isoformat()
        entry = make_log_entry(timestamp, event, run_id, portal1, portal2, bridge_strength, transfer_result, extra)
        self.records.append(entry)

    def export_csv(self):
        if not self.records:
            print("[Logger] No records to export.")
            return
        keys = self.records[0].keys()
        with open(self.csv_filename, "w", newline='') as f:
            writer = csv.DictWriter(f, keys)
            writer.writeheader()
            writer.writerows(self.records)
        print(f"[Logger] Exported log to {self.csv_filename}")

    def export_json(self):
        if not self.records:
            print("[Logger] No records to export.")
            return
        with open(self.json_filename, "w") as f:
            json.dump(self.records, f, indent=4)
        print(f"[Logger] Exported audit to {self.json_filename}")

    def clear(self):
        self.records.clear()

if __name__ == "__main__":
    from portal import Portal
    from dualportal import DualPortal

    dp = DualPortal()
    dp.initialize_run(payload_volume=0.1, payload_mass=75, floor_temp1=-196.0, floor_contact1=True, floor_temp2=-196.0, floor_contact2=True)
    dp.portal1.update_energy(dt=1.0)
    dp.portal2.update_energy(dt=1.0)
    dp.form_bridge(t=1.0)
    result = dp.transfer_payload()

    logger = SimulationLogger()
    logger.log_event("Start Run", dp.run_id, dp.portal1, dp.portal2, dp.bridge_strength, None, "Run initialized")
    logger.log_event("Bridge Update", dp.run_id, dp.portal1, dp.portal2, dp.bridge_strength, None, "Bridge formed/updated")
    logger.log_event("Transfer Attempt", dp.run_id, dp.portal1, dp.portal2, dp.bridge_strength, result, "Final transfer result")
    logger.export_csv()
    logger.export_json()
    print("[Logger] Demo complete. Log files created.")
