#!/usr/bin/env python3
"""
BRETT Unified Optimal HTML Generator
Generates comprehensive HTML presentation of the unified system
"""

import os
import json
from datetime import datetime
from unified_brett_engine import BrettUnifiedOptimalEngine

def generate_unified_html():
    """Generate comprehensive HTML for the unified optimal system"""
    
    engine = BrettUnifiedOptimalEngine()
    
    test_locations = [
        {'name': 'Los Angeles, CA', 'lat': 34.0522, 'lng': -118.2437, 'type': 'earthquake'},
        {'name': 'Mount Vesuvius, Italy', 'lat': 40.8218, 'lng': 14.4289, 'type': 'volcanic'},
        {'name': 'Kamchatka Peninsula, Russia', 'lat': 56.0, 'lng': 160.0, 'type': 'both'},
        {'name': 'Yellowstone, USA', 'lat': 44.4280, 'lng': -110.5885, 'type': 'volcanic'}
    ]
    
    results = {}
    for location in test_locations:
        result = engine.calculate_unified_prediction(
            location['lat'], location['lng'], location['type']
        )
        results[location['name']] = result
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRETT Unified Optimal System - Scientific Demonstration</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffffff;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            padding-bottom: 20px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .subtitle {{
            font-size: 1.2em;
            margin: 10px 0;
            opacity: 0.9;
        }}
        
        .system-overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .overview-card {{
            background: rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .overview-card h3 {{
            color: #FFD700;
            margin-top: 0;
            font-size: 1.3em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .metric-card {{
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid rgba(0, 255, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #00FF00;
            display: block;
        }}
        
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 5px;
        }}
        
        .location-results {{
            margin: 30px 0;
        }}
        
        .location-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 25px;
            margin: 20px 0;
            border-left: 4px solid #FFD700;
        }}
        
        .location-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .location-name {{
            font-size: 1.4em;
            font-weight: bold;
            color: #FFD700;
        }}
        
        .prediction-type {{
            background: rgba(255, 165, 0, 0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            border: 1px solid #FFA500;
        }}
        
        .prediction-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .prediction-section {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 20px;
        }}
        
        .prediction-section h4 {{
            color: #87CEEB;
            margin-top: 0;
            font-size: 1.2em;
        }}
        
        .prediction-list {{
            list-style: none;
            padding: 0;
        }}
        
        .prediction-list li {{
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
        }}
        
        .prediction-list li:last-child {{
            border-bottom: none;
        }}
        
        .high-risk {{
            color: #FF6B6B;
            font-weight: bold;
        }}
        
        .medium-risk {{
            color: #FFD93D;
            font-weight: bold;
        }}
        
        .low-risk {{
            color: #6BCF7F;
        }}
        
        .technical-params {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .technical-params h4 {{
            color: #87CEEB;
            margin-top: 0;
        }}
        
        .param-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .param-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .param-label {{
            opacity: 0.8;
        }}
        
        .param-value {{
            color: #00FF00;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid rgba(255, 255, 255, 0.3);
            opacity: 0.8;
        }}
        
        .data-section {{
            margin: 30px 0;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 25px;
        }}
        
        .data-section h3 {{
            color: #FFD700;
            margin-top: 0;
        }}
        
        .variable-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .variable-category {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 15px;
        }}
        
        .variable-category h4 {{
            color: #87CEEB;
            margin-top: 0;
            font-size: 1.1em;
        }}
        
        .variable-list {{
            font-size: 0.9em;
            line-height: 1.4;
        }}
        
        .variable-list div {{
            padding: 3px 0;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>BRETT Unified Optimal System</h1>
            <div class="subtitle">Electromagnetic-Geological Correlation Framework</div>
            <div class="subtitle">12-Space Data Tables • 24-Earth Resonance Datasets • CMYK Tetrahedral Lens</div>
            <div class="subtitle">Developed by Nicolas Brett, Administrator, Plebeian Tribunal South Africa</div>
            <div class="subtitle">Published as prior art, linked to <a href="https://www.amazon.com/dp/979-8294613495" style="color: #FFD700;">La Lingua della Tirannia</a> (ISBN 979-8294613495)</div>
            <div class="subtitle">Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC • Version: {engine.version}</div>
        </div>
        
        <div class="system-overview">
            <div class="overview-card">
                <h3>🌌 12-Space Data Tables (RGB Engine)</h3>
                <p>Complete electromagnetic space weather monitoring including solar wind, magnetic fields, cosmic rays, ionospheric density, geomagnetic activity, solar flares, coronal mass ejections, Schumann resonance, atmospheric pressure, magnetosphere, plasma density, and electromagnetic frequencies.</p>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <span class="metric-value">12</span>
                        <div class="metric-label">Space Variables</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-value">RGB</span>
                        <div class="metric-label">Color Engine</div>
                    </div>
                </div>
            </div>
            
            <div class="overview-card">
                <h3>🌍 24-Earth Resonance Datasets (CMYK Engine)</h3>
                <p>Comprehensive earth system modeling with 12 GAL-CRM dimensions (surface to core + space layers), 6 vibration fields (tectonic to volcanic), and 6 chamber factors for volcanic-specific calibrations.</p>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <span class="metric-value">24</span>
                        <div class="metric-label">Earth Variables</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-value">CMYK</span>
                        <div class="metric-label">Color Engine</div>
                    </div>
                </div>
            </div>
            
            <div class="overview-card">
                <h3>🔺 CMYK Tetrahedral Lens Mechanics</h3>
                <p>Advanced electromagnetic focusing system using tetrahedral geometry (base 54.74°) with RGB-CMYK complementary wave interference patterns for precise geolocation targeting.</p>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <span class="metric-value">54.74°</span>
                        <div class="metric-label">Base Angle</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-value">RGB+CMYK</span>
                        <div class="metric-label">Lens System</div>
                    </div>
                </div>
            </div>
            
            <div class="overview-card">
                <h3>🌐 Firmament Height (80-85 km)</h3>
                <p>Sun ray refraction calculations at ionospheric boundary with location-specific height adjustments and electromagnetic coupling factors for optimal energy transfer.</p>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <span class="metric-value">82.5</span>
                        <div class="metric-label">Base Height (km)</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-value">80-85</span>
                        <div class="metric-label">Range (km)</div>
                    </div>
                </div>
            </div>
            
            <div class="overview-card">
                <h3>⏱️ Lag Time Corrections</h3>
                <p>Critical temporal adjustments for electromagnetic propagation delays: 48h solar rotation, 24h plasma arrival, 8h plasma propagation, 6h geomagnetic processing, 24h ionospheric response, 12h atmospheric coupling.</p>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <span class="metric-value">6</span>
                        <div class="metric-label">Lag Categories</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-value">48h</span>
                        <div class="metric-label">Max Lag Time</div>
                    </div>
                </div>
            </div>
            
            <div class="overview-card">
                <h3>📅 21-Day Prediction Window</h3>
                <p>Optimal prediction timeframe based on solar rotation cycles (27 days), geomagnetic cycles (11 days), and resonance amplification/nullification patterns with daily resolution updates.</p>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <span class="metric-value">21</span>
                        <div class="metric-label">Days Window</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-value">Daily</span>
                        <div class="metric-label">Resolution</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="data-section">
            <h3>🔬 System Architecture Overview</h3>
            <div class="variable-grid">
                <div class="variable-category">
                    <h4>12-Space Data Tables (RGB Engine)</h4>
                    <div class="variable-list">
                        <div>• VAR_SOLAR_WIND (0.12 weight, 400 km/s)</div>
                        <div>• VAR_MAGNETIC_FIELD (0.10 weight, 50000 nT)</div>
                        <div>• VAR_COSMIC_RAYS (0.08 weight, 3.2 GV)</div>
                        <div>• VAR_IONOSPHERIC (0.15 weight, 20 TECU)</div>
                        <div>• VAR_GEOMAGNETIC (0.12 weight, 2.1 Kp)</div>
                        <div>• VAR_SOLAR_FLARES (0.10 weight, 103.5 SFU)</div>
                        <div>• VAR_CORONAL_MASS (0.08 weight, 0.8 events/day)</div>
                        <div>• VAR_SCHUMANN (0.06 weight, 7.83 Hz)</div>
                        <div>• VAR_ATMOSPHERIC (0.09 weight, 1013.25 hPa)</div>
                        <div>• VAR_MAGNETOSPHERE (0.07 weight, -15 nT)</div>
                        <div>• VAR_PLASMA_DENSITY (0.03 weight, 5.0 cm⁻³)</div>
                        <div>• VAR_ELECTROMAGNETIC (0.03 weight, 2.7 MHz)</div>
                    </div>
                </div>
                
                <div class="variable-category">
                    <h4>12 GAL-CRM Dimensions</h4>
                    <div class="variable-list">
                        <div>• D1: Surface seismic (0 km, 0.1 Hz)</div>
                        <div>• D2: Crustal stress (15 km, 0.2 Hz)</div>
                        <div>• D3: Upper mantle (50 km, 0.3 Hz)</div>
                        <div>• D4: Lower mantle (200 km, 0.4 Hz)</div>
                        <div>• D5: Outer core (2900 km, 0.5 Hz)</div>
                        <div>• D6: Inner core (5150 km, 0.6 Hz)</div>
                        <div>• D7: Near space (85 km, 7.83 Hz)</div>
                        <div>• D8: Mid space (200 km, 15.66 Hz)</div>
                        <div>• D9: Far space (400 km, 31.32 Hz)</div>
                        <div>• D10: Magnetosphere (1000 km, 62.64 Hz)</div>
                        <div>• D11: Plasmasphere (4000 km, 125.28 Hz)</div>
                        <div>• D12: Exosphere (10000 km, 250.56 Hz)</div>
                    </div>
                </div>
                
                <div class="variable-category">
                    <h4>6 Vibration Fields + 6 Chamber Factors</h4>
                    <div class="variable-list">
                        <div>• VF1: Tectonic stress (0.01 Hz, 1.2×10⁻⁶ m)</div>
                        <div>• VF2: Magma pressure (0.02 Hz, 8.9×10⁻⁷ m)</div>
                        <div>• VF3: Crustal deformation (0.03 Hz, 6.4×10⁻⁷ m)</div>
                        <div>• VF4: Fault coupling (0.04 Hz, 4.1×10⁻⁷ m)</div>
                        <div>• VF5: Chamber resonance (0.05 Hz, 2.8×10⁻⁷ m)</div>
                        <div>• VF6: Volcanic tremor (0.06 Hz, 1.9×10⁻⁷ m)</div>
                        <div>• CF1-CF6: Chamber depth/volume factors</div>
                        <div>• Depth range: 8-30 km</div>
                        <div>• Volume range: 50-2000 km³</div>
                    </div>
                </div>
                
                <div class="variable-category">
                    <h4>CMYK Tetrahedral Lens System</h4>
                    <div class="variable-list">
                        <div><strong>RGB Space Engine:</strong></div>
                        <div>• Red (Solar): 650 nm, 0.85 coupling</div>
                        <div>• Green (Geomagnetic): 550 nm, 0.82 coupling</div>
                        <div>• Blue (Ionospheric): 450 nm, 0.80 coupling</div>
                        <div><strong>CMYK Earth Engine:</strong></div>
                        <div>• Cyan (Seismic): 0.1 Hz, 50 km penetration</div>
                        <div>• Magenta (EMF): 7.83 Hz, 25 km penetration</div>
                        <div>• Yellow (Atmospheric): 15.66 Hz, 10 km penetration</div>
                        <div>• Black (Stress): 31.32 Hz, 5 km penetration</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="location-results">
            <h2 style="color: #FFD700; text-align: center; margin-bottom: 30px;">🌍 Unified System Demonstration Results</h2>
"""
    
    for location_name, result in results.items():
        if result['success']:
            location_data = next(loc for loc in test_locations if loc['name'] == location_name)
            
            html_content += f"""
            <div class="location-card">
                <div class="location-header">
                    <div class="location-name">{location_name}</div>
                    <div class="prediction-type">{result['prediction_type'].upper()}</div>
                </div>
                
                <div class="technical-params">
                    <h4>🔧 Technical Parameters</h4>
                    <div class="param-grid">
                        <div class="param-item">
                            <span class="param-label">Coordinates:</span>
                            <span class="param-value">{result['location']['latitude']:.4f}°, {result['location']['longitude']:.4f}°</span>
                        </div>
                        <div class="param-item">
                            <span class="param-label">Firmament Height:</span>
                            <span class="param-value">{result['system_parameters']['firmament_height_km']:.1f} km</span>
                        </div>
                        <div class="param-item">
                            <span class="param-label">Tetrahedral Angle:</span>
                            <span class="param-value">{result['system_parameters']['tetrahedral_angle_degrees']:.2f}°</span>
                        </div>
                        <div class="param-item">
                            <span class="param-label">Total Variables:</span>
                            <span class="param-value">{result['system_parameters']['total_variables']}</span>
                        </div>
                        <div class="param-item">
                            <span class="param-label">Prediction Window:</span>
                            <span class="param-value">{result['system_parameters']['prediction_window_days']} days</span>
                        </div>
                        <div class="param-item">
                            <span class="param-label">Sun Ray Intensity:</span>
                            <span class="param-value">{result['sun_ray_refraction'].get('sun_ray_intensity', 0):.1f}</span>
                        </div>
                    </div>
                </div>
                
                <div class="prediction-grid">
"""
            
            if result['prediction_type'] in ['earthquake', 'both']:
                eq_analysis = result['summary_statistics']['earthquake_analysis']
                html_content += f"""
                    <div class="prediction-section">
                        <h4>🌋 Earthquake Predictions (Target: 76% Accuracy)</h4>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <span class="metric-value">{eq_analysis['max_probability']:.1f}%</span>
                                <div class="metric-label">Max Probability</div>
                            </div>
                            <div class="metric-card">
                                <span class="metric-value">{eq_analysis['max_magnitude']:.1f}</span>
                                <div class="metric-label">Max Magnitude</div>
                            </div>
                            <div class="metric-card">
                                <span class="metric-value">Day {eq_analysis['peak_risk_day']}</span>
                                <div class="metric-label">Peak Risk</div>
                            </div>
                        </div>
                        <ul class="prediction-list">
"""
                
                eq_predictions = sorted(result['predictions_21_day'], 
                                      key=lambda x: x['earthquake_probability'], reverse=True)[:5]
                for pred in eq_predictions:
                    risk_class = 'high-risk' if pred['earthquake_probability'] > 60 else 'medium-risk' if pred['earthquake_probability'] > 30 else 'low-risk'
                    html_content += f"""
                            <li>
                                <span>Day {pred['day']} ({pred['date']})</span>
                                <span class="{risk_class}">{pred['earthquake_probability']:.1f}% (M{pred['earthquake_magnitude']:.1f})</span>
                            </li>
"""
                
                html_content += """
                        </ul>
                    </div>
"""
            
            if result['prediction_type'] in ['volcanic', 'both']:
                vol_analysis = result['summary_statistics']['volcanic_analysis']
                html_content += f"""
                    <div class="prediction-section">
                        <h4>🌋 Volcanic Predictions (Target: 86% Accuracy)</h4>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <span class="metric-value">{vol_analysis['max_probability']:.1f}%</span>
                                <div class="metric-label">Max Probability</div>
                            </div>
                            <div class="metric-card">
                                <span class="metric-value">{vol_analysis['max_magnitude']:.1f}</span>
                                <div class="metric-label">Max Magnitude</div>
                            </div>
                            <div class="metric-card">
                                <span class="metric-value">Day {vol_analysis['peak_risk_day']}</span>
                                <div class="metric-label">Peak Risk</div>
                            </div>
                        </div>
                        <ul class="prediction-list">
"""
                
                vol_predictions = sorted(result['predictions_21_day'], 
                                       key=lambda x: x['volcanic_probability'], reverse=True)[:5]
                for pred in vol_predictions:
                    risk_class = 'high-risk' if pred['volcanic_probability'] > 60 else 'medium-risk' if pred['volcanic_probability'] > 30 else 'low-risk'
                    html_content += f"""
                            <li>
                                <span>Day {pred['day']} ({pred['date']})</span>
                                <span class="{risk_class}">{pred['volcanic_probability']:.1f}% (M{pred['volcanic_magnitude']:.1f})</span>
                            </li>
"""
                
                html_content += """
                        </ul>
                    </div>
"""
            
            html_content += """
                </div>
            </div>
"""
        else:
            html_content += f"""
            <div class="location-card">
                <div class="location-header">
                    <div class="location-name">{location_name}</div>
                    <div class="prediction-type">ERROR</div>
                </div>
                <p style="color: #FF6B6B;">Prediction failed: {result.get('error', 'Unknown error')}</p>
            </div>
"""
    
    html_content += f"""
        </div>
        
        <div class="data-section">
            <h3>📊 System Performance Metrics</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-value">76%</span>
                    <div class="metric-label">Earthquake Accuracy Target</div>
                </div>
                <div class="metric-card">
                    <span class="metric-value">86%</span>
                    <div class="metric-label">Volcanic Accuracy Target</div>
                </div>
                <div class="metric-card">
                    <span class="metric-value">36</span>
                    <div class="metric-label">Total Variables (12+24)</div>
                </div>
                <div class="metric-card">
                    <span class="metric-value">21</span>
                    <div class="metric-label">Prediction Window (Days)</div>
                </div>
                <div class="metric-card">
                    <span class="metric-value">80-85</span>
                    <div class="metric-label">Firmament Height (km)</div>
                </div>
                <div class="metric-card">
                    <span class="metric-value">54.74°</span>
                    <div class="metric-label">Base Tetrahedral Angle</div>
                </div>
                <div class="metric-card">
                    <span class="metric-value">6</span>
                    <div class="metric-label">Lag Correction Categories</div>
                </div>
                <div class="metric-card">
                    <span class="metric-value">RGB+CMYK</span>
                    <div class="metric-label">Tetrahedral Lens System</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <h2 style="color: #FFD700;">🏆 BRETT Unified Optimal System - Scientific Achievement</h2>
            <p><strong>Irrefutable, Incontestable, and Undeniably Refined to Optimal Performance</strong></p>
            <p>This system represents the complete integration of electromagnetic-geological correlation mechanisms with:</p>
            <ul style="text-align: left; display: inline-block; margin: 20px 0;">
                <li>✅ 12-Space Data Tables with comprehensive electromagnetic monitoring</li>
                <li>✅ 24-Earth Resonance Datasets including GAL-CRM dimensions, vibration fields, and chamber factors</li>
                <li>✅ CMYK Tetrahedral Lens Mechanics with RGB-CMYK complementary wave interference</li>
                <li>✅ Firmament Height Calculations (80-85 km) with sun ray refraction optimization</li>
                <li>✅ Complete Lag Time Corrections for all electromagnetic propagation delays</li>
                <li>✅ 21-Day Prediction Window with daily resolution and temporal enhancement</li>
                <li>✅ 76% Earthquake and 86% Volcanic prediction accuracy targets</li>
                <li>✅ Scientific documentation ready for peer review and journal submission</li>
            </ul>
            <p><strong>Developed by Nicolas Brett, Administrator, Plebeian Tribunal South Africa</strong></p>
            <p>Published as prior art, linked to <a href="https://www.amazon.com/dp/979-8294613495" style="color: #FFD700;">La Lingua della Tirannia</a> (ISBN 979-8294613495)</p>
            <p>For technical support or scientific collaboration, refer to the BRETT documentation or contact system administrators.</p>
            <p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC • Engine Version: {engine.version}</em></p>
        </div>
    </div>
</body>
</html>"""
    
    output_file = "/home/ubuntu/repos/brett_unified_optimal/index.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Unified HTML generated: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_unified_html()
