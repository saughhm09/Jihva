import { useState } from 'react'
import './App.css'
import Analytics from '../components/Analytics'
import ControlPanel from '../components/ControlPanel'
import HeaderSection from '../components/HeaderSection'
import KeywordAnalyzer from '../components/KeywordAnalyzer'
import SummaryChamber from '../components/SummaryChamber'
import TranscriptTerminal from '../components/TranscriptTerminal'

function App() {

  return (
    <>
      <HeaderSection />
      <ControlPanel />
      <TranscriptTerminal />
      <Analytics />
      <KeywordAnalyzer />
      <SummaryChamber />
    </>
  )
}

export default App
