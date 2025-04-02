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
            await room.localParticipant.enableCameraAndMicrophone();
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