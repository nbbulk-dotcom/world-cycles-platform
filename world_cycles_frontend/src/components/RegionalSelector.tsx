import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Calendar, MapPin } from 'lucide-react'

interface RegionalSelectorProps {
  onRegionSelect: (region: string, subregion: string, dateRange: {start: number, end: number}) => void
}

export function RegionalSelector({ onRegionSelect }: RegionalSelectorProps) {
  const [selectedRegion, setSelectedRegion] = useState<string>('')
  const [selectedSubregion, setSelectedSubregion] = useState<string>('')
  const [startYear, setStartYear] = useState<number>(-3000)
  const [endYear, setEndYear] = useState<number>(2025)

  const regionData = {
    americas: ['north_america', 'central_america', 'south_america'],
    asia: ['east_asia', 'southeast_asia', 'western_asia', 'south_asia', 'central_asia'],
    europe: ['northern_europe', 'southern_europe', 'eastern_europe', 'western_europe'],
    africa: ['central_africa', 'east_africa', 'north_africa', 'south_africa', 'west_africa'],
    oceania: ['oceania'],
    middle_east: ['middle_east'],
    arctic: ['arctic']
  }

  const handleAnalyze = () => {
    if (selectedRegion && selectedSubregion) {
      onRegionSelect(selectedRegion, selectedSubregion, { start: startYear, end: endYear })
    }
  }

  const handleRegionChange = (region: string) => {
    setSelectedRegion(region)
    setSelectedSubregion('')
  }

  return (
    <Card className="bg-black/40 border-purple-500/30">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2 text-white">
          <MapPin className="h-5 w-5 text-purple-400" />
          <span>Regional Cycle Analysis</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-300 mb-2 block">Region</label>
            <Select value={selectedRegion} onValueChange={handleRegionChange}>
              <SelectTrigger className="bg-black/20 border-gray-600 text-white">
                <SelectValue placeholder="Select region" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-600">
                {Object.keys(regionData).map(region => (
                  <SelectItem key={region} value={region} className="text-white">
                    {region.replace('_', ' ').toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {selectedRegion && (
            <div>
              <label className="text-sm text-gray-300 mb-2 block">Subregion</label>
              <Select value={selectedSubregion} onValueChange={setSelectedSubregion}>
                <SelectTrigger className="bg-black/20 border-gray-600 text-white">
                  <SelectValue placeholder="Select subregion" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-600">
                  {regionData[selectedRegion as keyof typeof regionData].map(subregion => (
                    <SelectItem key={subregion} value={subregion} className="text-white">
                      {subregion.replace('_', ' ').toUpperCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-300 mb-2 block">Start Year</label>
            <input
              type="number"
              value={startYear}
              onChange={(e) => setStartYear(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-black/20 border border-gray-600 rounded-md text-white"
              min={-3000}
              max={2025}
            />
          </div>
          <div>
            <label className="text-sm text-gray-300 mb-2 block">End Year</label>
            <input
              type="number"
              value={endYear}
              onChange={(e) => setEndYear(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-black/20 border border-gray-600 rounded-md text-white"
              min={-3000}
              max={2025}
            />
          </div>
        </div>

        <Button 
          onClick={handleAnalyze}
          disabled={!selectedRegion || !selectedSubregion}
          className="w-full bg-purple-600 hover:bg-purple-700"
        >
          <Calendar className="h-4 w-4 mr-2" />
          Analyze Regional Cycles
        </Button>
      </CardContent>
    </Card>
  )
}
