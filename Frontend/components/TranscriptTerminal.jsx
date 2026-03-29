import React from 'react'

const TranscriptTerminal = ({ results, error, loading }) => {
    let content = <p>Awaiting audio input...</p>

    if (error) {
        content = <p style={{ color: 'var(--terminal-green)' }}>[SYSTEM ERROR] Connection failed.<br />{error}</p>
    } else if (loading) {
        content = <p>Analyzing audio frequencies... Stand by...</p>
    } else if (results) {
        content = (
            <>
                <p>
                    [Language Detected: {results.language_info?.language} | Confidence: {((results.language_info?.confidence || 0) * 100).toFixed(1)}%]
                </p>
                <br />
                {results.segments && results.segments.length > 0 ? (
                    results.segments.map((seg, idx) => (
                        <p key={idx}><strong>{seg.time_str}</strong>: {seg.text}</p>
                    ))
                ) : (
                    <p>No speech detected or processing failed.</p>
                )}
            </>
        )
    }

    return (
        <section className="brass-box panel terminal-panel">
            <h2 className="panel-title">Transcript Terminal</h2>
            <div id="transcript-output" className="terminal-screen">
                {content}
                <span className="cursor">_</span>
            </div>
        </section>
    )
}

export default TranscriptTerminal