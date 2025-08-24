#!/usr/bin/env python3

import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tetrahedron_analysis import TetrahedronAnalysis, CyclePhase, RegionalCalibration

class TestTetrahedronAnalysis(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.tetrahedron = TetrahedronAnalysis()
        self.sample_events = [
            {'year': 1453, 'event': 'Fall of Constantinople', 'religious_influence': 0.85, 
             'political_impact': 0.95, 'economic_impact': 0.75, 'cultural_impact': 0.90},
            {'year': 1572, 'event': 'St. Bartholomew\'s Day Massacre', 'religious_influence': 0.90, 
             'political_impact': 0.85, 'economic_impact': 0.70, 'cultural_impact': 0.95},
            {'year': -586, 'event': 'Babylonian Conquest', 'religious_influence': 0.95,
             'political_impact': 0.90, 'economic_impact': 0.80, 'cultural_impact': 0.85}
        ]
    
    def test_phase_calculation_accuracy(self):
        """Test phase calculation accuracy with known values"""
        phase_1453 = self.tetrahedron.calculate_phase(1453, 250)
        expected_phase = ((1453 + 46664) % 250) / 250
        self.assertAlmostEqual(phase_1453, expected_phase, places=6)
        
        phase_bce = self.tetrahedron.calculate_phase(-586, 250)
        expected_phase_bce = ((-586 + 46664) % 250) / 250
        self.assertAlmostEqual(phase_bce, expected_phase_bce, places=6)
    
    def test_phase_calculation_edge_cases(self):
        """Test phase calculation with edge cases"""
        phase_bce = self.tetrahedron.calculate_phase(-586, 250)
        self.assertGreaterEqual(phase_bce, 0.0)
        self.assertLessEqual(phase_bce, 1.0)
        
        phase_zero = self.tetrahedron.calculate_phase(0, 250)
        self.assertIsInstance(phase_zero, float)
        self.assertGreaterEqual(phase_zero, 0.0)
        self.assertLessEqual(phase_zero, 1.0)
        
        phase_large = self.tetrahedron.calculate_phase(10000, 250)
        self.assertGreaterEqual(phase_large, 0.0)
        self.assertLessEqual(phase_large, 1.0)
        
        phase_zero_period = self.tetrahedron.calculate_phase(1453, 0)
        self.assertEqual(phase_zero_period, 0.0)
    
    def test_reset_window_detection(self):
        """Test reset window detection logic"""
        self.assertTrue(self.tetrahedron.determine_reset_window(0.05))  # Early reset
        self.assertTrue(self.tetrahedron.determine_reset_window(0.95))  # Late reset
        self.assertTrue(self.tetrahedron.determine_reset_window(0.0))   # Exact start
        self.assertTrue(self.tetrahedron.determine_reset_window(1.0))   # Exact end (wraps to 0)
        
        self.assertFalse(self.tetrahedron.determine_reset_window(0.5))  # Middle
        self.assertFalse(self.tetrahedron.determine_reset_window(0.3))  # Normal
        self.assertFalse(self.tetrahedron.determine_reset_window(0.15)) # Just outside
    
    def test_rgb_mapping_generation(self):
        """Test RGB color mapping generation"""
        phase = 0.1  # Reset window phase
        rgb = self.tetrahedron.generate_rgb_mapping(phase, 250, 1.0)
        
        self.assertIsInstance(rgb, tuple)
        self.assertEqual(len(rgb), 3)
        for value in rgb:
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 255)
            self.assertIsInstance(value, int)
        
        rgb_20 = self.tetrahedron.generate_rgb_mapping(0.5, 20, 1.0)
        rgb_500 = self.tetrahedron.generate_rgb_mapping(0.5, 500, 1.0)
        self.assertNotEqual(rgb_20, rgb_500)  # Different periods should give different colors
        
        rgb_neg = self.tetrahedron.generate_rgb_mapping(0.5, 250, -1.0)
        self.assertIsInstance(rgb_neg, tuple)
        self.assertEqual(len(rgb_neg), 3)
    
    def test_cmyk_mapping_generation(self):
        """Test CMYK color mapping generation"""
        phase = 0.3
        cmyk = self.tetrahedron.generate_cmyk_mapping(phase, 250, 1.0)
        
        self.assertIsInstance(cmyk, tuple)
        self.assertEqual(len(cmyk), 4)
        for value in cmyk:
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 100.0)
            self.assertIsInstance(value, float)
        
        cmyk_zero = self.tetrahedron.generate_cmyk_mapping(0.0, 250, 1.0)
        cmyk_one = self.tetrahedron.generate_cmyk_mapping(1.0, 250, 1.0)
        self.assertIsInstance(cmyk_zero, tuple)
        self.assertIsInstance(cmyk_one, tuple)
    
    def test_regional_calibration(self):
        """Test regional calibration calculations"""
        calibration = self.tetrahedron.calculate_regional_calibration("Europe", self.sample_events)
        
        self.assertIsInstance(calibration, RegionalCalibration)
        self.assertEqual(calibration.region, "Europe")
        self.assertGreaterEqual(calibration.accuracy_improvement, 0.0)
        self.assertLessEqual(calibration.accuracy_improvement, 1.0)
        self.assertGreaterEqual(calibration.correlation_coefficient, 0.0)
        self.assertLessEqual(calibration.correlation_coefficient, 1.0)
        self.assertGreaterEqual(calibration.reset_window_events, 0)
        self.assertIn(calibration.confidence_level, ["Very High", "High", "Medium", "Low", "No Data"])
        self.assertEqual(calibration.total_events, len(self.sample_events))
        
        empty_calibration = self.tetrahedron.calculate_regional_calibration("Empty", [])
        self.assertEqual(empty_calibration.total_events, 0)
        self.assertEqual(empty_calibration.confidence_level, "No Data")
    
    def test_cycle_period_distribution(self):
        """Test cycle period distribution analysis"""
        distribution = self.tetrahedron.analyze_cycle_period_distribution(self.sample_events)
        
        self.assertIsInstance(distribution, dict)
        
        for period in self.tetrahedron.cycle_periods:
            period_key = f"{period}y"
            self.assertIn(period_key, distribution)
            
            period_data = distribution[period_key]
            self.assertIn("cycle_period", period_data)
            self.assertIn("type", period_data)
            self.assertIn("active_events", period_data)
            self.assertIn("harmonic_resonance", period_data)
            self.assertIn("confidence", period_data)
            
            self.assertEqual(period_data["cycle_period"], period)
            self.assertIn(period_data["type"], ["Micro", "Medium", "Macro", "Meta"])
    
    def test_comprehensive_analysis_integration(self):
        """Test comprehensive analysis integration"""
        analysis = self.tetrahedron.generate_comprehensive_analysis(
            "Europe", "Byzantine Empire", self.sample_events
        )
        
        required_keys = [
            'region', 'subregion', 'total_events', 'phase_calculations',
            'regional_calibration', 'cycle_period_distribution',
            'religious_influence_tracking', 'predictive_accuracy'
        ]
        
        for key in required_keys:
            self.assertIn(key, analysis)
        
        self.assertEqual(analysis['region'], "Europe")
        self.assertEqual(analysis['subregion'], "Byzantine Empire")
        self.assertEqual(analysis['total_events'], len(self.sample_events))
        self.assertGreater(len(analysis['phase_calculations']), 0)
        
        phase_calc = analysis['phase_calculations'][0]
        phase_required_keys = [
            'year', 'event', 'cycle_period', 'phase_value',
            'rgb_mapping', 'cmyk_mapping', 'reset_window'
        ]
        for key in phase_required_keys:
            self.assertIn(key, phase_calc)
    
    def test_performance_caching(self):
        """Test performance caching functionality"""
        self.tetrahedron.phase_cache.clear()
        
        phase1 = self.tetrahedron.calculate_phase(1453, 250)
        self.assertIn("1453_250", self.tetrahedron.phase_cache)
        
        phase2 = self.tetrahedron.calculate_phase(1453, 250)
        self.assertEqual(phase1, phase2)
        
        self.assertEqual(self.tetrahedron.phase_cache["1453_250"], phase1)
    
    def test_mathematical_edge_cases(self):
        """Test mathematical edge cases and error handling"""
        phase = self.tetrahedron.calculate_phase(1453, 0)
        self.assertEqual(phase, 0.0)
        
        phase_large = self.tetrahedron.calculate_phase(999999, 250)
        self.assertGreaterEqual(phase_large, 0.0)
        self.assertLessEqual(phase_large, 1.0)
        
        rgb = self.tetrahedron.generate_rgb_mapping(0.5, 250, -1.0)
        self.assertIsInstance(rgb, tuple)
        self.assertEqual(len(rgb), 3)
        
        cmyk = self.tetrahedron.generate_cmyk_mapping(0.5, 250, -1.0)
        self.assertIsInstance(cmyk, tuple)
        self.assertEqual(len(cmyk), 4)
    
    def test_religious_pattern_analysis(self):
        """Test religious pattern analysis"""
        analysis = self.tetrahedron.generate_comprehensive_analysis(
            "Europe", "Test", self.sample_events
        )
        
        religious_analysis = analysis['religious_influence_tracking']
        
        self.assertIn('total_religious_events', religious_analysis)
        self.assertIn('religious_event_density', religious_analysis)
        self.assertIn('scripture_version_timeline', religious_analysis)
        self.assertIn('cycle_correlation', religious_analysis)
        
        scripture_timeline = religious_analysis['scripture_version_timeline']
        self.assertIsInstance(scripture_timeline, dict)
    
    def test_predictive_metrics_calculation(self):
        """Test predictive metrics calculation"""
        analysis = self.tetrahedron.generate_comprehensive_analysis(
            "Europe", "Test", self.sample_events
        )
        
        predictive_metrics = analysis['predictive_accuracy']
        
        required_keys = [
            'overall_accuracy', 'confidence_interval', 'prediction_strength',
            'pattern_consistency', 'total_predictions', 'correct_predictions'
        ]
        
        for key in required_keys:
            self.assertIn(key, predictive_metrics)
        
        confidence_interval = predictive_metrics['confidence_interval']
        self.assertIn('lower', confidence_interval)
        self.assertIn('upper', confidence_interval)
        
        self.assertIn(predictive_metrics['prediction_strength'], 
                     ["Very High", "High", "Medium", "Low", "No Data", "Error"])
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        malformed_events = [
            {'invalid': 'data'},
            {'year': 'not_a_number', 'event': 'Test'},
            {}
        ]
        
        analysis = self.tetrahedron.generate_comprehensive_analysis(
            "Test", "Error", malformed_events
        )
        
        self.assertIn('region', analysis)
        self.assertIn('total_events', analysis)
        
        calibration = self.tetrahedron.calculate_regional_calibration("Test", malformed_events)
        self.assertIsInstance(calibration, RegionalCalibration)

if __name__ == '__main__':
    unittest.main(verbosity=2)
