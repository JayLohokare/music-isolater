document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const uploadPanel = document.getElementById('upload-panel');
    const processingPanel = document.getElementById('processing-panel');
    const resultPanel = document.getElementById('result-panel');
    const processingStatus = document.getElementById('processing-status');
    const errorMessage = document.getElementById('error-message');
    const tracksContainer = document.getElementById('tracks-container');
    const resetBtn = document.getElementById('reset-btn');

    // Drag and Drop Logic
    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    resetBtn.addEventListener('click', () => {
        resultPanel.classList.remove('active');
        uploadPanel.classList.add('active');
        fileInput.value = '';
    });

    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
        setTimeout(() => {
            errorMessage.classList.add('hidden');
        }, 5000);
    }

    function switchPanel(panelToShow) {
        [uploadPanel, processingPanel, resultPanel].forEach(panel => {
            if (panel === panelToShow) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });
    }

    async function handleFile(file) {
        // Basic validation
        const validTypes = ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/ogg', 'audio/mp4'];
        if (!validTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|flac|ogg|m4a)$/i)) {
            showError("Invalid file type. Please upload an audio file.");
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        switchPanel(processingPanel);
        processingStatus.textContent = "Uploading...";

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Upload failed");
            }

            // Upload succeeded, start polling for status
            pollStatus(data.task_id);
            
        } catch (err) {
            switchPanel(uploadPanel);
            showError(err.message);
        }
    }

    async function pollStatus(taskId) {
        processingStatus.textContent = "Separating Stems...";
        
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`/status/${taskId}`);
                const data = await response.json();

                if (data.status === 'done') {
                    clearInterval(interval);
                    renderResults(taskId, data.files);
                } else if (data.status === 'error') {
                    clearInterval(interval);
                    switchPanel(uploadPanel);
                    showError("Processing failed: " + data.error);
                }
                // If 'processing' or 'queued', wait for next interval
            } catch (err) {
                console.error("Error polling status", err);
            }
        }, 3000); // Check every 3 seconds
    }

    function renderResults(taskId, files) {
        tracksContainer.innerHTML = ''; // clear previous
        
        // Define icons for typical stem names
        const icons = {
            'vocals': '🎤',
            'drums': '🥁',
            'bass': '🎸',
            'other': '🎹'
        };

        files.forEach(file => {
            const nameWithoutExt = file.replace('.wav', '');
            const stemType = nameWithoutExt.toLowerCase();
            const icon = icons[stemType] || '🎵';

            const trackHTML = `
                <div class="track-item">
                    <div class="track-icon ${stemType}">
                        ${icon}
                    </div>
                    <div class="track-info">
                        <h4>${nameWithoutExt}</h4>
                        <audio class="custom-audio-player" controls preload="none">
                            <source src="/listen/${taskId}/${file}" type="audio/wav">
                            Your browser does not support the audio element.
                        </audio>
                    </div>
                    <a href="/download/${taskId}/${file}" class="download-btn" title="Download Setup">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </a>
                </div>
            `;
            tracksContainer.insertAdjacentHTML('beforeend', trackHTML);
        });

        switchPanel(resultPanel);
    }
});
