const SPELL_ANIMATIONS = {
    Lumos: {
        animation: 'Lumos.gif',
        idle: null,
        duration: 5000
    },
    Accio: {
        animation: 'Accio.gif',
        idle: 'first-frame',
        duration: 3000
    },
    Alohomora: {
        animation: 'Alohomora.gif',
        idle: 'first-frame',
        duration: 3500
    },
    'Avada Kedavra': {
        animation: 'Avada Kedavra.gif',
        idle: 'enemy-idle',
        idleAnimation: 'enemy idle.gif',
        duration: 5000
    },
    Crucio: {
        animation: 'Crucio.gif',
        idle: 'enemy-idle',
        idleAnimation: 'enemy II idle.gif',
        duration: 5000
    },
    Expelliarmus: {
        animation: 'Expelliarmus.gif',
        idle: 'first-frame',
        duration: 3800
    },
    'Expecto Patronum': {
        animation: 'Expecto Patronum.gif',
        idle: 'enemy-idle',
        idleAnimation: 'enemy idle.gif',
        duration: 5000
    },
    Nox: {
        animation: null,
        idle: 'lumos-animation',
        idleAnimation: 'Lumos.gif',
        duration: 2000
    },
    'Wingardium Leviosa': {
        animation: 'Wingardium Leviosa.gif',
        idle: 'enemy-idle',
        idleAnimation: 'Wingardium Leviosa idle.gif',
        duration: 5000
    },
    'Petrificus Totalus': {
        animation: 'Petrificus Totalus.gif',
        idle: 'enemy-idle',
        idleAnimation: 'enemy II idle.gif',
        duration: 5000
    },
    Stupefy: {
        animation: 'Stupefy.gif',
        idle: 'enemy-idle',
        idleAnimation: 'enemy II idle.gif',
        duration: 5000
    },
    Rictusempra: {
        animation: 'Rictusempra.gif',
        idle: 'first-frame',
        duration: 3000
    },
    Expulso: {
        animation: 'Expulso.gif',
        idle: 'enemy-idle',
        idleAnimation: 'Expulso idle.gif',
        duration: 5000
    },
    Diffindo: {
        animation: 'Diffindo.gif',
        idle: 'enemy-idle',
        idleAnimation: 'slime idle.gif',
        duration: 5000
    },
    Reparo: {
        animation: 'Reparo.gif',
        idle: 'first-frame',
        duration: 4500
    },
    Obliviate: {
        animation: 'Obliviate.gif',
        idle: 'first-frame',
        duration: 4000
    },
    Silencio: {
        animation: 'Silencio.gif',
        idle: 'first-frame',
        duration: 3200
    },
    Incendio: {
        animation: 'Incendio.gif',
        idle: 'first-frame',
        duration: 3800
    },
    Aguamenti: {
        animation: 'Aguamenti.gif',
        idle: 'enemy-idle',
        idleAnimation: 'Aguamenti dile.gif',
        duration: 3500
    },
    'Finite Incantatem': {
        animation: 'enemy II idle.gif',
        idle: 'enemy-idle',
        idleAnimation: 'Petrificus Totalus.gif',
        duration: 5000
    },
    Rennervate: {
        animation: 'Rennervate.gif',
        idle: 'first-frame',
        duration: 3600
    },
    Colloportus: {
        animation: 'Colloportus.gif',
        idle: 'first-frame',
        duration: 3300
    },
    Reducto: {
        animation: 'Reducto.gif',
        idle: 'enemy-idle',
        idleAnimation: 'Expulso idle.gif',
        duration: 850
    },
    Impervius: {
        animation: 'Impervius.gif',
        idle: 'enemy-idle',
        idleAnimation: 'joey idle.gif',
        duration: 4000
    },
    Tarantallegra: {
        animation: 'Tarantallegra.gif',
        idle: 'enemy-idle',
        idleAnimation: 'Skeleton Idle.gif',
        duration: 5000
    },
    Obscuro: {
        animation: 'Obscuro.gif',
        idle: 'enemy-idle',
        idleAnimation: 'joey idle.gif',
        duration: 5000
    }
};

let recognition = null;
let isListening = false;
let currentAnimation = null;
let currentSpell = null;

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let audioStream = null;
let currentMimeType = 'audio/webm';

function initSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.warn('Speech recognition not supported in this browser');
        return false;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript.trim();
        console.log('Recognized:', transcript);
        handleSpellRecognition(transcript);
    };

    recognition.onerror = (event) => {
        console.error('Recognition error:', event.error);
        updateOutputWindow('Recognition error: ' + event.error);
        isListening = false;
        updateVoiceButton();
    };

    recognition.onend = () => {
        isListening = false;
        updateVoiceButton();
        if (!currentAnimation) {
            updateOutputWindow('Recognition ended. Click to try again.');
        }
    };

    return true;
}

function handleSpellRecognition(transcript) {
    const normalized = transcript.toLowerCase().trim();
    
    if (SPELL_ANIMATIONS[transcript]) {
        playSpellAnimation(transcript);
        updateOutputWindow(`Recognized: ${transcript}`, transcript);
        return;
    }
    
    if (normalized.includes('lumos')) {
        playSpellAnimation('Lumos');
        updateOutputWindow('Recognized: Lumos', 'Lumos');
    } else if (normalized.includes('accio')) {
        playSpellAnimation('Accio');
        updateOutputWindow('Recognized: Accio', 'Accio');
    } else if (normalized.includes('alohomora')) {
        playSpellAnimation('Alohomora');
        updateOutputWindow('Recognized: Alohomora', 'Alohomora');
    } else if (normalized.includes('avada') || normalized.includes('kedavra')) {
        playSpellAnimation('Avada Kedavra');
        updateOutputWindow('Recognized: Avada Kedavra', 'Avada Kedavra');
    } else if (normalized.includes('crucio')) {
        playSpellAnimation('Crucio');
        updateOutputWindow('Recognized: Crucio', 'Crucio');
    } else if (normalized.includes('expelliarmus')) {
        playSpellAnimation('Expelliarmus');
        updateOutputWindow('Recognized: Expelliarmus', 'Expelliarmus');
    } else if (normalized.includes('expecto') || normalized.includes('patronum')) {
        playSpellAnimation('Expecto Patronum');
        updateOutputWindow('Recognized: Expecto Patronum', 'Expecto Patronum');
    } else if (normalized.includes('nox')) {
        playSpellAnimation('Nox');
        updateOutputWindow('Recognized: Nox', 'Nox');
    } else if (normalized.includes('wingardium') || normalized.includes('leviosa')) {
        playSpellAnimation('Wingardium Leviosa');
        updateOutputWindow('Recognized: Wingardium Leviosa', 'Wingardium Leviosa');
    } else if (normalized.includes('petrificus') || normalized.includes('totalus')) {
        playSpellAnimation('Petrificus Totalus');
        updateOutputWindow('Recognized: Petrificus Totalus', 'Petrificus Totalus');
    } else if (normalized.includes('stupefy')) {
        playSpellAnimation('Stupefy');
        updateOutputWindow('Recognized: Stupefy', 'Stupefy');
    } else if (normalized.includes('rictusempra')) {
        playSpellAnimation('Rictusempra');
        updateOutputWindow('Recognized: Rictusempra', 'Rictusempra');
    } else if (normalized.includes('expulso')) {
        playSpellAnimation('Expulso');
        updateOutputWindow('Recognized: Expulso', 'Expulso');
    } else if (normalized.includes('diffindo')) {
        playSpellAnimation('Diffindo');
        updateOutputWindow('Recognized: Diffindo', 'Diffindo');
    } else if (normalized.includes('reparo')) {
        playSpellAnimation('Reparo');
        updateOutputWindow('Recognized: Reparo', 'Reparo');
    } else if (normalized.includes('obliviate')) {
        playSpellAnimation('Obliviate');
        updateOutputWindow('Recognized: Obliviate', 'Obliviate');
    } else if (normalized.includes('silencio')) {
        playSpellAnimation('Silencio');
        updateOutputWindow('Recognized: Silencio', 'Silencio');
    } else if (normalized.includes('incendio')) {
        playSpellAnimation('Incendio');
        updateOutputWindow('Recognized: Incendio', 'Incendio');
    } else if (normalized.includes('aguamenti')) {
        playSpellAnimation('Aguamenti');
        updateOutputWindow('Recognized: Aguamenti', 'Aguamenti');
    } else if (normalized.includes('finite') || normalized.includes('incantatem')) {
        playSpellAnimation('Finite Incantatem');
        updateOutputWindow('Recognized: Finite Incantatem', 'Finite Incantatem');
    } else if (normalized.includes('rennervate')) {
        playSpellAnimation('Rennervate');
        updateOutputWindow('Recognized: Rennervate', 'Rennervate');
    } else if (normalized.includes('colloportus')) {
        playSpellAnimation('Colloportus');
        updateOutputWindow('Recognized: Colloportus', 'Colloportus');
    } else if (normalized.includes('reducto')) {
        playSpellAnimation('Reducto');
        updateOutputWindow('Recognized: Reducto', 'Reducto');
    } else if (normalized.includes('impervius')) {
        playSpellAnimation('Impervius');
        updateOutputWindow('Recognized: Impervius', 'Impervius');
    } else if (normalized.includes('tarantallegra')) {
        playSpellAnimation('Tarantallegra');
        updateOutputWindow('Recognized: Tarantallegra', 'Tarantallegra');
    } else if (normalized.includes('obscuro')) {
        playSpellAnimation('Obscuro');
        updateOutputWindow('Recognized: Obscuro', 'Obscuro');
    } else {
        updateOutputWindow('No spell recognized. Try saying "Lumos", "Accio", "Alohomora", "Avada Kedavra", "Crucio", "Expelliarmus", "Expecto Patronum", "Nox", "Wingardium Leviosa", "Petrificus Totalus", "Stupefy", "Rictusempra", "Expulso", "Diffindo", "Reparo", "Obliviate", "Silencio", "Incendio", "Aguamenti", "Finite Incantatem", "Rennervate", "Colloportus", "Reducto", "Impervius", "Tarantallegra", or "Obscuro"');
    }
}

