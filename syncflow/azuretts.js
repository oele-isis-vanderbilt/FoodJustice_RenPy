class AzureTTS{
    static playAzureAudio (utterance, voice, key, volume) {
        const audio = document.createElement("audio");		
        var url = "https://eastus.tts.speech.microsoft.com/cognitiveservices/v1";

        fetch(url, {
            "headers": {
                "content-type": "application/ssml+xml",
                "Ocp-Apim-Subscription-Key": key,
                "X-Microsoft-OutputFormat": "audio-24khz-160kbitrate-mono-mp3"
            },
            "body": "<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" xmlns:mstts=\"http://www.w3.org/2001/mstts\" xml:lang=\"en-US\"><voice name=\"" + voice + "\">" + utterance + "</voice></speak>",
            "method": "POST"
        })
        .then(resp => resp.blob())
        .then(URL.createObjectURL)
        .then(url => {
        audio.src = url;
        audio.volume = volume/100;
        audio.play();
            window.AzureAudio = audio
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