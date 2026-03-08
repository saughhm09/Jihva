import React from 'react'

const ControlPanel = () => {
    return (
        <section className='brass-box panel control-panel'>
            <h2 className='panel-title'>Steam Console Control</h2>
            <div className='controls-grid'>
                <div className='control-group'>
                    <label>Action:</label>
                    <button id='btn-record' className='pixel-btn rec-btn'>● REC</button>
                    <span id='recording-indicator' className='hidden blinking'>Recording. . .</span>
                    <label className='custom-file-upload pixel-btn'>
                        <input type='file' id='file-upload' accept='audio/*' />
                        ↑ Upload .WAV
                    </label>
                </div>
                <div className='control-group'>
                    <label for='speaker-select'>Speaker Dial (2-5):</label>
                    <input type='range' id='speaker-select' min='2' max='5' value='2' className='brass-slider' />
                    <span id='speaker-val' className='val-display'>2</span>
                </div>
                <div className='control-group toggles'>
                    <label className='toggle-label'><input type='checkbox' id='toggle-filter' checked /> Filter Fillers</label>
                    <label className='toggle-label'><input type='checkbox' id='toggle-noise' checked /> Noise Reduc</label>
                    <label className='toggle-label'><input type='checkbox' id='toggle-silence' /> Silence Rem</label>
                </div>
                <button id='process-btn' className='pixel-btn process-btn' disabled>ENGAGE ENGINE ⚡</button>
                <div id='loader' className='hidden'>
                    <div className='steam-loader'></div>
                    <p>Processing text via clockwork mechanisms...</p>
                </div>
            </div>
        </section>
    )
}

export default ControlPanel