function showGifFirstFrame(gifPath, placeholder, spellName) {
    return new Promise((resolve) => {
        const tempImg = new Image();
        
        tempImg.onload = () => {
            try {
                const canvas = document.createElement('canvas');
                canvas.width = tempImg.width;
                canvas.height = tempImg.height;
                const ctx = canvas.getContext('2d');
                
                ctx.drawImage(tempImg, 0, 0);
                
                const firstFrameImg = document.createElement('img');
                firstFrameImg.src = canvas.toDataURL('image/png');
                firstFrameImg.alt = `${spellName} idle`;
                firstFrameImg.className = 'spell-animation spell-idle';
                firstFrameImg.style.width = '80%';
                firstFrameImg.style.height = '80%';
                firstFrameImg.style.maxWidth = '80%';
                firstFrameImg.style.maxHeight = '80%';
                firstFrameImg.style.objectFit = 'contain';
                
                placeholder.appendChild(firstFrameImg);
                currentAnimation = firstFrameImg;
                resolve(firstFrameImg);
            } catch (error) {
                console.warn('Failed to extract first frame:', error);
                const fallbackImg = document.createElement('img');
                fallbackImg.src = `/static/anime/${gifPath}`;
                fallbackImg.alt = `${spellName} idle`;
                fallbackImg.className = 'spell-animation spell-idle';
                fallbackImg.style.width = '80%';
                fallbackImg.style.height = '80%';
                fallbackImg.style.maxWidth = '80%';
                fallbackImg.style.maxHeight = '80%';
                fallbackImg.style.objectFit = 'contain';
                placeholder.appendChild(fallbackImg);
                currentAnimation = fallbackImg;
                resolve(fallbackImg);
            }
        };
        
        tempImg.onerror = () => {
            console.warn('Failed to load GIF for first frame extraction');
            resolve(null);
        };
        
        tempImg.src = `/static/anime/${gifPath}`;
    });
}

