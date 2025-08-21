import { Link, useLocation } from 'react-router-dom'
import { Globe, Search, Calendar, Telescope, Building, TrendingUp, Eye, MapPin, Settings } from 'lucide-react'

export function Navigation() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Home', icon: Globe },
    { path: '/global-analysis', label: 'Global Analysis', icon: TrendingUp },
    { path: '/vatican-analysis', label: 'Vatican Analysis', icon: Eye },
    { path: '/predictions', label: 'Predictions', icon: Calendar },
    { path: '/civilizations', label: 'Civilizations', icon: Building },
    { path: '/astronomical', label: 'Astronomical', icon: Telescope },
    { path: '/regional-analysis', label: 'Regional Analysis', icon: MapPin },
    { path: '/advanced-mechanical', label: 'Advanced Mechanical', icon: Settings },
    { path: '/search', label: 'Search', icon: Search },
  ]

  return (
    <nav className="bg-black/20 backdrop-blur-md border-b border-purple-500/20">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <Globe className="h-8 w-8 text-purple-400" />
            <span className="text-xl font-bold text-white">World Cycles Platform</span>
          </div>
          
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-300 hover:bg-purple-700/50 hover:text-white'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}
