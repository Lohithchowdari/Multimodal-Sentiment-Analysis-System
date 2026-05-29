// ==================== AUDIO RECORDING ====================

let mediaRecorder;
let audioChunks = [];
let recordingTimer;
let countdownInterval;

function startCountdown(callback) {
    let count = 3;
    const countdownEl = document.getElementById('countdown');
    const micBtn = document.getElementById('mic-button');
    
    if (countdownEl) {
        countdownEl.style.display = 'block';
        countdownEl.textContent = count;
        
        countdownInterval = setInterval(() => {
            count--;
            if (count > 0) {
                countdownEl.textContent = count;
            } else {
                clearInterval(countdownInterval);
                countdownEl.style.display = 'none';
                callback();
            }
        }, 1000);
    }
}

async function startRecording() {
    const micBtn = document.getElementById('mic-button');
    const statusEl = document.getElementById('recording-status');
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                sampleSize: 16
            } 
        });
        
        startCountdown(() => {
            // Try to use WAV format if supported, otherwise use webm
            let options = { mimeType: 'audio/webm' };
            
            mediaRecorder = new MediaRecorder(stream, options);
            audioChunks = [];
            
            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });
            
            mediaRecorder.addEventListener('stop', () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                uploadAudio(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            });
            
            mediaRecorder.start();
            micBtn.classList.add('recording');
            micBtn.innerHTML = '<i class="fas fa-stop"></i>';
            statusEl.textContent = 'Recording... Click to stop';
            statusEl.style.color = 'var(--danger)';
            
            // Auto-stop after 30 seconds
            recordingTimer = setTimeout(() => {
                stopRecording();
            }, 30000);
        });
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Could not access microphone. Please check permissions.');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        clearTimeout(recordingTimer);
        mediaRecorder.stop();
        
        const micBtn = document.getElementById('mic-button');
        const statusEl = document.getElementById('recording-status');
        
        micBtn.classList.remove('recording');
        micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        statusEl.textContent = 'Processing audio...';
        statusEl.style.color = 'var(--primary)';
    }
}

function toggleRecording() {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        startRecording();
    } else {
        stopRecording();
    }
}

async function uploadAudio(audioBlob) {
    const loadingEl = document.getElementById('loading-overlay');
    const resultEl = document.getElementById('audio-result');
    
    if (loadingEl) loadingEl.style.display = 'flex';
    
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    
    try {
        const response = await fetch('/api/audio-analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (loadingEl) loadingEl.style.display = 'none';
        
        if (data.error) {
            alert(data.error);
            location.reload();
        } else {
            displayAudioResult(data);
        }
        
    } catch (error) {
        console.error('Error uploading audio:', error);
        if (loadingEl) loadingEl.style.display = 'none';
        alert('Failed to analyze audio. Please try again.');
        location.reload();
    }
}

function displayAudioResult(data) {
    const resultEl = document.getElementById('audio-result');
    const recordingControlEl = document.getElementById('recording-control');
    
    if (recordingControlEl) recordingControlEl.style.display = 'none';
    
    const sentimentIcons = {
        positive: '😊',
        neutral: '😐',
        negative: '😔'
    };
    
    const sentimentTexts = {
        positive: 'Positive',
        neutral: 'Neutral',
        negative: 'Negative'
    };
    
    resultEl.innerHTML = `
        <div class="result-card fade-in">
            <div class="result-icon ${data.sentiment}">
                ${sentimentIcons[data.sentiment]}
            </div>
            <h2>Analysis Complete</h2>
            <div class="sentiment-badge sentiment-${data.sentiment}">
                ${sentimentTexts[data.sentiment]} Sentiment
            </div>
            <div class="suggestion-box">
                <h4>💡 Insight & Suggestion</h4>
                <p>${data.suggestion}</p>
                ${data.sentiment === 'negative' ? '<p class="mt-2"><strong>📧 A support email has been sent to you.</strong></p>' : ''}
            </div>
            <div class="mt-4">
                <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
                <a href="/audio-analysis" class="btn btn-secondary">Analyze Again</a>
            </div>
        </div>
    `;
    
    resultEl.style.display = 'block';
}

// ==================== ANALYTICS CHARTS ====================

async function loadAnalytics() {
    const days = document.getElementById('days-select')?.value || 30;
    
    try {
        const response = await fetch(`/api/analytics-data?days=${days}`);
        const data = await response.json();
        
        // Timeline Chart
        const timelineCtx = document.getElementById('timeline-chart');
        if (timelineCtx) {
            if (window.timelineChart) {
                window.timelineChart.destroy();
            }
            
            window.timelineChart = new Chart(timelineCtx, {
                type: 'line',
                data: {
                    labels: data.timeline.labels,
                    datasets: [
                        {
                            label: 'Positive',
                            data: data.timeline.positive,
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'Neutral',
                            data: data.timeline.neutral,
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'Negative',
                            data: data.timeline.negative,
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            fill: true,
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#cbd5e1' }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(139, 92, 246, 0.1)' }
                        },
                        x: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(139, 92, 246, 0.1)' }
                        }
                    }
                }
            });
        }
        
        // Distribution Chart
        const distributionCtx = document.getElementById('distribution-chart');
        if (distributionCtx) {
            if (window.distributionChart) {
                window.distributionChart.destroy();
            }
            
            window.distributionChart = new Chart(distributionCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Text Analysis', 'Image Analysis', 'Audio Analysis'],
                    datasets: [{
                        data: [data.distribution.text, data.distribution.image, data.distribution.audio],
                        backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#cbd5e1' }
                        }
                    }
                }
            });
        }
        
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// ==================== ADMIN USER ANALYTICS ====================

async function loadUserAnalytics(userId) {
    const days = document.getElementById('admin-days-select')?.value || 30;
    
    try {
        const response = await fetch(`/admin/api/user-analytics/${userId}?days=${days}`);
        const data = await response.json();
        
        const ctx = document.getElementById('user-timeline-chart');
        if (ctx) {
            if (window.userTimelineChart) {
                window.userTimelineChart.destroy();
            }
            
            window.userTimelineChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Positive',
                            data: data.positive,
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'Neutral',
                            data: data.neutral,
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'Negative',
                            data: data.negative,
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            fill: true,
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#cbd5e1' }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(139, 92, 246, 0.1)' }
                        },
                        x: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(139, 92, 246, 0.1)' }
                        }
                    }
                }
            });
        }
        
    } catch (error) {
        console.error('Error loading user analytics:', error);
    }
}

// ==================== IMAGE PREVIEW ====================

function previewImage(input) {
    const preview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            previewImg.src = e.target.result;
            preview.style.display = 'block';
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// ==================== SMOOTH SCROLL ====================

document.addEventListener('DOMContentLoaded', () => {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// ==================== AUTO-HIDE ALERTS ====================

setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}, 100);