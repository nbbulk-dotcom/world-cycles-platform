import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Navigation } from './components/Navigation'
import { HomePage } from './pages/HomePage'
import { GlobalAnalysisPage } from './pages/GlobalAnalysisPage'
import { VaticanAnalysisPage } from './pages/VaticanAnalysisPage'
import { PredictionsPage } from './pages/PredictionsPage'
import { CivilizationsPage } from './pages/CivilizationsPage'
import { SearchPage } from './pages/SearchPage'
import { RegionalAnalysisPage } from './pages/RegionalAnalysisPage'
import { AstronomicalPage } from './pages/AstronomicalPage'
import { AdvancedMechanicalAnalysisPage } from './pages/AdvancedMechanicalAnalysisPage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/global-analysis" element={<GlobalAnalysisPage />} />
            <Route path="/vatican-analysis" element={<VaticanAnalysisPage />} />
            <Route path="/predictions" element={<PredictionsPage />} />
            <Route path="/civilizations" element={<CivilizationsPage />} />
            <Route path="/astronomical" element={<AstronomicalPage />} />
            <Route path="/regional-analysis" element={<RegionalAnalysisPage />} />
            <Route path="/advanced-mechanical" element={<AdvancedMechanicalAnalysisPage />} />
            <Route path="/search" element={<SearchPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
