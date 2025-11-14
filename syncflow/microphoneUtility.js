class MicrophoneUtility {

    // NOTE: Commas must separate functions

    static MicrophoneUtilityGlobals = {
        sampleHz: 44100,
        mediaRecorder: null,
        chunks: null,
        audioBuffer: null,
        blob:null
    }

    StartRecordingJS () {
        var MicrophoneUtilityGlobals = MicrophoneUtility.MicrophoneUtilityGlobals;

        MicrophoneUtilityGlobals.chunks = [];
        navigator.mediaDevices
            .getUserMedia({ audio: true })
            .then((stream) => {
                // create MediaRecorder
                MicrophoneUtilityGlobals.mediaRecorder = new MediaRecorder(stream, {
                    audioBitsPerSecond: 16 * MicrophoneUtilityGlobals.sampleHz,
                    // not specifying a mimetype since wav is not currently supported
                    // we can just make the raw audio data available to the AudioRecordingService since conversion is done there
                });

                MicrophoneUtilityGlobals.mediaRecorder.onstart = (e) => {
                    console.log("MediaRecorder.start() called.");
                    MicrophoneUtilityGlobals.chunks = [];
                };

                MicrophoneUtilityGlobals.mediaRecorder.onstop = (e) => {
                    console.log("MediaRecorder.stop() called.");
                    // stop all tracks of the stream so the browser no longer shows the microphone as in use
                    stream.getTracks().forEach(function (track) {
                        track.stop();
                    });

                    // combine chunks into a single blob
                    const fullBlob = new Blob(MicrophoneUtilityGlobals.chunks, {type:'audio/wav'});
                    MicrophoneUtilityGlobals.blob = fullBlob;
                    
                    var base_url = "https://nleprototype-rlengine-asr.soc240019.projects.jetstream-cloud.org";
                    
                    const formData = new FormData();
                    formData.append("InputAudioRecording", fullBlob, "InputAudioRecording");
                    try{

                        fetch(base_url + "/GetTranscribedAudio", 
                            {
                                method: 'POST',
                                body: formData
                            }
                        ).then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.json(); 
                        })
                        .then(data => {
                            console.log('Upload successful:', data);

                            var asrResponse = data.TranscribedInputUtterance;
                            window.renpy_exec("ASRresponse(\""+asrResponse+"\")");
                        })
                        .catch(error => {
                            console.error('Error during upload:', error);
                        });
                    }
                    catch(e){
                        console.log(e);
                    }
                };

                MicrophoneUtilityGlobals.mediaRecorder.ondataavailable = (e) => {
                    MicrophoneUtilityGlobals.chunks.push(e.data);
                };

                // start recording
                MicrophoneUtilityGlobals.mediaRecorder.start();
            })
            .catch((err) => {
                console.error(`The following error occurred: ${err}`);
            });

    }

    StopRecordingJS () {
        var MicrophoneUtilityGlobals = MicrophoneUtility.MicrophoneUtilityGlobals;
        // stop recording
        MicrophoneUtilityGlobals.mediaRecorder.stop();
    }
};


window.microphoneUtil = new MicrophoneUtility();

