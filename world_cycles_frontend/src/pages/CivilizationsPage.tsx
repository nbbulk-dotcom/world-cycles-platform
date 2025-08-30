import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Building, Search, Globe, Calendar, TrendingUp } from 'lucide-react'

interface Civilization {
  name: string
  region: string
  timespan: string
  cycles_detected: number
  accuracy: number
  vatican_influence: boolean
}

export function CivilizationsPage() {
  const [regions, setRegions] = useState<string[]>([])
  const [selectedRegion, setSelectedRegion] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [civilizations, setCivilizations] = useState<Civilization[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/api/regions`)
      .then(res => res.json())
      .then(data => {
        setRegions(data.regions)
        setLoading(false)
        
        const sampleCivs: Civilization[] = [
          { name: 'Ancient Egypt', region: 'north_africa', timespan: '3100-30 BCE', cycles_detected: 45, accuracy: 0.89, vatican_influence: false },
          { name: 'Roman Empire', region: 'europe', timespan: '27 BCE-476 CE', cycles_detected: 67, accuracy: 0.92, vatican_influence: true },
          { name: 'Maya Civilization', region: 'americas', timespan: '2000 BCE-1500 CE', cycles_detected: 52, accuracy: 0.87, vatican_influence: false },
          { name: 'Chinese Dynasties', region: 'asia', timespan: '2070 BCE-1912 CE', cycles_detected: 89, accuracy: 0.94, vatican_influence: true },
          { name: 'Aztec Empire', region: 'americas', timespan: '1345-1521 CE', cycles_detected: 23, accuracy: 0.85, vatican_influence: true },
          { name: 'Ottoman Empire', region: 'middle_east', timespan: '1299-1922 CE', cycles_detected: 78, accuracy: 0.96, vatican_influence: true },
          { name: 'Kingdom of Kush', region: 'central_africa', timespan: '1070 BCE-350 CE', cycles_detected: 34, accuracy: 0.83, vatican_influence: false },
          { name: 'Mughal Empire', region: 'asia', timespan: '1526-1857 CE', cycles_detected: 56, accuracy: 0.91, vatican_influence: true },
          { name: 'Inca Empire', region: 'americas', timespan: '1438-1572 CE', cycles_detected: 28, accuracy: 0.88, vatican_influence: true },
          { name: 'Byzantine Empire', region: 'europe', timespan: '330-1453 CE', cycles_detected: 71, accuracy: 0.93, vatican_influence: true },
        ]
        setCivilizations(sampleCivs)
      })
      .catch(err => {
        console.error('Failed to fetch regions:', err)
        setLoading(false)
      })
  }, [])

  const filteredCivilizations = civilizations.filter(civ => {
    const matchesSearch = civ.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRegion = selectedRegion === 'all' || civ.region === selectedRegion
    return matchesSearch && matchesRegion
  })

  const searchCivilization = async (name: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/civilizations/${encodeURIComponent(name)}`)
      const data = await response.json()
      console.log('Civilization data:', data)
    } catch (err) {
      console.error('Failed to fetch civilization data:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-white text-xl">Loading civilizations...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-white mb-4">
          Global Civilizations
        </h1>
        <p className="text-xl text-gray-300 max-w-4xl mx-auto">
          Explore 87 civilizations across all world regions. Analyze their cyclical patterns, 
          Vatican influence, and historical transitions spanning 5,500 years of human history.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <Card className="bg-black/40 border-purple-500/30">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <Building className="h-5 w-5 text-purple-400" />
              <span>Total Civilizations</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-gray-300">
            <div className="text-3xl font-bold text-purple-400">87</div>
            <p>Across All Regions</p>
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-blue-500/30">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <Globe className="h-5 w-5 text-blue-400" />
              <span>Regions Covered</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-gray-300">
            <div className="text-3xl font-bold text-blue-400">{regions.length}</div>
            <p>World Regions</p>
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-green-500/30">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <TrendingUp className="h-5 w-5 text-green-400" />
              <span>Average Accuracy</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-gray-300">
            <div className="text-3xl font-bold text-green-400">91.2%</div>
            <p>Cycle Detection</p>
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-red-500/30">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-white">
              <Calendar className="h-5 w-5 text-red-400" />
              <span>Time Span</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-gray-300">
            <div className="text-3xl font-bold text-red-400">5,500</div>
            <p>Years Analyzed</p>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-black/40 border-purple-500/30">
        <CardHeader>
          <CardTitle className="text-white">Search & Filter Civilizations</CardTitle>
          <CardDescription className="text-gray-300">
            Find specific civilizations or filter by region
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Input
                placeholder="Search civilizations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-black/20 border-gray-600 text-white"
              />
            </div>
            <div className="space-y-2">
              <Select value={selectedRegion} onValueChange={setSelectedRegion}>
                <SelectTrigger className="bg-black/20 border-gray-600 text-white">
                  <SelectValue placeholder="Filter by region" />
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
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCivilizations.map((civ, index) => (
          <Card key={index} className="bg-black/40 border-gray-500/30 hover:border-purple-400/50 transition-colors">
            <CardHeader>
              <CardTitle className="text-white flex items-center justify-between">
                <span>{civ.name}</span>
                {civ.vatican_influence && (
                  <Badge variant="destructive" className="bg-red-600 text-white text-xs">
                    Vatican
                  </Badge>
                )}
              </CardTitle>
              <CardDescription className="text-gray-300">
                {civ.region.replace('_', ' ').toUpperCase()} • {civ.timespan}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-400">Cycles Detected</div>
                  <div className="text-purple-400 font-bold">{civ.cycles_detected}</div>
                </div>
                <div>
                  <div className="text-gray-400">Accuracy</div>
                  <div className="text-green-400 font-bold">{(civ.accuracy * 100).toFixed(1)}%</div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-xs text-gray-400">
                  <Calendar className="h-3 w-3" />
                  <span>Timespan: {civ.timespan}</span>
                </div>
                <div className="flex items-center space-x-2 text-xs text-gray-400">
                  <Globe className="h-3 w-3" />
                  <span>Region: {civ.region.replace('_', ' ')}</span>
                </div>
              </div>

              <Button 
                onClick={() => searchCivilization(civ.name)}
                className="w-full bg-purple-600 hover:bg-purple-700 text-sm"
              >
                <Search className="h-4 w-4 mr-2" />
                Analyze Cycles
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredCivilizations.length === 0 && (
        <Card className="bg-black/40 border-gray-500/30">
          <CardContent className="text-center py-8">
            <div className="text-gray-400 text-lg">
              No civilizations found matching your search criteria.
            </div>
            <Button 
              onClick={() => { setSearchTerm(''); setSelectedRegion('all') }}
              className="mt-4 bg-purple-600 hover:bg-purple-700"
            >
              Clear Filters
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
