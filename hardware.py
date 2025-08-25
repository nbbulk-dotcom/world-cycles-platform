"""
Version 2.1 — Sensor, Power, and Hardware API Layer
Dual Portal Stargate Simulation System

Enables integration with real-world lab sensors, power modules, and failsafe interfaces.
Includes stub classes for temperature sensor, contact sensor, battery control, failsafe management, 
and basic environment reading. Each class includes API, status, and update methods, plus 
demonstration/test routines.
"""

class TemperatureSensor:
    """Interface for ambient or floor temperature sensors"""
    def __init__(self, name="TempSensor", initial=-196.0):
        self.name = name
        self.value = initial  # °C
        self.status = "OK"

    def read(self):
        """Read temperature value (override for hardware API)"""
        return self.value

    def update(self, new_value):
        """Update sim/hardware temperature value"""
        self.value = new_value
        self.status = "OK" if new_value < -100 else "WARN"

class ContactSensor:
    """Interface for solid floor contact (True/False)"""
    def __init__(self, name="ContactSensor", initial=True):
        self.name = name
        self.contact = initial
        self.status = "OK" if initial else "FAIL"

    def read(self):
        """Read contact status (replace with hardware switch input)"""
        return self.contact

    def update(self, state):
        self.contact = state
        self.status = "OK" if state else "FAIL"

class TeslaBattery:
    """Stub/API for Tesla battery management"""
    def __init__(self, capacity_kwh=13.5, charge_pct=100.0):
        self.capacity = capacity_kwh      # kWh
        self.charge_pct = charge_pct      # %
        self.failsafe_engaged = False

    def supply_power(self, rate_W):
        """Draws power from the battery, updates charge status"""
        used_kWh = rate_W / 1000.0 / 3600.0
        self.capacity -= used_kWh
        self.charge_pct = max(0.0, self.charge_pct - (used_kWh / 13.5) * 100)
        self.failsafe_engaged = self.charge_pct < 10.0
        return rate_W if not self.failsafe_engaged else 0.0

    def status(self):
        return {
            "capacity_kWh": self.capacity,
            "charge_pct": self.charge_pct,
            "failsafe_engaged": self.failsafe_engaged
        }

    def reset(self):
        self.capacity = 13.5
        self.charge_pct = 100.0
        self.failsafe_engaged = False

class FailsafeBlock:
    """Simulates a failsafe system, can be extended to real cutover logic."""
    def __init__(self):
        self.engaged = False

    def test(self):
        self.engaged = True

    def reset(self):
        self.engaged = False

class EnvironmentMonitor:
    """Stub for site environment: can hold pressure, humidity, ELF field, etc."""
    def __init__(self, temp=-196, humidity=0.5, pressure=101.3):
        self.temp = temp
        self.humidity = humidity
        self.pressure = pressure  # kPa

    def read_all(self):
        return {"temp": self.temp, "humidity": self.humidity, "pressure": self.pressure}

    def update(self, temp=None, humidity=None, pressure=None):
        if temp is not None: self.temp = temp
        if humidity is not None: self.humidity = humidity
        if pressure is not None: self.pressure = pressure

if __name__ == "__main__":
    temp_sensor = TemperatureSensor("LN2Floor", -200.0)
    contact_sensor = ContactSensor("FloorContact", True)
    battery = TeslaBattery()
    failsafe1 = FailsafeBlock()
    env = EnvironmentMonitor()

    print("[Sensor API Demo] Initial Read:")
    print("Temp:", temp_sensor.read())
    print("Contact:", contact_sensor.read())
    print("Battery:", battery.status())
    print("Failsafe:", failsafe1.engaged)
    print("Environment:", env.read_all())

    print("[Testing battery drain/failsafe...]")
    for i in range(50):
        power_supplied = battery.supply_power(13500)  # Draw at max for 1s
        if battery.failsafe_engaged:
            failsafe1.test()
            print(f"Failsafe activated at cycle {i}")
            break

    print("Final battery status:", battery.status())
    print("Failsafe status:", failsafe1.engaged)
