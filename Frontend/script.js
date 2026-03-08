// DOM Elements
const btnRecord = document.getElementById('btn-record');
const recIndicator = document.getElementById('recording-indicator');
const fileUpload = document.getElementById('file-upload');
const processBtn = document.getElementById('process-btn');
const speakerSelect = document.getElementById('speaker-select');
const speakerVal = document.getElementById('speaker-val');

// Toggles
const toggleFilter = document.getElementById('toggle-filter');
const toggleNoise = document.getElementById('toggle-noise');
const toggleSilence = document.getElementById('toggle-silence');
const summaryMode = document.getElementById('summary-mode');

// Output Panels
const transcriptOut = document.getElementById('transcript-output');
const sentimentOut = document.getElementById('sentiment-output');
const accentOut = document.getElementById('accent-output');
const keywordOut = document.getElementById('keyword-output');
const summaryOut = document.getElementById('summary-output');
const loader = document.getElementById('loader');

// Audio Recording Setup
let mediaRecorder;
let audioChunks = [];
let audioBlob = null;
let isRecording = false;
let uploadedFile = null;

// Update Speaker Slider value
speakerSelect.addEventListener('input', (e) => {
    speakerVal.textContent = e.target.value;
});

// File Upload Event
fileUpload.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        uploadedFile = e.target.files[0];
        audioBlob = null; // Clear recorded blob if file is uploaded
        btnRecord.textContent = "● REC";
        btnRecord.style.backgroundColor = "#8B0000";
        btnRecord.style.color = "white";
        processBtn.disabled = false;
        processBtn.textContent = `ENGAGE ENGINE ⚡ (${uploadedFile.name})`;
    }
});

// Setup MediaRecorder
async function setupAudio() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = e => {
                audioChunks.push(e.data);
            };
            
            mediaRecorder.onstop = () => {
                audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioChunks = [];
                uploadedFile = null; // Clear uploaded file if we just recorded
                processBtn.disabled = false;
                processBtn.textContent = "ENGAGE ENGINE ⚡ (Recorded Audio)";
            };
        } catch (err) {
            console.error('Microphone access denied:', err);
            processBtn.textContent = "MIC ERROR";
        }
    }
}

// Ensure Audio Setup
setupAudio();

// Record Button Click
btnRecord.addEventListener('click', () => {
    if (!mediaRecorder) {
        alert("Microphone not initialized. Please ensure access is allowed.");
        return;
    }
    
    if (!isRecording) {
        // Start
        audioChunks = [];
        mediaRecorder.start();
        isRecording = true;
        btnRecord.textContent = "■ STOP";
        btnRecord.style.backgroundColor = "var(--bg-dark)";
        btnRecord.style.color = "#FF0000";
        recIndicator.classList.remove('hidden');
        processBtn.disabled = true;
    } else {
        // Stop
        mediaRecorder.stop();
        isRecording = false;
        btnRecord.textContent = "● REC";
        btnRecord.style.backgroundColor = "#8B0000";
        btnRecord.style.color = "white";
        recIndicator.classList.add('hidden');
    }
});

