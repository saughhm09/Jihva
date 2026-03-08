import React from 'react'

const Analytics = () => {
    return (
        <>
            <section className="brass-box panel gauge-panel">
                <h2 className="panel-title">Sentiment Pressure</h2>
                <div id="sentiment-output" className="gauge-container">
                    <p className="placeholder-text">Insert data to build pressure.</p>
                </div>
            </section>
            <section className="brass-box panel accent-panel">
                <h2 className="panel-title">Accent Detection Meter</h2>
                <div id="accent-output" className="gauge-container center-text">
                    <p className="placeholder-text">Scanning regional dialects.</p>
                </div>
            </section>
        </>
    )
}

export default Analytics