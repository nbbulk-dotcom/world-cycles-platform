import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LineChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Customized } from 'recharts'
import { Calendar, Zap } from 'lucide-react'

interface TimelineData {
  region: string
  subregion: string
  date_range: { start: number, end: number }
  timeline_data: {
    cycles: Record<number, Array<{
      year: number
      cycle_length: number
      category: string
      vatican_influence: number
      phase: string
    }>>
    convergence_points: Array<{
      year: number
      converging_cycles: number[]
      cycle_count: number
      intensity: number
      is_catastrophic: boolean
    }>
    catastrophic_resets: Array<any>
    phase_transitions: Array<any>
  }
  astrological_cycles: number[]
}

interface TimelineVisualizationProps {
  region: string
  subregion: string
  dateRange: { start: number, end: number }
}

type ViewMode = 'cyclical' | 'catastrophic' | 'hybrid'

export function TimelineVisualization({ region, subregion, dateRange }: TimelineVisualizationProps) {
  const [timelineData, setTimelineData] = useState<TimelineData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('hybrid')

  const CYCLE_COLORS: Record<number, string> = {
    20: '#8B5CF6',
    50: '#3B82F6',
    160: '#10B981',
    250: '#F59E0B',
    500: '#EF4444',
    2000: '#EC4899'
  }

  useEffect(() => {
    if (region && subregion) {
      fetchTimelineData()
    }
  }, [region, subregion, dateRange])

  const fetchTimelineData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/timeline/analysis/${region}/${subregion}?start_year=${dateRange.start}&end_year=${dateRange.end}`
      )
      
      if (!response.ok) {
        throw new Error('Failed to fetch timeline data')
      }
      
      const data = await response.json()
      console.log('Timeline data received:', data)
      setTimelineData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  const generateTimelineChartData = () => {
    if (!timelineData) return []
    
    const chartData: Array<{ year: number, [key: string]: any }> = []
    const yearRange = dateRange.end - dateRange.start
    const step = Math.max(1, Math.floor(yearRange / 100))
    
    for (let year = dateRange.start; year <= dateRange.end; year += step) {
      const dataPoint: any = { year }
      
      timelineData.astrological_cycles.forEach(cycleLength => {
        const cyclePoints = timelineData.timeline_data.cycles[cycleLength] || []
        const nearbyPoint = cyclePoints.find(p => Math.abs(p.year - year) <= step)
        dataPoint[`cycle_${cycleLength}`] = nearbyPoint ? 1 : 0
      })
      
      chartData.push(dataPoint)
    }
    
    return chartData
  }

  const CustomHalfCircles = (props: any) => {
    if (!timelineData) return null
    
    console.log('CustomHalfCircles props:', props)
    
    const chartWidth = props.width || 1134
    const chartHeight = props.height || 400
    
    const margin = { top: 20, right: 30, bottom: 60, left: 60 }
    const plotWidth = chartWidth - margin.left - margin.right
    const plotHeight = chartHeight - margin.top - margin.bottom
    
    const xScale = plotWidth / (dateRange.end - dateRange.start)
    console.log('Chart dimensions:', { chartWidth, chartHeight, plotWidth, plotHeight, xScale })
    
    return (
      <g>
        {timelineData.astrological_cycles.map((cycleLength, index) => {
          const cyclePoints = timelineData.timeline_data.cycles[cycleLength] || []
          const color = CYCLE_COLORS[cycleLength]
          const radius = 15 + (index * 8)
          
          return cyclePoints
            .filter(point => {
              if (viewMode === 'cyclical') return point.phase !== 'Catastrophic'
              if (viewMode === 'catastrophic') return point.phase === 'Catastrophic'
              return true
            })
            .map(point => {
              const pointX = margin.left + ((point.year - dateRange.start) * xScale)
              const pointY = margin.top + plotHeight - radius - 20
              
              if (pointX < margin.left || pointX > margin.left + plotWidth) return null
              
              return (
                <g key={`${cycleLength}-${point.year}`}>
                  <path
                    d={`M ${pointX - radius} ${pointY} A ${radius} ${radius} 0 0 1 ${pointX + radius} ${pointY} Z`}
                    fill={color}
                    fillOpacity={0.7}
                    stroke={color}
                    strokeWidth={2}
                  />
                  <text
                    x={pointX}
                    y={pointY - 5}
                    textAnchor="middle"
                    fontSize="10"
                    fill="white"
                    fontWeight="bold"
                  >
                    {cycleLength}y
                  </text>
                </g>
              )
            })
        })}
        
        {timelineData.timeline_data.convergence_points.map(convergence => {
          const pointX = margin.left + ((convergence.year - dateRange.start) * xScale)
          if (pointX < margin.left || pointX > margin.left + plotWidth) return null
          
          return (
            <g key={`convergence-${convergence.year}`}>
              <line
                x1={pointX}
                y1={margin.top}
                x2={pointX}
                y2={margin.top + plotHeight}
                stroke={convergence.is_catastrophic ? '#EF4444' : '#F59E0B'}
                strokeWidth={convergence.is_catastrophic ? 4 : 2}
                strokeDasharray={convergence.is_catastrophic ? '0' : '5,5'}
                opacity={0.8}
              />
              <text
                x={pointX + 5}
                y={margin.top + 20}
                fontSize="12"
                fill={convergence.is_catastrophic ? '#EF4444' : '#F59E0B'}
                fontWeight="bold"
              >
                {convergence.is_catastrophic ? 'RESET' : 'CONV'}
              </text>
            </g>
          )
        })}
      </g>
    )
  }

  if (loading) {
    return (
      <Card className="bg-black/40 border-purple-500/30">
        <CardContent className="p-6">
          <div className="text-white text-center">Loading timeline visualization...</div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="bg-red-900/20 border-red-500/30">
        <CardContent className="p-6">
          <div className="text-red-400 text-center">Error: {error}</div>
        </CardContent>
      </Card>
    )
  }

  if (!timelineData) return null

  return (
    <div className="space-y-6">
      <Card className="bg-black/40 border-purple-500/30">
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-white">
            <span className="flex items-center space-x-2">
              <Calendar className="h-5 w-5 text-purple-400" />
              <span>Astrological Cycles Timeline</span>
            </span>
            <div className="flex space-x-2">
              {(['cyclical', 'catastrophic', 'hybrid'] as ViewMode[]).map(mode => (
                <Button
                  key={mode}
                  variant={viewMode === mode ? "default" : "outline"}
                  size="sm"
                  onClick={() => setViewMode(mode)}
                  className={viewMode === mode ? "bg-purple-600" : ""}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </Button>
              ))}
            </div>
          </CardTitle>
          <CardDescription className="text-gray-300">
            Interactive timeline showing {timelineData.astrological_cycles.join(', ')} year cycles with convergence points and catastrophic resets
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={generateTimelineChartData()}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="year" 
                stroke="#9CA3AF"
                domain={[dateRange.start, dateRange.end]}
              />
              <YAxis hide />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #6B7280',
                  borderRadius: '8px'
                }}
              />
              <Customized component={CustomHalfCircles} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="bg-black/40 border-blue-500/30">
        <CardHeader>
          <CardTitle className="text-white">Cycle Legend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {timelineData.astrological_cycles.map(cycleLength => (
              <div key={cycleLength} className="flex items-center space-x-2">
                <div 
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: CYCLE_COLORS[cycleLength] }}
                />
                <span className="text-white text-sm">
                  {cycleLength} years ({timelineData.timeline_data.cycles[cycleLength]?.length || 0} points)
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {timelineData.timeline_data.convergence_points.length > 0 && (
        <Card className="bg-black/40 border-red-500/30">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <Zap className="h-5 w-5 text-red-400" />
              <span>Convergence Points</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {timelineData.timeline_data.convergence_points.slice(0, 6).map((convergence, index) => (
                <div key={index} className="bg-black/20 p-4 rounded-lg border border-red-500/20">
                  <div className="text-lg font-bold text-red-400">{convergence.year} CE</div>
                  <div className="text-sm text-gray-300 mb-2">
                    {convergence.cycle_count} cycles converging
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {convergence.converging_cycles.map((cycle: number) => (
                      <Badge 
                        key={cycle}
                        variant="secondary"
                        className="text-xs"
                        style={{ backgroundColor: CYCLE_COLORS[cycle] + '40' }}
                      >
                        {cycle}y
                      </Badge>
                    ))}
                  </div>
                  {convergence.is_catastrophic && (
                    <Badge variant="destructive" className="mt-2">
                      CATASTROPHIC RESET
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