// Process Button Click (Send to API)
processBtn.addEventListener('click', async () => {
    let finalFile = null;
    
    if (uploadedFile) {
        finalFile = uploadedFile;
    } else if (audioBlob) {
        finalFile = new File([audioBlob], "recording.wav", { type: "audio/wav" });
    } else {
        alert("No audio data found.");
        return;
    }
    
    const formData = new FormData();
    formData.append("file", finalFile);
    formData.append("num_speakers", speakerSelect.value);
    formData.append("remove_fillers", toggleFilter.checked);
    formData.append("noise_reduction", toggleNoise.checked);
    formData.append("silence_removal", toggleSilence.checked);
    formData.append("summary_mode", summaryMode.value);
    
    // UI Update
    processBtn.disabled = true;
    loader.classList.remove('hidden');
    clearOutputs();
    transcriptOut.innerHTML = "<p>Analyzing audio frequencies... Stand by...</p>";
    
    try {
        const response = await fetch("/api/process-audio", {
            method: "POST",
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }
        
        const data = await response.json();
        renderResults(data);
        
    } catch (error) {
        console.error("API Error:", error);
        transcriptOut.innerHTML = `<p style="color:var(--terminal-green)">[SYSTEM ERROR] Connection failed or processing aborted.<br>${error.message}</p>`;
    } finally {
        processBtn.disabled = false;
        loader.classList.add('hidden');
    }
});

function clearOutputs() {
    transcriptOut.innerHTML = "";
    sentimentOut.innerHTML = "";
    accentOut.innerHTML = "";
    keywordOut.innerHTML = "";
    summaryOut.innerHTML = "";
}

function renderResults(data) {
    // 1. Transcript
    let tHTML = `<p>[Language Detected: ${data.language_info.language} | Confidence: ${(data.language_info.confidence*100).toFixed(1)}%]</p><br>`;
    if (data.segments && data.segments.length > 0) {
        data.segments.forEach(seg => {
            tHTML += `<p><strong>${seg.time_str}</strong>: ${seg.text}</p>`;
        });
    } else {
        tHTML += `<p>No speech detected or processing failed.</p>`;
    }
    tHTML += `<span class="cursor">_</span>`;
    transcriptOut.innerHTML = tHTML;
    
    // 2. Sentiment
    let sHTML = "";
    if (Object.keys(data.sentiment).length > 0) {
        for (const [speaker, stats] of Object.entries(data.sentiment)) {
            sHTML += `<div><strong>${speaker}</strong></div>`;
            sHTML += `
                <div class="bar-container">
                    <div class="bar-pos" style="width: ${stats.positive}%" title="Positive"></div>
                    <div class="bar-neu" style="width: ${stats.neutral}%" title="Neutral"></div>
                    <div class="bar-neg" style="width: ${stats.negative}%" title="Negative"></div>
                </div>
                <div style="font-size:0.8rem; margin-bottom:15px;">POS: ${stats.positive}% | NEU: ${stats.neutral}% | NEG: ${stats.negative}%</div>
            `;
        }
    } else {
        sHTML = "<p>Data insufficient for sentiment pressure calculation.</p>";
    }
    sentimentOut.innerHTML = sHTML;
    
    // 3. Accent
    if (data.accent) {
        let aHTML = `<div class="accent-result">${data.accent.prediction}</div>`;
        for (const [dialect, conf] of Object.entries(data.accent.confidences)) {
            aHTML += `<p>${dialect}: ${conf}%</p>`;
        }
        accentOut.innerHTML = aHTML;
    }
    
    // 4. Keywords
    let kHTML = "";
    if (data.keywords && Object.keys(data.keywords).length > 0) {
        for (const [word, count] of Object.entries(data.keywords)) {
            // Scale font size based on count, bounded
            let size = Math.min(2.0, 1.0 + (count * 0.1));
            kHTML += `<span class="keyword-item" style="font-size:${size}rem">${word} (${count})</span>`;
        }
    } else {
        kHTML = "<p>No significant keywords detected.</p>";
    }
    keywordOut.innerHTML = kHTML;
    
    // 5. Summary
    if (data.summary) {
        let sumHTML = `<p><strong>[Compression Ratio: ${data.summary.compression_ratio}x]</strong></p>`;
        sumHTML += `<h3>Overall Synthesis:</h3>`;
        // Format bullet points properly with HTML line breaks
        sumHTML += `<p>${data.summary.overall.replace(/\n/g, '<br>')}</p>`;
        
        if (Object.keys(data.summary.per_speaker).length > 0) {
            sumHTML += `<h3>Speaker Contributions:</h3>`;
            for (const [spk, txt] of Object.entries(data.summary.per_speaker)) {
                sumHTML += `<p><strong>${spk}</strong>: ${txt.replace(/\n/g, '<br>')}</p>`;
            }
        }
        summaryOut.innerHTML = sumHTML;
    }
}
