from dataclasses import dataclass
from enum import Enum, auto
import math
import random


class Phase(Enum):
    BREWING = auto()
    THRESHOLD = auto()
    FULL_STORM = auto()
    END = auto()


@dataclass
class StormState:
    temperature: float
    pressure: float
    wind_speed: float
    wind_direction: float
    wind_instability: float
    humidity: float
    soil_temperature: float
    shadow_density: float
    petrichor_detected: bool
    lightning_events: int
    thunder_delay: float
    rain_sound_detected: bool
    rain_intensity: float
    downdraft_force: float
    lightning_frequency: float
    turbulence: float
    rain_particle_density: float


class Storm:
    def __init__(self):
        self.state = Phase.BREWING
        self.full_stage = "impact"
        self.iteration = 0
        self.constants = {
            "brew_target_temp": 12.0,
            "brew_temp_drop": 0.3,
            "brew_pressure_drop": 0.5,
            "brew_shadow_gain": 0.05,
            "brew_wind_gain": 0.2,
            "brew_humidity_gain": 1.5,
            "petrichor_humidity": 68.0,
            "petrichor_soil": 18.0,
            "brew_pressure_threshold": 990.0,
            "brew_wind_instability_threshold": 5.0,
            "brew_shadow_threshold": 0.9,
            "threshold_lightning_charge_gain": 8.0,
            "threshold_lightning_threshold": 24.0,
            "threshold_wind_gain": 1.1,
            "threshold_humidity_gain": 2.2,
            "threshold_saturation": 98.0,
            "threshold_turbulent_wind": 18.0,
            "threshold_min_lightning": 4,
            "threshold_rain_distance_drop": 1.7,
            "full_vertical_burst": 35.0,
            "full_downpour_intensity": 60.0,
            "full_frenzy_frequency": 12.0,
            "full_turbulence_peak": 40.0,
            "full_particle_density_peak": 85.0,
            "silence_decay": 4.5,
        }
        self.charge = 0.0
        self.lightning_distance = 18.0
        self.sound_speed = 0.34
        random.seed(0)
        self.s = StormState(
            temperature=20.0,
            pressure=1012.0,
            wind_speed=0.0,
            wind_direction=0.0,
            wind_instability=0.0,
            humidity=45.0,
            soil_temperature=20.0,
            shadow_density=0.1,
            petrichor_detected=False,
            lightning_events=0,
            thunder_delay=0.0,
            rain_sound_detected=False,
            rain_intensity=0.0,
            downdraft_force=0.0,
            lightning_frequency=0.0,
            turbulence=0.0,
            rain_particle_density=0.0,
        )

    def run(self):
        while self.state is not Phase.END:
            if self.state is Phase.BREWING:
                self._brewing_phase()
            elif self.state is Phase.THRESHOLD:
                self._threshold_phase()
            elif self.state is Phase.FULL_STORM:
                self._full_storm_phase()
            self.iteration += 1

    def _brewing_phase(self):
        self.s.temperature = max(self.constants["brew_target_temp"], self.s.temperature - self.constants["brew_temp_drop"])
        self.s.pressure = max(self.constants["brew_pressure_threshold"], self.s.pressure - self.constants["brew_pressure_drop"])
        self.s.wind_instability += self.constants["brew_wind_gain"]
        self.s.wind_speed = min(self.s.wind_speed + self.constants["brew_wind_gain"], self.constants["threshold_turbulent_wind"])
        self.s.wind_direction = (self.s.wind_direction + 7.0 + math.sin(self.iteration)) % 360
        self.s.humidity = min(100.0, self.s.humidity + self.constants["brew_humidity_gain"])
        self.s.soil_temperature = max(10.0, self.s.soil_temperature - 0.1)
        self.s.shadow_density = min(1.0, self.s.shadow_density + self.constants["brew_shadow_gain"])
        if not self.s.petrichor_detected:
            if self.s.humidity >= self.constants["petrichor_humidity"] and self.s.soil_temperature <= self.constants["petrichor_soil"]:
                self.s.petrichor_detected = True
        if self._brewing_complete():
            self.state = Phase.THRESHOLD

    def _brewing_complete(self):
        return (
            self.s.temperature <= self.constants["brew_target_temp"]
            and self.s.pressure <= self.constants["brew_pressure_threshold"]
            and self.s.wind_instability >= self.constants["brew_wind_instability_threshold"]
            and self.s.shadow_density >= self.constants["brew_shadow_threshold"]
            and self.s.petrichor_detected
        )

    def _threshold_phase(self):
        self.charge += self.constants["threshold_lightning_charge_gain"]
        if self.charge >= self.constants["threshold_lightning_threshold"]:
            self.s.lightning_events += 1
            self.charge -= self.constants["threshold_lightning_threshold"] * 0.7
        self.s.wind_speed += self.constants["threshold_wind_gain"]
        self.s.wind_direction = (self.s.wind_direction + 23.0 + random.random()) % 360
        self.s.wind_instability += 0.8
        self.lightning_distance = max(1.0, self.lightning_distance - self.constants["threshold_rain_distance_drop"])
        self.s.thunder_delay = self.lightning_distance / self.sound_speed
        if self.lightning_distance <= 8.0:
            self.s.rain_sound_detected = True
        self.s.humidity = min(100.0, self.s.humidity + self.constants["threshold_humidity_gain"])
        if self._threshold_complete():
            self.state = Phase.FULL_STORM

    def _threshold_complete(self):
        return (
            self.s.lightning_events >= self.constants["threshold_min_lightning"]
            and self.s.thunder_delay <= 20.0
            and self.s.wind_speed >= self.constants["threshold_turbulent_wind"]
            and self.s.rain_sound_detected
            and self.s.humidity >= self.constants["threshold_saturation"]
        )

    def _full_storm_phase(self):
        if self.full_stage == "impact":
            self.s.rain_intensity += self.constants["full_vertical_burst"]
            self.s.temperature = max(5.0, self.s.temperature - 1.8)
            self.s.downdraft_force += 6.0
            if self.s.rain_intensity >= self.constants["full_vertical_burst"]:
                self.full_stage = "downpour"
        elif self.full_stage == "downpour":
            self.s.rain_intensity = min(self.constants["full_downpour_intensity"], self.s.rain_intensity + 5.0)
            self.s.lightning_frequency = max(self.s.lightning_frequency, 4.0 + random.random())
            self.s.wind_speed = min(40.0, self.s.wind_speed + 2.0)
            self.s.turbulence += 3.5
            if self.s.rain_intensity >= self.constants["full_downpour_intensity"] and self.s.turbulence >= 10.0:
                self.full_stage = "frenzy"
        elif self.full_stage == "frenzy":
            self.s.lightning_frequency = min(self.constants["full_frenzy_frequency"], self.s.lightning_frequency + random.uniform(1.5, 3.0))
            self.s.turbulence = min(self.constants["full_turbulence_peak"], self.s.turbulence + 4.2)
            self.s.rain_particle_density = min(self.constants["full_particle_density_peak"], self.s.rain_particle_density + 9.0)
            self.s.rain_intensity = min(80.0, self.s.rain_intensity + 4.0)
            if self.s.lightning_frequency >= self.constants["full_frenzy_frequency"] and self.s.turbulence >= 24.0:
                self.full_stage = "chaos"
        elif self.full_stage == "chaos":
            self.s.turbulence = min(self.constants["full_turbulence_peak"], self.s.turbulence + 2.0)
            self.s.rain_particle_density = min(self.constants["full_particle_density_peak"], self.s.rain_particle_density + 4.0)
            self.s.wind_speed = min(50.0, self.s.wind_speed + 1.5)
            self.s.lightning_frequency = max(self.s.lightning_frequency, 10.0 + random.uniform(0.0, 2.5))
            if self.s.turbulence >= self.constants["full_turbulence_peak"] and self.s.rain_particle_density >= self.constants["full_particle_density_peak"]:
                self.full_stage = "silence"
        elif self.full_stage == "silence":
            self.s.rain_intensity = max(0.0, self.s.rain_intensity - self.constants["silence_decay"])
            self.s.wind_speed = max(0.0, self.s.wind_speed - self.constants["silence_decay"])
            self.s.turbulence = max(0.0, self.s.turbulence - self.constants["silence_decay"])
            self.s.lightning_frequency = max(0.0, self.s.lightning_frequency - self.constants["silence_decay"])
            self.s.rain_particle_density = max(0.0, self.s.rain_particle_density - self.constants["silence_decay"])
            self.s.downdraft_force = max(0.0, self.s.downdraft_force - self.constants["silence_decay"])
            if all(value <= 0.1 for value in [
                self.s.rain_intensity,
                self.s.wind_speed,
                self.s.turbulence,
                self.s.lightning_frequency,
                self.s.rain_particle_density,
                self.s.downdraft_force,
            ]):
                self.state = Phase.END


if __name__ == "__main__":
    Storm().run()
