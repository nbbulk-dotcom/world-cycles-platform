import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Search, Calendar, Globe, Filter, TrendingUp } from 'lucide-react'

interface SearchResult {
  year: number
  event: string
  civilization: string
  region: string
  subregion: string
  impact_level: string
}

export function SearchPage() {
  const [query, setQuery] = useState('')
  const [startYear, setStartYear] = useState<number | undefined>()
  const [endYear, setEndYear] = useState<number | undefined>()
  const [selectedRegion, setSelectedRegion] = useState('all')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [totalResults, setTotalResults] = useState(0)

  const regions = [
    'americas', 'europe', 'asia', 'oceania', 'middle_east', 'arctic',
    'central_africa', 'east_africa', 'north_africa', 'south_africa', 'west_africa'
  ]

  const performSearch = async () => {
    if (!query.trim()) return

    setLoading(true)
    try {
      const params = new URLSearchParams({
        query: query.trim()
      })
      
      if (startYear) params.append('start_year', startYear.toString())
      if (endYear) params.append('end_year', endYear.toString())
      if (selectedRegion && selectedRegion !== 'all') params.append('region', selectedRegion)

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/search?${params}`)
      const data = await response.json()
      
      setResults(data.results || [])
      setTotalResults(data.total_results || 0)
    } catch (err) {
      console.error('Search failed:', err)
      setResults([])
      setTotalResults(0)
    }
    setLoading(false)
  }

  const clearSearch = () => {
    setQuery('')
    setStartYear(undefined)
    setEndYear(undefined)
    setSelectedRegion('all')
    setResults([])
    setTotalResults(0)
  }

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high': return 'bg-red-600'
      case 'medium': return 'bg-orange-600'
      case 'low': return 'bg-yellow-600'
      default: return 'bg-gray-600'
    }
  }

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-white mb-4">
          Global Search
        </h1>
        <p className="text-xl text-gray-300 max-w-4xl mx-auto">
          Search across all datasets and time periods. Multi-dimensional exploration through 
          events, civilizations, astronomical correlations, and Vatican influence patterns.
        </p>
      </div>

      <Card className="bg-black/40 border-purple-500/30">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-white">
            <Search className="h-5 w-5 text-purple-400" />
            <span>Search Parameters</span>
          </CardTitle>
          <CardDescription className="text-gray-300">
            Configure your search across the global cycles database
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="query" className="text-white">Search Query</Label>
              <Input
                id="query"
                placeholder="e.g., empire, war, eclipse, vatican..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="bg-black/20 border-gray-600 text-white"
                onKeyPress={(e) => e.key === 'Enter' && performSearch()}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="region" className="text-white">Region Filter</Label>
              <Select value={selectedRegion} onValueChange={setSelectedRegion}>
                <SelectTrigger className="bg-black/20 border-gray-600 text-white">
                  <SelectValue placeholder="All regions" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-600">
                  <SelectItem value="all" className="text-white">All Regions</SelectItem>
                  {regions.map(region => (
                    <SelectItem key={region} value={region} className="text-white">
                      {region.replace('_', ' ').toUpperCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="startYear" className="text-white">Start Year</Label>
              <Input
                id="startYear"
                type="number"
                placeholder="e.g., -3000 (3000 BCE)"
                value={startYear || ''}
                onChange={(e) => setStartYear(e.target.value ? parseInt(e.target.value) : undefined)}
                className="bg-black/20 border-gray-600 text-white"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="endYear" className="text-white">End Year</Label>
              <Input
                id="endYear"
                type="number"
                placeholder="e.g., 2025"
                value={endYear || ''}
                onChange={(e) => setEndYear(e.target.value ? parseInt(e.target.value) : undefined)}
                className="bg-black/20 border-gray-600 text-white"
              />
            </div>
          </div>

          <div className="flex space-x-4">
            <Button 
              onClick={performSearch}
              disabled={loading || !query.trim()}
              className="bg-purple-600 hover:bg-purple-700 flex-1"
            >
              <Search className="h-4 w-4 mr-2" />
              {loading ? 'Searching...' : 'Search'}
            </Button>
            <Button 
              onClick={clearSearch}
              variant="outline"
              className="border-gray-600 text-gray-300 hover:bg-gray-700"
            >
              Clear
            </Button>
          </div>
        </CardContent>
      </Card>

      {totalResults > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <Card className="bg-black/40 border-green-500/30">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-white">
                <TrendingUp className="h-5 w-5 text-green-400" />
                <span>Results Found</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-gray-300">
              <div className="text-3xl font-bold text-green-400">{totalResults}</div>
              <p>Matching Events</p>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-blue-500/30">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-white">
                <Calendar className="h-5 w-5 text-blue-400" />
                <span>Time Range</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-gray-300">
              <div className="text-lg font-bold text-blue-400">
                {results.length > 0 ? 
                  `${Math.min(...results.map(r => r.year))} - ${Math.max(...results.map(r => r.year))}` : 
                  'N/A'
                }
              </div>
              <p>Years Covered</p>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-yellow-500/30">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-white">
                <Globe className="h-5 w-5 text-yellow-400" />
                <span>Regions</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-gray-300">
              <div className="text-3xl font-bold text-yellow-400">
                {new Set(results.map(r => r.region)).size}
              </div>
              <p>Different Regions</p>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-purple-500/30">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-white">
                <Filter className="h-5 w-5 text-purple-400" />
                <span>Civilizations</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-gray-300">
              <div className="text-3xl font-bold text-purple-400">
                {new Set(results.map(r => r.civilization)).size}
              </div>
              <p>Different Civilizations</p>
            </CardContent>
          </Card>
        </div>
      )}

      {results.length > 0 && (
        <Card className="bg-black/40 border-purple-500/30">
          <CardHeader>
            <CardTitle className="text-white">Search Results</CardTitle>
            <CardDescription className="text-gray-300">
              Showing {results.length} of {totalResults} results for "{query}"
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {results.map((result, index) => (
                <div key={index} className="p-4 bg-gray-900/40 rounded-lg border border-gray-600/30 hover:border-purple-400/50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-4">
                      <div className="text-lg font-bold text-white">
                        {result.year > 0 ? `${result.year} CE` : `${Math.abs(result.year)} BCE`}
                      </div>
                      <div className="text-purple-400 font-semibold">{result.event}</div>
                    </div>
                    <Badge 
                      variant="secondary" 
                      className={`${getImpactColor(result.impact_level)} text-white`}
                    >
                      {result.impact_level}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-300">
                    <div>
                      <span className="text-gray-400">Civilization:</span> {result.civilization}
                    </div>
                    <div>
                      <span className="text-gray-400">Region:</span> {result.region.replace('_', ' ').toUpperCase()}
                    </div>
                    <div>
                      <span className="text-gray-400">Subregion:</span> {result.subregion.replace('_', ' ')}
                    </div>
                  </div>

                  {result.year >= 1582 && (
                    <div className="mt-2">
                      <Badge variant="destructive" className="bg-red-600 text-white text-xs">
                        Vatican Observatory Era
                      </Badge>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {query && results.length === 0 && !loading && (
        <Card className="bg-black/40 border-gray-500/30">
          <CardContent className="text-center py-8">
            <div className="text-gray-400 text-lg mb-4">
              No results found for "{query}"
            </div>
            <div className="text-sm text-gray-500 mb-4">
              Try adjusting your search terms or filters
            </div>
            <Button 
              onClick={clearSearch}
              className="bg-purple-600 hover:bg-purple-700"
            >
              Clear Search
            </Button>
          </CardContent>
        </Card>
      )}

      {!query && (
        <Card className="bg-black/40 border-gray-500/30">
          <CardContent className="text-center py-8">
            <div className="text-gray-400 text-lg mb-4">
              Enter a search query to explore the global cycles database
            </div>
            <div className="text-sm text-gray-500 space-y-2">
              <p><strong>Example searches:</strong></p>
              <p>• "empire" - Find all empire-related events</p>
              <p>• "eclipse" - Astronomical correlations</p>
              <p>• "vatican" - Vatican/Jesuit influence</p>
              <p>• "war" - Military conflicts and cycles</p>
              <p>• "babylon" - Specific civilization events</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
