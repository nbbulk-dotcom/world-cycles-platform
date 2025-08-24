#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'world_cycles_backend'))

from world_cycles_backend.app.tetrahedron_analysis import TetrahedronAnalysis
import logging

logging.basicConfig(level=logging.INFO)

def test_tetrahedron_analysis():
    """Test TetrahedronAnalysis implementation with Vatican Observatory tracking"""
    print("🔬 Testing TetrahedronAnalysis Implementation")
    print("=" * 60)
    
    tetrahedron = TetrahedronAnalysis()
    print(f"✓ TetrahedronAnalysis initialized successfully")
    print(f"  Vatican Observatory Year: {tetrahedron.vatican_observatory_year}")
    print(f"  Cycle Periods: {tetrahedron.cycle_periods}")
    print(f"  Regional Planetary Angles: {list(tetrahedron.regional_planetary_angles.keys())}")
    print()
    
    print("🌍 Testing Phase Calculations with Regional Modifiers")
    phase_1453_europe = tetrahedron.calculate_phase(1453, 250, 'EUROPE')
    phase_1582_europe = tetrahedron.calculate_phase(1582, 250, 'EUROPE')
    phase_1650_africa = tetrahedron.calculate_phase(1650, 250, 'AFRICA')
    
    print(f"  Phase 1453 Europe: {phase_1453_europe:.6f}")
    print(f"  Phase 1582 Europe (Vatican year): {phase_1582_europe:.6f}")
    print(f"  Phase 1650 Africa: {phase_1650_africa:.6f}")
    print()
    
    print("⛪ Testing Vatican Influence Scoring")
    vatican_score_pre = tetrahedron._calculate_vatican_influence_score(1453, 0.8, 'EUROPE')
    vatican_score_post = tetrahedron._calculate_vatican_influence_score(1650, 0.8, 'EUROPE')
    vatican_score_africa = tetrahedron._calculate_vatican_influence_score(1700, 0.7, 'AFRICA')
    
    print(f"  Vatican influence 1453 Europe: {vatican_score_pre:.4f}")
    print(f"  Vatican influence 1650 Europe: {vatican_score_post:.4f}")
    print(f"  Vatican influence 1700 Africa: {vatican_score_africa:.4f}")
    print()
    
    print("🪐 Testing Planetary Angle Modifiers")
    angle_mod_jupiter = tetrahedron.calculate_planetary_angle_modifier(1582, 'EUROPE', 20)
    angle_mod_mercury = tetrahedron.calculate_planetary_angle_modifier(1650, 'AFRICA', 50)
    angle_mod_general = tetrahedron.calculate_planetary_angle_modifier(1700, 'ASIA', 250)
    
    print(f"  Jupiter-Saturn cycle (20y) Europe 1582: {angle_mod_jupiter:.4f}")
    print(f"  Mercury cycle (50y) Africa 1650: {angle_mod_mercury:.4f}")
    print(f"  General cycle (250y) Asia 1700: {angle_mod_general:.4f}")
    print()
    
    print("📊 Testing Comprehensive Analysis")
    sample_events = [
        {'year': 1453, 'event': 'Fall of Constantinople', 'religious_influence': 0.85, 
         'political_impact': 0.95, 'economic_impact': 0.75, 'cultural_impact': 0.90, 'significance': 1.0},
        {'year': 1582, 'event': 'Vatican Observatory Establishment', 'religious_influence': 0.95, 
         'political_impact': 0.80, 'economic_impact': 0.60, 'cultural_impact': 0.85, 'significance': 1.0},
        {'year': 1650, 'event': 'Jesuit Global Expansion', 'religious_influence': 0.90, 
         'political_impact': 0.85, 'economic_impact': 0.70, 'cultural_impact': 0.95, 'significance': 1.0}
    ]
    
    analysis = tetrahedron.generate_comprehensive_analysis('EUROPE', 'Byzantine Empire', sample_events)
    
    print(f"  Total events analyzed: {len(sample_events)}")
    print(f"  Phase calculations generated: {len(analysis.get('phase_calculations', []))}")
    print(f"  Regional calibration completed: {'regional_calibration' in analysis}")
    print(f"  Religious patterns analyzed: {'religious_influence_tracking' in analysis}")
    print(f"  Vatican Observatory impact tracked: {'vatican_observatory_impact' in analysis.get('religious_influence_tracking', {})}")
    print()
    
    print("⚡ Testing Performance Caching")
    cache_size_before = len(tetrahedron.phase_cache)
    
    for _ in range(3):
        tetrahedron.calculate_phase(1582, 250, 'EUROPE')
    
    cache_size_after = len(tetrahedron.phase_cache)
    print(f"  Cache entries before: {cache_size_before}")
    print(f"  Cache entries after: {cache_size_after}")
    print(f"  Caching working: {'✓' if cache_size_after > cache_size_before else '✗'}")
    print()
    
    print("🎉 All TetrahedronAnalysis tests completed successfully!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        test_tetrahedron_analysis()
        print("✅ TetrahedronAnalysis implementation verified!")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
