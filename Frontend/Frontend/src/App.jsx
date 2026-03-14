import { useState } from 'react'
import './App.css'
import Analytics from '../components/Analytics'
import ControlPanel from '../components/ControlPanel'
import HeaderSection from '../components/HeaderSection'
import KeywordAnalyzer from '../components/KeywordAnalyzer'
import SummaryChamber from '../components/SummaryChamber'
import TranscriptTerminal from '../components/TranscriptTerminal'

function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [summaryMode, setSummaryMode] = useState('Detailed')
  const [loadingMessage, setLoadingMessage] = useState('Processing text via clockwork mechanisms...')

  const processAudio = async (formData) => {
    formData.append("summary_mode", summaryMode)
    setLoading(true)
    setError(null)
    setResults(null)
    setLoadingMessage('Analyzing audio frequencies... Stand by...')
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/process-audio', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`)
      }
      
      const data = await response.json()
      setResults(data)
    } catch (err) {
      console.error("API Error:", err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <HeaderSection />
      <ControlPanel onProcess={processAudio} loading={loading} loadingMessage={loadingMessage} />
      <TranscriptTerminal results={results} error={error} loading={loading} />
      <Analytics results={results} />
      <KeywordAnalyzer results={results} />
      <SummaryChamber results={results} summaryMode={summaryMode} setSummaryMode={setSummaryMode} />
    </>
  )
}

export default App
