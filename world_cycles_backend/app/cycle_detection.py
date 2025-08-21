#!/usr/bin/env python3
"""
Cycle Detection Engine for World Cycles Platform
Implements advanced algorithms for detecting and analyzing global cycles
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import math
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CycleDetectionEngine:
    """Advanced cycle detection and analysis engine"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            deployed_path = Path(__file__).parent.parent / "data"
            local_path = Path("/home/ubuntu/world_cycles_platform/data")
            if deployed_path.exists():
                data_dir = str(deployed_path)
            elif local_path.exists():
                data_dir = str(local_path)
            else:
                data_dir = str(deployed_path)  # Default to deployed path
        self.data_dir = Path(data_dir)
        self.cycle_types = {
            "micro": [20, 25, 30],
            "medium": [50, 52, 56],
            "macro": [100, 120, 156, 160, 180, 250],
            "meta": [500, 1000, 2000, 2500, 5500]
        }
        
        self.vatican_markers = {
            1540: "Jesuit Order Founded",
            1582: "Vatican Observatory & Calendar Reform",
            1773: "Jesuit Suppression",
            1814: "Jesuit Restoration"
        }
        
        self.anchor_year = -586
        
        self.significance_threshold = 1e-89
        
        self.global_datasets = {}
        self.vatican_influence_data = None
        
    def load_global_datasets(self):
        """Load all global civilization datasets including subregions"""
        logger.info("Loading global datasets...")
        
        regions = {
            "americas": ["north_america", "central_america", "south_america"],
            "asia": ["east_asia", "southeast_asia", "western_asia", "south_asia", "central_asia"],
            "europe": ["northern_europe", "southern_europe", "eastern_europe", "western_europe"],
            "africa": ["central_africa", "east_africa", "north_africa", "south_africa", "west_africa"],
            "oceania": ["oceania"], 
            "middle_east": ["middle_east"], 
            "arctic": ["arctic"]
        }
        
        total_subregions = 0
        for region, subregions in regions.items():
            for subregion in subregions:
                if region == "africa":
                    subregion_path = self.data_dir / subregion
                else:
                    subregion_path = self.data_dir / region / subregion
                    
                if subregion_path.exists():
                    if region not in self.global_datasets:
                        self.global_datasets[region] = {}
                    self.global_datasets[region][subregion] = self._load_region_data(subregion_path)
                    total_subregions += 1
        
        vatican_path = self.data_dir / "vatican_analysis" / "vatican_global_influence_timeline.csv"
        if vatican_path.exists():
            self.vatican_influence_data = pd.read_csv(vatican_path)
            
        logger.info(f"Loaded datasets for {len(self.global_datasets)} regions with {total_subregions} subregions")
        
    def _load_region_data(self, region_path: Path) -> pd.DataFrame:
        """Load comprehensive analysis CSV file for a specific subregion"""
        for csv_file in region_path.glob("*comprehensive_analysis*.csv"):
            try:
                df = pd.read_csv(csv_file)
                logger.info(f"Loaded comprehensive analysis from {csv_file}: {len(df)} events")
                return df
            except Exception as e:
                logger.warning(f"Failed to load {csv_file}: {e}")
        
        for csv_file in region_path.glob("*.csv"):
            if csv_file.name.endswith('_summary_report.md'):
                continue
            try:
                df = pd.read_csv(csv_file)
                if len(df) > 10:
                    logger.info(f"Loaded fallback data from {csv_file}: {len(df)} events")
                    return df
            except Exception as e:
                logger.warning(f"Failed to load {csv_file}: {e}")
        
        logger.warning(f"No suitable data files found in {region_path}")
        return pd.DataFrame()
    
    def detect_cycles_in_dataset(self, df: pd.DataFrame, region: str) -> List[Dict[str, Any]]:
        """Detect cycles in a specific dataset"""
        detected_cycles = []
        
        date_column = None
        for col in ['Year', 'Date', 'year', 'date', 'BCE_CE_Year', 'Historical_Year']:
            if col in df.columns:
                date_column = col
                break
        
        if date_column is None:
            df = df.copy()
            df['Year'] = range(-3000, -3000 + len(df))
            date_column = 'Year'
            logger.info(f"Generated synthetic years for {region} dataset")
        
        df_sorted = df.sort_values(date_column)
        years = df_sorted[date_column].values
        
        for cycle_category, cycle_lengths in self.cycle_types.items():
            for cycle_length in cycle_lengths:
                cycle_events = self._find_cycle_events(df_sorted, cycle_length, region)
                if cycle_events:
                    detected_cycles.extend(cycle_events)
        
        return detected_cycles
    
    def _find_cycle_events(self, df: pd.DataFrame, cycle_length: int, region: str) -> List[Dict[str, Any]]:
        """Find events that match a specific cycle length"""
        cycle_events = []
        
        date_column = 'Year'
        for col in ['Year', 'Date', 'year', 'date', 'BCE_CE_Year', 'Historical_Year']:
            if col in df.columns:
                date_column = col
                break
        
        years = df[date_column].values
        
        current_year = 2025
        cycle_points = []
        
        year = self.anchor_year
        while year <= current_year:
            cycle_points.append(year)
            year += cycle_length
        
        year = self.anchor_year - cycle_length
        while year >= -5500:  # 5500 year span
            cycle_points.insert(0, year)
            year -= cycle_length
        
        tolerance = 5
        
        for cycle_point in cycle_points:
            matching_events = df[
                (df[date_column] >= cycle_point - tolerance) & 
                (df[date_column] <= cycle_point + tolerance)
            ]
            
            if not matching_events.empty:
                for _, event in matching_events.iterrows():
                    vatican_influence = self._get_vatican_influence(event['Year'], region)
                    
                    significance = self._calculate_significance(
                        event['Year'], cycle_point, cycle_length, len(years)
                    )
                    
                    safe_vatican_influence = float(vatican_influence) if not (math.isnan(vatican_influence) or math.isinf(vatican_influence)) else 0.0
                    safe_significance = float(significance) if not (math.isnan(significance) or math.isinf(significance)) else 0.0
                    safe_deviation = float(abs(event['Year'] - cycle_point))
                    if math.isnan(safe_deviation) or math.isinf(safe_deviation):
                        safe_deviation = 0.0
                    
                    cycle_event = {
                        "cycle_length": int(cycle_length),
                        "cycle_category": self._get_cycle_category(cycle_length),
                        "predicted_year": int(cycle_point),
                        "actual_year": int(event[date_column]),
                        "deviation": safe_deviation,
                        "event_name": str(event.get('Event_Name', 'Unknown')),
                        "civilization": str(event.get('Civilization', 'Unknown')),
                        "region": str(region),
                        "impact_level": str(event.get('Impact_Level', 'Unknown')),
                        "vatican_influence": safe_vatican_influence,
                        "statistical_significance": safe_significance,
                        "anchor_distance": int(abs(event['Year'] - self.anchor_year)),
                        "post_1582": bool(event['Year'] >= 1582),
                        "astronomical_correlation": self._get_astronomical_correlation(event, region)
                    }
                    
                    cycle_events.append(cycle_event)
        
        return cycle_events
    
    def _get_cycle_category(self, cycle_length: int) -> str:
        """Determine cycle category based on length"""
        for category, lengths in self.cycle_types.items():
            if cycle_length in lengths:
                return category
        return "unknown"
    
    def _get_vatican_influence(self, year: int, region: str) -> float:
        """Get Vatican influence level for a specific year and region"""
        if self.vatican_influence_data is None:
            return 0.0
        
        vatican_data = self.vatican_influence_data[
            (self.vatican_influence_data['Region'] == region.title()) &
            (self.vatican_influence_data['Year'] <= year)
        ]
        
        if vatican_data.empty:
            return 0.0
        
        latest_data = vatican_data.iloc[-1]
        return float(latest_data['Vatican_Influence'])
    
    def _calculate_significance(self, actual_year: int, predicted_year: int, 
                              cycle_length: int, total_events: int) -> float:
        """Calculate statistical significance of cycle match"""
        deviation = abs(actual_year - predicted_year)
        tolerance = 5
        
        random_probability = (2 * tolerance) / cycle_length
        
        adjusted_probability = random_probability * total_events
        
        if adjusted_probability > 0:
            significance = 1 / adjusted_probability
        else:
            significance = float('inf')
        
        return min(significance, 1e90)  # Cap at very high significance
    
    def _get_astronomical_correlation(self, event: pd.Series, region: str = None) -> Dict[str, Any]:
        """Extract astronomical correlation data from event with regional visibility"""
        from .astronomical_visibility import AstronomicalVisibilityEngine
        
        astronomical_data = {}
        visibility_engine = AstronomicalVisibilityEngine()
        
        planets = ['Jupiter_Position', 'Saturn_Position', 'Mars_Position', 
                  'Venus_Position', 'Mercury_Position']
        
        planetary_positions = {}
        for planet in planets:
            if planet in event and pd.notna(event[planet]):
                value = float(event[planet])
                if not (math.isnan(value) or math.isinf(value)):
                    planet_name = planet.replace('_Position', '')
                    planetary_positions[planet_name] = value
                    astronomical_data[planet_name] = value
        
        if 'Primary_Angle_Events' in event and pd.notna(event['Primary_Angle_Events']):
            value = int(event['Primary_Angle_Events'])
            if not math.isnan(value):
                astronomical_data['primary_angles'] = value
        
        if 'Perfect_Alignment' in event and pd.notna(event['Perfect_Alignment']):
            astronomical_data['perfect_alignment'] = bool(event['Perfect_Alignment'])
        
        if 'Enhanced_Score' in event and pd.notna(event['Enhanced_Score']):
            value = float(event['Enhanced_Score'])
            if not (math.isnan(value) or math.isinf(value)):
                astronomical_data['enhanced_score'] = value
        
        if region and planetary_positions and 'Year' in event:
            year = int(event['year'])
            visible_planets = visibility_engine.calculate_planetary_visibility(
                region, year, planetary_positions
            )
            astronomical_data['regional_visibility'] = visible_planets
            astronomical_data['visible_planet_count'] = sum(visible_planets.values())
            
            astronomical_data['regional_influence_factor'] = (
                astronomical_data['visible_planet_count'] / len(planetary_positions)
                if planetary_positions else 0.0
            )
        
        return astronomical_data
    
    def analyze_vatican_patterns(self) -> Dict[str, Any]:
        """Analyze Vatican/Jesuit manipulation patterns across all data"""
        if not self.global_datasets:
            self.load_global_datasets()
        
        vatican_analysis = {
            "pre_1582_accuracy": [],
            "post_1582_accuracy": [],
            "regional_influence": {},
            "cycle_standardization": {},
            "manipulation_events": []
        }
        
        for region, subregions in self.global_datasets.items():
            for subregion, df in subregions.items():
                if 'Year' not in df.columns:
                    continue
                
                pre_1582 = df[df['Year'] < 1582]
                post_1582 = df[df['Year'] >= 1582]
                
                pre_accuracy = self._calculate_cycle_accuracy(pre_1582, region)
                post_accuracy = self._calculate_cycle_accuracy(post_1582, region)
                
                vatican_analysis["pre_1582_accuracy"].append(pre_accuracy)
                vatican_analysis["post_1582_accuracy"].append(post_accuracy)
                
                if region not in vatican_analysis["regional_influence"]:
                    vatican_analysis["regional_influence"][region] = {
                        "pre_1582": pre_accuracy,
                        "post_1582": post_accuracy,
                        "improvement": post_accuracy - pre_accuracy
                    }
        
        pre_1582_mean = float(np.mean(vatican_analysis["pre_1582_accuracy"])) if vatican_analysis["pre_1582_accuracy"] else 0.0
        post_1582_mean = float(np.mean(vatican_analysis["post_1582_accuracy"])) if vatican_analysis["post_1582_accuracy"] else 0.0
        
        vatican_analysis["overall_pre_1582"] = pre_1582_mean if not (math.isnan(pre_1582_mean) or math.isinf(pre_1582_mean)) else 0.0
        vatican_analysis["overall_post_1582"] = post_1582_mean if not (math.isnan(post_1582_mean) or math.isinf(post_1582_mean)) else 0.0
        vatican_analysis["vatican_impact"] = vatican_analysis["overall_post_1582"] - vatican_analysis["overall_pre_1582"]
        
        return vatican_analysis
    
    def _calculate_cycle_accuracy(self, df: pd.DataFrame, region: str) -> float:
        """Calculate cycle prediction accuracy for a dataset"""
        if df.empty:
            return 0.0
        
        total_events = len(df)
        accurate_predictions = 0
        
        for cycle_length in [20, 50, 160, 250, 500]:
            cycle_events = self._find_cycle_events(df, cycle_length, region)
            accurate_predictions += len([e for e in cycle_events if e['deviation'] <= 5])
        
        return accurate_predictions / total_events if total_events > 0 else 0.0
    
    def predict_future_cycles(self, start_year: int = 2025, end_year: int = 2050) -> List[Dict[str, Any]]:
        """Predict future cycle events based on historical patterns"""
        predictions = []
        
        for cycle_category, cycle_lengths in self.cycle_types.items():
            for cycle_length in cycle_lengths:
                year = self.anchor_year
                while year <= end_year:
                    if start_year <= year <= end_year:
                        prediction = {
                            "predicted_year": int(year),
                            "cycle_length": int(cycle_length),
                            "cycle_category": str(cycle_category),
                            "confidence": float(self._calculate_prediction_confidence(cycle_length)),
                            "expected_impact": str(self._predict_impact_level(year, cycle_length)),
                            "vatican_influence": float(self._predict_vatican_influence(year)),
                            "anchor_distance": int(abs(year - self.anchor_year)),
                            "astronomical_window": self._predict_astronomical_window(year)
                        }
                        predictions.append(prediction)
                    
                    year += cycle_length
        
        return sorted(predictions, key=lambda x: x['predicted_year'])
    
    def _calculate_prediction_confidence(self, cycle_length: int) -> float:
        """Calculate confidence level for cycle predictions"""
        base_confidence = 0.7
        length_factor = min(cycle_length / 500, 1.0) * 0.25
        return min(base_confidence + length_factor, 0.98)
    
    def _predict_impact_level(self, year: int, cycle_length: int) -> str:
        """Predict impact level based on cycle characteristics"""
        if cycle_length >= 500:
            return "Catastrophic"
        elif cycle_length >= 160:
            return "Major"
        elif cycle_length >= 50:
            return "Significant"
        else:
            return "Minor"
    
    def _predict_vatican_influence(self, year: int) -> float:
        """Predict Vatican influence level for future years"""
        if year >= 1582:
            return 0.95
        else:
            return 0.1
    
    def _predict_astronomical_window(self, year: int) -> Dict[str, Any]:
        """Predict optimal astronomical timing window"""
        return {
            "optimal_months": ["March", "September"],  # Equinoxes
            "planetary_alignments": "High probability",
            "eclipse_correlation": "Possible"
        }
    
    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive analysis of all global cycles"""
        if not self.global_datasets:
            self.load_global_datasets()
        
        analysis = {
            "global_summary": {
                "total_regions": len(self.global_datasets),
                "total_civilizations": 0,
                "total_events": 0,
                "date_range": {"earliest": float('inf'), "latest": float('-inf')}
            },
            "cycle_detection_results": {},
            "vatican_analysis": self.analyze_vatican_patterns(),
            "statistical_validation": {},
            "future_predictions": self.predict_future_cycles(),
            "regional_breakdown": {}
        }
        
        all_detected_cycles = []
        
        for region, subregions in self.global_datasets.items():
            region_cycles = []
            region_events = 0
            
            for subregion, df in subregions.items():
                if df.empty:
                    continue
                
                analysis["global_summary"]["total_civilizations"] += len(df['Civilization'].unique()) if 'Civilization' in df.columns else 1
                analysis["global_summary"]["total_events"] += len(df)
                region_events += len(df)
                
                if 'Year' in df.columns:
                    min_year = int(df['Year'].min())
                    max_year = int(df['Year'].max())
                    analysis["global_summary"]["date_range"]["earliest"] = min(
                        analysis["global_summary"]["date_range"]["earliest"], min_year
                    )
                    analysis["global_summary"]["date_range"]["latest"] = max(
                        analysis["global_summary"]["date_range"]["latest"], max_year
                    )
                
                cycles = self.detect_cycles_in_dataset(df, region)
                region_cycles.extend(cycles)
                all_detected_cycles.extend(cycles)
            
            cycle_accuracy = 0.0
            if region_cycles:
                significances = [c['statistical_significance'] for c in region_cycles if not (math.isnan(c['statistical_significance']) or math.isinf(c['statistical_significance']))]
                if significances:
                    cycle_accuracy = float(np.mean(significances))
                    if math.isnan(cycle_accuracy) or math.isinf(cycle_accuracy):
                        cycle_accuracy = 0.0
            
            analysis["regional_breakdown"][region] = {
                "total_events": int(region_events),
                "detected_cycles": int(len(region_cycles)),
                "cycle_accuracy": cycle_accuracy
            }
        
        analysis["cycle_detection_results"] = {
            "total_detected_cycles": len(all_detected_cycles),
            "by_category": {},
            "by_length": {},
            "accuracy_metrics": self._calculate_accuracy_metrics(all_detected_cycles)
        }
        
        for cycle in all_detected_cycles:
            category = cycle["cycle_category"]
            length = cycle["cycle_length"]
            
            if category not in analysis["cycle_detection_results"]["by_category"]:
                analysis["cycle_detection_results"]["by_category"][category] = 0
            analysis["cycle_detection_results"]["by_category"][category] += 1
            
            if length not in analysis["cycle_detection_results"]["by_length"]:
                analysis["cycle_detection_results"]["by_length"][length] = 0
            analysis["cycle_detection_results"]["by_length"][length] += 1
        
        return analysis
    
    def _calculate_accuracy_metrics(self, cycles: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate overall accuracy metrics"""
        if not cycles:
            return {"overall_accuracy": 0.0, "average_deviation": 0.0, "average_significance": 0.0, "total_cycles_detected": 0}
        
        deviations = [c['deviation'] for c in cycles if not (math.isnan(c['deviation']) or math.isinf(c['deviation']))]
        significances = [c['statistical_significance'] for c in cycles 
                        if not (math.isnan(c['statistical_significance']) or math.isinf(c['statistical_significance']))]
        
        overall_accuracy = 0.0
        if deviations:
            overall_accuracy = float(len([d for d in deviations if d <= 5]) / len(deviations))
            if math.isnan(overall_accuracy) or math.isinf(overall_accuracy):
                overall_accuracy = 0.0
        
        average_deviation = 0.0
        if deviations:
            average_deviation = float(np.mean(deviations))
            if math.isnan(average_deviation) or math.isinf(average_deviation):
                average_deviation = 0.0
        
        average_significance = 0.0
        if significances:
            average_significance = float(np.mean(significances))
            if math.isnan(average_significance) or math.isinf(average_significance):
                average_significance = 0.0
        
        return {
            "overall_accuracy": overall_accuracy,
            "average_deviation": average_deviation,
            "average_significance": average_significance,
            "total_cycles_detected": int(len(cycles))
        }
    
    def detect_cycles_in_region(self, region: str, subregion: str, start_year: int = -3000, end_year: int = 2025) -> List[Dict[str, Any]]:
        """Detect cycles for a specific region and subregion with date filtering"""
        if region not in self.global_datasets or subregion not in self.global_datasets[region]:
            return []
        
        df = self.global_datasets[region][subregion]
        
        date_column = None
        for col in ['Year', 'Date', 'year', 'date', 'BCE_CE_Year', 'Historical_Year']:
            if col in df.columns:
                date_column = col
                break
        
        if date_column:
            df = df[(df[date_column] >= start_year) & (df[date_column] <= end_year)]
        
        cycles = self.detect_cycles_in_dataset(df, f"{region}_{subregion}")
        
        for cycle in cycles:
            if 'events' in cycle:
                for event in cycle['events']:
                    if 'year' in event:
                        visibility = self.calculate_planetary_visibility_for_year(region, subregion, event['year'])
                        event['planetary_visibility'] = visibility
        
        return cycles

    def analyze_regional_planetary_visibility(self, region: str, subregion: str, start_year: int, end_year: int) -> Dict[str, Any]:
        """Analyze planetary visibility patterns for a region over time"""
        from .astronomical_visibility import AstronomicalVisibilityEngine
        
        visibility_engine = AstronomicalVisibilityEngine()
        
        if region not in self.global_datasets or subregion not in self.global_datasets[region]:
            return {}
        
        df = self.global_datasets[region][subregion]
        
        date_column = None
        for col in ['Year', 'Date', 'year', 'date', 'BCE_CE_Year', 'Historical_Year']:
            if col in df.columns:
                date_column = col
                break
        
        if date_column:
            df = df[(df[date_column] >= start_year) & (df[date_column] <= end_year)]
        
        visibility_analysis = {
            "total_events": len(df),
            "planetary_influence_events": 0,
            "visibility_by_planet": {},
            "high_influence_periods": []
        }
        
        for _, event in df.iterrows():
            if date_column and date_column in event:
                year = int(event['year'])
                planetary_positions = {}
                
                for planet in ['Jupiter_Position', 'Saturn_Position', 'Mars_Position', 'Venus_Position', 'Mercury_Position']:
                    if planet in event and pd.notna(event[planet]):
                        planetary_positions[planet.replace('_Position', '')] = float(event[planet])
                
                if planetary_positions:
                    visible_planets = visibility_engine.calculate_planetary_visibility(subregion, year, planetary_positions)
                    visible_count = sum(visible_planets.values())
                    
                    if visible_count > 0:
                        visibility_analysis["planetary_influence_events"] += 1
                    
                    if visible_count >= 3:
                        visibility_analysis["high_influence_periods"].append({
                            "year": year,
                            "visible_planets": visible_planets,
                            "influence_level": visible_count / len(planetary_positions)
                        })
        
        return visibility_analysis
    
    def calculate_planetary_visibility_for_year(self, region: str, subregion: str, year: int) -> Dict[str, Any]:
        """Calculate planetary visibility for a specific region and year"""
        from .astronomical_visibility import AstronomicalVisibilityEngine
        
        visibility_engine = AstronomicalVisibilityEngine()
        
        if region not in self.global_datasets or subregion not in self.global_datasets[region]:
            return {}
        
        df = self.global_datasets[region][subregion]
        
        date_column = None
        for col in ['Year', 'Date', 'year', 'date', 'BCE_CE_Year', 'Historical_Year']:
            if col in df.columns:
                date_column = col
                break
        
        year_events = df[df[date_column] == year] if date_column else df
        
        if year_events.empty:
            return {}
        
        event = year_events.iloc[0]
        planetary_positions = {}
        
        for planet in ['Jupiter_Position', 'Saturn_Position', 'Mars_Position', 'Venus_Position', 'Mercury_Position']:
            if planet in event and pd.notna(event[planet]):
                planetary_positions[planet.replace('_Position', '')] = float(event[planet])
        
        if planetary_positions:
            visible_planets = visibility_engine.calculate_planetary_visibility(subregion, year, planetary_positions)
            influence_factor = visibility_engine.calculate_regional_influence_factor(subregion, year, planetary_positions)
            
            return {
                "year": year,
                "region": region,
                "subregion": subregion,
                "planetary_positions": planetary_positions,
                "visible_planets": visible_planets,
                "influence_factor": influence_factor,
                "enforcement_level": visibility_engine._calculate_enforcement_level(influence_factor)
            }
        
        return {}
    
    def get_all_regions_and_subregions(self) -> Dict[str, List[str]]:
        """Get all available regions and their subregions"""
        regions_map = {}
        for region, subregions in self.global_datasets.items():
            if isinstance(subregions, dict):
                regions_map[region] = list(subregions.keys())
            else:
                regions_map[region] = [region]
        return regions_map
    
    def generate_timeline_data(self, region: str, subregion: str, start_year: int, end_year: int, astrological_cycles: List[int]) -> Dict[str, Any]:
        """Generate timeline visualization data with convergence detection"""
        timeline_data = {
            "cycles": {},
            "convergence_points": [],
            "phase_transitions": [],
            "catastrophic_resets": []
        }
        
        for cycle_length in astrological_cycles:
            cycle_points = []
            year = self.anchor_year
            
            while year <= end_year:
                if year >= start_year:
                    cycle_points.append({
                        "year": year,
                        "cycle_length": cycle_length,
                        "category": self._get_cycle_category(cycle_length),
                        "vatican_influence": self._get_vatican_influence(year, region),
                        "phase": self._determine_phase(year, cycle_length)
                    })
                year += cycle_length
            
            year = self.anchor_year - cycle_length
            while year >= start_year:
                if year <= end_year:
                    cycle_points.insert(0, {
                        "year": year,
                        "cycle_length": cycle_length,
                        "category": self._get_cycle_category(cycle_length),
                        "vatican_influence": self._get_vatican_influence(year, region),
                        "phase": self._determine_phase(year, cycle_length)
                    })
                year -= cycle_length
            
            timeline_data["cycles"][cycle_length] = cycle_points
        
        # Detect convergence points (where multiple cycles meet within tolerance)
        timeline_data["convergence_points"] = self._detect_convergence_points(
            timeline_data["cycles"], tolerance=10
        )
        
        timeline_data["catastrophic_resets"] = self._identify_catastrophic_resets(
            timeline_data["convergence_points"]
        )
        
        timeline_data["phase_transitions"] = self._determine_phase_transitions(
            timeline_data["cycles"]
        )
        
        return timeline_data
    
    def _determine_phase(self, year: int, cycle_length: int) -> str:
        """Determine phase: Homeostatic, Critical, or Catastrophic"""
        cycle_position = (year - self.anchor_year) % cycle_length
        cycle_progress = cycle_position / cycle_length
        
        if cycle_progress < 0.3:
            return "Homeostatic"
        elif cycle_progress < 0.8:
            return "Critical"
        else:
            return "Catastrophic"
    
    def _detect_convergence_points(self, cycles_data: Dict[int, List], tolerance: int = 10) -> List[Dict]:
        """Detect points where multiple cycles converge"""
        convergence_points = []
        all_points = []
        
        for cycle_length, points in cycles_data.items():
            for point in points:
                all_points.append((point["year"], cycle_length, point))
        
        all_points.sort(key=lambda x: x[0])
        
        i = 0
        while i < len(all_points):
            current_year = all_points[i][0]
            converging_cycles = [all_points[i]]
            
            j = i + 1
            while j < len(all_points) and all_points[j][0] <= current_year + tolerance:
                if abs(all_points[j][0] - current_year) <= tolerance:
                    converging_cycles.append(all_points[j])
                j += 1
            
            if len(converging_cycles) >= 2:
                convergence_points.append({
                    "year": current_year,
                    "converging_cycles": [c[1] for c in converging_cycles],
                    "cycle_count": len(converging_cycles),
                    "intensity": len(converging_cycles) / len(cycles_data),
                    "is_catastrophic": len(converging_cycles) >= 4
                })
            
            i = j if j > i + 1 else i + 1
        
        return convergence_points
    
    def _identify_catastrophic_resets(self, convergence_points: List[Dict]) -> List[Dict]:
        """Identify major catastrophic reset points"""
        return [cp for cp in convergence_points if cp["is_catastrophic"]]
    
    def _determine_phase_transitions(self, cycles_data: Dict[int, List]) -> List[Dict]:
        """Determine phase transition points"""
        transitions = []
        for cycle_length, points in cycles_data.items():
            for point in points:
                if point["phase"] == "Catastrophic":
                    transitions.append({
                        "year": point["year"],
                        "cycle_length": cycle_length,
                        "transition_type": "Catastrophic",
                        "vatican_influence": point["vatican_influence"]
                    })
        return transitions
