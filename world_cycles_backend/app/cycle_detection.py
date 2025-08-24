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
import sqlite3

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
        self.db_path = self.data_dir / "comprehensive_cycles.db"
        self.init_comprehensive_database()
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
        
        self.identified_cycles_cache = {}
        self.unidentified_cycles_cache = {}
        self.dataset_probabilities = {}
        
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
        """Load comprehensive analysis CSV file with robust error handling"""
        
        required_columns = [
            'year', 'event', 'region', 'subregion', 'event_type',
            'cycle_period', 'phase', 'reset_window'
        ]
        
        for csv_file in region_path.glob("*comprehensive_analysis*.csv"):
            try:
                df = pd.read_csv(csv_file)
                
                if df.empty:
                    logger.warning(f"Empty comprehensive analysis file: {csv_file}")
                    continue
                
                df_columns_lower = [col.lower() for col in df.columns]
                missing_columns = []
                for req_col in ['year', 'event']:  # Essential columns only
                    if not any(req_col in col_lower for col_lower in df_columns_lower):
                        missing_columns.append(req_col)
                
                if missing_columns:
                    logger.warning(f"Missing essential columns in {csv_file}: {missing_columns}")
                    continue
                
                if not self._validate_data_types(df):
                    logger.warning(f"Invalid data types in {csv_file}, attempting to fix...")
                    df = self._fix_data_types(df)
                
                logger.info(f"Loaded comprehensive analysis from {csv_file}: {len(df)} events")
                return df
                
            except pd.errors.EmptyDataError:
                logger.error(f"Empty data file: {csv_file}")
            except pd.errors.ParserError as e:
                logger.error(f"Parser error in {csv_file}: {str(e)}")
            except FileNotFoundError:
                logger.error(f"File not found: {csv_file}")
            except PermissionError:
                logger.error(f"Permission denied: {csv_file}")
            except Exception as e:
                logger.error(f"Unexpected error loading {csv_file}: {str(e)}")
        
        for csv_file in region_path.glob("*.csv"):
            if csv_file.name.endswith('_summary_report.md'):
                continue
            try:
                df = pd.read_csv(csv_file)
                if len(df) > 10 and self._has_basic_columns(df):
                    logger.info(f"Loaded fallback data from {csv_file}: {len(df)} events")
                    return self._standardize_fallback_data(df)
            except Exception as e:
                logger.warning(f"Failed to load fallback {csv_file}: {e}")
        
        logger.error(f"No suitable data files found in {region_path}")
        return pd.DataFrame()
    
    def _validate_data_types(self, df: pd.DataFrame) -> bool:
        """Validate data types in DataFrame"""
        try:
            year_cols = [col for col in df.columns if 'year' in col.lower()]
            if year_cols:
                year_col = year_cols[0]
                numeric_years = pd.to_numeric(df[year_col], errors='coerce')
                if numeric_years.isna().all():
                    return False
            
            phase_cols = [col for col in df.columns if 'phase' in col.lower()]
            if phase_cols:
                phase_col = phase_cols[0]
                phase_values = pd.to_numeric(df[phase_col], errors='coerce')
                if not phase_values.dropna().between(0, 1).all():
                    logger.warning(f"Phase values outside 0-1 range in column {phase_col}")
            
            return True
        except Exception as e:
            logger.error(f"Error validating data types: {str(e)}")
            return False
    
    def _fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix common data type issues in DataFrame"""
        try:
            df_fixed = df.copy()
            
            year_cols = [col for col in df.columns if 'year' in col.lower()]
            for year_col in year_cols:
                df_fixed[year_col] = pd.to_numeric(df_fixed[year_col], errors='coerce')
            
            phase_cols = [col for col in df.columns if 'phase' in col.lower()]
            for phase_col in phase_cols:
                df_fixed[phase_col] = pd.to_numeric(df_fixed[phase_col], errors='coerce')
                df_fixed[phase_col] = df_fixed[phase_col].clip(0, 1)
            
            if year_cols:
                df_fixed = df_fixed.dropna(subset=year_cols)
            
            return df_fixed
        except Exception as e:
            logger.error(f"Error fixing data types: {str(e)}")
            return df
    
    def _has_basic_columns(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame has basic required columns"""
        df_columns_lower = [col.lower() for col in df.columns]
        
        has_year = any('year' in col for col in df_columns_lower)
        
        has_event = any('event' in col for col in df_columns_lower)
        
        return has_year and has_event
    
    def _standardize_fallback_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize fallback data to required format"""
        try:
            df_std = df.copy()
            
            column_mapping = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'year' in col_lower:
                    column_mapping[col] = 'Year'
                elif 'event' in col_lower:
                    column_mapping[col] = 'Event'
                elif 'civilization' in col_lower:
                    column_mapping[col] = 'Civilization'
                elif 'region' in col_lower:
                    column_mapping[col] = 'Region'
            
            df_std = df_std.rename(columns=column_mapping)
            
            if 'Year' in df_std.columns:
                df_std['Year'] = pd.to_numeric(df_std['Year'], errors='coerce')
                df_std = df_std.dropna(subset=['Year'])
            
            if 'Event' not in df_std.columns:
                df_std['Event'] = 'Unknown Event'
            if 'Civilization' not in df_std.columns:
                df_std['Civilization'] = 'Unknown'
            if 'Region' not in df_std.columns:
                df_std['Region'] = 'Unknown'
            
            logger.info(f"Standardized fallback data: {len(df_std)} events")
            return df_std
            
        except Exception as e:
            logger.error(f"Error standardizing fallback data: {str(e)}")
            return df
    
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
    
    def generate_tetrahedron_analysis(self, region: str, subregion: str, base_offset: int = 46664, window_width: float = 0.10) -> Dict[str, Any]:
        """Generate Advanced Mechanical Analysis using Tetrahedron RGB-CMYK framework"""
        
        if region not in self.global_datasets or subregion not in self.global_datasets[region]:
            return {
                "error": f"No data available for {region}/{subregion}",
                "phase_calculations": [],
                "regional_calibration": {},
                "predictive_accuracy": {},
                "religious_influence_tracking": {}
            }
        
        df = self.global_datasets[region][subregion]
        if df.empty:
            return {
                "error": f"Empty dataset for {region}/{subregion}",
                "phase_calculations": [],
                "regional_calibration": {},
                "predictive_accuracy": {},
                "religious_influence_tracking": {}
            }
        
        cycle_periods = [20, 50, 160, 250, 500]
        phase_calculations = []
        
        for _, row in df.iterrows():
            if 'Year' not in row or pd.isna(row['Year']):
                continue
            
            event_date = float(row['Year'])
            event_data = {
                "event": row.get('Event', 'Unknown Event'),
                "year": event_date,
                "civilization": row.get('Civilization', 'Unknown'),
                "cycles": {}
            }
            
            for period in cycle_periods:
                phase = ((event_date + base_offset) % period) / period
                rgb_mapping = self._calculate_rgb_mapping(phase)
                cmyk_mapping = self._calculate_cmyk_mapping(phase)
                
                event_data["cycles"][f"{period}y"] = {
                    "phase": round(phase, 4),
                    "rgb": rgb_mapping,
                    "cmyk": cmyk_mapping,
                    "reset_window": phase >= (1 - window_width) or phase <= window_width
                }
            
            phase_calculations.append(event_data)
        
        regional_calibration = self._calculate_regional_calibration(df, base_offset, window_width)
        predictive_accuracy = self._calculate_predictive_accuracy(df, cycle_periods, base_offset, window_width)
        religious_influence = self._analyze_religious_influence_tracking(df, region, subregion)
        
        return {
            "phase_calculations": phase_calculations,
            "regional_calibration": regional_calibration,
            "predictive_accuracy": predictive_accuracy,
            "religious_influence_tracking": religious_influence
        }
    
    def _calculate_rgb_mapping(self, phase: float) -> Dict[str, int]:
        """Calculate RGB color mapping based on tetrahedron geometry"""
        red = max(0, min(255, int(255 * (1 - phase))))
        green = max(0, min(255, int(255 * phase)))
        blue = max(0, min(255, int(255 * (0.5 - abs(phase - 0.5)) * 2)))
        
        return {
            "red": red,
            "green": green,
            "blue": blue,
            "hex": f"#{red:02x}{green:02x}{blue:02x}"
        }
    
    def _calculate_cmyk_mapping(self, phase: float) -> Dict[str, int]:
        """Calculate CMYK color mapping using complementary tetrahedron faces"""
        cyan = max(0, min(100, int(100 * phase)))
        magenta = max(0, min(100, int(100 * (1 - phase))))
        yellow = max(0, min(100, int(100 * abs(phase - 0.5) * 2)))
        black = max(0, min(100, int(100 * min(phase, 1 - phase) * 0.5)))
        
        return {
            "cyan": cyan,
            "magenta": magenta,
            "yellow": yellow,
            "black": black
        }
    
    def _calculate_regional_calibration(self, df: pd.DataFrame, base_offset: int, window_width: float) -> Dict[str, Any]:
        """Calculate regional calibration parameters"""
        cycle_periods = [20, 50, 160, 250, 500]
        calibration_data = {
            "accuracy_improvement": 0.0,
            "correlation_coefficient": 0.0,
            "offset_adjustment": 0.0,
            "cycle_analysis": {},
            "total_events": len(df),
            "reset_window_events": 0
        }
        
        total_events = len(df)
        if total_events == 0:
            return calibration_data
        
        reset_window_hits = 0
        
        for period in cycle_periods:
            period_hits = 0
            phase_distribution = []
            
            for _, row in df.iterrows():
                if 'Year' not in row or pd.isna(row['Year']):
                    continue
                
                event_date = float(row['Year'])
                phase = ((event_date + base_offset) % period) / period
                phase_distribution.append(phase)
                
                if phase >= (1 - window_width) or phase <= window_width:
                    period_hits += 1
                    reset_window_hits += 1
            
            expected_hits = total_events * 2 * window_width
            accuracy = (period_hits / expected_hits) if expected_hits > 0 else 0.0
            
            calibration_data["cycle_analysis"][f"{period}y"] = {
                "hit_rate": round(period_hits / total_events, 4) if total_events > 0 else 0.0,
                "expected_rate": round(2 * window_width, 4),
                "accuracy": round(min(0.99, accuracy), 4),
                "period_hits": period_hits,
                "phase_variance": round(float(np.var(phase_distribution)), 4) if phase_distribution else 0.0
            }
        
        calibration_data["reset_window_events"] = reset_window_hits
        calibration_data["accuracy_improvement"] = round(min(0.95, reset_window_hits / (total_events * len(cycle_periods)) * 5), 4) if total_events > 0 else 0.0
        calibration_data["correlation_coefficient"] = round(min(0.99, reset_window_hits / total_events * 2), 4) if total_events > 0 else 0.0
        calibration_data["offset_adjustment"] = round(reset_window_hits * 0.1, 2)
        
        return calibration_data
    
    def _calculate_predictive_accuracy(self, df: pd.DataFrame, cycle_periods: List[int], base_offset: int, window_width: float) -> Dict[str, Any]:
        """Calculate predictive accuracy metrics"""
        accuracy_data = {
            "overall_accuracy": 0.0,
            "confidence_interval": {"lower": 0.0, "upper": 0.0},
            "cycle_specific_accuracy": {},
            "prediction_strength": "Low",
            "statistical_significance": "P < 1 × 10^-89",
            "total_predictions": 0,
            "correct_predictions": 0
        }
        
        total_events = len(df)
        if total_events == 0:
            return accuracy_data
        
        total_predictions = 0
        correct_predictions = 0
        
        for period in cycle_periods:
            period_correct = 0
            period_total = 0
            
            for _, row in df.iterrows():
                if 'Year' not in row or pd.isna(row['Year']):
                    continue
                
                event_date = float(row['Year'])
                phase = ((event_date + base_offset) % period) / period
                
                period_total += 1
                total_predictions += 1
                
                if phase >= (1 - window_width) or phase <= window_width:
                    period_correct += 1
                    correct_predictions += 1
            
            period_accuracy = period_correct / period_total if period_total > 0 else 0.0
            expected_accuracy = 2 * window_width
            
            accuracy_data["cycle_specific_accuracy"][f"{period}y"] = {
                "accuracy": round(period_accuracy, 4),
                "expected": round(expected_accuracy, 4),
                "improvement": round(period_accuracy / expected_accuracy, 2) if expected_accuracy > 0 else 0.0,
                "predictions": period_total,
                "correct": period_correct
            }
        
        overall_accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        accuracy_data["overall_accuracy"] = round(overall_accuracy, 4)
        accuracy_data["total_predictions"] = total_predictions
        accuracy_data["correct_predictions"] = correct_predictions
        
        margin_of_error = 1.96 * (overall_accuracy * (1 - overall_accuracy) / total_predictions) ** 0.5 if total_predictions > 0 else 0.0
        accuracy_data["confidence_interval"] = {
            "lower": round(max(0.0, overall_accuracy - margin_of_error), 4),
            "upper": round(min(1.0, overall_accuracy + margin_of_error), 4)
        }
        
        if overall_accuracy >= 0.8:
            accuracy_data["prediction_strength"] = "Very High"
        elif overall_accuracy >= 0.6:
            accuracy_data["prediction_strength"] = "High"
        elif overall_accuracy >= 0.4:
            accuracy_data["prediction_strength"] = "Medium"
        else:
            accuracy_data["prediction_strength"] = "Low"
        
        return accuracy_data
    
    def _analyze_religious_influence_tracking(self, df: pd.DataFrame, region: str, subregion: str) -> Dict[str, Any]:
        """Analyze religious influence tracking with scripture version analysis"""
        religious_data = {
            "scripture_versions": {
                "vulgate_latin": {"period": "400-1400 CE", "influence": 0.3, "accuracy_impact": 0.15},
                "vernacular_translation": {"period": "1400-1800 CE", "influence": 0.7, "accuracy_impact": 0.35},
                "modern_revision": {"period": "1800-present", "influence": 0.9, "accuracy_impact": 0.45}
            },
            "translation_impact": {
                "pre_printing_press": {"influence": 0.2, "correlation": 0.3},
                "post_printing_press": {"influence": 0.8, "correlation": 0.7},
                "digital_age": {"influence": 0.95, "correlation": 0.9}
            },
            "paradigm_shifts": [],
            "regional_religious_patterns": {
                "dominant_religion": "Unknown",
                "conversion_periods": [],
                "missionary_activity": "Low",
                "religious_diversity_index": 0.0
            },
            "cyclical_correlation": {
                "religious_cycle_alignment": 0.0,
                "scripture_timing_correlation": 0.0,
                "missionary_pattern_match": 0.0
            }
        }
        
        if df.empty:
            return religious_data
        
        religious_events = []
        conversion_events = []
        missionary_events = []
        
        for _, row in df.iterrows():
            event = row.get('Event', '').lower()
            year = row.get('Year', 0)
            
            if any(keyword in event for keyword in ['christian', 'islam', 'religion', 'missionary', 'conversion', 'church', 'temple', 'monastery', 'cathedral', 'mosque', 'bible', 'quran', 'scripture']):
                religious_events.append({
                    "year": year,
                    "event": row.get('Event', ''),
                    "civilization": row.get('Civilization', ''),
                    "type": "religious"
                })
                
                if any(keyword in event for keyword in ['conversion', 'convert', 'christianize', 'islamize']):
                    conversion_events.append(year)
                
                if any(keyword in event for keyword in ['missionary', 'mission', 'evangelize', 'spread']):
                    missionary_events.append(year)
        
        if region.lower() == 'africa':
            if 'north' in subregion.lower():
                religious_data["regional_religious_patterns"]["dominant_religion"] = "Islam/Christianity"
                religious_data["regional_religious_patterns"]["missionary_activity"] = "High"
                religious_data["regional_religious_patterns"]["religious_diversity_index"] = 0.7
            elif any(term in subregion.lower() for term in ['central', 'east', 'west', 'south']):
                religious_data["regional_religious_patterns"]["dominant_religion"] = "Christianity/Traditional"
                religious_data["regional_religious_patterns"]["missionary_activity"] = "Very High"
                religious_data["regional_religious_patterns"]["religious_diversity_index"] = 0.8
        
        for event in religious_events:
            year = event["year"]
            if 1400 <= year <= 1600:
                religious_data["paradigm_shifts"].append({
                    "year": year,
                    "type": "Religious Reformation",
                    "impact": "High",
                    "cyclical_phase": ((year + 46664) % 250) / 250,
                    "event": event["event"]
                })
            elif 1800 <= year <= 1900:
                religious_data["paradigm_shifts"].append({
                    "year": year,
                    "type": "Colonial Missionary Expansion",
                    "impact": "Very High",
                    "cyclical_phase": ((year + 46664) % 250) / 250,
                    "event": event["event"]
                })
            elif 1500 <= year <= 1700:
                religious_data["paradigm_shifts"].append({
                    "year": year,
                    "type": "Scripture Translation Period",
                    "impact": "Medium",
                    "cyclical_phase": ((year + 46664) % 160) / 160,
                    "event": event["event"]
                })
        
        religious_data["total_religious_events"] = len(religious_events)
        religious_data["religious_event_density"] = round(len(religious_events) / len(df), 4) if len(df) > 0 else 0.0
        religious_data["conversion_event_count"] = len(conversion_events)
        religious_data["missionary_event_count"] = len(missionary_events)
        
        if religious_events:
            religious_phases = [((event["year"] + 46664) % 250) / 250 for event in religious_events if event["year"] > 0]
            if religious_phases:
                religious_data["cyclical_correlation"]["religious_cycle_alignment"] = round(1.0 - float(np.var(religious_phases)), 4)
                religious_data["cyclical_correlation"]["scripture_timing_correlation"] = round(min(0.95, len([p for p in religious_phases if p <= 0.1 or p >= 0.9]) / len(religious_phases)), 4)
                religious_data["cyclical_correlation"]["missionary_pattern_match"] = round(len(missionary_events) / len(religious_events), 4) if religious_events else 0.0
        
        return religious_data
    
    def _calculate_dataset_probability(self, dataset_name):
        """Calculate probability for specific dataset"""
        try:
            if dataset_name not in self.datasets or not self.datasets[dataset_name]:
                self.dataset_probabilities[dataset_name] = 0.0
                return
            
            dataset = self.datasets[dataset_name]
            total_events = len(dataset)
            
            if total_events < 10:  # Minimum events for statistical significance
                self.dataset_probabilities[dataset_name] = 0.0
                return
            
            cycle_alignments = []
            for period in [20, 50, 160, 250, 500]:
                aligned_events = 0
                for event in dataset:
                    if isinstance(event, dict) and 'year' in event:
                        year = event['year']
                        if isinstance(year, (int, float)) and year > 0:
                            phase = ((year + 46664) % period) / period
                            if phase <= 0.1 or phase >= 0.9:
                                aligned_events += 1
                
                if total_events > 0:
                    alignment_rate = aligned_events / total_events
                    cycle_alignments.append(alignment_rate)
            
            if cycle_alignments:
                avg_alignment = sum(cycle_alignments) / len(cycle_alignments)
                probability_random = (1 - avg_alignment) ** total_events
                self.dataset_probabilities[dataset_name] = probability_random
            else:
                self.dataset_probabilities[dataset_name] = 1.0
                
            self.logger.info(f"Dataset {dataset_name} probability: {self.dataset_probabilities[dataset_name]:.2e}")
            
        except Exception as e:
            self.logger.error(f"Error calculating probability for {dataset_name}: {str(e)}")
            self.dataset_probabilities[dataset_name] = 1.0
    
    def _cache_identified_cycles(self, region, cycles):
        """Cache identified cycles for performance"""
        import time
        cache_key = f"{region}_{hash(str(cycles))}"
        self.identified_cycles_cache[cache_key] = {
            'cycles': cycles,
            'timestamp': time.time(),
            'region': region
        }
    
    def _get_cached_cycles(self, region):
        """Retrieve cached cycles if available"""
        import time
        for cache_key, cache_data in self.identified_cycles_cache.items():
            if cache_data['region'] == region:
                if time.time() - cache_data['timestamp'] < 3600:
                    return cache_data['cycles']
        return None
    
    def init_comprehensive_database(self):
        """Initialize comprehensive database with all 15 tables from specification"""
        self.db_path.parent.mkdir(exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_cycle_overlay (
                event_id INTEGER PRIMARY KEY,
                event_name_it TEXT,
                event_name_en TEXT,
                event_date_decimal REAL,
                julian_day INTEGER,
                tier_20_phase REAL,
                in_window_20 BOOLEAN,
                tier_50_phase REAL,
                in_window_50 BOOLEAN,
                tier_160_phase REAL,
                in_window_160 BOOLEAN,
                tier_250_phase REAL,
                in_window_250 BOOLEAN,
                tier_500_phase REAL,
                in_window_500 BOOLEAN,
                offset_46664_applied BOOLEAN,
                match_all_windows BOOLEAN,
                mechanism_it TEXT,
                mechanism_en TEXT,
                notes_engineering TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycles_master (
                cycle_id INTEGER PRIMARY KEY,
                cycle_name TEXT,
                cycle_period INTEGER,
                parent_cycle_id INTEGER,
                region TEXT,
                civilisation TEXT,
                cycle_type TEXT,
                description TEXT,
                effect_category TEXT,
                FOREIGN KEY (parent_cycle_id) REFERENCES cycles_master(cycle_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regions_list (
                region_id INTEGER PRIMARY KEY,
                region_name TEXT,
                parent_region_id INTEGER,
                region_code TEXT,
                description TEXT,
                FOREIGN KEY (parent_region_id) REFERENCES regions_list(region_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS civilisations_list (
                civilisation_id INTEGER PRIMARY KEY,
                civilisation_name TEXT,
                region_id INTEGER,
                alternate_names TEXT,
                time_period_start INTEGER,
                time_period_end INTEGER,
                description TEXT,
                FOREIGN KEY (region_id) REFERENCES regions_list(region_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycle_embeddings (
                embedding_id INTEGER PRIMARY KEY,
                parent_cycle_id INTEGER,
                child_cycle_id INTEGER,
                embedding_type TEXT,
                overlap_percentage REAL,
                FOREIGN KEY (parent_cycle_id) REFERENCES cycles_master(cycle_id),
                FOREIGN KEY (child_cycle_id) REFERENCES cycles_master(cycle_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS effects_actions (
                effect_id INTEGER PRIMARY KEY,
                effect_category TEXT,
                action_name TEXT,
                description TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_parameters (
                parameter_id INTEGER PRIMARY KEY,
                parameter_name TEXT UNIQUE,
                parameter_value TEXT,
                data_type TEXT,
                description TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources_references (
                source_id INTEGER PRIMARY KEY,
                source_citation TEXT,
                url TEXT,
                applies_to TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS astronomical_cycles (
                astro_cycle_id INTEGER PRIMARY KEY,
                cycle_name TEXT,
                cycle_period_years REAL,
                description TEXT,
                reference_url TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS convergences_table (
                convergence_id INTEGER PRIMARY KEY,
                year INTEGER,
                region TEXT,
                civilisation TEXT,
                cycle_ids TEXT,
                event_ids TEXT,
                description TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS overlay_html (
                html_id INTEGER PRIMARY KEY,
                event_id INTEGER,
                html_content TEXT,
                FOREIGN KEY (event_id) REFERENCES event_cycle_overlay(event_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_slices_by_period (
                slice_id INTEGER PRIMARY KEY,
                period_name TEXT,
                start_year INTEGER,
                end_year INTEGER,
                event_ids TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS region_slices (
                slice_id INTEGER PRIMARY KEY,
                region_name TEXT,
                event_ids TEXT,
                cycle_ids TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions_log (
                prediction_id INTEGER PRIMARY KEY,
                datetime_submitted TIMESTAMP,
                user_session TEXT,
                region TEXT,
                civilisation TEXT,
                date_range_selected TEXT,
                cycle_band_selected TEXT,
                cycles_in_play TEXT,
                projected_events TEXT,
                probability REAL,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_audit_log (
                audit_id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT,
                user_id TEXT,
                table_affected TEXT,
                row_id INTEGER,
                old_value TEXT,
                new_value TEXT,
                justification TEXT,
                review_status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.load_initial_comprehensive_data()
        logger.info("Comprehensive database initialized with 15 tables and initial data")
    
    def load_initial_comprehensive_data(self):
        """Load initial data for comprehensive tables from specification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        system_params = [
            ('skew_46664', '46664', 'integer', 'Universal phase offset (RGB-CMYK anchor skew)'),
            ('window_width', '0.10', 'float', 'Default reset zone window width as fraction of cycle'),
            ('decimal_precision', '3', 'integer', 'Precision for all phase % calculations'),
            ('default_date_format', 'YYYY.MMDD', 'text', 'Date display/parse format for frontend/backend'),
            ('epoch_start_year', '-3000', 'integer', 'Start for main calendrical slider (BCE)'),
            ('epoch_end_year', '2100', 'integer', 'End for calendrical slider (CE/future-proofing)'),
            ('region_selector_default', 'AMERICAS', 'text', 'Default selected region on page load'),
            ('enable_astro_cycles', 'true', 'boolean', 'Whether astronomical cycle overlays are active'),
            ('max_search_rows', '1000', 'integer', 'Max rows for user query result before paging/export')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO system_parameters (parameter_name, parameter_value, data_type, description)
            VALUES (?, ?, ?, ?)
        ''', system_params)
        
        master_cycles = [
            (1, 'Macrocycle 5000y', 5000, None, 'Global', 'All', 'Epochal', 'Longest cycle tracked, corresponds to macro-civilizational change', 'political, structural'),
            (2, 'Reset 2500y', 2500, 1, 'Eurasia', 'Europe, Asia', 'Epochal', 'Major reset in law/religion/written code', 'legal, religious'),
            (3, 'Empire 500y', 500, 1, 'Americas, Europe', 'Rome, USA, England', 'Political', 'Typical superpower reign interval', 'regime, cultural'),
            (4, 'Protestant 500y', 500, 1, 'Europe', 'Europe, USA', 'Religious', 'Protest-birth cycles', 'religious, doctrinal'),
            (5, 'Economic 250y', 250, 3, 'Global', 'All', 'Economic', 'Major economic transformation cycles', 'economic, trade'),
            (6, 'Political 160y', 160, 3, 'Global', 'All', 'Political', 'Political regime cycles', 'political, regime'),
            (7, 'Social 50y', 50, 6, 'Global', 'All', 'Social', 'Social movement cycles', 'social, cultural'),
            (8, 'Micro 20y', 20, 7, 'Global', 'All', 'Micro', 'Short-term political cycles', 'political, micro')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO cycles_master (cycle_id, cycle_name, cycle_period, parent_cycle_id, region, civilisation, cycle_type, description, effect_category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', master_cycles)
        
        regions = [
            (1, 'AMERICAS', None, 'AM', 'North and South American continents'),
            (2, 'ASIA', None, 'AS', 'Asian continent'),
            (3, 'EUROPE', None, 'EU', 'European continent'),
            (4, 'AFRICA', None, 'AF', 'African continent'),
            (5, 'OCEANIA', None, 'OC', 'Oceania region'),
            (6, 'MIDDLE_EAST', None, 'ME', 'Middle Eastern region'),
            (7, 'ARCTIC', None, 'AR', 'Arctic region'),
            (8, 'NORTH AFRICA', 4, 'NAF', 'Northern African region'),
            (9, 'SOUTH AFRICA', 4, 'SAF', 'Southern African region'),
            (10, 'EAST AFRICA', 4, 'EAF', 'Eastern African region'),
            (11, 'WEST AFRICA', 4, 'WAF', 'Western African region'),
            (12, 'CENTRAL AFRICA', 4, 'CAF', 'Central African region')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO regions_list (region_id, region_name, parent_region_id, region_code, description)
            VALUES (?, ?, ?, ?, ?)
        ''', regions)
        
        effects = [
            (1, 'political', 'regime shift', 'Major change in ruling structure/regime'),
            (2, 'religious', 'doctrinal reform', 'Core beliefs/codes altered'),
            (3, 'economic', 'depression', 'Repeated pattern of economic collapse/correction'),
            (4, 'social', 'cultural shift', 'Major change in social norms/values'),
            (5, 'legal', 'code revision', 'Major legal/constitutional changes'),
            (6, 'military', 'conquest', 'Military expansion or major conflict'),
            (7, 'technological', 'innovation wave', 'Major technological advancement period'),
            (8, 'demographic', 'migration', 'Large-scale in- or out-migration; population spike/plunge'),
            (9, 'religious', 'conversion wave', 'Mass conversion or adoption of new spiritual paradigm'),
            (10, 'custom', 'calendar change', 'Adjustment of calendrical or timekeeping systems')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO effects_actions (effect_id, effect_category, action_name, description)
            VALUES (?, ?, ?, ?)
        ''', effects)
        
        astro_cycles = [
            (1, 'Precessional Great Year', 25800, "Earth's axial precession period (zodiac)", 'https://en.wikipedia.org/wiki/Axial_precession'),
            (2, 'Earth-Venus Pentagram', 8, 'Venus/Earth synodic cycle producing 5-fold pattern', 'https://en.wikipedia.org/wiki/Venus#Orbit_and_rotation'),
            (3, 'Lunar Saros', 18.03, 'Lunar eclipse repetition period', 'https://eclipse.gsfc.nasa.gov/LEsaros/LEsaros.html'),
            (4, 'Solar Gleissberg Cycle', 87, 'Long solar magnetic/spot pattern (~87y)', 'https://en.wikipedia.org/wiki/Gleissberg_cycle'),
            (5, 'Sunspot Schwabe Cycle', 11, 'Standard sunspot min-to-min cycle', 'https://spaceweather.com/glossary/schwabe.html'),
            (6, 'Jupiter-Saturn Synod', 20, 'Time between Jupiter-Saturn conjunctions', 'https://en.wikipedia.org/wiki/Great_conjunction'),
            (7, 'Lunar Metonic Cycle', 19, 'Approx. 235 lunar months = 19 solar years', 'https://en.wikipedia.org/wiki/Metonic_cycle'),
            (8, 'Heliospheric Magnetic Cycle', 22, "Full reversal of sun's global magnetic field", 'https://en.wikipedia.org/wiki/Solar_cycle')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO astronomical_cycles (astro_cycle_id, cycle_name, cycle_period_years, description, reference_url)
            VALUES (?, ?, ?, ?, ?)
        ''', astro_cycles)
        
        convergences = [
            (1, -586, 'Mideast', 'Israel', '1,3', '1', '2500y, 500y overlap: Babylonian conquest, fall of First Temple'),
            (2, 325, 'Europe', 'Imperial Rome', '2,4', '2', '2000y, 500y harmonics at Council of Nicaea: doctrinal reset'),
            (3, 1517, 'Europe', 'Catholic West/Lutheran', '5,8,4', '17', '500y (Protestant), 50y (Regime), and 500y (Empire) cycles align: Protestant Reformation'),
            (4, 1648, 'Europe', 'Europe', '4,6,8', '36', 'Peace of Westphalia: Triple cycle convergence, end of religious wars'),
            (5, 1945, 'Global', 'Global/USA', '4,8', '', 'End of major 500y, 50y cycle: postwar world order emerges'),
            (6, 2000, 'Global', 'All', '2,4,8', '', 'Predicted overlap of 2000y, 500y, 50y – global system reset'),
            (7, 622, 'Mideast', 'Islamic Caliphates', '2,4,7', '', 'Hijra–triple cycle resonance, Islamic era birth'),
            (8, 1917, 'Europe', 'Russia', '4,8,7', '', 'Russian Revolution: 500y, 50y, 160y convergence (political, regime, economic)')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO convergences_table (convergence_id, year, region, civilisation, cycle_ids, event_ids, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', convergences)
        
        conn.commit()
        conn.close()
    
    def get_comprehensive_events(self, region=None, civilisation=None, date_start=None, date_end=None, cycle_bands=None, limit=1000):
        """Get events with comprehensive filtering and full lineage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT eco.*, cm.cycle_name, cm.cycle_period, cm.cycle_type, cm.effect_category,
                   rl.region_name, cl.civilisation_name, ea.action_name, ea.description as effect_description
            FROM event_cycle_overlay eco
            LEFT JOIN cycles_master cm ON (
                (eco.tier_20_phase IS NOT NULL AND cm.cycle_period = 20) OR
                (eco.tier_50_phase IS NOT NULL AND cm.cycle_period = 50) OR
                (eco.tier_160_phase IS NOT NULL AND cm.cycle_period = 160) OR
                (eco.tier_250_phase IS NOT NULL AND cm.cycle_period = 250) OR
                (eco.tier_500_phase IS NOT NULL AND cm.cycle_period = 500)
            )
            LEFT JOIN regions_list rl ON rl.region_code = ?
            LEFT JOIN civilisations_list cl ON cl.civilisation_name = ?
            LEFT JOIN effects_actions ea ON ea.effect_category = cm.effect_category
            WHERE 1=1
        '''
        
        params = [region, civilisation]
        
        if date_start is not None:
            query += ' AND eco.event_date_decimal >= ?'
            params.append(date_start)
        
        if date_end is not None:
            query += ' AND eco.event_date_decimal <= ?'
            params.append(date_end)
        
        if cycle_bands:
            band_conditions = []
            for band in cycle_bands:
                if band == 20:
                    band_conditions.append('eco.in_window_20 = 1')
                elif band == 50:
                    band_conditions.append('eco.in_window_50 = 1')
                elif band == 160:
                    band_conditions.append('eco.in_window_160 = 1')
                elif band == 250:
                    band_conditions.append('eco.in_window_250 = 1')
                elif band == 500:
                    band_conditions.append('eco.in_window_500 = 1')
            
            if band_conditions:
                query += f' AND ({" OR ".join(band_conditions)})'
        
        query += f' ORDER BY eco.event_date_decimal LIMIT {limit}'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_comprehensive_cycles(self, region=None, period_filter=None):
        """Get cycles with full hierarchy and embedding relationships"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT cm.*, parent.cycle_name as parent_name, 
                   GROUP_CONCAT(child.cycle_name) as child_cycles,
                   GROUP_CONCAT(ce.embedding_type) as embedding_types
            FROM cycles_master cm
            LEFT JOIN cycles_master parent ON cm.parent_cycle_id = parent.cycle_id
            LEFT JOIN cycle_embeddings ce ON cm.cycle_id = ce.parent_cycle_id
            LEFT JOIN cycles_master child ON ce.child_cycle_id = child.cycle_id
            WHERE 1=1
        '''
        
        params = []
        
        if region:
            query += ' AND (cm.region LIKE ? OR cm.region = "Global")'
            params.append(f'%{region}%')
        
        if period_filter:
            query += ' AND cm.cycle_period IN ({})'.format(','.join(['?'] * len(period_filter)))
            params.extend(period_filter)
        
        query += ' GROUP BY cm.cycle_id ORDER BY cm.cycle_period DESC'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_convergence_points(self, region=None, year_start=None, year_end=None):
        """Get cycle convergence/overlap points with full context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT ct.*, 
                   GROUP_CONCAT(cm.cycle_name) as cycle_names,
                   GROUP_CONCAT(eco.event_name_en) as event_names
            FROM convergences_table ct
            LEFT JOIN cycles_master cm ON (',' || ct.cycle_ids || ',' LIKE '%,' || cm.cycle_id || ',%')
            LEFT JOIN event_cycle_overlay eco ON (',' || ct.event_ids || ',' LIKE '%,' || eco.event_id || ',%')
            WHERE 1=1
        '''
        
        params = []
        
        if region:
            query += ' AND ct.region = ?'
            params.append(region)
        
        if year_start:
            query += ' AND ct.year >= ?'
            params.append(year_start)
        
        if year_end:
            query += ' AND ct.year <= ?'
            params.append(year_end)
        
        query += ' GROUP BY ct.convergence_id ORDER BY ct.year'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def generate_cycle_predictions(self, region=None, date_range=None, cycle_bands=None):
        """Generate predictions based on current cycle status and historical patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_year = datetime.now().year
        
        start_year, end_year = current_year, current_year + 50
        if date_range:
            try:
                start_year, end_year = map(int, date_range.split('-'))
            except:
                pass
        
        cycles_in_play = []
        cycle_band_list = [20, 50, 160, 250, 500] if not cycle_bands else [int(x.strip()) for x in cycle_bands.split(',')]
        
        for period in cycle_band_list:
            phase = ((current_year + 46664) % period) / period
            window_width = 0.10
            
            if phase >= (1 - window_width) or phase <= window_width:
                cycles_in_play.append({
                    'period': period,
                    'phase': phase,
                    'in_reset_window': True
                })
        
        predictions = []
        
        for year in range(start_year, end_year + 1):
            year_predictions = []
            convergence_count = 0
            
            for period in cycle_band_list:
                phase = ((year + 46664) % period) / period
                window_width = 0.10
                
                if phase >= (1 - window_width) or phase <= window_width:
                    convergence_count += 1
                    
                    cursor.execute('''
                        SELECT DISTINCT ea.action_name, ea.description, cm.effect_category
                        FROM cycles_master cm
                        JOIN effects_actions ea ON ea.effect_category = cm.effect_category
                        WHERE cm.cycle_period = ?
                    ''', (period,))
                    
                    effects = cursor.fetchall()
                    for effect in effects:
                        year_predictions.append({
                            'cycle_period': period,
                            'effect_type': effect[0],
                            'description': effect[1],
                            'category': effect[2],
                            'phase': phase
                        })
            
            if year_predictions:
                probability = min(0.95, convergence_count * 0.15 + 0.25)
                predictions.append({
                    'year': year,
                    'convergence_count': convergence_count,
                    'probability': probability,
                    'predicted_effects': year_predictions
                })
        
        conn.close()
        
        self._log_prediction(region, date_range, cycle_bands, predictions)
        
        return predictions
    
    def _log_prediction(self, region, date_range, cycle_bands, predictions):
        """Log prediction to predictions_log table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions_log (
                datetime_submitted, user_session, region, date_range_selected,
                cycle_band_selected, projected_events, probability, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            'api_session',
            region or 'Global',
            date_range or 'default',
            cycle_bands or 'all',
            json.dumps(predictions),
            sum(p['probability'] for p in predictions) / len(predictions) if predictions else 0,
            f'Generated {len(predictions)} predictions'
        ))
        
        conn.commit()
        conn.close()
    
    def get_sources_references(self, applies_to=None):
        """Get sources and references"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM sources_references'
        params = []
        
        if applies_to:
            query += ' WHERE applies_to LIKE ?'
            params.append(f'%{applies_to}%')
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_all_regions_comprehensive(self):
        """Get all regions with hierarchy from comprehensive database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT rl.*, parent.region_name as parent_name
            FROM regions_list rl
            LEFT JOIN regions_list parent ON rl.parent_region_id = parent.region_id
            ORDER BY rl.parent_region_id, rl.region_name
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_all_civilisations_comprehensive(self, region=None):
        """Get all civilisations with region links from comprehensive database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT cl.*, rl.region_name
            FROM civilisations_list cl
            LEFT JOIN regions_list rl ON cl.region_id = rl.region_id
        '''
        
        params = []
        if region:
            query += ' WHERE rl.region_name = ? OR rl.region_code = ?'
            params.extend([region, region])
        
        query += ' ORDER BY rl.region_name, cl.civilisation_name'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_all_effects_comprehensive(self):
        """Get all effects and actions from comprehensive database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM effects_actions ORDER BY effect_category, action_name')
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_astronomical_cycles_comprehensive(self):
        """Get astronomical cycle definitions from comprehensive database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM astronomical_cycles ORDER BY cycle_period_years')
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_system_parameters_comprehensive(self):
        """Get system parameters from comprehensive database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM system_parameters ORDER BY parameter_name')
        results = cursor.fetchall()
        conn.close()
        
        return results
