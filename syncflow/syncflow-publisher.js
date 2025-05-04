class SyncFlowPublisher{
    constructor(
        enabled,
        enableCamera,
        enableMicrophone,
        enableScreenShare,
    ) {
        this.enabled = enabled;
        this.enableCamera = enableCamera;
        this.enableMicrophone = enableMicrophone;
        this.enableScreenShare = enableScreenShare;
        this.room = null;
        this.encoder = new TextEncoder();
    }

    static async initialize() {
        const API_URL = "/syncflow/runtime-settings";
        const response = await fetch(API_URL);
        if (!response.ok) {
            return new SyncFlowPublisher(false, false, false, false);
        } else {
            const data = await response.json();
            return new SyncFlowPublisher(
                data.enabled,
                data.enableCamera,
                data.enableMicrophone,
                data.enableScreenShare
            );
        }
    }  

    async startPublishing(identity, name) {
        await this.stopPublishing();
        const TOKEN_ENDPOINT = `/syncflow/token?identity=${identity}`;
        const response = await fetch(
            TOKEN_ENDPOINT
        );

        if (response.ok && window.LivekitClient) {
            const tokenResponse = await response.json();

            const room = new window.LivekitClient.Room({
                adaptiveStream: true,
                dynacast: true,

                videoCaptureDefaults: {
                    resolution: window.LivekitClient.VideoPresets.h720.resolution
                }
            });

            await room.connect(tokenResponse.livekitServerUrl, tokenResponse.token);
            // await room.localParticipant.enableCameraAndMicrophone();   
            console.log("Publishing screenshare");         
            const publication = await room.localParticipant.setScreenShareEnabled(
				true,
				{
					contentHint: 'detail',
					audio: false,
                    resolution: { width: 1920, height: 1080 },
					video: { displaySurface: 'window' }
				},
				{
					videoCodec: 'h264',
					simulcast: true
				}
			);
            console.log("Screenshare enabled");
            this.room = room;
        }
    }

    async logEvent(user, action, view, timestamp, payload) {    
        if (this.room) {
            console.log("Publishing data to room");
            await this.room.localParticipant.publishData(
                this.encoder.encode(
                    JSON.stringify({
                        user: user,
                        action: action,
                        view: view,
                        timestamp: timestamp,
                        payload: payload
                    })
                ),
                {
                    reliable: true
                }
            );
            console.log("Published data to room");
        }
    }

    async stopPublishing() {
        if (this.room) {
            await this.room.disconnect();
        }
    }
}

SyncFlowPublisher.initialize().then((publisher) => {
    console.log("SyncFlowPublisher initialized");
    console.log("SyncFlowPublisher enabled: " + publisher.enabled);
    console.log("SyncFlowPublisher enableCamera: " + publisher.enableCamera);
    console.log("SyncFlowPublisher enableMicrophone: " + publisher.enableMicrophone);
    console.log("SyncFlowPublisher enableScreenShare: " + publisher.enableScreenShare);
    window.syncFlowPublisher = publisher;
});