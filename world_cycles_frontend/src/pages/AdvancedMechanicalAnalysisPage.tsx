import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter } from 'recharts'
import { Settings, Calculator, TrendingUp, Zap, Globe, Database } from 'lucide-react'

interface TetrahedronAnalysisData {
  base_offset: number
  cycle_periods: number[]
  phase_calculations: Array<{
    event_date: number
    cycle_period: number
    phase: number
    reset_window: boolean
    rgb_mapping: { r: number, g: number, b: number }
    cmyk_mapping: { c: number, m: number, y: number, k: number }
  }>
  regional_calibration: Record<string, {
    offset_adjustment: number
    accuracy_improvement: number
    correlation_coefficient: number
  }>
  predictive_accuracy: {
    overall_accuracy: number
    regional_accuracy: Record<string, number>
    confidence_intervals: Array<{ year: number, lower: number, upper: number }>
  }
  religious_influence_tracking: {
    scripture_versions: Array<{
      region: string
      version: string
      adoption_year: number
      paradigm_shift_correlation: number
    }>
    translation_impacts: Array<{
      year: number
      region: string
      impact_magnitude: number
      cycle_correlation: number
    }>
  }
}

interface RegionData {
  region: string
  subregions: string[]
}

export function AdvancedMechanicalAnalysisPage() {
  const [analysisData, setAnalysisData] = useState<TetrahedronAnalysisData | null>(null)
  const [regions, setRegions] = useState<RegionData[]>([])
  const [selectedRegion, setSelectedRegion] = useState<string>('')
  const [selectedSubregion, setSelectedSubregion] = useState<string>('')
  const [baseOffset, setBaseOffset] = useState<number>(46664)
  const [windowWidth, setWindowWidth] = useState<number>(0.10)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const CYCLE_PERIODS = [20, 50, 160, 250, 500]
  const TETRAHEDRON_COLORS = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF']

  useEffect(() => {
    fetchRegions()
  }, [])

  const fetchRegions = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/regions`)
      if (!response.ok) throw new Error('Failed to fetch regions')
      const data = await response.json()
      
      const regionData: RegionData[] = Object.entries(data.regions_map).map(([region, subregions]) => ({
        region,
        subregions: subregions as string[]
      }))
      setRegions(regionData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load regions')
    }
  }

  const runTetrahedronAnalysis = async () => {
    if (!selectedRegion || !selectedSubregion) {
      setError('Please select both region and subregion')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/advanced-mechanical/analysis/${selectedRegion}/${selectedSubregion}?base_offset=${baseOffset}&window_width=${windowWidth}`
      )
      
      if (!response.ok) {
        throw new Error('Failed to fetch tetrahedron analysis')
      }
      
      const data = await response.json()
      setAnalysisData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const getPhaseVisualizationData = () => {
    if (!analysisData?.phase_calculations) return []
    
    return analysisData.phase_calculations.slice(0, 50).map(calc => ({
      year: calc.event_date,
      phase: calc.phase,
      cycle_period: calc.cycle_period,
      reset_window: calc.reset_window ? 1 : 0,
      rgb_intensity: (calc.rgb_mapping.r + calc.rgb_mapping.g + calc.rgb_mapping.b) / 3,
      cmyk_intensity: (calc.cmyk_mapping.c + calc.cmyk_mapping.m + calc.cmyk_mapping.y + calc.cmyk_mapping.k) / 4
    }))
  }

  const getRegionalCalibrationData = () => {
    if (!analysisData?.regional_calibration) return []
    
    return Object.entries(analysisData.regional_calibration).map(([region, data]) => ({
      region: region.replace('_', ' ').toUpperCase(),
      accuracy: Math.round(data.accuracy_improvement * 100),
      correlation: Math.round(data.correlation_coefficient * 100),
      offset: data.offset_adjustment
    }))
  }

  const getReligiousInfluenceData = () => {
    if (!analysisData?.religious_influence_tracking?.translation_impacts) return []
    
    return analysisData.religious_influence_tracking.translation_impacts.slice(0, 20).map(impact => ({
      year: impact.year,
      region: impact.region.replace('_', ' ').toUpperCase(),
      impact: Math.round(impact.impact_magnitude * 100),
      correlation: Math.round(impact.cycle_correlation * 100)
    }))
  }

  const getCurrentSubregions = () => {
    const region = regions.find(r => r.region === selectedRegion)
    return region?.subregions || []
  }

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-white mb-4">
          Advanced Mechanical Analysis
        </h1>
        <p className="text-xl text-gray-300 max-w-4xl mx-auto">
          Tetrahedron RGB-CMYK harmonic ratio model with base offset 46664. 
          Regional calibration capabilities with multi-religious framework integration.
        </p>
        <Badge variant="secondary" className="text-lg px-4 py-2">
          Mathematical Framework: Phase = ((event_date + 46664) mod period) / period
        </Badge>
      </div>

      {/* Configuration Panel */}
      <Card className="bg-black/40 border-purple-500/30">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-white">
            <Settings className="h-5 w-5 text-purple-400" />
            <span>Tetrahedron Configuration</span>
          </CardTitle>
          <CardDescription className="text-gray-300">
            Configure the mathematical framework parameters and regional analysis scope
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="base-offset" className="text-white">Base Offset (Skew Factor)</Label>
              <Input
                id="base-offset"
                type="number"
                value={baseOffset}
                onChange={(e) => setBaseOffset(Number(e.target.value))}
                className="bg-black/20 border-gray-600 text-white"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="window-width" className="text-white">Reset Window Width</Label>
              <Input
                id="window-width"
                type="number"
                step="0.01"
                value={windowWidth}
                onChange={(e) => setWindowWidth(Number(e.target.value))}
                className="bg-black/20 border-gray-600 text-white"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="region" className="text-white">Region</Label>
              <Select value={selectedRegion} onValueChange={setSelectedRegion}>
                <SelectTrigger className="bg-black/20 border-gray-600 text-white">
                  <SelectValue placeholder="Select region" />
                </SelectTrigger>
                <SelectContent>
                  {regions.map(region => (
                    <SelectItem key={region.region} value={region.region}>
                      {region.region.replace('_', ' ').toUpperCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="subregion" className="text-white">Subregion</Label>
              <Select value={selectedSubregion} onValueChange={setSelectedSubregion}>
                <SelectTrigger className="bg-black/20 border-gray-600 text-white">
                  <SelectValue placeholder="Select subregion" />
                </SelectTrigger>
                <SelectContent>
                  {getCurrentSubregions().map(subregion => (
                    <SelectItem key={subregion} value={subregion}>
                      {subregion.replace('_', ' ').toUpperCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex justify-center">
            <Button 
              onClick={runTetrahedronAnalysis}
              disabled={loading || !selectedRegion || !selectedSubregion}
              className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-2"
            >
              {loading ? (
                <>
                  <Calculator className="h-4 w-4 mr-2 animate-spin" />
                  Running Analysis...
                </>
              ) : (
                <>
                  <Calculator className="h-4 w-4 mr-2" />
                  Run Tetrahedron Analysis
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card className="bg-red-900/20 border-red-500/30">
          <CardContent className="p-6">
            <div className="text-red-400 text-center">Error: {error}</div>
          </CardContent>
        </Card>
      )}

      {analysisData && (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <Card className="bg-black/40 border-green-500/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <TrendingUp className="h-5 w-5 text-green-400" />
                  <span>Overall Accuracy</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-400">
                  {Math.round(analysisData.predictive_accuracy.overall_accuracy * 100)}%
                </div>
                <p className="text-gray-300">Predictive Model</p>
              </CardContent>
            </Card>

            <Card className="bg-black/40 border-blue-500/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Database className="h-5 w-5 text-blue-400" />
                  <span>Base Offset</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-400">{analysisData.base_offset}</div>
                <p className="text-gray-300">Skew Factor</p>
              </CardContent>
            </Card>

            <Card className="bg-black/40 border-orange-500/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Globe className="h-5 w-5 text-orange-400" />
                  <span>Cycle Periods</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-400">{analysisData.cycle_periods.length}</div>
                <p className="text-gray-300">Active Cycles</p>
              </CardContent>
            </Card>

            <Card className="bg-black/40 border-red-500/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Zap className="h-5 w-5 text-red-400" />
                  <span>Phase Events</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-400">
                  {analysisData.phase_calculations.length}
                </div>
                <p className="text-gray-300">Calculated</p>
              </CardContent>
            </Card>
          </div>

          {/* Phase Visualization */}
          <Card className="bg-black/40 border-purple-500/30">
            <CardHeader>
              <CardTitle className="text-white">Tetrahedron Phase Calculations</CardTitle>
              <CardDescription className="text-gray-300">
                RGB-CMYK harmonic ratio visualization with reset window detection
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart data={getPhaseVisualizationData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="year" stroke="#9CA3AF" />
                  <YAxis dataKey="phase" stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #6B7280',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Scatter 
                    name="Phase Values" 
                    dataKey="phase" 
                    fill="#8B5CF6"
                  />
                  <Scatter 
                    name="Reset Windows" 
                    dataKey="reset_window" 
                    fill="#EF4444"
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Regional Calibration */}
          <Card className="bg-black/40 border-blue-500/30">
            <CardHeader>
              <CardTitle className="text-white">Regional Calibration Results</CardTitle>
              <CardDescription className="text-gray-300">
                Accuracy improvements and correlation coefficients by region
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={getRegionalCalibrationData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="region" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #6B7280',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="accuracy" 
                    stroke="#3B82F6" 
                    strokeWidth={2}
                    name="Accuracy %"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="correlation" 
                    stroke="#10B981" 
                    strokeWidth={2}
                    name="Correlation %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Religious Influence Tracking */}
          {analysisData.religious_influence_tracking && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-black/40 border-yellow-500/30">
                <CardHeader>
                  <CardTitle className="text-white">Religious Translation Impacts</CardTitle>
                  <CardDescription className="text-gray-300">
                    Scripture version changes and paradigm shift correlations
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={getReligiousInfluenceData()}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="year" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1F2937', 
                          border: '1px solid #6B7280',
                          borderRadius: '8px'
                        }}
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="impact" 
                        stroke="#F59E0B" 
                        strokeWidth={2}
                        name="Impact Magnitude %"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="correlation" 
                        stroke="#EC4899" 
                        strokeWidth={2}
                        name="Cycle Correlation %"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className="bg-black/40 border-green-500/30">
                <CardHeader>
                  <CardTitle className="text-white">Scripture Version Timeline</CardTitle>
                  <CardDescription className="text-gray-300">
                    Regional adoption patterns and paradigm shifts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4 max-h-80 overflow-y-auto">
                    {Object.entries(analysisData.religious_influence_tracking.scripture_versions).slice(0, 10).map(([key, version], index) => (
                      <div key={index} className="bg-black/20 p-4 rounded-lg border border-green-500/20">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="text-lg font-bold text-green-400">
                              {key.replace('_', ' ').toUpperCase()}
                            </div>
                            <div className="text-sm text-gray-300">{version.period}</div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm text-gray-400">Influence: {Math.round(version.influence * 100)}%</div>
                            <Badge 
                              variant="secondary"
                              className="mt-1"
                            >
                              {Math.round(version.accuracy_impact * 100)}% Impact
                            </Badge>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Cycle Period Analysis */}
          <Card className="bg-black/40 border-red-500/30">
            <CardHeader>
              <CardTitle className="text-white">Cycle Period Distribution</CardTitle>
              <CardDescription className="text-gray-300">
                Tetrahedron harmonic analysis across {CYCLE_PERIODS.join(', ')} year cycles
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {CYCLE_PERIODS.map((period, index) => (
                  <div key={period} className="text-center">
                    <div 
                      className="w-16 h-16 rounded-full mx-auto mb-2 flex items-center justify-center text-white font-bold"
                      style={{ backgroundColor: TETRAHEDRON_COLORS[index] }}
                    >
                      {period}
                    </div>
                    <div className="text-sm text-gray-300">
                      {period === 20 ? 'Political' : 
                       period === 50 ? 'Economic' :
                       period === 160 ? 'Empire' :
                       period === 250 ? 'Civilizational' : 'Meta'}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
