#!/usr/bin/env python3

import unittest
import pandas as pd
import tempfile
import os
from pathlib import Path
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.cycle_detection import CycleDetectionEngine

class TestDataLoading(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.engine = CycleDetectionEngine(data_dir=self.temp_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_csv(self, filename: str, data: dict, path: Path = None):
        """Helper to create test CSV files"""
        if path is None:
            path = self.temp_path
        
        df = pd.DataFrame(data)
        csv_path = path / filename
        df.to_csv(csv_path, index=False)
        return csv_path
    
    def test_load_valid_comprehensive_analysis(self):
        """Test loading valid comprehensive analysis file"""
        valid_data = {
            'year': [1453, 1572, 1789],
            'event': ['Fall of Constantinople', 'St. Bartholomew Massacre', 'French Revolution'],
            'region': ['Europe', 'Europe', 'Europe'],
            'subregion': ['Byzantine', 'France', 'France'],
            'event_type': ['Political', 'Religious', 'Political'],
            'cycle_period': [250, 250, 250],
            'phase': [0.1, 0.9, 0.3],
            'reset_window': [True, True, False]
        }
        
        test_region = self.temp_path / "test_region"
        test_region.mkdir()
        self.create_test_csv("test_comprehensive_analysis.csv", valid_data, test_region)
        
        df = self.engine._load_region_data(test_region)
        
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 3)
        self.assertIn('year', df.columns)
        self.assertIn('event', df.columns)
    
    def test_load_empty_file(self):
        """Test handling of empty CSV files"""
        test_region = self.temp_path / "empty_region"
        test_region.mkdir()
        
        empty_csv = test_region / "empty_comprehensive_analysis.csv"
        empty_csv.touch()
        
        df = self.engine._load_region_data(test_region)
        self.assertTrue(df.empty)
    
    def test_load_missing_columns(self):
        """Test handling of files with missing required columns"""
        test_region = self.temp_path / "missing_cols_region"
        test_region.mkdir()
        
        invalid_data = {
            'date': [1453, 1572],  # Wrong column name
            'description': ['Event 1', 'Event 2']  # Wrong column name
        }
        
        self.create_test_csv("missing_comprehensive_analysis.csv", invalid_data, test_region)
        
        df = self.engine._load_region_data(test_region)
        self.assertTrue(df.empty)
    
    def test_load_invalid_data_types(self):
        """Test handling of invalid data types"""
        test_region = self.temp_path / "invalid_types_region"
        test_region.mkdir()
        
        invalid_data = {
            'year': ['not_a_year', 'also_not_year', 1453],
            'event': ['Event 1', 'Event 2', 'Event 3'],
            'phase': [1.5, -0.5, 0.5]  # Invalid phase values
        }
        
        self.create_test_csv("invalid_comprehensive_analysis.csv", invalid_data, test_region)
        
        df = self.engine._load_region_data(test_region)
        
        if not df.empty:
            numeric_years = pd.to_numeric(df['year'], errors='coerce')
            self.assertFalse(numeric_years.isna().all())
    
    def test_fallback_to_basic_csv(self):
        """Test fallback to basic CSV files when comprehensive analysis not available"""
        test_region = self.temp_path / "fallback_region"
        test_region.mkdir()
        
        basic_data = {
            'Year': [1453, 1572, 1789, 1848, 1914, 1939, 1945, 1989, 2001, 2008, 2020],
            'Event': ['Fall of Constantinople', 'St. Bartholomew Massacre', 'French Revolution',
                     'Revolutions of 1848', 'WWI Start', 'WWII Start', 'WWII End', 
                     'Berlin Wall Fall', '9/11 Attacks', 'Financial Crisis', 'COVID Pandemic'],
            'Civilization': ['Byzantine', 'French', 'French', 'European', 'European', 
                           'European', 'European', 'European', 'American', 'Global', 'Global']
        }
        
        self.create_test_csv("basic_events.csv", basic_data, test_region)
        
        df = self.engine._load_region_data(test_region)
        
        self.assertFalse(df.empty)
        self.assertGreater(len(df), 10)  # Should have more than 10 events
        self.assertIn('Year', df.columns)
        self.assertIn('Event', df.columns)
    
    def test_data_type_validation(self):
        """Test data type validation methods"""
        valid_df = pd.DataFrame({
            'year': [1453, 1572, 1789],
            'event': ['Event 1', 'Event 2', 'Event 3'],
            'phase': [0.1, 0.5, 0.9]
        })
        
        self.assertTrue(self.engine._validate_data_types(valid_df))
        
        invalid_df = pd.DataFrame({
            'year': ['not_a_year', 'also_not_year'],
            'event': ['Event 1', 'Event 2'],
            'phase': [1.5, -0.5]  # Invalid phase values
        })
        
        result = self.engine._validate_data_types(invalid_df)
        self.assertIsInstance(result, bool)
    
    def test_data_type_fixing(self):
        """Test data type fixing functionality"""
        problematic_df = pd.DataFrame({
            'year': ['1453', '1572.0', 1789, 'invalid'],
            'event': ['Event 1', 'Event 2', 'Event 3', 'Event 4'],
            'phase': [0.1, 1.5, -0.5, 0.5]  # Some invalid phase values
        })
        
        fixed_df = self.engine._fix_data_types(problematic_df)
        
        self.assertTrue(pd.api.types.is_numeric_dtype(fixed_df['year']))
        
        if 'phase' in fixed_df.columns:
            phase_values = fixed_df['phase'].dropna()
            if not phase_values.empty:
                self.assertTrue(phase_values.between(0, 1).all())
    
    def test_basic_columns_detection(self):
        """Test basic columns detection"""
        standard_df = pd.DataFrame({
            'Year': [1453, 1572],
            'Event': ['Event 1', 'Event 2']
        })
        
        self.assertTrue(self.engine._has_basic_columns(standard_df))
        
        lowercase_df = pd.DataFrame({
            'year': [1453, 1572],
            'event': ['Event 1', 'Event 2']
        })
        
        self.assertTrue(self.engine._has_basic_columns(lowercase_df))
        
        missing_df = pd.DataFrame({
            'date': [1453, 1572],
            'description': ['Event 1', 'Event 2']
        })
        
        self.assertFalse(self.engine._has_basic_columns(missing_df))
    
    def test_fallback_data_standardization(self):
        """Test fallback data standardization"""
        fallback_df = pd.DataFrame({
            'Historical_Year': [1453, 1572, 1789],
            'Event_Description': ['Event 1', 'Event 2', 'Event 3'],
            'Civilization_Name': ['Byzantine', 'French', 'French'],
            'Geographic_Region': ['Europe', 'Europe', 'Europe']
        })
        
        standardized_df = self.engine._standardize_fallback_data(fallback_df)
        
        self.assertIn('Year', standardized_df.columns)
        self.assertTrue(pd.api.types.is_numeric_dtype(standardized_df['Year']))
        
        expected_columns = ['Event', 'Civilization', 'Region']
        for col in expected_columns:
            if col not in fallback_df.columns:
                self.assertIn(col, standardized_df.columns)
    
    def test_file_permission_errors(self):
        """Test handling of file permission errors"""
        test_region = self.temp_path / "permission_region"
        test_region.mkdir()
        
        test_file = test_region / "unreadable_comprehensive_analysis.csv"
        test_file.touch()
        
        try:
            os.chmod(test_file, 0o000)  # Remove all permissions
            
            df = self.engine._load_region_data(test_region)
            
            self.assertTrue(df.empty)
            
        except (OSError, PermissionError):
            self.skipTest("Cannot modify file permissions on this system")
        finally:
            try:
                os.chmod(test_file, 0o644)
            except (OSError, PermissionError):
                pass
    
    def test_corrupted_csv_handling(self):
        """Test handling of corrupted CSV files"""
        test_region = self.temp_path / "corrupted_region"
        test_region.mkdir()
        
        corrupted_file = test_region / "corrupted_comprehensive_analysis.csv"
        with open(corrupted_file, 'w') as f:
            f.write("year,event\n")
            f.write("1453,Event 1\n")
            f.write("invalid_csv_content_here\n")
            f.write("1572,Event 2")  # Missing newline
            f.write("extra,columns,without,header\n")
        
        df = self.engine._load_region_data(test_region)
        
        self.assertIsInstance(df, pd.DataFrame)
    
    def test_large_file_handling(self):
        """Test handling of large CSV files"""
        test_region = self.temp_path / "large_region"
        test_region.mkdir()
        
        large_data = {
            'year': list(range(-3000, 2025)),
            'event': [f'Event {i}' for i in range(-3000, 2025)],
            'region': ['Test'] * 5025,
            'subregion': ['Large'] * 5025
        }
        
        self.create_test_csv("large_comprehensive_analysis.csv", large_data, test_region)
        
        df = self.engine._load_region_data(test_region)
        
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 5025)
        
        self.assertTrue(pd.api.types.is_numeric_dtype(df['year']))

if __name__ == '__main__':
    unittest.main(verbosity=2)
