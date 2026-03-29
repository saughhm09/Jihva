import React from 'react'

const Analytics = ({ results }) => {
    return (
        <>
            <section className="brass-box panel gauge-panel">
                <h2 className="panel-title">Sentiment Pressure</h2>
                <div id="sentiment-output" className="gauge-container">
                    {!results ? (
                        <p className="placeholder-text">Insert data to build pressure.</p>
                    ) : results.sentiment && Object.keys(results.sentiment).length > 0 ? (
                        Object.entries(results.sentiment).map(([speaker, stats]) => (
                            <div key={speaker}>
                                <div><strong>{speaker}</strong></div>
                                <div className="bar-container">
                                    <div className="bar-pos" style={{ width: `${stats.positive}%` }} title="Positive"></div>
                                    <div className="bar-neu" style={{ width: `${stats.neutral}%` }} title="Neutral"></div>
                                    <div className="bar-neg" style={{ width: `${stats.negative}%` }} title="Negative"></div>
                                </div>
                                <div style={{ fontSize: '0.8rem', marginBottom: '15px' }}>
                                    POS: {stats.positive}% | NEU: {stats.neutral}% | NEG: {stats.negative}%
                                </div>
                            </div>
                        ))
                    ) : (
                        <p>Data insufficient for sentiment pressure calculation.</p>
                    )}
                </div>
            </section>
            
            <section className="brass-box panel accent-panel">
                <h2 className="panel-title">Accent Detection Meter</h2>
                <div id="accent-output" className="gauge-container center-text">
                    {!results ? (
                        <p className="placeholder-text">Scanning regional dialects.</p>
                    ) : results.accent ? (
                        <>
                            <div className="accent-result">{results.accent.prediction}</div>
                            {Object.entries(results.accent.confidences || {}).map(([dialect, conf]) => (
                                <p key={dialect}>{dialect}: {conf}%</p>
                            ))}
                        </>
                    ) : (
                        <p>No accent data available.</p>
                    )}
                </div>
            </section>
        </>
    )
}

export default Analytics