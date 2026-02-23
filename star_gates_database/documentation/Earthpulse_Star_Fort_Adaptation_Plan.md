# Earthpulse Star Fort Adaptation Plan

## Overview

This document outlines how to adapt the Earthpulse engines (CMYK Earth + RGB Space) to analyze 215 star fort locations with real empirical data.

---

## Input Requirements

### Star Fort Location Data Format

```typescript
interface StarFortLocation {
  id: number;
  name: string;
  latitude: number;   // Decimal degrees (-90 to 90)
  longitude: number;  // Decimal degrees (-180 to 180)
  country?: string;
  type?: string;
  notes?: string;
}
```

**Example Input:**
```csv
id,name,latitude,longitude,country
1,Fort Bourtange,53.0063,7.1906,Netherlands
2,Palmanova,45.9061,13.3103,Italy
3,Naarden,52.2956,5.1622,Netherlands
...
```

---

## Output Format

### Per-Location Output (24 Variables)

```typescript
interface StarFortAnalysisResult {
  // Location info
  fortId: number;
  fortName: string;
  latitude: number;
  longitude: number;
  analysisTimestamp: Date;
  
  // EARTH ENGINE (CMYK) - 12 variables
  earth: {
    cyan: number;              // Seismic resonance (0-1)
    magenta: number;           // EMF resonance (0-1)
    yellow: number;            // Atmospheric resonance (0-1)
    black: number;             // Stress concentration (0-1)
    earthResonance: number;    // Combined (0-1)
    activeLayer: string;       // Earth layer name
    layerFrequency: number;    // Hz
    layerDepth: number;        // km (default 10)
    tectonicZone: string | null;
    tectonicAmplification: number;
    isDeepSubduction: boolean;
    pWaveVelocity: number;     // km/s
  };
  
  // SPACE ENGINE (RGB) - 12 variables
  space: {
    red: number;               // Solar resonance (0-1)
    green: number;             // Geomagnetic resonance (0-1)
    blue: number;              // Ionospheric resonance (0-1)
    spaceResonance: number;    // Combined (0-1)
    angleOfIncidence: number;  // degrees
    ionosphericHeight: number; // km
    solarDeclination: number;  // degrees
    solarElevation: number;    // degrees
    hourAngle: number;         // degrees
    lagTimeHours: number;      // hours
    solarFluxFactor: number;   // 0-1
    solarCyclePhase: number;   // 0-1
  };
  
  // Combined resonance overlay
  resonanceOverlay: {
    combinedResonance: number;
    phaseAlignment: number;
    interferenceFactor: number;
  };
}
```

---

## Processing Workflow

### Step 1: Data Preparation

```python
# Load 215 star fort locations
star_forts = load_csv('/path/to/star_forts.csv')

# Validate coordinates
for fort in star_forts:
    assert -90 <= fort.latitude <= 90
    assert -180 <= fort.longitude <= 180
```

### Step 2: Fetch Real-Time Data (Once)

```typescript
// Fetch current space weather (shared for all locations)
const spaceWeather = await spaceWeatherService.fetchCurrent();
// Returns: solarFlux, kpIndex, dstIndex, solarWindSpeed

// This data is fresh for ~5 minutes
// All 215 locations can use the same space weather data
```

### Step 3: Process Each Location

```typescript
for (const fort of starForts) {
  // Fetch USGS earthquake data for this location (last 30 days)
  const earthquakes = await usgsService.fetchHistorical(
    thirtyDaysAgo,
    now,
    fort.latitude,
    fort.longitude,
    500 // km radius
  );
  
  // Calculate CMYK Earth resonance
  const earthResult = cmykEarthEngine.calculate(
    fort.latitude,
    fort.longitude,
    10, // default depth
    { recentEarthquakes: earthquakes }
  );
  
  // Calculate RGB Space resonance
  const spaceResult = rgbSpaceEngine.calculate(
    fort.latitude,
    fort.longitude,
    new Date(),
    spaceWeather.summary
  );
  
  // Calculate resonance overlay
  const overlay = resonanceOverlayEngine.calculate(
    fort.latitude,
    fort.longitude,
    new Date(),
    spaceWeather.summary,
    { recentEarthquakes: earthquakes }
  );
  
  results.push({ fort, earthResult, spaceResult, overlay });
}
```

### Step 4: Output Generation

```typescript
// Export to CSV
const csv = results.map(r => ({
  id: r.fort.id,
  name: r.fort.name,
  latitude: r.fort.latitude,
  longitude: r.fort.longitude,
  // Earth variables
  cyan: r.earthResult.cyan,
  magenta: r.earthResult.magenta,
  yellow: r.earthResult.yellow,
  black: r.earthResult.black,
  earthResonance: r.earthResult.earthResonance,
  tectonicZone: r.earthResult.tectonicZone,
  // Space variables
  red: r.spaceResult.red,
  green: r.spaceResult.green,
  blue: r.spaceResult.blue,
  spaceResonance: r.spaceResult.spaceResonance,
  lagTimeHours: r.spaceResult.lagTimeHours,
  // Combined
  combinedResonance: r.overlay.combinedResonance
}));

exportToCsv(csv, 'star_fort_analysis.csv');
```

