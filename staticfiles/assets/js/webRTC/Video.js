
// Material UI styles are not used in plain JavaScript; instead, styles are directly added
function VideoComponent(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Create main video container
  const videoContainer = document.createElement('div');
  videoContainer.style.position = 'relative';
  videoContainer.style.padding = '10px';
  videoContainer.style.border = '1px solid #ccc';

  // Set up initial state
  let isMouseHovering = false;

  // Video element
  const videoElement = document.createElement('video');
  videoElement.setAttribute('controls', 'true');
  videoElement.style.width = '100%';
  videoElement.style.height = 'auto';

  // Hover effect
  videoContainer.addEventListener('mouseenter', () => {
    isMouseHovering = true;
    videoElement.style.opacity = '0.8'; // Change style on hover
  });

  videoContainer.addEventListener('mouseleave', () => {
    isMouseHovering = false;
    videoElement.style.opacity = '1.0'; // Revert style
  });

  // Append elements
  videoContainer.appendChild(videoElement);
  container.appendChild(videoContainer);
}

// Usage: VideoComponent('your-container-id');