function playSpellAnimation(spellName) {
    const spellConfig = SPELL_ANIMATIONS[spellName];
    if (!spellConfig) {
        console.warn(`No animation config for spell: ${spellName}`);
        return;
    }

    const placeholder = document.querySelector('.viz-placeholder');
    if (!placeholder) return;

    clearAnimation();

    currentSpell = spellName;
    
    updateVoiceButton();

    const hint = placeholder.querySelector('.viz-hint');
    if (hint) {
        hint.style.display = 'none';
    }

    if (!spellConfig.animation) {
        const animationDuration = spellConfig.duration || 2000;
        
        setTimeout(() => {
            resetToIdle();
        }, animationDuration);
        return;
    }

    const timestamp = new Date().getTime();
    const gifUrl = `/static/anime/${spellConfig.animation}?t=${timestamp}`;
    
    const tempImg = new Image();
    
    tempImg.onload = () => {
        const img = document.createElement('img');
        img.alt = `${spellName} spell animation`;
        img.className = 'spell-animation';
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'contain';
        
        const freshTimestamp = new Date().getTime();
        const freshGifUrl = `/static/anime/${spellConfig.animation}?t=${freshTimestamp}`;
        
        img.src = freshGifUrl;
        
        placeholder.appendChild(img);
        currentAnimation = img;
        
        const animationDuration = spellConfig.duration || 5000;
        
        setTimeout(() => {
            resetToIdle();
        }, animationDuration);
        
        img.onerror = () => {
            console.warn(`Failed to load animation for ${spellName}`);
            updateOutputWindow(`Failed to load animation for ${spellName}`);
        };
    };
    
    tempImg.onerror = () => {
        console.warn(`Failed to preload animation for ${spellName}`);
        const img = document.createElement('img');
        img.alt = `${spellName} spell animation`;
        img.className = 'spell-animation';
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'contain';
        img.src = gifUrl;
        placeholder.appendChild(img);
        currentAnimation = img;
        
        const animationDuration = spellConfig.duration || 5000;
        
        setTimeout(() => {
            resetToIdle();
        }, animationDuration);
    };
    
    tempImg.src = gifUrl;
}

function clearAnimation() {
    const placeholder = document.querySelector('.viz-placeholder');
    if (!placeholder) return;

    const animation = placeholder.querySelector('.spell-animation');
    if (animation) {
        animation.remove();
    }

    currentAnimation = null;
}

function playIdleAnimation(idleAnimationFile, placeholder, spellName) {
    const hint = placeholder.querySelector('.viz-hint');
    if (hint) {
        hint.style.display = 'none';
    }
    
    const img = document.createElement('img');
    img.src = `/static/anime/${idleAnimationFile}`;
    img.alt = `${spellName} idle animation`;
    img.className = 'spell-animation spell-idle';
    img.style.width = '80%';
    img.style.height = '80%';
    img.style.maxWidth = '80%';
    img.style.maxHeight = '80%';
    img.style.objectFit = 'contain';
    
    placeholder.appendChild(img);
    currentAnimation = img;
}

function resetToIdle() {
    clearAnimation();
    
    const placeholder = document.querySelector('.viz-placeholder');
    if (!placeholder) return;

    if (currentSpell) {
        const spellConfig = SPELL_ANIMATIONS[currentSpell];
        if (spellConfig) {
            if (spellConfig.idle === 'first-frame') {
                showGifFirstFrame(spellConfig.animation, placeholder, currentSpell);
                return;
            } else if (spellConfig.idle === 'enemy-idle' && spellConfig.idleAnimation) {
                playIdleAnimation(spellConfig.idleAnimation, placeholder, currentSpell);
                return;
            } else if (spellConfig.idle === 'lumos-animation' && spellConfig.idleAnimation) {
                playIdleAnimation(spellConfig.idleAnimation, placeholder, currentSpell);
                return;
            }
        }
    }

    const hint = placeholder.querySelector('.viz-hint');
    if (hint) {
        hint.style.display = 'block';
    }
}

async function startAudioCollection() {
    try {
        if (!audioStream) {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            updateOutputWindow('Microphone access granted. Click to start recording...');
        }
        
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    } catch (error) {
        console.error('Error accessing microphone:', error);
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            updateOutputWindow('Microphone permission denied. Please allow microphone access and try again.');
        } else if (error.name === 'NotFoundError') {
            updateOutputWindow('No microphone found. Please connect a microphone and try again.');
        } else {
            updateOutputWindow('Error accessing microphone: ' + error.message);
        }
    }
}

