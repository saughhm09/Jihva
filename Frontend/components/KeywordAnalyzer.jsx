import React from 'react'

const KeywordAnalyzer = ({ results }) => {
    return (
        <section className="brass-box panel keyword-panel">
            <h2 className="panel-title">Keyword Analyzer</h2>
            <div id="keyword-output" className="keyword-cloud">
                {!results ? (
                    <p className="placeholder-text">Awaiting frequency extraction.</p>
                ) : results.keywords && Object.keys(results.keywords).length > 0 ? (
                    Object.entries(results.keywords).map(([word, count]) => {
                        let size = Math.min(2.0, 1.0 + (count * 0.1));
                        return (
                            <span key={word} className="keyword-item" style={{ fontSize: `${size}rem` }}>
                                {word} ({count})
                            </span>
                        )
                    })
                ) : (
                    <p>No significant keywords detected.</p>
                )}
            </div>
        </section>
    )
}

export default KeywordAnalyzer