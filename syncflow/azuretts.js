class AzureTTS{
    static playAzureAudio (utterance, voice, volume, rate, style, fallbackVoice) {
        window.AzureTtsRequestId = (window.AzureTtsRequestId || 0) + 1;
        const requestId = window.AzureTtsRequestId;
        if (window.AzureTtsAbortController) {
            try { window.AzureTtsAbortController.abort(); } catch (e) {}
        }
        window.AzureTtsAbortController = new AbortController();
        const abortSignal = window.AzureTtsAbortController.signal;
        if (window.AzureAudio != null) {
            try {
                window.AzureAudio.pause();
                window.AzureAudio.currentTime = 0;
            } catch (e) {}
        }
        const audio = document.createElement("audio");		
        const url = "/tts/azure";
        const safeRate = (rate || "0%").toString();
        const safeStyle = (style || "").toString().trim();
        const voicesToTry = [voice];
        if (fallbackVoice && fallbackVoice !== voice) {
            voicesToTry.push(fallbackVoice);
        }

        const attemptSynthesis = (index) => {
            if (index >= voicesToTry.length) {
                console.error("Azure TTS playback failed: no usable voice for utterance.");
                return;
            }
            const voiceName = voicesToTry[index];

            fetch(url, {
                "headers": {
                    "content-type": "application/json"
                },
                "body": JSON.stringify({
                    utterance: utterance || "",
                    voice: voiceName,
                    rate: safeRate,
                    style: safeStyle
                }),
                "method": "POST",
                "signal": abortSignal,
            })
            .then(resp => {
                if (!resp.ok) {
                    throw new Error("Azure TTS request failed with status " + resp.status + " for voice " + voiceName);
                }
                return resp.blob();
            })
            .then(URL.createObjectURL)
            .then(url => {
                if (requestId !== window.AzureTtsRequestId) {
                    try { URL.revokeObjectURL(url); } catch (e) {}
                    throw new Error("Azure TTS superseded by newer request.");
                }
                audio.src = url;
                audio.volume = volume/100;
                return audio.play();
            })
            .then(() => {
                if (requestId !== window.AzureTtsRequestId) {
                    try {
                        audio.pause();
                        audio.currentTime = 0;
                    } catch (e) {}
                    return;
                }
                window.AzureAudio = audio;
            })
            .catch(err => {
                if (abortSignal.aborted) {
                    return;
                }
                if (index + 1 < voicesToTry.length) {
                    console.warn("Azure TTS voice failed, retrying with fallback:", err);
                    attemptSynthesis(index + 1);
                } else {
                    console.error("Azure TTS playback failed:", err);
                }
            });
        };

        attemptSynthesis(0);
    }

    static stopAzureAudio() {
        window.AzureTtsRequestId = (window.AzureTtsRequestId || 0) + 1;
        if (window.AzureTtsAbortController) {
            try { window.AzureTtsAbortController.abort(); } catch (e) {}
        }
        if(window.AzureAudio != null) {
            window.AzureAudio.pause();
            window.AzureAudio.currentTime = 0;
        }
    }
}

window.playAzureAudio = AzureTTS.playAzureAudio;
window.stopAzureAudio = AzureTTS.stopAzureAudio;
