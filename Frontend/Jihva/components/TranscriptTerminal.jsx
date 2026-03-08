import React from 'react'

const TranscriptTerminal = () => {
    return (
        <section className="brass-box panel terminal-panel">
            <h2 className="panel-title">Transcript Terminal</h2>
            <div id="transcript-output" className="terminal-screen">
                <span className="cursor">_</span>
                <p>Awaiting audio input...</p>
            </div>
        </section>
    )
}

export default TranscriptTerminal