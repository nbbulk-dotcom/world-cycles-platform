import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { RegionalSelector } from '@/components/RegionalSelector'
import { TimelineVisualization } from '@/components/TimelineVisualization'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { TrendingUp, Eye, MapPin, Telescope } from 'lucide-react'

interface RegionalAnalysisData {
  region: string
  subregion: string
  date_range: { start: number, end: number }
  cycles: any[]
  total_cycles: number
  planetary_visibility_analysis: any
}

export function RegionalAnalysisPage() {
  const [analysisData, setAnalysisData] = useState<RegionalAnalysisData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleRegionSelect = async (region: string, subregion: string, dateRange: {start: number, end: number}) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/regional/analysis/${region}/${subregion}?start_year=${dateRange.start}&end_year=${dateRange.end}`
      )
      
      if (!response.ok) {
        throw new Error('Failed to fetch regional analysis')
      }
      
      const data = await response.json()
      setAnalysisData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  const COLORS = ['#8B5CF6', '#3B82F6', '#10B981', '#F59E0B', '#EF4444']

  const getPlanetaryVisibilityChart = () => {
    if (!analysisData?.planetary_visibility_analysis?.high_influence_periods) return []
    
    return analysisData.planetary_visibility_analysis.high_influence_periods.slice(0, 10).map((period: any) => ({
      year: period.year,
      influence: Math.round(period.influence_level * 100),
      visible_planets: Object.values(period.visible_planets).filter(Boolean).length
    }))
  }

  const getCycleTypeDistribution = () => {
    if (!analysisData?.cycles) return []
    
    const typeCount: Record<string, number> = {}
    analysisData.cycles.forEach(cycle => {
      const type = cycle.cycle_category || 'Unknown'
      typeCount[type] = (typeCount[type] || 0) + 1
    })
    
    return Object.entries(typeCount).map(([type, count]) => ({
      type,
      count,
      percentage: Math.round((count / analysisData.cycles.length) * 100)
    }))
  }

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-white mb-4">
          Regional Cycle Analysis
        </h1>
        <p className="text-xl text-gray-300 max-w-4xl mx-auto">
          Analyze cycles for specific regions with planetary visibility mechanics. 
          Planets only affect regions when observable, creating dynamic flow patterns.
        </p>
      </div>

      <RegionalSelector onRegionSelect={handleRegionSelect} />

      {loading && (
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="text-white text-xl">Loading regional analysis...</div>
        </div>
      )}

      {error && (
        <Card className="bg-red-900/20 border-red-500/30">
          <CardContent className="p-6">
            <div className="text-red-400 text-center">
              Error: {error}
            </div>
          </CardContent>
        </Card>
      )}

      {analysisData && !loading && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <Card className="bg-black/40 border-purple-500/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <MapPin className="h-5 w-5 text-purple-400" />
                  <span>Region</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="text-gray-300">
                <div className="text-2xl font-bold text-purple-400">
                  {analysisData.subregion.replace('_', ' ').toUpperCase()}
                </div>
                <p className="text-sm">{analysisData.region.replace('_', ' ').toUpperCase()}</p>
                <Badge variant="secondary" className="mt-2">
                  {analysisData.date_range.start} to {analysisData.date_range.end}
                </Badge>
              </CardContent>
            </Card>

            <Card className="bg-black/40 border-green-500/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <TrendingUp className="h-5 w-5 text-green-400" />
                  <span>Total Cycles</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="text-gray-300">
                <div className="text-3xl font-bold text-green-400">{analysisData.total_cycles}</div>
                <p>Detected Patterns</p>
              </CardContent>
            </Card>

            <Card className="bg-black/40 border-blue-500/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Telescope className="h-5 w-5 text-blue-400" />
                  <span>Planetary Events</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="text-gray-300">
                <div className="text-3xl font-bold text-blue-400">
                  {analysisData.planetary_visibility_analysis?.planetary_influence_events || 0}
                </div>
                <p>Visible Influences</p>
              </CardContent>
            </Card>

            <Card className="bg-black/40 border-orange-500/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-white">
                  <Eye className="h-5 w-5 text-orange-400" />
                  <span>High Control</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="text-gray-300">
                <div className="text-3xl font-bold text-orange-400">
                  {analysisData.planetary_visibility_analysis?.high_influence_periods?.length || 0}
                </div>
                <p>Peak Periods</p>
              </CardContent>
            </Card>
          </div>

          <TimelineVisualization 
            region={analysisData.region}
            subregion={analysisData.subregion}
            dateRange={analysisData.date_range}
          />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-black/40 border-purple-500/30">
              <CardHeader>
                <CardTitle className="text-white">Planetary Visibility Over Time</CardTitle>
                <CardDescription className="text-gray-300">
                  Regional influence based on visible planets
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={getPlanetaryVisibilityChart()}>
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
                      dataKey="influence" 
                      stroke="#8B5CF6" 
                      strokeWidth={2}
                      name="Influence %"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="visible_planets" 
                      stroke="#3B82F6" 
                      strokeWidth={2}
                      name="Visible Planets"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="bg-black/40 border-blue-500/30">
              <CardHeader>
                <CardTitle className="text-white">Cycle Type Distribution</CardTitle>
                <CardDescription className="text-gray-300">
                  Categories of detected cycles
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={getCycleTypeDistribution()}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ type, percentage }) => `${type}: ${percentage}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {getCycleTypeDistribution().map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {analysisData.planetary_visibility_analysis?.high_influence_periods?.length > 0 && (
            <Card className="bg-black/40 border-red-500/30">
              <CardHeader>
                <CardTitle className="text-white">High Control Periods</CardTitle>
                <CardDescription className="text-gray-300">
                  Periods of maximum planetary influence and cult religious order enforcement
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {analysisData.planetary_visibility_analysis.high_influence_periods.slice(0, 6).map((period: any, index: number) => (
                    <div key={index} className="bg-black/20 p-4 rounded-lg border border-red-500/20">
                      <div className="text-lg font-bold text-red-400">{period.year} CE</div>
                      <div className="text-sm text-gray-300 mb-2">
                        Influence: {Math.round(period.influence_level * 100)}%
                      </div>
                      <div className="space-y-1">
                        {Object.entries(period.visible_planets).map(([planet, visible]: [string, any]) => (
                          <div key={planet} className="flex items-center justify-between text-xs">
                            <span className="text-gray-400">{planet}</span>
                            <Badge 
                              variant={visible ? "default" : "secondary"}
                              className={visible ? "bg-green-600" : "bg-gray-600"}
                            >
                              {visible ? "Visible" : "Hidden"}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
