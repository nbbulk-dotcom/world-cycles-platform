# Earthpulse Engines - All 24 Variables Documentation

## Overview

The Earthpulse system uses two complementary engines that together produce 24 primary variables for geophysical analysis:
- **CMYK Earth Engine** - 12 Earth-based variables
- **RGB Space Engine** - 12 Space-based variables

Both engines use **ONLY real empirical data** from verified government and scientific sources.

---

## CMYK Earth Engine (12 Variables)

The Earth engine calculates resonance factors using tetrahedral geometry and real seismic/geomagnetic data.

### Primary Component Variables (0-1 normalized)

| # | Variable | Data Source | Description | Units |
|---|----------|-------------|-------------|-------|
| 1 | **cyan** | USGS Seismic Data | Seismic resonance factor - P/S wave velocity, depth attenuation, layer resonance | 0-1 |
| 2 | **magenta** | Geomagnetic Models | EMF resonance factor - electromagnetic anomalies, magnetic variations, telluric currents | 0-1 |
| 3 | **yellow** | NOAA Atmospheric | Atmospheric resonance - pressure coupling, Schumann resonance amplitude | 0-1 |
| 4 | **black** | Tectonic Stress Models | Stress concentration - tectonic strain accumulation, fault proximity | 0-1 |

### Derived Variables

| # | Variable | Calculation | Description | Units |
|---|----------|-------------|-------------|-------|
| 5 | **earthResonance** | Tetrahedral projection | Combined CMYK resonance (vector magnitude) | 0-1 |
| 6 | **activeLayer** | Depth lookup | Earth layer name (surface, crust, mantle, core) | string |
| 7 | **layerFrequency** | PREM Model | Resonance frequency for the depth layer | Hz |
| 8 | **layerDepth** | Input parameter | Depth being analyzed | km |
| 9 | **tectonicZone** | Geographic lookup | Tectonic zone classification (Ring of Fire, Mediterranean-Alpine, etc.) | string |
| 10 | **tectonicAmplification** | Zone-based | Amplification factor for the tectonic zone | 1.0-1.8 |
| 11 | **isDeepSubduction** | Geographic lookup | Whether location is in a deep subduction zone | boolean |
| 12 | **pWaveVelocity** | PREM Model | P-wave seismic velocity at depth | km/s |

### Additional Detail Variables (bonus)

| Variable | Data Source | Description | Units |
|----------|-------------|-------------|-------|
| sWaveVelocity | PREM Model | S-wave velocity at depth | km/s |
| depthAttenuation | Physics formula | Exponential attenuation with depth | 0-1 |
| magneticAnomaly | Geomagnetic Model | Magnetic field anomaly at location | 0-1 |
| schumannAmplitude | Schumann Constants | Schumann resonance amplitude | 0-1 |
| stressAccumulation | Historical Seismic | Accumulated tectonic stress | 0-1 |

---

## RGB Space Engine (12 Variables)

The Space engine calculates resonance factors from the 85km ionospheric viewpoint using real space weather data.

### Primary Component Variables (0-1 normalized)

| # | Variable | Data Source | Description | Units |
|---|----------|-------------|-------------|-------|
| 1 | **red** | NOAA SWPC | Solar resonance - F10.7 flux, solar wind, cycle phase | 0-1 |
| 2 | **green** | NOAA SWPC | Geomagnetic resonance - Kp/Dst indices, field strength | 0-1 |
| 3 | **blue** | Ionospheric Models | Ionospheric coupling - electron density, Schumann coupling | 0-1 |

### Derived Variables

| # | Variable | Calculation | Description | Units |
|---|----------|-------------|-------------|-------|
| 4 | **spaceResonance** | Tetrahedral projection | Combined RGB resonance (vector magnitude) | 0-1 |
| 5 | **angleOfIncidence** | Solar geometry | Angle from vertical at 85km observation point | degrees |
| 6 | **ionosphericHeight** | Latitude-based | Height of D-region ionosphere at location | km (80-85) |
| 7 | **solarDeclination** | Astronomical | Solar declination angle | degrees |
| 8 | **solarElevation** | Astronomical | Solar elevation above horizon | degrees |
| 9 | **hourAngle** | Time-based | Solar hour angle at location | degrees |
| 10 | **lagTimeHours** | Angle calculation | Prediction lag time from ionospheric viewpoint | hours |
| 11 | **solarFluxFactor** | NOAA F10.7 | Normalized solar flux factor | 0-1 |
| 12 | **solarCyclePhase** | Date calculation | Position in 11-year solar cycle | 0-1 |

