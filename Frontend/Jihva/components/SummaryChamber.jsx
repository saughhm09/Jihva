import React from 'react'

const SummaryChamber = () => {
    return (
        <section className="brass-box panel summary-panel">
            <h2 className="panel-title">Steam Condenser Summary</h2>
            <div className="summary-controls">
                <select id="summary-mode" className="pixel-select">
                    <option value="Detailed">Detailed Extraction</option>
                    <option value="Short">Executive Output</option>
                    <option value="Bullet">Bullet Protocol</option>
                </select>
            </div>
            <div id="summary-output" className="parchment-screen">
                <p className="placeholder-text">Ready to condense meaning.</p>
            </div>
        </section>
    )
}

export default SummaryChamber