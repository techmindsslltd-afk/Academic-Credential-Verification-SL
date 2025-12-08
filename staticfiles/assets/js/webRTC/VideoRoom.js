
// WebRTC peer connection using simple-peer replaced with native WebRTC APIs
function VideoRoomComponent(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Main container for video room
  const videoRoomContainer = document.createElement('div');
  videoRoomContainer.style.display = 'flex';
  videoRoomContainer.style.flexDirection = 'column';
  videoRoomContainer.style.alignItems = 'center';

  // Local video element
  const localVideo = document.createElement('video');
  localVideo.autoplay = true;
  localVideo.muted = true; // mute local video to prevent echo
  localVideo.style.width = '300px';
  localVideo.style.marginBottom = '10px';
  
  // Controls
  const controlsContainer = document.createElement('div');
  controlsContainer.style.display = 'flex';
  controlsContainer.style.justifyContent = 'space-around';
  controlsContainer.style.width = '100%';

  // Mute/Unmute button
  const muteButton = document.createElement('button');
  muteButton.innerText = 'Mute';
  let isMuted = false;
  muteButton.addEventListener('click', () => {
    isMuted = !isMuted;
    localVideo.muted = isMuted;
    muteButton.innerText = isMuted ? 'Unmute' : 'Mute';
  });

  // Toggle video button
  const videoButton = document.createElement('button');
  videoButton.innerText = 'Stop Video';
  let isVideoEnabled = true;
  videoButton.addEventListener('click', () => {
    isVideoEnabled = !isVideoEnabled;
    localVideo.style.display = isVideoEnabled ? 'block' : 'none';
    videoButton.innerText = isVideoEnabled ? 'Stop Video' : 'Start Video';
  });

  // Append controls
  controlsContainer.appendChild(muteButton);
  controlsContainer.appendChild(videoButton);
  videoRoomContainer.appendChild(localVideo);
  videoRoomContainer.appendChild(controlsContainer);
  container.appendChild(videoRoomContainer);

  // WebRTC setup (assuming a signaling server is available)
  navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(stream => {
      localVideo.srcObject = stream;
    })
    .catch(error => {
      console.error('Error accessing media devices.', error);
    });
}

// Usage: VideoRoomComponent('your-container-id');