### Additional Detail Variables (bonus)

| Variable | Data Source | Description | Units |
|----------|-------------|-------------|-------|
| geomagneticStrength | Magnetic Model | Geomagnetic field strength at magnetic latitude | 0-1 |
| magneticLatitude | Geographic calc | Magnetic latitude (differs from geographic) | degrees |
| ionosphericDensity | Chapman function | Electron density in D-region | 0-1 |
| schumannCoupling | Lightning proximity | Coupling to Schumann resonance | 0-1 |

---

## Complete 24-Variable Summary Table

### Earth-Based (CMYK Engine)

| # | Variable Name | Source Type | Data Source |
|---|---------------|-------------|-------------|
| E1 | cyan | Real Data | USGS Earthquake Data |
| E2 | magenta | Model + Data | Geomagnetic Field Models |
| E3 | yellow | Real Data | NOAA Atmospheric Data |
| E4 | black | Calculated | Tectonic Stress Models |
| E5 | earthResonance | Calculated | Tetrahedral Math |
| E6 | activeLayer | Model | PREM Earth Model |
| E7 | layerFrequency | Model | Earth Resonance Layers |
| E8 | layerDepth | Input | User-specified |
| E9 | tectonicZone | Database | Tectonic Zone Lookup |
| E10 | tectonicAmplification | Database | Zone Amplification Factors |
| E11 | isDeepSubduction | Database | Subduction Zone Lookup |
| E12 | pWaveVelocity | Model | PREM Velocity Model |

### Space-Based (RGB Engine)

| # | Variable Name | Source Type | Data Source |
|---|---------------|-------------|-------------|
| S1 | red | Real Data | NOAA SWPC Solar Data |
| S2 | green | Real Data | NOAA SWPC Geomagnetic |
| S3 | blue | Model + Data | Ionospheric Models |
| S4 | spaceResonance | Calculated | Tetrahedral Math |
| S5 | angleOfIncidence | Calculated | Solar Geometry |
| S6 | ionosphericHeight | Model | Ionosphere Height Model |
| S7 | solarDeclination | Astronomical | Solar Position Calc |
| S8 | solarElevation | Astronomical | Solar Position Calc |
| S9 | hourAngle | Astronomical | Time-based Calc |
| S10 | lagTimeHours | Calculated | Angle-based Prediction |
| S11 | solarFluxFactor | Real Data | NOAA F10.7 Index |
| S12 | solarCyclePhase | Calculated | Solar Cycle Position |

---

## Tetrahedral Angle Constants

### RGB (Space) Projection Angles
- **Red (Solar)**: 26.565°
- **Green (Geomagnetic)**: 54.74° (arctan(√2))
- **Blue (Ionospheric)**: 70.53°

### CMYK (Earth) Projection Angles
- **Cyan (Seismic)**: 19.47°
- **Magenta (EMF)**: 35.26°
- **Yellow (Atmospheric)**: 54.74°
- **Black (Stress)**: 70.53°

---

## Data Freshness

| Data Type | Update Frequency | Source |
|-----------|------------------|--------|
| Solar Wind | Real-time (1 min) | NOAA SWPC |
| Kp Index | 3-hourly | NOAA SWPC |
| Solar Flux (F10.7) | 3x daily | NOAA SWPC |
| Earthquake Data | Real-time | USGS FDSNWS |
| Geomagnetic Models | Static reference | IGRF/WMM |
| Tectonic Zones | Static reference | Scientific literature |

---

*Generated: February 23, 2026*
*Plebeian Tribunal Academy - EARTHPULSE v4.0*