function startRecording() {
    if (!audioStream) {
        updateOutputWindow('Microphone not available. Please click to request access.');
        return;
    }
    
    audioChunks = [];
    
    let mimeType = 'audio/webm;codecs=opus';
    if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/webm';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = 'audio/mp4';
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                mimeType = '';
            }
        }
    }
    
    const options = mimeType ? { mimeType: mimeType } : {};
    mediaRecorder = new MediaRecorder(audioStream, options);
    currentMimeType = mimeType || mediaRecorder.mimeType || 'audio/webm';
    
    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            audioChunks.push(event.data);
        }
    };
    
    mediaRecorder.onstop = () => {
        uploadAudio();
    };
    
    mediaRecorder.onerror = (event) => {
        console.error('Recording error:', event.error);
        updateOutputWindow('Recording error: ' + event.error);
        isRecording = false;
        updateVoiceButton();
    };
    
    mediaRecorder.start();
    isRecording = true;
    const spellName = currentSpell || 'Unknown spell';
    if (currentSpell) {
        loadSpellData().then(spellData => {
            const spell = spellData.find(s => s.spell === spellName);
            const pron = spell?.pronunciation || "-";
            updateOutputWindow(
                `Recording... Click to stop.<br>Spell: ${spellName}<br>Pronunciation: ${pron}`,
                spellName
            );
        });
    } else {
        updateOutputWindow('Recording... Click to stop and upload.');
    }
    updateVoiceButton();
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        updateOutputWindow('Processing audio...');
        updateVoiceButton();
    }
}

async function uploadAudio() {
    if (audioChunks.length === 0) {
        updateOutputWindow('No audio recorded. Please try again.');
        return;
    }
    
    const audioBlob = new Blob(audioChunks, { type: currentMimeType });
    const formData = new FormData();
    const extension = currentMimeType.includes('mp4') ? 'mp4' : 'webm';
    formData.append('audio', audioBlob, `recording-${Date.now()}.${extension}`);
    
    const spellName = currentSpell || 'Unknown';
    formData.append('spell', spellName);
    
    try {
        const response = await fetch('/api/audio', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        console.log('ML result:', result);

        if (!response.ok) {
            updateOutputWindow('Upload error: ' + (result.error || 'Unknown error'));
            return;
        }

        const displaySpell = result.spell || spellName;

        if (result.success) {
            const displaySpell = result.spell || spellName;
            const recognized = result.recognized_text || '(no speech recognized)';
            const grade = result.grade || 'N/A';
            const comment = result.grade_label || '';

            updateOutputWindow(
                `Spell: ${displaySpell}<br>` +
                // `You said: "${recognized}"<br>` +
                `Grade: ${grade} – ${comment}`,
                displaySpell
            );

            if (currentSpell && SPELL_ANIMATIONS[currentSpell]) {
                playSpellAnimation(currentSpell);
            }
        } else {
            updateOutputWindow(
                `We couldn't recognize your spell "${displaySpell}". ` +
                (result.error || 'Please try again.'),
                displaySpell
            );
        }
    } catch (error) {
        console.error('Upload error:', error);
        updateOutputWindow('Upload error: ' + error.message);
    }
}

function showAssessmentResult(result, spellName) {
    const statusLine = document.getElementById('status-line');
    const gradeLine = document.getElementById('assessment-grade-line');
    const gradeSpan = document.getElementById('assessment-grade');
    const textLine = document.getElementById('assessment-text-line');
    const textSpan = document.getElementById('assessment-text');

    if (!result.success) {
        if (statusLine) {
            statusLine.textContent =
                'Pronunciation assessment failed: ' + (result.error || 'Unknown error');
        }
        if (gradeLine) gradeLine.style.display = 'none';
        if (textLine) textLine.style.display = 'none';
        return;
    }

    if (statusLine) {
        statusLine.textContent = `You cast ${spellName}!`;
    }

    if (gradeLine && gradeSpan) {
        gradeSpan.textContent = `${result.grade} – ${result.grade_label}`;
        gradeLine.style.display = 'block';
    }

    if (textLine && textSpan) {
        const recognized = result.recognized_text || '(no text recognized)';
        textSpan.textContent = recognized;
        textLine.style.display = 'block';
    }
}

async function assessPronunciation(fileId, spellName) {
    try {
        const response = await fetch('/api/pronunciation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_id: fileId,
                spell: spellName
            })
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            updateOutputWindow('Pronunciation assessment failed: ' + (result.error || 'Unknown error'));
            return;
        }

        showAssessmentResult(result, spellName);

        const msgLines = [
            `Spell: ${spellName}`,
            `Recognized: ${result.recognized_text || '(no text)'}`,
            `Grade: ${result.grade} – ${result.grade_label}`,
        ];

        updateOutputWindow(msgLines.join('\n'), spellName);

        if (SPELL_ANIMATIONS[spellName] && (result.grade != 'T')) {
            playSpellAnimation(spellName);
        }

    } catch (error) {
        console.error('Assessment error:', error);
        updateOutputWindow('Assessment error: ' + error.message);
    }
}

