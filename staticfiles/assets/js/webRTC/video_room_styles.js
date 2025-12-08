
// Plain JavaScript styles object for Video Room
const videoRoomStyles = {
  floatingButtons: {
    zIndex: 1,
    position: "fixed",
    bottom: "0",
    left: "50%",
    transform: "translate(-50%, -50%)",
  },
  floatingButton: {
    margin: "0 0.5rem",
  },
  videoGrid: {
    marginTop: "1rem",
    marginBottom: "15rem",
    width: "100%",
    display: "grid",
    gridTemplateColumns: "repeat(2, 1fr)",
    gridTemplateRows: "auto",
    gap: "0.3rem",
  },
  // Additional styles as required can be added here
};

// Example usage: 
// const element = document.createElement('div');
// Object.assign(element.style, videoRoomStyles.floatingButtons);
