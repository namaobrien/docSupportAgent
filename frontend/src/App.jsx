import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import IssueBrowser from './components/IssueBrowser'
import AnalysisDashboard from './components/AnalysisDashboard'
import ReviewQueue from './components/ReviewQueue'
import FastResults from './components/FastResults'
import './styles/App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="container">
            <div className="nav-content">
              <h1 className="nav-title">Doc Support Agent</h1>
              <div className="nav-links">
                <Link to="/" className="nav-link">Issues</Link>
                <Link to="/review-queue" className="nav-link">Review Queue</Link>
              </div>
            </div>
          </div>
        </nav>
        
        <main className="main-content">
          <div className="container">
            <Routes>
              <Route path="/" element={<IssueBrowser />} />
              <Route path="/analysis/:analysisId" element={<AnalysisDashboard />} />
              <Route path="/results" element={<FastResults />} />
              <Route path="/review-queue" element={<ReviewQueue />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  )
}

export default App