function updateVoiceButton() {
    const button = document.querySelector('.voice-trigger');
    if (button) {
        if (isRecording) {
            button.textContent = 'Stop Recording';
            button.disabled = false;
        } else if (audioStream) {
            button.textContent = 'Start Recording';
            button.disabled = false;
        } else {
            button.textContent = 'Collect Audio';
            button.disabled = false;
        }
    }
}

let spellDataCache = null;

async function loadSpellData() {
    if (spellDataCache) {
        return spellDataCache;
    }
    
    try {
        const response = await fetch('/api/spells');
        spellDataCache = await response.json();
        return spellDataCache;
    } catch (error) {
        console.warn('Failed to load spell data:', error);
        return null;
    }
}

function updateOutputWindow(message, spellName = null) {
    const outputWindow = document.querySelector('.output-window');
    if (!outputWindow) return;

    // Clear previous content
    outputWindow.innerHTML = '';

    // Main status / feedback line
    const msgP = document.createElement('p');
    msgP.innerHTML = message;
    outputWindow.appendChild(msgP);

    // Optional: show which spell the user is working on
    /*
    if (spellName) {
        const spellP = document.createElement('p');
        spellP.innerHTML = `<span class="spell-meta">Spell:</span> ${spellName}`;
        outputWindow.appendChild(spellP);
    }
    */
}

function simulateVoiceRecognition(spellName) {
    console.log('Simulating recognition:', spellName);
    handleSpellRecognition(spellName);
}

function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

function checkURLForSpell() {
    const spellName = getURLParameter('spell');
    if (spellName && SPELL_ANIMATIONS[spellName]) {
        currentSpell = spellName;
        const spellConfig = SPELL_ANIMATIONS[spellName];
        
        setTimeout(() => {
            const placeholder = document.querySelector('.viz-placeholder');
            if (placeholder) {
                const hint = placeholder.querySelector('.viz-hint');
                if (hint) {
                    hint.style.display = 'none';
                }
                
                if (spellConfig) {
                    if (spellConfig.idle === 'first-frame') {
                        showGifFirstFrame(spellConfig.animation, placeholder, spellName);
                    } else if (spellConfig.idle === 'enemy-idle' && spellConfig.idleAnimation) {
                        playIdleAnimation(spellConfig.idleAnimation, placeholder, spellName);
                    } else if (spellConfig.idle === 'lumos-animation' && spellConfig.idleAnimation) {
                        playIdleAnimation(spellConfig.idleAnimation, placeholder, spellName);
                    } else {
                        updateOutputWindow(`Ready to play: ${spellName}`);
                    }
                } else {
                    updateOutputWindow(`Ready to play: ${spellName}`);
                }
            }
            
            updateVoiceButton();
            
            const url = new URL(window.location);
            url.searchParams.delete('spell');
            window.history.replaceState({}, '', url);
        }, 100);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const voiceButton = document.querySelector('.voice-trigger');
    if (voiceButton) {
        voiceButton.addEventListener('click', startAudioCollection);
    }

    checkURLForSpell();

    initSpeechRecognition();
    
    updateVoiceButton();
});

document.addEventListener("DOMContentLoaded", () => {
    const filterForm = document.querySelector(".filters form");
    
    document.querySelector("#spell-type").addEventListener("change", () => {
        filterForm.submit();
    });

    document.querySelector("#difficulty").addEventListener("change", () => {
        filterForm.submit();
    });
});

