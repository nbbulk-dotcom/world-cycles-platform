import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Globe, Calendar, Eye, TrendingUp, Telescope, Building } from 'lucide-react'

interface ApiStatus {
  message: string
  version: string
  description: string
  vatican_analysis: string
  anchor_year: number
  statistical_significance: string
}

export function HomePage() {
  const [apiStatus, setApiStatus] = useState<ApiStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/`)
      .then(res => res.json())
      .then(data => {
        setApiStatus(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to fetch API status:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-white text-xl">Loading platform status...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-5xl font-bold text-white mb-4">
          World Cycles Platform
        </h1>
        <p className="text-xl text-gray-300 max-w-4xl mx-auto">
          The most comprehensive predictive cycles analysis platform ever created. 
          Analyzing global civilizations across 5,500 years of history to expose 
          the hidden patterns that shape our world.
        </p>
        {apiStatus && (
          <div className="flex justify-center space-x-4 mt-6">
            <Badge variant="secondary" className="bg-purple-600 text-white">
              Version {apiStatus.version}
            </Badge>
            <Badge variant="secondary" className="bg-green-600 text-white">
              {apiStatus.statistical_significance}
            </Badge>
            <Badge variant="secondary" className="bg-red-600 text-white">
              Anchor: {apiStatus.anchor_year} BCE
            </Badge>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card className="bg-black/40 border-purple-500/30 hover:border-purple-400/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <TrendingUp className="h-5 w-5 text-purple-400" />
              <span>Global Analysis</span>
            </CardTitle>
            <CardDescription className="text-gray-300">
              Comprehensive cycle detection across all world civilizations
            </CardDescription>
          </CardHeader>
          <CardContent className="text-gray-300">
            <p>Analyze patterns across 11 regions including Americas, Europe, Asia, Africa, and Oceania. 
            Detect micro (20y), medium (50y), macro (500y), and meta (5500y) cycles.</p>
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-red-500/30 hover:border-red-400/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <Eye className="h-5 w-5 text-red-400" />
              <span>Vatican Analysis</span>
            </CardTitle>
            <CardDescription className="text-gray-300">
              Exposing the 1582 observatory establishment impact
            </CardDescription>
          </CardHeader>
          <CardContent className="text-gray-300">
            <p>Reveal how ancient astronomical manipulation went global after 1582. 
            Track Vatican/Jesuit influence patterns and the "hidden clock" controlling world events.</p>
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-blue-500/30 hover:border-blue-400/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <Calendar className="h-5 w-5 text-blue-400" />
              <span>Future Predictions</span>
            </CardTitle>
            <CardDescription className="text-gray-300">
              Predict upcoming transitions with unprecedented accuracy
            </CardDescription>
          </CardHeader>
          <CardContent className="text-gray-300">
            <p>Generate probability-weighted scenarios for 2025-2050 based on 
            586 BCE anchor point and validated cyclical patterns.</p>
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-green-500/30 hover:border-green-400/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <Building className="h-5 w-5 text-green-400" />
              <span>Civilizations</span>
            </CardTitle>
            <CardDescription className="text-gray-300">
              Explore 87 civilizations across all world regions
            </CardDescription>
          </CardHeader>
          <CardContent className="text-gray-300">
            <p>Deep dive into specific civilizations and their cyclical patterns. 
            From ancient Babylon to modern nations, uncover the recurring themes.</p>
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-yellow-500/30 hover:border-yellow-400/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <Telescope className="h-5 w-5 text-yellow-400" />
              <span>Astronomical</span>
            </CardTitle>
            <CardDescription className="text-gray-300">
              Celestial correlations with historical events
            </CardDescription>
          </CardHeader>
          <CardContent className="text-gray-300">
            <p>Discover the impossible correlations between planetary alignments 
            and major historical transitions across 5,500 years.</p>
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-orange-500/30 hover:border-orange-400/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <Globe className="h-5 w-5 text-orange-400" />
              <span>Global Search</span>
            </CardTitle>
            <CardDescription className="text-gray-300">
              Search across all datasets and time periods
            </CardDescription>
          </CardHeader>
          <CardContent className="text-gray-300">
            <p>Multi-dimensional search through events, civilizations, time periods, 
            and astronomical correlations across the entire global dataset.</p>
          </CardContent>
        </Card>
      </div>

      {apiStatus && (
        <Card className="bg-black/40 border-purple-500/30">
          <CardHeader>
            <CardTitle className="text-white">Platform Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-gray-300">
            <p><strong>Description:</strong> {apiStatus.description}</p>
            <p><strong>Vatican Analysis:</strong> {apiStatus.vatican_analysis}</p>
            <p><strong>Statistical Significance:</strong> {apiStatus.statistical_significance}</p>
            <p><strong>Anchor Year:</strong> {apiStatus.anchor_year} BCE (Last Complete Reset)</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
