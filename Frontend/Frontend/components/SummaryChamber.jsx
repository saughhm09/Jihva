import React from 'react'

const SummaryChamber = ({ results, summaryMode, setSummaryMode }) => {
    const renderWithLineBreaks = (text) => {
        return text.split('\n').map((line, i) => (
            <React.Fragment key={i}>
                {line}
                <br />
            </React.Fragment>
        ));
    }

    return (
        <section className="brass-box panel summary-panel">
            <h2 className="panel-title">Steam Condenser Summary</h2>
            <div className="summary-controls">
                <select 
                    id="summary-mode" 
                    className="pixel-select" 
                    value={summaryMode} 
                    onChange={(e) => setSummaryMode(e.target.value)}
                >
                    <option value="Detailed">Detailed Extraction</option>
                    <option value="Short">Executive Output</option>
                    <option value="Bullet">Bullet Protocol</option>
                </select>
            </div>
            <div id="summary-output" className="parchment-screen">
                {!results ? (
                    <p className="placeholder-text">Ready to condense meaning.</p>
                ) : results.summary ? (
                    <>
                        <p><strong>[Compression Ratio: {results.summary.compression_ratio}x]</strong></p>
                        <h3>Overall Synthesis:</h3>
                        <p>{renderWithLineBreaks(results.summary.overall)}</p>

                        {Object.keys(results.summary.per_speaker || {}).length > 0 && (
                            <>
                                <h3>Speaker Contributions:</h3>
                                {Object.entries(results.summary.per_speaker).map(([spk, txt]) => (
                                    <p key={spk}><strong>{spk}</strong>: {renderWithLineBreaks(txt)}</p>
                                ))}
                            </>
                        )}
                    </>
                ) : (
                    <p>No summary generated.</p>
                )}
            </div>
        </section>
    )
}

export default SummaryChamber