---

## Code Modifications Required

### 1. Create Batch Processing Module

**New file:** `lib/engines/batch-analysis.ts`

```typescript
import { cmykEarthEngine } from './cmyk-earth-engine';
import { rgbSpaceEngine } from './rgb-space-engine';
import { usgsEarthquakeService } from '../services/usgs-earthquake-service';
import { spaceWeatherService } from '../services/space-weather-service';

export async function analyzeStarForts(
  locations: Array<{id: number; name: string; lat: number; lng: number}>
): Promise<StarFortAnalysisResult[]> {
  
  // 1. Fetch shared space weather data
  const spaceWeather = await spaceWeatherService.fetchCurrent();
  
  // 2. Process each location
  const results: StarFortAnalysisResult[] = [];
  
  for (const loc of locations) {
    // Rate limit: 1 request per second to USGS
    await delay(1000);
    
    // Fetch local seismic data
    const seismicData = await usgsEarthquakeService.fetchHistorical(
      thirtyDaysAgo(),
      new Date(),
      loc.lat,
      loc.lng,
      500
    );
    
    // Calculate both engines
    const earth = cmykEarthEngine.calculate(
      loc.lat, loc.lng, 10,
      { recentEarthquakes: seismicData.earthquakes }
    );
    
    const space = rgbSpaceEngine.calculate(
      loc.lat, loc.lng, new Date(),
      spaceWeather.summary
    );
    
    results.push({
      fortId: loc.id,
      fortName: loc.name,
      latitude: loc.lat,
      longitude: loc.lng,
      analysisTimestamp: new Date(),
      earth,
      space,
      resonanceOverlay: calculateOverlay(earth, space)
    });
    
    console.log(`Processed ${loc.name} (${results.length}/${locations.length})`);
  }
  
  return results;
}
```

### 2. API Endpoint for Batch Analysis

**New file:** `app/api/analyze/star-forts/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { analyzeStarForts } from '@/lib/engines/batch-analysis';

export async function POST(request: NextRequest) {
  const { locations } = await request.json();
  
  if (!locations || !Array.isArray(locations)) {
    return NextResponse.json({ error: 'Invalid locations array' }, { status: 400 });
  }
  
  const results = await analyzeStarForts(locations);
  
  return NextResponse.json({
    success: true,
    count: results.length,
    timestamp: new Date().toISOString(),
    results
  });
}
```

---

## Estimated Processing Time

| Factor | Value |
|--------|-------|
| Locations | 215 |
| USGS API delay | 1 second per location |
| Engine calculations | ~10ms per location |
| **Total estimated time** | **~4-5 minutes** |

*Note: The 1-second delay is a conservative rate limit to respect USGS API guidelines.*

---

## Limitations and Constraints

### API Limitations

| API | Limitation | Mitigation |
|-----|------------|------------|
| USGS | 2-year historical max | Use recent data for live analysis |
| USGS | ~20,000 events per query max | Use location radius to limit |
| NOAA | 7-day plasma data | Sufficient for current analysis |

### Excluded Data

The following is **explicitly excluded** from star fort analysis:

- ❌ **Volcanic Cavity Engine** - Not applicable to star forts (no magma chambers)
- ❌ **Cavern Resonance Data** - Star forts are surface structures
- ❌ **Synthetic/Simulated Data** - All data is real empirical measurements

### Geographic Coverage

| Region | Coverage |
|--------|----------|
| Europe | Full USGS/NOAA coverage ✅ |
| Americas | Full USGS/NOAA coverage ✅ |
| Asia | Full USGS/NOAA coverage ✅ |
| Africa | Full USGS/NOAA coverage ✅ |
| Oceania | Full USGS/NOAA coverage ✅ |

---

## Implementation Checklist

- [ ] Create `batch-analysis.ts` module
- [ ] Add CSV input parser for star fort locations
- [ ] Create API endpoint for batch processing
- [ ] Add progress reporting
- [ ] Create CSV export function
- [ ] Add error handling for API failures
- [ ] Test with sample of 10 locations
- [ ] Run full 215-location analysis
- [ ] Generate final report

---

## Sample Script Usage

```bash
# Install dependencies (if not already)
cd /home/ubuntu/earthpulse_engines/extracted
yarn install

# Run star fort analysis
npx ts-node scripts/analyze-star-forts.ts \
  --input /path/to/star_forts.csv \
  --output /home/ubuntu/star_fort_results.csv
```

---

*Adaptation Plan Version: 1.0*
*Date: February 23, 2026*
