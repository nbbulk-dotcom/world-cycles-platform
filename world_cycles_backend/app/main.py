from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import json
import logging
import pandas as pd
from datetime import datetime

from .cycle_detection import CycleDetectionEngine
from .tetrahedron_analysis import TetrahedronAnalysis

logger = logging.getLogger(__name__)

app = FastAPI(
    title="World Cycles Platform API",
    description="Comprehensive predictive world cycles analysis platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cycle_engine = CycleDetectionEngine()
tetrahedron_engine = TetrahedronAnalysis()

@app.on_event("startup")
async def startup_event():
    """Load datasets on startup"""
    cycle_engine.load_global_datasets()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {
        "message": "World Cycles Platform API",
        "version": "1.0.0",
        "description": "Analyzing global cycles across all civilizations",
        "vatican_analysis": "Exposing 1582 observatory establishment impact",
        "anchor_year": -586,
        "statistical_significance": "P < 1 × 10^-89"
    }

@app.get("/api/regions")
def get_regions():
    """Get all available regions and subregions"""
    regions_map = cycle_engine.get_all_regions_and_subregions()
    all_regions = list(regions_map.keys())
    total_subregions = sum(len(subregions) for subregions in regions_map.values())
    
    return {
        "regions": all_regions,
        "regions_map": regions_map,
        "total_regions": len(all_regions),
        "total_subregions": total_subregions,
        "vatican_analysis_available": cycle_engine.vatican_influence_data is not None
    }

@app.get("/api/cycles/detect/{region}")
def detect_cycles_by_region(region: str):
    """Detect cycles for a specific region"""
    if region not in cycle_engine.global_datasets:
        raise HTTPException(status_code=404, detail=f"Region {region} not found")
    
    all_cycles = []
    for subregion, df in cycle_engine.global_datasets[region].items():
        cycles = cycle_engine.detect_cycles_in_dataset(df, region)
        all_cycles.extend(cycles)
    
    return {
        "region": region,
        "total_cycles_detected": len(all_cycles),
        "cycles": all_cycles
    }

@app.get("/api/status")
def get_api_status():
    """Get API status and platform information"""
    regions_map = cycle_engine.get_all_regions_and_subregions()
    total_regions = len(regions_map)
    total_subregions = sum(len(subregions) for subregions in regions_map.values())
    
    return {
        "status": "operational",
        "version": "1.0.0",
        "total_regions": total_regions,
        "total_subregions": total_subregions,
        "vatican_analysis_available": cycle_engine.vatican_influence_data is not None,
        "anchor_year": cycle_engine.anchor_year,
        "statistical_significance": "P < 1 × 10^-89"
    }

@app.get("/api/global/analysis")
def get_global_analysis():
    """Get comprehensive global cycle analysis"""
    analysis = cycle_engine.generate_comprehensive_analysis()
    return analysis

@app.get("/api/cycles/global")
def get_global_cycle_analysis():
    """Get comprehensive global cycle analysis"""
    analysis = cycle_engine.generate_comprehensive_analysis()
    return analysis

@app.get("/api/vatican/analysis")
def get_vatican_analysis():
    """Get Vatican/Jesuit manipulation pattern analysis"""
    vatican_analysis = cycle_engine.analyze_vatican_patterns()
    return {
        "analysis": vatican_analysis,
        "key_dates": cycle_engine.vatican_markers,
        "anchor_year": cycle_engine.anchor_year,
        "observatory_establishment": 1582,
        "global_impact": "Ancient astronomical manipulation went global post-1582"
    }

@app.get("/api/predictions/future")
def get_future_predictions(
    start_year: int = Query(2025, description="Start year for predictions"),
    end_year: int = Query(2050, description="End year for predictions")
):
    """Get future cycle predictions"""
    if start_year >= end_year or end_year > 2100:
        raise HTTPException(status_code=400, detail="Invalid year range")
    
    predictions = cycle_engine.predict_future_cycles(start_year, end_year)
    return {
        "prediction_period": f"{start_year}-{end_year}",
        "total_predictions": len(predictions),
        "predictions": predictions,
        "methodology": "Based on 586 BCE anchor point and Vatican post-1582 patterns"
    }

@app.get("/api/cycles/by-length/{cycle_length}")
def get_cycles_by_length(cycle_length: int):
    """Get all cycles of a specific length across all regions"""
    if cycle_length not in [20, 25, 30, 50, 52, 56, 100, 120, 156, 160, 180, 250, 500, 1000, 2000, 2500, 5500]:
        raise HTTPException(status_code=400, detail="Invalid cycle length")
    
    all_cycles = []
    for region, subregions in cycle_engine.global_datasets.items():
        for subregion, df in subregions.items():
            cycles = cycle_engine.detect_cycles_in_dataset(df, region)
            matching_cycles = [c for c in cycles if c['cycle_length'] == cycle_length]
            all_cycles.extend(matching_cycles)
    
    return {
        "cycle_length": cycle_length,
        "cycle_category": cycle_engine._get_cycle_category(cycle_length),
        "total_matches": len(all_cycles),
        "cycles": all_cycles
    }

@app.get("/api/civilizations/{civilization}")
def get_civilization_data(civilization: str):
    """Get data for a specific civilization"""
    civilization_data = []
    
    for region, subregions in cycle_engine.global_datasets.items():
        for subregion, df in subregions.items():
            if 'Civilization' in df.columns:
                civ_data = df[df['Civilization'].str.contains(civilization, case=False, na=False)]
                if not civ_data.empty:
                    cycles = cycle_engine.detect_cycles_in_dataset(civ_data, region)
                    civilization_data.extend(cycles)
    
    if not civilization_data:
        raise HTTPException(status_code=404, detail=f"Civilization {civilization} not found")
    
    return {
        "civilization": civilization,
        "total_events": len(civilization_data),
        "cycles": civilization_data
    }

@app.get("/api/astronomical/correlations")
def get_astronomical_correlations():
    """Get astronomical correlations across all cycles"""
    correlations = []
    
    for region, subregions in cycle_engine.global_datasets.items():
        for subregion, df in subregions.items():
            cycles = cycle_engine.detect_cycles_in_dataset(df, region)
            for cycle in cycles:
                if cycle['astronomical_correlation']:
                    correlations.append({
                        "year": cycle['actual_year'],
                        "event": cycle['event_name'],
                        "region": cycle['region'],
                        "civilization": cycle['civilization'],
                        "astronomical_data": cycle['astronomical_correlation'],
                        "vatican_influence": cycle['vatican_influence']
                    })
    
    return {
        "total_correlations": len(correlations),
        "correlations": correlations
    }

@app.get("/api/statistics/significance")
def get_statistical_significance():
    """Get overall statistical significance analysis"""
    analysis = cycle_engine.generate_comprehensive_analysis()
    
    return {
        "overall_significance": "P < 1 × 10^-89",
        "accuracy_metrics": analysis["cycle_detection_results"]["accuracy_metrics"],
        "vatican_impact": analysis["vatican_analysis"],
        "anchor_year_validation": cycle_engine.anchor_year,
        "methodology": "236/239 pattern matching framework"
    }

@app.get("/api/search")
def search_events(
    query: str = Query(..., description="Search term"),
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    region: Optional[str] = Query(None, description="Region filter")
):
    """Search for events across all datasets"""
    results = []
    
    for region_name, subregions in cycle_engine.global_datasets.items():
        if region and region.lower() not in region_name.lower():
            continue
            
        for subregion, df in subregions.items():
            if df.empty:
                continue
                
            filtered_df = df
            if start_year is not None and 'Year' in df.columns:
                filtered_df = filtered_df[filtered_df['Year'] >= start_year]
            if end_year is not None and 'Year' in df.columns:
                filtered_df = filtered_df[filtered_df['Year'] <= end_year]
            
            if 'Event_Name' in filtered_df.columns:
                matches = filtered_df[filtered_df['Event_Name'].str.contains(query, case=False, na=False)]
                for _, match in matches.iterrows():
                    results.append({
                        "year": int(match['Year']) if 'Year' in match else None,
                        "event": match['Event_Name'],
                        "civilization": match.get('Civilization', 'Unknown'),
                        "region": region_name,
                        "subregion": subregion,
                        "impact_level": match.get('Impact_Level', 'Unknown')
                    })
    
    return {
        "query": query,
        "total_results": len(results),
        "results": results[:100]  # Limit to first 100 results
    }

@app.get("/api/regional/analysis/{region}/{subregion}")
def get_regional_analysis(region: str, subregion: str, start_year: int = Query(-3000), end_year: int = Query(2025)):
    """Get detailed analysis for a specific region and subregion with date filtering"""
    try:
        cycles = cycle_engine.detect_cycles_in_region(region, subregion, start_year, end_year)
        visibility_analysis = cycle_engine.analyze_regional_planetary_visibility(region, subregion, start_year, end_year)
        
        return {
            "region": region,
            "subregion": subregion,
            "date_range": {"start": start_year, "end": end_year},
            "cycles": cycles,
            "total_cycles": len(cycles),
            "planetary_visibility_analysis": visibility_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/planetary/visibility/{region}/{subregion}")
def get_planetary_visibility(region: str, subregion: str, year: int = Query(...)):
    """Get planetary visibility for a specific region and year"""
    try:
        visibility_data = cycle_engine.calculate_planetary_visibility_for_year(region, subregion, year)
        return visibility_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/timeline/analysis/{region}/{subregion}")
def get_timeline_analysis(
    region: str, 
    subregion: str, 
    start_year: int = Query(-3000), 
    end_year: int = Query(2025)
):
    """Get timeline visualization data with convergence detection for 6 astrological cycles"""
    try:
        astrological_cycles = [20, 50, 160, 250, 500, 2000]
        timeline_data = cycle_engine.generate_timeline_data(
            region, subregion, start_year, end_year, astrological_cycles
        )
        
        return {
            "region": region,
            "subregion": subregion,
            "date_range": {"start": start_year, "end": end_year},
            "timeline_data": timeline_data,
            "astrological_cycles": astrological_cycles,
            "convergence_points": timeline_data.get("convergence_points", []),
            "phase_transitions": timeline_data.get("phase_transitions", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/advanced-mechanical/analysis/{region}/{subregion}")
def get_advanced_mechanical_analysis(
    region: str,
    subregion: str,
    base_offset: int = Query(46664, description="Base offset (skew factor)"),
    window_width: float = Query(0.10, description="Reset window width")
):
    """Get Enhanced Advanced Mechanical Analysis using Tetrahedron RGB-CMYK framework"""
    try:
        if region not in cycle_engine.global_datasets or subregion not in cycle_engine.global_datasets[region]:
            raise HTTPException(status_code=404, detail=f"No data available for {region}/{subregion}")
        
        df = cycle_engine.global_datasets[region][subregion]
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Empty dataset for {region}/{subregion}")
        
        # Convert DataFrame to events list for TetrahedronAnalysis
        events = []
        for _, row in df.iterrows():
            year_col = None
            for col in ['Year', 'year', 'Date', 'date', 'BCE_CE_Year']:
                if col in row and not pd.isna(row[col]):
                    year_col = col
                    break
            
            if year_col:
                try:
                    year = int(float(row[year_col]))
                    events.append({
                        'year': year,
                        'event': str(row.get('Event', row.get('event', 'Unknown Event'))),
                        'religious_influence': float(row.get('religious_influence', 0.5)),
                        'political_impact': float(row.get('political_impact', 0.5)),
                        'economic_impact': float(row.get('economic_impact', 0.5)),
                        'cultural_impact': float(row.get('cultural_impact', 0.5)),
                        'significance': 1.0
                    })
                except (ValueError, TypeError):
                    continue
        
        if not events:
            raise HTTPException(status_code=404, detail=f"No valid events found for {region}/{subregion}")
        
        # Generate comprehensive tetrahedron analysis
        tetrahedron_analysis = tetrahedron_engine.generate_comprehensive_analysis(
            region, subregion, events
        )
        
        return {
            "region": region,
            "subregion": subregion,
            "base_offset": base_offset,
            "window_width": window_width,
            "cycle_periods": tetrahedron_engine.cycle_periods,
            "mathematical_framework": "Phase = ((event_date + 46664) mod period) / period",
            "pattern_consistency": "P < 1 × 10^-89",
            "vatican_observatory_year": 1582,
            **tetrahedron_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in advanced mechanical analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@app.get("/api/events")
async def get_events(
    region: str = Query(None, description="Region filter"),
    civilisation: str = Query(None, description="Civilisation filter"),
    date_start: float = Query(None, description="Start date filter"),
    date_end: float = Query(None, description="End date filter"),
    cycle_bands: str = Query(None, description="Comma-separated cycle periods"),
    limit: int = Query(1000, description="Maximum results"),
    format: str = Query("json", description="Output format (json/csv)")
):
    """Fetch events filtered by region, civilisation, period, cycles, effect type, etc."""
    try:
        cycle_band_list = None
        if cycle_bands:
            cycle_band_list = [int(x.strip()) for x in cycle_bands.split(',')]
        
        events = cycle_engine.get_comprehensive_events(
            region=region,
            civilisation=civilisation,
            date_start=date_start,
            date_end=date_end,
            cycle_bands=cycle_band_list,
            limit=limit
        )
        
        if format == "csv":
            return {"format": "csv", "data": events}
        
        return {"events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cycles")
async def get_cycles(
    region: str = Query(None, description="Region filter"),
    period_filter: str = Query(None, description="Comma-separated periods"),
    format: str = Query("json", description="Output format (json/csv)")
):
    """List/display cycles, period, parent/child, embed relationships"""
    try:
        period_list = None
        if period_filter:
            period_list = [int(x.strip()) for x in period_filter.split(',')]
        
        cycles = cycle_engine.get_comprehensive_cycles(
            region=region,
            period_filter=period_list
        )
        
        if format == "csv":
            return {"format": "csv", "data": cycles}
        
        return {"cycles": cycles, "count": len(cycles)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/convergences")
async def get_convergences(
    region: str = Query(None, description="Region filter"),
    year_start: int = Query(None, description="Start year filter"),
    year_end: int = Query(None, description="End year filter"),
    format: str = Query("json", description="Output format (json/csv)")
):
    """Fetch cycle convergence/overlap points"""
    try:
        convergences = cycle_engine.get_convergence_points(
            region=region,
            year_start=year_start,
            year_end=year_end
        )
        
        if format == "csv":
            return {"format": "csv", "data": convergences}
        
        return {"convergences": convergences, "count": len(convergences)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predictions")
async def get_predictions(
    region: str = Query(None, description="Region filter"),
    date_range: str = Query(None, description="Date range (YYYY-YYYY)"),
    cycle_bands: str = Query(None, description="Comma-separated cycle periods")
):
    """Produce and log forecasts (events, regime shifts, etc.) given filters"""
    try:
        predictions = cycle_engine.generate_cycle_predictions(
            region=region,
            date_range=date_range,
            cycle_bands=cycle_bands
        )
        
        return {"predictions": predictions, "count": len(predictions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sources")
async def get_sources(
    applies_to: str = Query(None, description="Filter by what the source applies to")
):
    """Return references/citations for any data point"""
    try:
        sources = cycle_engine.get_sources_references(applies_to=applies_to)
        return {"sources": sources, "count": len(sources)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/regions/comprehensive")
async def get_regions_comprehensive():
    """Direct lookup endpoint for regions with full hierarchy"""
    try:
        regions = cycle_engine.get_all_regions_comprehensive()
        return {"regions": regions, "count": len(regions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/civilisations")
async def get_civilisations(
    region: str = Query(None, description="Region filter")
):
    """Direct lookup endpoint for civilisations"""
    try:
        civilisations = cycle_engine.get_all_civilisations_comprehensive(region=region)
        return {"civilisations": civilisations, "count": len(civilisations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/effects")
async def get_effects():
    """Direct lookup endpoint for effects/actions"""
    try:
        effects = cycle_engine.get_all_effects_comprehensive()
        return {"effects": effects, "count": len(effects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/astronomical-cycles")
async def get_astronomical_cycles():
    """Get astronomical cycle definitions"""
    try:
        astro_cycles = cycle_engine.get_astronomical_cycles_comprehensive()
        return {"astronomical_cycles": astro_cycles, "count": len(astro_cycles)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system-parameters")
async def get_system_parameters():
    """Get system parameters and configuration"""
    try:
        params = cycle_engine.get_system_parameters_comprehensive()
        return {"parameters": params, "count": len(params)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
