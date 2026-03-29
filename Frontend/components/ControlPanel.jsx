import React, { useState, useRef, useEffect } from 'react'

const ControlPanel = ({ onProcess, loading, loadingMessage }) => {
    const [speakerCount, setSpeakerCount] = useState(2)
    const [toggleFilter, setToggleFilter] = useState(true)
    const [toggleNoise, setToggleNoise] = useState(true)
    const [toggleSilence, setToggleSilence] = useState(false)
    const [uploadedFile, setUploadedFile] = useState(null)
    const [isRecording, setIsRecording] = useState(false)
    const [audioBlob, setAudioBlob] = useState(null)
    
    // MediaRecorder ref
    const mediaRecorderRef = useRef(null)
    const audioChunksRef = useRef([])

    useEffect(() => {
        // We will initialize the microphone on-demand instead of on load,
        // to prevent the browser from blocking the permission prompt!
    }, [])

    const handleFileUpload = (e) => {
        if (e.target.files.length > 0) {
            setUploadedFile(e.target.files[0])
            setAudioBlob(null) // clear recording if file used
        }
    }

    const startRecordingFlow = (mediaRecorder) => {
        audioChunksRef.current = []
        mediaRecorder.start()
        setIsRecording(true)
    }

    const toggleRecording = () => {
        if (!mediaRecorderRef.current) {
            // Initialize on demand
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({ audio: true })
                    .then(stream => {
                        const mediaRecorder = new MediaRecorder(stream)
                        mediaRecorderRef.current = mediaRecorder

                        mediaRecorder.ondataavailable = e => {
                            if (e.data && e.data.size > 0) {
                                audioChunksRef.current.push(e.data)
                            }
                        }

                        mediaRecorder.onstop = () => {
                            const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
                            setAudioBlob(blob)
                            audioChunksRef.current = [] // reset
                            setUploadedFile(null) // clear file if recording
                        }
                        
                        startRecordingFlow(mediaRecorder)
                    })
                    .catch(err => {
                        console.error('Microphone access denied:', err)
                        alert("Microphone access denied or not available.")
                    })
            } else {
                alert("Your browser does not support audio recording.")
            }
            return
        }

        if (!isRecording) {
            startRecordingFlow(mediaRecorderRef.current)
        } else {
            mediaRecorderRef.current.stop()
            setIsRecording(false)
        }
    }

    const handleProcess = () => {
        let finalFile = null
        if (uploadedFile) {
            finalFile = uploadedFile
        } else if (audioBlob) {
            // Browsers record in webm or similar, sending as webm allows backend ffmpeg to decode it
            finalFile = new File([audioBlob], "recording.webm", { type: "audio/webm" })
        } else {
            alert("No audio data found.")
            return
        }

        const formData = new FormData()
        formData.append("file", finalFile)
        formData.append("num_speakers", parseInt(speakerCount, 10))
        formData.append("remove_fillers", toggleFilter)
        formData.append("noise_reduction", toggleNoise)
        formData.append("silence_removal", toggleSilence)
        
        onProcess(formData)
    }

    const disableProcessBtn = loading || isRecording || (!uploadedFile && !audioBlob)
    const recBtnStyle = isRecording 
        ? { backgroundColor: "var(--bg-dark)", color: "#FF0000" } 
        : { backgroundColor: "#8B0000", color: "white" }

    const getProcessButtonText = () => {
        if (!mediaRecorderRef.current && !uploadedFile && !audioBlob) {
            return "AWAITING AUDIO ⚡"
        }
        if (uploadedFile) return `ENGAGE ENGINE ⚡ (${uploadedFile.name})`
        if (audioBlob) return "ENGAGE ENGINE ⚡ (Recorded Audio)"
        return "ENGAGE ENGINE ⚡"
    }

    return (
        <section className='brass-box panel control-panel'>
            <h2 className='panel-title'>Steam Console Control</h2>
            <div className='controls-grid'>
                <div className='control-group'>
                    <label>Action:</label>
                    <button 
                        id='btn-record' 
                        className='pixel-btn rec-btn' 
                        style={recBtnStyle} 
                        onClick={toggleRecording}
                    >
                        {isRecording ? "■ STOP" : "● REC"}
                    </button>
                    {isRecording && <span id='recording-indicator' className='blinking'>Recording. . .</span>}
                    <label className='custom-file-upload pixel-btn'>
                        <input type='file' id='file-upload' accept='audio/*' onChange={handleFileUpload} />
                        ↑ Upload .WAV
                    </label>
                </div>
                <div className='control-group'>
                    <label htmlFor='speaker-select'>Speaker Dial (2-5):</label>
                    <input 
                        type='range' 
                        id='speaker-select' 
                        min='2' 
                        max='5' 
                        value={speakerCount} 
                        onChange={(e) => setSpeakerCount(e.target.value)} 
                        className='brass-slider' 
                    />
                    <span id='speaker-val' className='val-display'>{speakerCount}</span>
                </div>
                <div className='control-group toggles'>
                    <label className='toggle-label'>
                        <input type='checkbox' checked={toggleFilter} onChange={() => setToggleFilter(!toggleFilter)} /> Filter Fillers
                    </label>
                    <label className='toggle-label'>
                        <input type='checkbox' checked={toggleNoise} onChange={() => setToggleNoise(!toggleNoise)} /> Noise Reduc
                    </label>
                    <label className='toggle-label'>
                        <input type='checkbox' checked={toggleSilence} onChange={() => setToggleSilence(!toggleSilence)} /> Silence Rem
                    </label>
                </div>
                <button 
                    id='process-btn' 
                    className='pixel-btn process-btn' 
                    disabled={disableProcessBtn}
                    onClick={handleProcess}
                >
                    {loading ? "PROCESSING..." : getProcessButtonText()}
                </button>
                {loading && (
                    <div id='loader'>
                        <div className='steam-loader'></div>
                        <p>{loadingMessage}</p>
                    </div>
                )}
            </div>
        </section>
    )
}

export default ControlPanel