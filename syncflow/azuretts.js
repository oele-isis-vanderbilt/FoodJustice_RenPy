class AzureTTS{
    static playAzureAudio (utterance, voice, key, volume, rate, style) {
        const audio = document.createElement("audio");		
        var url = "https://eastus.tts.speech.microsoft.com/cognitiveservices/v1";
        const escapedUtterance = (utterance || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
        const safeRate = (rate || "0%").toString();
        const safeStyle = (style || "").toString().trim();
        const styleOpen = safeStyle ? "<mstts:express-as style=\"" + safeStyle + "\">" : "";
        const styleClose = safeStyle ? "</mstts:express-as>" : "";
        const ssml = "<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" xmlns:mstts=\"http://www.w3.org/2001/mstts\" xml:lang=\"en-US\"><voice name=\"" + voice + "\">" + styleOpen + "<prosody rate=\"" + safeRate + "\">" + escapedUtterance + "</prosody>" + styleClose + "</voice></speak>";

        fetch(url, {
            "headers": {
                "content-type": "application/ssml+xml",
                "Ocp-Apim-Subscription-Key": key,
                "X-Microsoft-OutputFormat": "audio-24khz-160kbitrate-mono-mp3"
            },
            "body": ssml,
            "method": "POST"
        })
        .then(resp => {
            if (!resp.ok) {
                throw new Error("Azure TTS request failed with status " + resp.status);
            }
            return resp.blob();
        })
        .then(URL.createObjectURL)
        .then(url => {
            audio.src = url;
            audio.volume = volume/100;
            return audio.play();
        })
        .then(() => {
            window.AzureAudio = audio
        })
        .catch(err => {
            console.error("Azure TTS playback failed:", err);
        });
    }

    static stopAzureAudio() {
        if(window.AzureAudio != null) {
            window.AzureAudio.pause();
            window.AzureAudio.currentTime = 0;
        }
    }
}

window.playAzureAudio = AzureTTS.playAzureAudio;
window.stopAzureAudio = AzureTTS.stopAzureAudio;
