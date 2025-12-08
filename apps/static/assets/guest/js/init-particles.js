function initParticles() {
  try {
    if (typeof particlesJS === "undefined") {
      console.warn("particles.js library is not loaded.")
      return
    }
    const particlesElement = document.getElementById("particles-js")
    if (!particlesElement) {
      console.warn('Element with ID "particles-js" not found for particle initialization.')
      return
    }

    console.log("[v0] Initializing moving shapes...")

    particlesJS("particles-js", {
      particles: {
        number: {
          value: 20,
          density: {
            enable: true,
            value_area: 800,
          },
        },
        color: {
          value: ["#ffffff", "#f0f0f0", "#e0e0e0"],
        },
        shape: {
          type: ["circle", "triangle", "polygon", "edge"],
          stroke: {
            width: 1,
            color: "#ffffff",
          },
          polygon: {
            nb_sides: 6,
          },
        },
        opacity: {
          value: 0.7,
          random: true,
          anim: {
            enable: true,
            speed: 2,
            opacity_min: 0.3,
            sync: false,
          },
        },
        size: {
          value: 8,
          random: true,
          anim: {
            enable: true,
            speed: 3,
            size_min: 4,
            sync: false,
          },
        },
        line_linked: {
          enable: false,
        },
        move: {
          enable: true,
          speed: 2,
          direction: "none",
          random: true,
          straight: false,
          out_mode: "bounce",
          bounce: true,
          attract: {
            enable: false,
          },
        },
      },
      interactivity: {
        detect_on: "canvas",
        events: {
          onhover: {
            enable: true,
            mode: "repulse",
          },
          onclick: {
            enable: true,
            mode: "push",
          },
          resize: true,
        },
        modes: {
          grab: {
            distance: 140,
          },
          bubble: {
            distance: 200,
            size: 8,
            duration: 2,
            opacity: 0.8,
            speed: 3,
          },
          repulse: {
            distance: 100,
            duration: 0.4,
          },
          push: {
            particles_nb: 3,
          },
          remove: {
            particles_nb: 2,
          },
        },
      },
      retina_detect: true,
    })

    console.log("[v0] Moving shapes initialized successfully!")
  } catch (error) {
    console.error("An error occurred during particles.js initialization:", error)
  }
}
