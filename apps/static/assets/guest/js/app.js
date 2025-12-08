// CertChain - Blockchain Academic Credential Verification
// Enhanced Application JavaScript with Global Accreditation Layer

;(() => {
  // Global error handler to suppress browser extension errors
  window.addEventListener('error', (event) => {
    // Suppress browser extension message channel errors
    if (event.message && event.message.includes('message channel')) {
      event.preventDefault()
      return false
    }
  }, true)

  // Suppress unhandled promise rejections from browser extensions
  window.addEventListener('unhandledrejection', (event) => {
    if (event.reason && event.reason.message && event.reason.message.includes('message channel')) {
      event.preventDefault()
      return false
    }
  })

  // State Management
  const state = {
    currentPage: "home",
    isLoggedIn: false,
    user: null,
    theme: localStorage.getItem("theme") || "light",
    lastVerifiedCredential: null,
    showDemoWallet: false,
  }

  // Check if user is already logged in
  function checkLoginState() {
    // First, check if login/signup buttons exist in DOM (Django template shows them when user is NOT authenticated)
    const loginBtn = document.getElementById("login-btn")
    const signupBtn = document.getElementById("signup-btn")
    const userMenu = document.getElementById("user-menu")
    
    // If login/signup buttons exist in DOM, user is NOT authenticated in Django
    // If user menu exists, user IS authenticated in Django
    const isAuthenticatedInDjango = !!userMenu && !loginBtn && !signupBtn
    
    if (isAuthenticatedInDjango) {
      // User is authenticated in Django, check localStorage for user data
      const accessToken = localStorage.getItem("access_token")
      const userData = localStorage.getItem("user")
      
      if (accessToken && userData) {
        try {
          state.user = JSON.parse(userData)
          state.isLoggedIn = true
          updateWalletView()
          updateNavbarForLoggedIn()
        } catch (e) {
          console.error("Error parsing user data:", e)
          localStorage.removeItem("access_token")
          localStorage.removeItem("refresh_token")
          localStorage.removeItem("user")
          state.isLoggedIn = false
          state.user = null
          updateNavbarForLoggedIn()
        }
      }
    } else {
      // User is NOT authenticated in Django - clear any stale localStorage data
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
      localStorage.removeItem("user")
      state.isLoggedIn = false
      state.user = null
      
      // Force buttons to be visible if they exist
      if (loginBtn) {
        loginBtn.style.display = "inline-block"
        loginBtn.style.visibility = "visible"
        loginBtn.style.opacity = "1"
        loginBtn.style.position = "relative"
        loginBtn.removeAttribute("hidden")
        loginBtn.classList.remove("hidden")
      }
      if (signupBtn) {
        signupBtn.style.display = "inline-block"
        signupBtn.style.visibility = "visible"
        signupBtn.style.opacity = "1"
        signupBtn.style.position = "relative"
        signupBtn.removeAttribute("hidden")
        signupBtn.classList.remove("hidden")
      }
      if (userMenu) {
        userMenu.style.display = "none"
        userMenu.style.visibility = "hidden"
      }
      
      updateWalletView()
    }
  }

  // Update navbar for logged in users
  function updateNavbarForLoggedIn() {
    const loginBtn = document.getElementById("login-btn")
    const signupBtn = document.getElementById("signup-btn")
    const userMenu = document.getElementById("user-menu")
    
    // Check Django template state first (buttons exist = not authenticated, userMenu exists = authenticated)
    const isAuthenticatedInDjango = !!userMenu && !loginBtn && !signupBtn
    
    // Only update if buttons exist (they might not exist if Django template conditionally renders them)
    if (isAuthenticatedInDjango && state.isLoggedIn && state.user) {
      // User is authenticated - hide login/signup buttons, show logout button
      if (loginBtn) {
        loginBtn.style.display = "none"
        loginBtn.style.visibility = "hidden"
      }
      if (signupBtn) {
        signupBtn.style.display = "none"
        signupBtn.style.visibility = "hidden"
      }
      if (userMenu) {
        userMenu.style.display = "flex"
        userMenu.style.visibility = "visible"
      }
    } else {
      // User is NOT authenticated - show login/signup buttons, hide logout button
      // Only show if buttons exist (Django template shows them when user is not authenticated)
      if (loginBtn) {
        loginBtn.style.display = "inline-block"
        loginBtn.style.visibility = "visible"
        loginBtn.style.opacity = "1"
      }
      if (signupBtn) {
        signupBtn.style.display = "inline-block"
        signupBtn.style.visibility = "visible"
        signupBtn.style.opacity = "1"
      }
      if (userMenu) {
        userMenu.style.display = "none"
        userMenu.style.visibility = "hidden"
      }
    }
  }

  // Logout function
  function handleLogout() {
    const logoutBtn = document.getElementById("logout-btn")
    
    // Show loading state
    if (logoutBtn) {
      logoutBtn.disabled = true
      logoutBtn.innerHTML = '<span class="spinner" style="width: 14px; height: 14px; border-width: 2px; margin-right: 0.5rem;"></span> Logging out...'
    }

    // Get CSRF token
    const csrfToken = getCSRFToken()
    const refreshToken = localStorage.getItem("refresh_token")

    // Call logout endpoint
    fetch("/logout/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
      },
      body: JSON.stringify({
        refresh: refreshToken
      }),
      credentials: 'include'  // Include session cookie
    })
    .then(response => {
      // Always clear tokens and user data from localStorage, regardless of response
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
      localStorage.removeItem("user")
      
      // Update state
      state.isLoggedIn = false
      state.user = null
      
      // Update UI
      updateNavbarForLoggedIn()
      updateWalletView()
      
      // Show success message
      showToast("You have been logged out successfully", "success")
      
      // Redirect to home page
      setTimeout(() => {
        window.location.href = "/"  // Home page URL
      }, 1000)
      
      return response.json().catch(() => ({}))  // Handle non-JSON responses gracefully
    })
    .catch(error => {
      // Suppress browser extension errors
      if (error.message && error.message.includes('message channel')) {
        // Still clear local data even if extension error
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
        localStorage.removeItem("user")
        state.isLoggedIn = false
        state.user = null
        updateNavbarForLoggedIn()
        updateWalletView()
        return
      }
      
      console.error("Logout error:", error)
      
      // Even if logout fails, clear local data
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
      localStorage.removeItem("user")
      state.isLoggedIn = false
      state.user = null
      
      updateNavbarForLoggedIn()
      updateWalletView()
      
      showToast("Logged out successfully", "success")
      
      // Redirect to home page
      setTimeout(() => {
        window.location.href = "/"  // Home page URL
      }, 1000)
    })
    .finally(() => {
      if (logoutBtn) {
        logoutBtn.disabled = false
        logoutBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          Logout
        `
      }
    })
  }

  // Get CSRF token helper
  function getCSRFToken() {
    // First try to get from hidden input field
    let token = document.querySelector('[name=csrfmiddlewaretoken]')?.value
    
    // If not found, try to get from cookie
    if (!token) {
      const cookies = document.cookie.split(';')
      for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=')
        if (name === 'csrftoken') {
          token = value
          break
        }
      }
    }
    
    // If still not found, try to get from meta tag
    if (!token) {
      const metaTag = document.querySelector('meta[name=csrf-token]')
      if (metaTag) {
        token = metaTag.getAttribute('content')
      }
    }
    
    return token || ''
  }

  // Sample credential data - REMOVED: Now using API endpoint /api/v1/credentials/verify/
  /*
  const sampleCredentials = {
    "CERT-2024-SL-001234": {
      valid: true,
      holder: "Aminata Kamara",
      institution: "University of Sierra Leone",
      degree: "Bachelor of Science",
      program: "Computer Science & Information Technology",
      grade: "First Class Honours",
      issued: "December 15, 2024",
      hash: "0x7f8b5c9a2e4d6f8b1c3a5d7e9f0b2c4d6e8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f83e2a",
      status: "Active",
      ipfsHash: "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco",
      timeline: [
        {
          date: "Dec 15, 2024",
          event: "Credential Issued",
          type: "success",
          description: "Issued by University of Sierra Leone",
        },
        {
          date: "Dec 15, 2024",
          event: "Blockchain Recorded",
          type: "success",
          description: "Hash recorded on Ethereum mainnet",
        },
        {
          date: "Dec 15, 2024",
          event: "IPFS Backup",
          type: "success",
          description: "Stored on IPFS distributed network",
        },
        {
          date: "Dec 18, 2024",
          event: "First Verification",
          type: "success",
          description: "Verified by TechCorp Inc.",
        },
        {
          date: "Dec 20, 2024",
          event: "Shared via LinkedIn",
          type: "success",
          description: "Added to LinkedIn profile",
        },
      ],
    },
    "CERT-2024-NJ-005678": {
      valid: true,
      holder: "Mohamed Sesay",
      institution: "Njala University",
      degree: "Master of Business Administration",
      program: "Business Administration",
      grade: "Distinction",
      issued: "June 20, 2024",
      hash: "0x3a5c7d9e1f2b4c6d8e0a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a9f1b",
      status: "Active",
      ipfsHash: "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
      timeline: [
        {
          date: "Jun 20, 2024",
          event: "Credential Issued",
          type: "success",
          description: "Issued by Njala University",
        },
        {
          date: "Jun 20, 2024",
          event: "Blockchain Recorded",
          type: "success",
          description: "Hash recorded on Ethereum mainnet",
        },
      ],
    },
    "CERT-2023-LK-009012": {
      valid: false,
      holder: "Ibrahim Conteh",
      institution: "Limkokwing University",
      degree: "Diploma",
      program: "Graphic Design",
      grade: "Merit",
      issued: "March 10, 2023",
      hash: "0x9f1b3c5d7e9a1b3c5d7e9f1b3c5d7e9a1b3c5d7e9f1b3c5d7e9a1b3c5d7e9f1b3c5d7e9a1b3c5d7e9f1b3c5d7e9a1b3c5d7e9f1b3c5d7e9a1b3c5d7e9f1b3c5d7e9a1b3c5d7e0a2b",
      status: "Revoked",
      revokedReason: "Academic misconduct investigation",
      timeline: [
        {
          date: "Mar 10, 2023",
          event: "Credential Issued",
          type: "success",
          description: "Issued by Limkokwing University",
        },
        {
          date: "Mar 10, 2023",
          event: "Blockchain Recorded",
          type: "success",
          description: "Hash recorded on distributed ledger",
        },
        {
          date: "Nov 5, 2023",
          event: "Investigation Started",
          type: "warning",
          description: "Academic misconduct reported",
        },
        {
          date: "Dec 1, 2023",
          event: "Credential Revoked",
          type: "error",
          description: "Revoked due to academic misconduct",
        },
      ],
    },
  }
  */

  // Sample accreditation data - REMOVED: Now using API endpoint /api/public/accreditation/search/
  /*
  const accreditationDatabase = {
    "university of sierra leone": {
      name: "University of Sierra Leone",
      country: "Sierra Leone",
      countryCode: "SL",
      city: "Freetown",
      accredited: true,
      whedId: "IAU-012345",
      founded: 1827,
      type: "Public University",
      recognition: "Ministry of Education, Sierra Leone",
      accreditationBodies: ["Tertiary Education Commission (TEC)", "Association of African Universities (AAU)"],
      website: "https://usl.edu.sl",
      verificationContact: "registrar@usl.edu.sl",
      partnerStatus: true,
      degrees: ["Bachelor's", "Master's", "Doctorate"],
      studentCount: 12500,
      programs: [
        { name: "Bachelor of Science in Computer Science", level: "Bachelor's", duration: "4 years" },
        { name: "Bachelor of Arts in Economics", level: "Bachelor's", duration: "4 years" },
        { name: "Master of Business Administration", level: "Master's", duration: "2 years" },
        { name: "Doctor of Philosophy in Education", level: "Doctorate", duration: "3-5 years" },
      ],
      accreditationHistory: [
        { date: "2023", event: "Joined CertChain Platform", status: "success" },
        { date: "2020", event: "Re-accreditation by TEC", status: "success" },
        { date: "2015", event: "AAU Membership Renewed", status: "success" },
        { date: "1827", event: "Institution Founded", status: "success" },
      ],
    },
    "njala university": {
      name: "Njala University",
      country: "Sierra Leone",
      countryCode: "SL",
      city: "Njala",
      accredited: true,
      whedId: "IAU-012346",
      founded: 1964,
      type: "Public University",
      recognition: "Ministry of Education, Sierra Leone",
      accreditationBodies: ["Tertiary Education Commission (TEC)", "Association of African Universities (AAU)"],
      website: "https://njala.edu.sl",
      verificationContact: "registrar@njala.edu.sl",
      partnerStatus: true,
      degrees: ["Bachelor's", "Master's", "Doctorate"],
      studentCount: 8500,
      programs: [
        { name: "Bachelor of Science in Agriculture", level: "Bachelor's", duration: "4 years" },
        { name: "Bachelor of Education", level: "Bachelor's", duration: "4 years" },
        { name: "Master of Science in Environmental Science", level: "Master's", duration: "2 years" },
      ],
      accreditationHistory: [
        { date: "2022", event: "Joined CertChain Platform", status: "success" },
        { date: "2019", event: "TEC Accreditation Renewed", status: "success" },
        { date: "1964", event: "Institution Founded", status: "success" },
      ],
    },
    "harvard university": {
      name: "Harvard University",
      country: "United States",
      countryCode: "US",
      city: "Cambridge, Massachusetts",
      accredited: true,
      whedId: "IAU-000001",
      founded: 1636,
      type: "Private University",
      recognition: "New England Commission of Higher Education (NECHE)",
      accreditationBodies: ["NECHE", "AACSB", "ABA", "ABET"],
      website: "https://harvard.edu",
      verificationContact: "registrar@harvard.edu",
      partnerStatus: false,
      degrees: ["Bachelor's", "Master's", "Doctorate", "Professional"],
      studentCount: 36000,
      programs: [
        { name: "Bachelor of Arts", level: "Bachelor's", duration: "4 years" },
        { name: "Juris Doctor", level: "Professional", duration: "3 years" },
        { name: "Master of Business Administration", level: "Master's", duration: "2 years" },
        { name: "Doctor of Medicine", level: "Professional", duration: "4 years" },
      ],
      accreditationHistory: [
        { date: "2021", event: "NECHE Re-accreditation", status: "success" },
        { date: "2018", event: "AACSB Accreditation Renewed", status: "success" },
        { date: "1636", event: "Institution Founded", status: "success" },
      ],
    },
    "university of oxford": {
      name: "University of Oxford",
      country: "United Kingdom",
      countryCode: "GB",
      city: "Oxford",
      accredited: true,
      whedId: "IAU-000002",
      founded: 1096,
      type: "Public University",
      recognition: "Office for Students (OfS)",
      accreditationBodies: ["QAA", "AMBA", "EQUIS", "AACSB"],
      website: "https://ox.ac.uk",
      verificationContact: "academic.admin@ox.ac.uk",
      partnerStatus: false,
      degrees: ["Bachelor's", "Master's", "Doctorate"],
      studentCount: 26000,
      programs: [
        { name: "Bachelor of Arts in Philosophy, Politics and Economics", level: "Bachelor's", duration: "3 years" },
        { name: "Master of Science in Computer Science", level: "Master's", duration: "1 year" },
        { name: "Doctor of Philosophy", level: "Doctorate", duration: "3-4 years" },
      ],
      accreditationHistory: [
        { date: "2022", event: "QAA Review - Confidence Rating", status: "success" },
        { date: "2019", event: "Triple Crown Accreditation Maintained", status: "success" },
        { date: "1096", event: "Institution Founded", status: "success" },
      ],
    },
    "limkokwing university": {
      name: "Limkokwing University of Creative Technology",
      country: "Sierra Leone (Branch)",
      countryCode: "SL",
      city: "Freetown",
      accredited: true,
      whedId: "IAU-045678",
      founded: 1991,
      type: "Private University",
      recognition: "Ministry of Education, Sierra Leone",
      accreditationBodies: ["Tertiary Education Commission (TEC)"],
      website: "https://limkokwing.net",
      verificationContact: "registry@limkokwing.net",
      partnerStatus: true,
      degrees: ["Diploma", "Bachelor's", "Master's"],
      studentCount: 3200,
      programs: [
        { name: "Diploma in Graphic Design", level: "Diploma", duration: "2 years" },
        { name: "Bachelor of Arts in Creative Multimedia", level: "Bachelor's", duration: "3 years" },
        { name: "Master of Arts in Communication Design", level: "Master's", duration: "1.5 years" },
      ],
      accreditationHistory: [
        { date: "2023", event: "Joined CertChain Platform", status: "success" },
        { date: "2021", event: "TEC Accreditation", status: "success" },
        { date: "2010", event: "Sierra Leone Campus Established", status: "success" },
      ],
    },
    mit: {
      name: "Massachusetts Institute of Technology",
      country: "United States",
      countryCode: "US",
      city: "Cambridge, Massachusetts",
      accredited: true,
      whedId: "IAU-000003",
      founded: 1861,
      type: "Private University",
      recognition: "New England Commission of Higher Education (NECHE)",
      accreditationBodies: ["NECHE", "ABET", "AACSB"],
      website: "https://mit.edu",
      verificationContact: "registrar@mit.edu",
      partnerStatus: false,
      degrees: ["Bachelor's", "Master's", "Doctorate"],
      studentCount: 11500,
      programs: [
        { name: "Bachelor of Science in Computer Science", level: "Bachelor's", duration: "4 years" },
        { name: "Master of Engineering", level: "Master's", duration: "1 year" },
        { name: "Doctor of Philosophy in Physics", level: "Doctorate", duration: "5 years" },
      ],
      accreditationHistory: [
        { date: "2020", event: "NECHE Re-accreditation", status: "success" },
        { date: "2019", event: "ABET Accreditation Renewed", status: "success" },
        { date: "1861", event: "Institution Founded", status: "success" },
      ],
    },
    "university of lagos": {
      name: "University of Lagos",
      country: "Nigeria",
      countryCode: "NG",
      city: "Lagos",
      accredited: true,
      whedId: "IAU-023456",
      founded: 1962,
      type: "Public University",
      recognition: "National Universities Commission (NUC)",
      accreditationBodies: ["NUC", "Association of African Universities (AAU)"],
      website: "https://unilag.edu.ng",
      verificationContact: "registrar@unilag.edu.ng",
      partnerStatus: false,
      degrees: ["Bachelor's", "Master's", "Doctorate"],
      studentCount: 57000,
      programs: [
        { name: "Bachelor of Science in Accounting", level: "Bachelor's", duration: "4 years" },
        { name: "Bachelor of Engineering", level: "Bachelor's", duration: "5 years" },
        { name: "Master of Laws", level: "Master's", duration: "1 year" },
      ],
      accreditationHistory: [
        { date: "2022", event: "NUC Full Accreditation", status: "success" },
        { date: "2018", event: "AAU Membership Renewed", status: "success" },
        { date: "1962", event: "Institution Founded", status: "success" },
      ],
    },
    "university of ghana": {
      name: "University of Ghana",
      country: "Ghana",
      countryCode: "GH",
      city: "Accra",
      accredited: true,
      whedId: "IAU-034567",
      founded: 1948,
      type: "Public University",
      recognition: "Ghana Tertiary Education Commission",
      accreditationBodies: ["GTEC", "Association of African Universities (AAU)"],
      website: "https://ug.edu.gh",
      verificationContact: "registrar@ug.edu.gh",
      partnerStatus: false,
      degrees: ["Bachelor's", "Master's", "Doctorate"],
      studentCount: 40000,
      programs: [
        { name: "Bachelor of Arts in Political Science", level: "Bachelor's", duration: "4 years" },
        { name: "Bachelor of Science in Nursing", level: "Bachelor's", duration: "4 years" },
        { name: "Master of Public Health", level: "Master's", duration: "2 years" },
      ],
      accreditationHistory: [
        { date: "2021", event: "GTEC Accreditation Renewed", status: "success" },
        { date: "2017", event: "AAU Excellence Award", status: "success" },
        { date: "1948", event: "Institution Founded", status: "success" },
      ],
    },
    "stanford university": {
      name: "Stanford University",
      country: "United States",
      countryCode: "US",
      city: "Stanford, California",
      accredited: true,
      whedId: "IAU-000004",
      founded: 1885,
      type: "Private University",
      recognition: "WASC Senior College and University Commission",
      accreditationBodies: ["WSCUC", "AACSB", "ABET", "ABA"],
      website: "https://stanford.edu",
      verificationContact: "registrar@stanford.edu",
      partnerStatus: false,
      degrees: ["Bachelor's", "Master's", "Doctorate", "Professional"],
      studentCount: 17000,
      programs: [
        { name: "Bachelor of Science in Computer Science", level: "Bachelor's", duration: "4 years" },
        { name: "Master of Business Administration", level: "Master's", duration: "2 years" },
        { name: "Juris Doctor", level: "Professional", duration: "3 years" },
      ],
      accreditationHistory: [
        { date: "2021", event: "WSCUC Re-accreditation", status: "success" },
        { date: "2019", event: "AACSB Accreditation Maintained", status: "success" },
        { date: "1885", event: "Institution Founded", status: "success" },
      ],
    },
    "university of cape town": {
      name: "University of Cape Town",
      country: "South Africa",
      countryCode: "ZA",
      city: "Cape Town",
      accredited: true,
      whedId: "IAU-056789",
      founded: 1829,
      type: "Public University",
      recognition: "Council on Higher Education (CHE)",
      accreditationBodies: ["CHE", "Association of African Universities (AAU)", "AMBA"],
      website: "https://uct.ac.za",
      verificationContact: "registrar@uct.ac.za",
      partnerStatus: false,
      degrees: ["Bachelor's", "Master's", "Doctorate"],
      studentCount: 29000,
      programs: [
        { name: "Bachelor of Commerce", level: "Bachelor's", duration: "3 years" },
        { name: "Bachelor of Medicine", level: "Professional", duration: "6 years" },
        { name: "Master of Philosophy", level: "Master's", duration: "2 years" },
      ],
      accreditationHistory: [
        { date: "2022", event: "CHE Institutional Audit - Commendation", status: "success" },
        { date: "2020", event: "AMBA Accreditation Renewed", status: "success" },
        { date: "1829", event: "Institution Founded", status: "success" },
      ],
    },
    "fake university diploma mill": {
      name: "Fake University Diploma Mill",
      country: "Unknown",
      countryCode: "XX",
      city: "Unknown",
      accredited: false,
      whedId: null,
      founded: null,
      type: "Unaccredited",
      recognition: "None - Known Diploma Mill",
      accreditationBodies: [],
      website: null,
      verificationContact: null,
      partnerStatus: false,
      degrees: [],
      studentCount: 0,
      programs: [],
      accreditationHistory: [
        { date: "2023", event: "Flagged as Diploma Mill by UNESCO", status: "warning" },
        { date: "2020", event: "Multiple Fraud Reports Filed", status: "warning" },
      ],
    },
  }
  */

  // Additional institutions - REMOVED: Now using API endpoint /api/public/institutions/list/
  /*
  const additionalInstitutions = [
    { name: "Cambridge University", country: "United Kingdom", whedId: "IAU-000005", partnerStatus: false },
    { name: "Yale University", country: "United States", whedId: "IAU-000006", partnerStatus: false },
    { name: "Princeton University", country: "United States", whedId: "IAU-000007", partnerStatus: false },
    { name: "University of Nairobi", country: "Kenya", whedId: "IAU-067890", partnerStatus: false },
    { name: "Makerere University", country: "Uganda", whedId: "IAU-078901", partnerStatus: false },
    { name: "University of Ibadan", country: "Nigeria", whedId: "IAU-089012", partnerStatus: false },
    { name: "Addis Ababa University", country: "Ethiopia", whedId: "IAU-090123", partnerStatus: false },
    { name: "University of Dar es Salaam", country: "Tanzania", whedId: "IAU-101234", partnerStatus: false },
    { name: "Fourah Bay College", country: "Sierra Leone", whedId: "IAU-012347", partnerStatus: true },
    { name: "Ernest Bai Koroma University", country: "Sierra Leone", whedId: "IAU-012348", partnerStatus: true },
  ]
  */

  // Sample activities - REMOVED: Now using API endpoint /api/public/live-activities/
  /*
  const sampleActivities = [
    {
      type: "success",
      text: "<strong>TechCorp Inc.</strong> verified credential from University of Sierra Leone",
      time: "2 min ago",
    },
    {
      type: "success",
      text: "<strong>GlobalBank</strong> verified MBA credential from Njala University",
      time: "5 min ago",
    },
    { type: "warning", text: "Suspicious credential flagged for review", time: "12 min ago" },
    { type: "success", text: "<strong>StartupXYZ</strong> verified Computer Science degree", time: "18 min ago" },
    {
      type: "success",
      text: "<strong>HR Solutions</strong> completed bulk verification (15 credentials)",
      time: "25 min ago",
    },
  ]
  */

  // DOM Elements
  const elements = {
    pages: document.querySelectorAll(".page"),
    navLinks: document.querySelectorAll("[data-page]"),
    actionButtons: document.querySelectorAll("[data-action]"),
    loginModal: document.getElementById("login-modal"),
    signupModal: document.getElementById("signup-modal"),
    shareModal: document.getElementById("share-modal"),
    qrModal: document.getElementById("qr-modal"),
    closeModalBtns: document.querySelectorAll("[data-close-modal]"),
    verifyTabs: document.querySelectorAll(".verify-tab"),
    verifyResult: document.getElementById("verify-result"),
    toastContainer: document.getElementById("toast-container"),
    themeToggle: document.getElementById("theme-toggle"),
    notificationBtn: document.getElementById("notification-btn"),
    notificationPanel: document.getElementById("notification-panel"),
    activityList: document.getElementById("activity-list"),
    navbarLinks: document.getElementById("navbar-links"),
    mobileMenuBtn: document.getElementById("mobile-menu-btn"),
    accreditationResult: document.getElementById("accreditation-result"),
    walletLoginPrompt: document.getElementById("wallet-login-prompt"),
    walletDashboard: document.getElementById("wallet-dashboard"),
  }

  // Theme Management
  function initTheme() {
    if (state.theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark")
    }
  }

  function toggleTheme() {
    state.theme = state.theme === "light" ? "dark" : "light"
    localStorage.setItem("theme", state.theme)

    if (state.theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark")
    } else {
      document.documentElement.removeAttribute("data-theme")
    }

    showToast(`Switched to ${state.theme} mode`, "info")
  }

  // Navigation
  function navigateTo(pageId) {
    state.currentPage = pageId

    elements.pages.forEach((page) => {
      page.classList.remove("active")
      if (page.id === `page-${pageId}`) {
        page.classList.add("active")
      }
    })

    document.querySelectorAll(".navbar-link").forEach((link) => {
      link.classList.remove("active")
      if (link.dataset.page === pageId) {
        link.classList.add("active")
      }
    })

    window.scrollTo({ top: 0, behavior: "smooth" })

    if (elements.verifyResult) {
      elements.verifyResult.classList.remove("show")
    }

    if (elements.navbarLinks) {
      elements.navbarLinks.classList.remove("show")
    }

    // Handle wallet page state
    if (pageId === "wallet") {
      updateWalletView()
    }
  }

  // Update wallet view based on login state
  async function updateWalletView() {
    if (state.isLoggedIn || state.showDemoWallet) {
      elements.walletLoginPrompt?.classList.add("hidden")
      elements.walletDashboard?.classList.remove("hidden")
      
      // Check if credentials are already rendered from Django template
      const existingCredentials = document.querySelectorAll(".wallet-credential-card[data-credential-id]")
      
      // Load credentials only if not already rendered from template
      if (existingCredentials.length === 0) {
        if (state.showDemoWallet) {
          loadDemoWallet()
        } else if (state.isLoggedIn) {
          await loadUserCredentials()
        }
      } else {
        // Credentials already rendered from template, just attach event listeners
        attachCredentialActionListeners()
        // Update stats if needed (they're already in the template)
      }
    } else {
      elements.walletLoginPrompt?.classList.remove("hidden")
      elements.walletDashboard?.classList.add("hidden")
    }
  }

  // Load user credentials from API
  async function loadUserCredentials() {
    const credentialsGrid = document.querySelector(".wallet-credentials-grid")
    if (!credentialsGrid) return

    try {
      const accessToken = localStorage.getItem("access_token")
      if (!accessToken) {
        showToast("Please log in to view your credentials", "error")
        return
      }

      const response = await fetch("/api/v1/credentials/", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${accessToken}`,
          "Content-Type": "application/json"
        }
      })

      if (response.ok) {
        const credentials = await response.json()
        renderCredentials(credentials.results || credentials)
        updateWalletStats(credentials.results || credentials)
        updateWalletUserInfo()
      } else if (response.status === 401) {
        // Token expired, try to refresh
        const refreshed = await refreshAccessToken()
        if (refreshed) {
          await loadUserCredentials() // Retry
        } else {
          showToast("Session expired. Please log in again.", "error")
          handleLogout()
        }
      } else {
        showToast("Failed to load credentials", "error")
        renderCredentials([])
      }
    } catch (error) {
      console.error("Error loading credentials:", error)
      showToast("An error occurred while loading credentials", "error")
      renderCredentials([])
    }
  }

  // Load demo wallet with sample data
  function loadDemoWallet() {
    const demoCredentials = [
      {
        id: "demo-1",
        credential_id: "CERT-2024-SL-001234",
        credential_type: "degree",
        status: "issued",
        holder_name: "Aminata Kamara",
        institution_name: "University of Sierra Leone",
        program_name: "Computer Science & Information Technology",
        degree_level: "Bachelor of Science",
        grade: "First Class Honours",
        issue_date: "2024-12-15",
        completion_date: "2024-12-01",
        blockchain_hash: "0x1234567890abcdef..."
      },
      {
        id: "demo-2",
        credential_id: "CERT-2024-NJ-002345",
        credential_type: "professional",
        status: "issued",
        holder_name: "Aminata Kamara",
        institution_name: "Njala University",
        program_name: "Data Science & Analytics",
        degree_level: "Professional Certificate",
        grade: "With Distinction",
        issue_date: "2024-08-20",
        completion_date: "2024-08-15",
        blockchain_hash: "0xabcdef1234567890..."
      },
      {
        id: "demo-3",
        credential_id: "CERT-2024-LK-003456",
        credential_type: "degree",
        status: "pending",
        holder_name: "Aminata Kamara",
        institution_name: "Limkokwing University",
        program_name: "Business Administration",
        degree_level: "Master of Business Administration",
        grade: "",
        issue_date: null,
        completion_date: "2024-11-30",
        blockchain_hash: null
      }
    ]

    renderCredentials(demoCredentials)
    updateWalletStats(demoCredentials)
    
    // Update user info for demo
    const userInfo = document.querySelector(".wallet-user-details")
    if (userInfo) {
      const nameEl = userInfo.querySelector("h3")
      const emailEl = userInfo.querySelector("p")
      if (nameEl) nameEl.textContent = "Aminata Kamara"
      if (emailEl) emailEl.textContent = "aminata.kamara@email.com"
    }
    
    const avatar = document.querySelector(".wallet-avatar")
    if (avatar) avatar.textContent = "AK"
  }

  // Render credentials in the wallet grid
  function renderCredentials(credentials) {
    const credentialsGrid = document.querySelector(".wallet-credentials-grid")
    if (!credentialsGrid) return

    if (credentials.length === 0) {
      credentialsGrid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5" style="margin-bottom: 1rem;">
            <rect width="20" height="14" x="2" y="7" rx="2" ry="2"/>
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
          </svg>
          <h3 style="margin-bottom: 0.5rem;">No Credentials Yet</h3>
          <p style="color: var(--text-muted); margin-bottom: 1.5rem;">Your verified academic credentials will appear here</p>
          <button class="btn btn-primary" onclick="document.querySelector('[data-action=\\'signup\\']')?.click()">
            Get Started
          </button>
        </div>
      `
      return
    }

    credentialsGrid.innerHTML = credentials.map(cred => {
      const status = cred.status || "pending"
      const isVerified = status === "issued" || status === "verified"
      const isPending = status === "pending" || status === "draft"
      
      // Get institution initials
      const instName = cred.institution_name || ""
      const initials = instName.split(" ").map(w => w[0]).join("").substring(0, 3).toUpperCase() || "INST"
      
      // Format date
      const issueDate = cred.issue_date ? new Date(cred.issue_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : "Pending"
      const completionDate = cred.completion_date ? new Date(cred.completion_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : ""
      
      // Get credential type display
      const typeDisplay = cred.degree_level || cred.credential_type || "Credential"
      
      return `
        <div class="wallet-credential-card ${isPending ? 'pending' : ''}" data-credential-id="${cred.credential_id}" data-credential-uuid="${cred.id}">
          <div class="credential-card-header">
            <div class="credential-institution-logo">${initials}</div>
            <div class="credential-status-badge ${isVerified ? 'valid' : isPending ? 'pending' : 'revoked'}">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${isVerified ? '3' : '2'}">
                ${isVerified 
                  ? '<path d="m9 12 2 2 4-4"/>'
                  : isPending
                  ? '<path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>'
                  : '<path d="M18 6L6 18M6 6l12 12"/>'
                }
              </svg>
              ${isVerified ? 'Verified' : isPending ? 'Pending' : 'Revoked'}
            </div>
          </div>
          <div class="credential-card-body">
            <h4>${typeDisplay}</h4>
            <p class="credential-program">${cred.program_name || 'N/A'}</p>
            <p class="credential-institution">${instName}</p>
            <div class="credential-meta">
              ${cred.grade ? `<span>${cred.grade}</span>` : ''}
              <span>${completionDate || issueDate}</span>
            </div>
          </div>
          <div class="credential-card-footer">
            <div class="credential-id">${cred.credential_id}</div>
            <div class="credential-actions">
              <button class="btn btn-icon btn-ghost" title="View QR Code" data-action="view-qr" data-credential-id="${cred.credential_id}">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect width="5" height="5" x="3" y="3" rx="1"/>
                  <rect width="5" height="5" x="16" y="3" rx="1"/>
                  <rect width="5" height="5" x="3" y="16" rx="1"/>
                  <path d="M21 16h-3a2 2 0 0 0-2 2v3"/>
                </svg>
              </button>
              <button class="btn btn-icon btn-ghost" title="Share" data-action="share" data-credential-id="${cred.credential_id}">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
                  <line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/>
                  <line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/>
                </svg>
              </button>
              <button class="btn btn-icon btn-ghost" title="Download" data-action="download" data-credential-id="${cred.credential_id}">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" x2="12" y1="15" y2="3"/>
                </svg>
              </button>
            </div>
          </div>
          ${isVerified ? `
          <div class="credential-blockchain-info">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
            </svg>
            <span>Blockchain Secured</span>
          </div>
          ` : ''}
        </div>
      `
    }).join("")

    // Attach event listeners to credential actions
    attachCredentialActionListeners()
  }

  // Update wallet statistics
  function updateWalletStats(credentials) {
    const stats = {
      credentials: credentials.length,
      verifications: 0, // This would come from verification logs
      shares: 0 // This would come from share logs
    }

    const statElements = {
      credentials: document.querySelector(".wallet-stat:first-child .wallet-stat-value"),
      verifications: document.querySelector(".wallet-stat:nth-child(2) .wallet-stat-value"),
      shares: document.querySelector(".wallet-stat:last-child .wallet-stat-value")
    }

    if (statElements.credentials) statElements.credentials.textContent = stats.credentials
    if (statElements.verifications) statElements.verifications.textContent = stats.verifications
    if (statElements.shares) statElements.shares.textContent = stats.shares
  }

  // Update wallet user info from state (only if not already set from Django template)
  function updateWalletUserInfo() {
    if (!state.user) return

    // Only update if elements are empty (not already populated from Django template)
    const nameEl = document.getElementById("wallet-user-name")
    const emailEl = document.getElementById("wallet-user-email")
    const avatar = document.getElementById("wallet-avatar")
    
    if (nameEl && !nameEl.textContent.trim()) {
      nameEl.textContent = state.user.full_name || `${state.user.first_name || ''} ${state.user.last_name || ''}`.trim() || state.user.email
    }
    
    if (emailEl && !emailEl.textContent.trim()) {
      emailEl.textContent = state.user.email
    }
    
    if (avatar && !avatar.textContent.trim()) {
      const initials = (state.user.first_name?.[0] || '') + (state.user.last_name?.[0] || '') || state.user.email?.[0].toUpperCase() || 'U'
      avatar.textContent = initials.toUpperCase()
    }
  }

  // Attach event listeners to credential action buttons
  function attachCredentialActionListeners() {
    document.querySelectorAll('[data-action="view-qr"]').forEach(btn => {
      btn.addEventListener("click", (e) => {
        const credentialId = btn.dataset.credentialId
        viewCredentialQR(credentialId)
      })
    })

    document.querySelectorAll('[data-action="share"]').forEach(btn => {
      btn.addEventListener("click", (e) => {
        const credentialId = btn.dataset.credentialId
        shareCredential(credentialId)
      })
    })

    document.querySelectorAll('[data-action="download"]').forEach(btn => {
      btn.addEventListener("click", (e) => {
        const credentialId = btn.dataset.credentialId
        downloadCredential(credentialId)
      })
    })
  }

  // View credential QR code
  function viewCredentialQR(credentialId) {
    const verifyUrl = `${window.location.origin}/credentials/verify/${credentialId}/`
    
    // Create QR code modal
    const modalHTML = `
      <div class="modal-overlay" id="qr-modal">
        <div class="modal" style="max-width: 400px;">
          <div class="modal-header">
            <h3>Credential QR Code</h3>
            <button class="modal-close" onclick="closeModal(document.getElementById('qr-modal'))">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" x2="6" y1="6" y2="18"/>
                <line x1="6" x2="18" y1="6" y2="18"/>
              </svg>
            </button>
          </div>
          <div class="modal-body" style="text-align: center; padding: 2rem;">
            <div id="qr-code-container" style="margin-bottom: 1.5rem;"></div>
            <p style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 1rem;">
              Scan this QR code to verify the credential
            </p>
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md); margin-bottom: 1rem;">
              <p style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.5rem;">Verification URL:</p>
              <code style="font-size: 0.75rem; word-break: break-all;">${verifyUrl}</code>
            </div>
            <button class="btn btn-secondary" onclick="navigator.clipboard.writeText('${verifyUrl}').then(() => showToast('URL copied!', 'success'))">
              Copy Verification Link
            </button>
          </div>
        </div>
      </div>
    `

    // Remove existing modal if any
    const existingModal = document.getElementById("qr-modal")
    if (existingModal) existingModal.remove()

    // Add modal to body
    document.body.insertAdjacentHTML("beforeend", modalHTML)
    const modal = document.getElementById("qr-modal")
    
    // Generate QR code
    const qrContainer = document.getElementById("qr-code-container")
    if (typeof QRCode !== 'undefined') {
      qrContainer.innerHTML = ""
      QRCode.toCanvas(qrContainer, verifyUrl, { width: 256, margin: 2 }, (error) => {
        if (error) {
          console.error('QR code generation error:', error)
          // Fallback: use QR code API
          qrContainer.innerHTML = `<img src="https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${encodeURIComponent(verifyUrl)}" alt="QR Code" style="max-width: 100%;">`
        }
      })
    } else {
      // Fallback: use QR code API
      qrContainer.innerHTML = `<img src="https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${encodeURIComponent(verifyUrl)}" alt="QR Code" style="max-width: 100%;">`
    }

    openModal("qr-modal")
  }

  // Share credential
  async function shareCredential(credentialId) {
    const verifyUrl = `${window.location.origin}/credentials/verify/${credentialId}/`
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: "Verify My Credential",
          text: "Please verify my academic credential",
          url: verifyUrl
        })
        showToast("Credential shared successfully!", "success")
      } catch (error) {
        if (error.name !== 'AbortError') {
          // Fallback to clipboard
          navigator.clipboard.writeText(verifyUrl).then(() => {
            showToast("Verification link copied to clipboard!", "success")
          })
        }
      }
    } else {
      // Fallback to clipboard
      navigator.clipboard.writeText(verifyUrl).then(() => {
        showToast("Verification link copied to clipboard!", "success")
      })
    }
  }

  // Download credential
  function downloadCredential(credentialId) {
    const verifyUrl = `${window.location.origin}/credentials/verify/${credentialId}/`
    window.open(verifyUrl, '_blank')
    showToast("Opening credential page for download...", "info")
  }

  // Refresh access token
  async function refreshAccessToken() {
    try {
      const refreshToken = localStorage.getItem("refresh_token")
      if (!refreshToken) {
        return false
      }

      const response = await fetch("/api/v1/auth/token/refresh/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          refresh: refreshToken
        })
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem("access_token", data.access)
        if (data.refresh) {
          localStorage.setItem("refresh_token", data.refresh)
        }
        return true
      }
      return false
    } catch (error) {
      console.error("Error refreshing token:", error)
      return false
    }
  }


  // Modal Management
  function openModal(modalId) {
    const modal = document.getElementById(modalId)
    if (modal) {
      modal.classList.add("show")
      document.body.style.overflow = "hidden"
    }
  }

  function closeModal(modalElement) {
    if (modalElement) {
      modalElement.classList.remove("show")
      document.body.style.overflow = ""
    }
  }

  function closeAllModals() {
    document.querySelectorAll(".modal-overlay").forEach((modal) => {
      closeModal(modal)
    })
  }

  // Toast Notifications
  function showToast(message, type = "success") {
    const toast = document.createElement("div")
    toast.className = `toast ${type}`

    const icons = {
      success:
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="2"><path d="m9 12 2 2 4-4"/><circle cx="12" cy="12" r="10"/></svg>',
      error:
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--error)" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" x2="9" y1="9" y2="15"/><line x1="9" x2="15" y1="9" y2="15"/></svg>',
      info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--info)" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
      warning:
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--warning)" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    }

    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.success}</span>
      <span class="toast-message">${message}</span>
      <button class="toast-close" aria-label="Close">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/>
        </svg>
      </button>
    `

    elements.toastContainer.appendChild(toast)

    toast.querySelector(".toast-close").addEventListener("click", () => {
      toast.remove()
    })

    setTimeout(() => {
      toast.style.animation = "slideIn 0.3s ease reverse"
      setTimeout(() => toast.remove(), 300)
    }, 5000)
  }

  // Verification Logic
  async function verifyCredential(credentialId) {
    const verifyBtn = document.querySelector("#verify-by-id-btn, #quick-verify-btn, #employer-verify-btn")
    if (verifyBtn) {
      verifyBtn.disabled = true
      verifyBtn.innerHTML = '<span class="spinner"></span> Verifying...'
    }

    try {
      // Get CSRF token
      const csrfToken = getCSRFToken()
      
      const response = await fetch('/api/v1/credentials/verify/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || '',
          'X-CSRF-Token': csrfToken || ''  // Some Django versions expect this format
        },
        credentials: 'include',
        body: JSON.stringify({
          credential_id: credentialId.trim()
        })
      })

      // Check if response is JSON before parsing
      const contentType = response.headers.get('content-type')
      let data
      if (contentType && contentType.includes('application/json')) {
        data = await response.json()
      } else {
        // Handle non-JSON responses (like HTML error pages)
        const text = await response.text()
        console.error('Non-JSON response:', text.substring(0, 200))
        throw new Error(`Server returned ${response.status}: ${response.statusText}`)
      }

      if (response.ok && data.valid !== undefined) {
        // Transform API response to match expected format
        const credential = {
          credential_id: data.credential?.credential_id || credentialId,
          holder: data.credential?.holder_name || '',
          institution: data.credential?.institution?.name || data.credential?.institution || '',
          degree: data.credential?.degree_level || '',
          program: data.credential?.program_name || '',
          grade: data.credential?.grade || '',
          issued: data.credential?.issue_date || data.credential?.completion_date || '',
          hash: data.credential?.blockchain_hash || '',
          ipfsHash: data.credential?.ipfs_hash || '',
          valid: data.valid,
          status: data.status || (data.valid ? 'Verified' : 'Revoked'),
          revokedReason: data.credential?.revocation_reason || null,
          timeline: data.credential?.timeline || []
        }

        state.lastVerifiedCredential = credential
        displayVerificationResult(credential, true)
        if (credential.timeline && credential.timeline.length > 0) {
          displayCredentialTimeline(credential)
        } else {
          hideCredentialTimeline()
        }
        showToast(
          credential.valid ? "Credential verified successfully!" : "Credential found but has been revoked",
          credential.valid ? "success" : "error",
        )
      } else {
        displayVerificationResult(null, false)
        hideCredentialTimeline()
        const errorMsg = data.error || data.message || "Credential not found in our records"
        showToast(errorMsg, "error")
      }
    } catch (error) {
      console.error('Verification error:', error)
      displayVerificationResult(null, false)
      hideCredentialTimeline()
      
      // Provide more specific error messages
      let errorMessage = "An error occurred while verifying the credential. Please try again."
      if (error.message && error.message.includes('403')) {
        errorMessage = "Authentication error. Please refresh the page and try again."
      } else if (error.message && error.message.includes('CSRF')) {
        errorMessage = "Session expired. Please refresh the page and try again."
      } else if (error.message) {
        errorMessage = error.message
      }
      
      showToast(errorMessage, "error")
    } finally {
      if (verifyBtn) {
        verifyBtn.disabled = false
        verifyBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m9 12 2 2 4-4"/><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          Verify
        `
      }
    }
  }

  function displayVerificationResult(credential, found) {
    const resultElement = elements.verifyResult
    if (!resultElement) return

    const resultIcon = document.getElementById("result-icon")
    const resultTitle = document.getElementById("result-title")
    const resultSubtitle = document.getElementById("result-subtitle")
    const resultBadge = document.getElementById("result-badge")
    const resultDetails = document.getElementById("result-details")

    if (found && credential) {
      const isValid = credential.valid

      resultElement.className = `verify-result show ${isValid ? "verified" : "invalid"}`
      resultIcon.className = `result-icon ${isValid ? "success" : "error"}`
      resultIcon.innerHTML = isValid
        ? '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 12 2 2 4-4"/><circle cx="12" cy="12" r="10"/></svg>'
        : '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" x2="9" y1="9" y2="15"/><line x1="9" x2="15" y1="9" y2="15"/></svg>'

      resultTitle.textContent = isValid ? "Credential Verified" : "Credential Revoked"
      resultSubtitle.textContent = isValid
        ? "This credential is authentic and valid on the blockchain"
        : credential.revokedReason || "This credential has been revoked"

      resultBadge.className = `badge ${isValid ? "badge-success" : "badge-error"}`
      resultBadge.textContent = credential.status

      resultDetails.innerHTML = `
        <div class="result-item">
          <div class="result-item-label">Credential Holder</div>
          <div class="result-item-value">${credential.holder}</div>
        </div>
        <div class="result-item">
          <div class="result-item-label">Institution</div>
          <div class="result-item-value">${credential.institution}</div>
        </div>
        <div class="result-item">
          <div class="result-item-label">Degree</div>
          <div class="result-item-value">${credential.degree}</div>
        </div>
        <div class="result-item">
          <div class="result-item-label">Program</div>
          <div class="result-item-value">${credential.program}</div>
        </div>
        <div class="result-item">
          <div class="result-item-label">Grade/Classification</div>
          <div class="result-item-value">${credential.grade}</div>
        </div>
        <div class="result-item">
          <div class="result-item-label">Date Issued</div>
          <div class="result-item-value">${credential.issued}</div>
        </div>
        <div class="result-item" style="grid-column: span 2;">
          <div class="result-item-label">Blockchain Hash (SHA-256)</div>
          <div class="result-item-value" style="font-family: var(--font-mono); font-size: 0.75rem; word-break: break-all;">${credential.hash.substring(0, 66)}...</div>
        </div>
        ${
          credential.ipfsHash
            ? `
        <div class="result-item" style="grid-column: span 2;">
          <div class="result-item-label">IPFS Content Hash</div>
          <div class="result-item-value" style="font-family: var(--font-mono); font-size: 0.8125rem;">${credential.ipfsHash}</div>
        </div>
        `
            : ""
        }
      `
    } else {
      resultElement.className = "verify-result show invalid"
      resultIcon.className = "result-icon error"
      resultIcon.innerHTML =
        '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M16 16s-1.5-2-4-2-4 2-4 2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/></svg>'
      resultTitle.textContent = "Credential Not Found"
      resultSubtitle.textContent = "This credential ID was not found in our blockchain records"
      resultBadge.className = "badge badge-error"
      resultBadge.textContent = "Not Found"
      resultDetails.innerHTML = `
        <div class="result-item" style="grid-column: span 2;">
          <div class="result-item-label">Possible Reasons</div>
          <div class="result-item-value">
            <ul style="margin: 0; padding-left: 1.25rem; color: var(--text-secondary);">
              <li>The credential ID may be incorrect</li>
              <li>The credential may not have been issued through CertChain</li>
              <li>The issuing institution may not be a partner</li>
              <li>This could be a fraudulent credential</li>
            </ul>
          </div>
        </div>
      `
    }

    resultElement.scrollIntoView({ behavior: "smooth", block: "center" })
  }

  function displayCredentialTimeline(credential) {
    const timelineSection = document.getElementById("credential-timeline-section")
    const timelineContainer = document.getElementById("credential-timeline")

    if (!timelineSection || !timelineContainer || !credential.timeline) return

    timelineSection.classList.remove("hidden")

    timelineContainer.innerHTML = credential.timeline
      .map(
        (item) => `
      <div class="timeline-item ${item.type}">
        <div class="timeline-date">${item.date}</div>
        <div class="timeline-title">${item.event}</div>
        <div class="timeline-description">${item.description}</div>
      </div>
    `,
      )
      .join("")
  }

  function hideCredentialTimeline() {
    const timelineSection = document.getElementById("credential-timeline-section")
    if (timelineSection) {
      timelineSection.classList.add("hidden")
    }
  }

  // Show search results when multiple credentials found
  function showSearchResults(credentials) {
    const resultElement = elements.verifyResult
    if (!resultElement) return

    // Create a results list
    const resultsHTML = `
      <div style="margin-top: 1rem;">
        <h4 style="margin-bottom: 1rem;">Found ${credentials.length} matching credentials:</h4>
        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
          ${credentials.map(cred => `
            <div class="result-card" style="cursor: pointer; padding: 1rem; border: 1px solid var(--border-color); border-radius: var(--radius-md); transition: all 0.2s;" 
                 onclick="verifyCredential('${cred.credential_id}')"
                 onmouseover="this.style.borderColor='var(--accent-primary)'; this.style.background='var(--bg-secondary)'"
                 onmouseout="this.style.borderColor='var(--border-color)'; this.style.background='transparent'">
              <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                  <strong>${cred.holder_name}</strong>
                  <p style="margin: 0.25rem 0; color: var(--text-secondary);">${cred.program_name}</p>
                  <p style="margin: 0; font-size: 0.875rem; color: var(--text-muted);">
                    ${cred.institution} • ${cred.completion_date ? new Date(cred.completion_date).getFullYear() : 'N/A'}
                  </p>
                </div>
                <div style="text-align: right;">
                  <span class="badge badge-accent">${cred.credential_id}</span>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `

    resultElement.className = "verify-result show"
    const resultIcon = document.getElementById("result-icon")
    const resultTitle = document.getElementById("result-title")
    const resultSubtitle = document.getElementById("result-subtitle")
    const resultBadge = document.getElementById("result-badge")
    const resultDetails = document.getElementById("result-details")

    resultIcon.className = "result-icon info"
    resultIcon.innerHTML = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>'
    resultTitle.textContent = "Search Results"
    resultSubtitle.textContent = `Found ${credentials.length} credential${credentials.length !== 1 ? 's' : ''} matching your search`
    resultBadge.className = "badge badge-info"
    resultBadge.textContent = `${credentials.length} Found`
    resultDetails.innerHTML = resultsHTML

    resultElement.scrollIntoView({ behavior: "smooth", block: "center" })
  }

  // Accreditation Lookup
  async function searchAccreditation(institutionName, filters = {}) {
    const searchBtn = document.getElementById("accred-search-btn")
    const resultsList = document.getElementById("accreditation-results-list")
    const resultsGrid = document.getElementById("results-grid")
    const resultsCount = document.getElementById("results-count")

    if (searchBtn) {
      searchBtn.disabled = true
      searchBtn.innerHTML = '<span class="spinner"></span> Searching...'
    }

    try {
      // Get CSRF token
      const csrfToken = getCSRFToken()
      
      const response = await fetch('/api/public/accreditation/search/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || '',
          'X-CSRF-Token': csrfToken || ''  // Some Django versions expect this format
        },
        body: JSON.stringify({
          institution_name: institutionName.trim(),
          country: filters.country || '',
          institution_type: filters.type || ''
        })
      })

      const data = await response.json()

      if (data.success) {
        // Show results list
        if (resultsList) {
          resultsList.classList.remove("hidden")
        }
        
        if (resultsCount) {
          resultsCount.textContent = `${data.total_results || 0} institutions found`
        }
        
        // Display results in grid
        if (resultsGrid) {
          resultsGrid.innerHTML = ''
          
          // Display CertChain institutions
          if (data.institutions && data.institutions.length > 0) {
            data.institutions.forEach(inst => {
              const card = document.createElement('div')
              card.className = 'result-card'
              card.innerHTML = `
                <div class="result-card-header">
                  <h4>${inst.name}</h4>
                  ${inst.is_partner ? '<span class="badge badge-teal">Partner</span>' : ''}
                </div>
                <div class="result-card-body">
                  ${inst.country ? `<p><strong>Country:</strong> ${inst.country}</p>` : ''}
                  ${inst.city ? `<p><strong>City:</strong> ${inst.city}</p>` : ''}
                  ${inst.institution_type ? `<p><strong>Type:</strong> ${inst.institution_type}</p>` : ''}
                  <p><strong>Accreditation Status:</strong> ${inst.accreditation_status || 'Not Specified'}</p>
                  ${inst.is_verified ? '<p><span class="badge badge-success">Verified Institution</span></p>' : ''}
                </div>
              `
              resultsGrid.appendChild(card)
            })
          }
          
          // Display WHED records if any
          if (data.whed_records && data.whed_records.length > 0) {
            data.whed_records.forEach(whed => {
              const card = document.createElement('div')
              card.className = 'result-card'
              card.innerHTML = `
                <div class="result-card-header">
                  <h4>${whed.name}</h4>
                  <span class="badge badge-info">UNESCO WHED</span>
                </div>
                <div class="result-card-body">
                  ${whed.country ? `<p><strong>Country:</strong> ${whed.country}</p>` : ''}
                  ${whed.city ? `<p><strong>City:</strong> ${whed.city}</p>` : ''}
                  ${whed.accreditation_body ? `<p><strong>Accreditation Body:</strong> ${whed.accreditation_body}</p>` : ''}
                </div>
              `
              resultsGrid.appendChild(card)
            })
          }
          
          if (data.total_results === 0) {
            resultsGrid.innerHTML = '<div class="no-results"><p>No institutions found. Try a different search term.</p></div>'
          }
        }
        
        // If single result, show detail view
        if (data.institutions && data.institutions.length === 1 && !data.whed_records?.length) {
          displayAccreditationResult(data.institutions[0], institutionName)
          if (resultsList) {
            resultsList.classList.add("hidden")
          }
        }
      } else {
        showToast(data.error || 'Failed to search institutions', "error")
        if (resultsGrid) {
          resultsGrid.innerHTML = '<div class="no-results"><p>Error searching. Please try again.</p></div>'
        }
      }
    } catch (error) {
      console.error('Accreditation search error:', error)
      showToast("An error occurred while searching. Please try again.", "error")
      if (resultsGrid) {
        resultsGrid.innerHTML = '<div class="no-results"><p>Error searching. Please try again.</p></div>'
      }
    } finally {
      if (searchBtn) {
        searchBtn.disabled = false
        searchBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
          Search Accreditation Database
        `
      }
    }
  }

  let currentSearchResults = []
  let selectedResultIndex = -1

  function initAccreditationSearch() {
    const institutionInput = document.getElementById("accred-institution-input")
    const autocompleteDropdown = document.getElementById("accred-autocomplete")
    const autocompleteResults = document.getElementById("accred-autocomplete-results")
    const autocompleteLoading = document.querySelector(".autocomplete-loading")
    const searchBtn = document.getElementById("accred-search-btn")
    const searchModeButtons = document.querySelectorAll(".search-mode-btn")
    const basicSearchForm = document.getElementById("basic-search-form")
    const advancedSearchForm = document.getElementById("advanced-search-form")
    const advSearchBtn = document.getElementById("adv-search-btn")
    const advResetBtn = document.getElementById("adv-reset-btn")
    const resultsList = document.getElementById("accreditation-results-list")
    const backToResults = document.getElementById("back-to-results")

    // Search mode toggle
    searchModeButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        searchModeButtons.forEach((b) => b.classList.remove("active"))
        btn.classList.add("active")

        if (btn.dataset.mode === "basic") {
          basicSearchForm.classList.remove("hidden")
          advancedSearchForm.classList.add("hidden")
        } else {
          basicSearchForm.classList.add("hidden")
          advancedSearchForm.classList.remove("hidden")
        }
      })
    })

    // Autocomplete functionality
    let autocompleteTimeout

    if (institutionInput) {
      institutionInput.addEventListener("input", async (e) => {
        const query = e.target.value.trim()

        clearTimeout(autocompleteTimeout)

        if (query.length < 2) {
          autocompleteDropdown.classList.remove("show")
          return
        }

        // Show loading
        autocompleteDropdown.classList.add("show")
        autocompleteLoading.classList.add("show")
        autocompleteResults.innerHTML = ""

        // Debounce API call
        autocompleteTimeout = setTimeout(async () => {
          const results = await searchInstitutions(query)
          displayAutocompleteResults(results, autocompleteResults, autocompleteLoading, autocompleteDropdown)
        }, 500)
      })

      // Keyboard navigation
      institutionInput.addEventListener("keydown", (e) => {
        const items = autocompleteResults.querySelectorAll("li")

        if (e.key === "ArrowDown") {
          e.preventDefault()
          selectedResultIndex = Math.min(selectedResultIndex + 1, items.length - 1)
          updateAutocompleteSelection(items)
        } else if (e.key === "ArrowUp") {
          e.preventDefault()
          selectedResultIndex = Math.max(selectedResultIndex - 1, 0)
          updateAutocompleteSelection(items)
        } else if (e.key === "Enter" && selectedResultIndex >= 0) {
          e.preventDefault()
          items[selectedResultIndex]?.click()
        } else if (e.key === "Escape") {
          autocompleteDropdown.classList.remove("show")
        }
      })

      // Close autocomplete on outside click
      document.addEventListener("click", (e) => {
        if (!e.target.closest(".search-autocomplete-wrapper")) {
          autocompleteDropdown.classList.remove("show")
        }
      })
    }

    // Basic search button
    if (searchBtn) {
      searchBtn.addEventListener("click", () => {
        const institutionName = institutionInput?.value.trim()
        const country = document.getElementById("accred-country")?.value
        const type = document.getElementById("accred-type")?.value

        if (institutionName) {
          searchAccreditation(institutionName, { country, type })
        } else if (country) {
          // Search by country only - use searchAccreditation with empty name
          searchAccreditation('', { country, type })
        } else {
          showToast("Please enter an institution name or select a country", "warning")
        }
      })
    }

    // Advanced search button
    if (advSearchBtn) {
      advSearchBtn.addEventListener("click", () => {
        const filters = {
          name: document.getElementById("adv-institution-name")?.value.trim(),
          whedId: document.getElementById("adv-whed-id")?.value.trim(),
          country: document.getElementById("adv-country")?.value,
          city: document.getElementById("adv-city")?.value.trim(),
          type: document.getElementById("adv-type")?.value,
          yearFrom: document.getElementById("adv-year-from")?.value,
          yearTo: document.getElementById("adv-year-to")?.value,
          accredBody: document.getElementById("adv-accred-body")?.value,
          degreeLevel: document.getElementById("adv-degree-level")?.value,
          partnerOnly: document.getElementById("adv-partner-only")?.checked,
          accreditedOnly: document.getElementById("adv-accredited-only")?.checked,
        }

        searchByFilters(filters)
      })
    }

    // Reset advanced search
    if (advResetBtn) {
      advResetBtn.addEventListener("click", () => {
        document.getElementById("adv-institution-name").value = ""
        document.getElementById("adv-whed-id").value = ""
        document.getElementById("adv-country").value = ""
        document.getElementById("adv-city").value = ""
        document.getElementById("adv-type").value = ""
        document.getElementById("adv-year-from").value = ""
        document.getElementById("adv-year-to").value = ""
        document.getElementById("adv-accred-body").value = ""
        document.getElementById("adv-degree-level").value = ""
        document.getElementById("adv-partner-only").checked = false
        document.getElementById("adv-accredited-only").checked = true
      })
    }

    // Back to results button
    if (backToResults) {
      backToResults.addEventListener("click", () => {
        document.getElementById("accreditation-result").classList.add("hidden")
        resultsList.classList.remove("hidden")
      })
    }

    // Institution tabs
    document.querySelectorAll(".inst-tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".inst-tab").forEach((t) => t.classList.remove("active"))
        document.querySelectorAll(".inst-tab-content").forEach((c) => c.classList.remove("active"))

        tab.classList.add("active")
        document.getElementById(`tab-${tab.dataset.tab}`).classList.add("active")
      })
    })

    // Filter chips
    document.querySelectorAll(".filter-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        document.querySelectorAll(".filter-chip").forEach((c) => c.classList.remove("active"))
        chip.classList.add("active")
        filterResults(chip.dataset.filter)
      })
    })

    // View on WHED button
    document.getElementById("accred-view-whed")?.addEventListener("click", () => {
      window.open("https://www.whed.net/home.php", "_blank")
    })

    // Download report button
    document.getElementById("accred-download-report")?.addEventListener("click", () => {
      showToast("Generating PDF report...", "info")
      setTimeout(() => showToast("Report downloaded successfully", "success"), 1500)
    })
  }

  async function searchInstitutions(query) {
    if (!query || query.length < 2) {
      return []
    }

    try {
      // Get CSRF token
      const csrfToken = getCSRFToken()
      
      const response = await fetch('/api/public/accreditation/search/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || '',
          'X-CSRF-Token': csrfToken || ''  // Some Django versions expect this format
        },
        body: JSON.stringify({
          institution_name: query.trim()
        })
      })

      const data = await response.json()

      if (data.success) {
        // Transform API response to match autocomplete format
        const results = []
        
        // Add CertChain institutions
        if (data.institutions && data.institutions.length > 0) {
          data.institutions.forEach(inst => {
            results.push({
              name: inst.name,
              country: inst.country || '',
              countryCode: inst.country || '',
              city: inst.city || '',
              type: inst.institution_type || '',
              whedId: inst.whed_id || '',
              is_partner: inst.is_partner || false
            })
          })
        }
        
        // Add WHED records
        if (data.whed_records && data.whed_records.length > 0) {
          data.whed_records.forEach(whed => {
            results.push({
              name: whed.name || whed.institution_name || '',
              country: whed.country || '',
              countryCode: whed.country || '',
              city: whed.city || '',
              type: whed.institution_type || '',
              whedId: whed.whed_id || '',
              is_partner: false
            })
          })
        }
        
        return results.slice(0, 8) // Limit results
      }
      
      return []
    } catch (error) {
      console.error('Institution search error:', error)
      return []
    }
  }

  function displayAutocompleteResults(results, container, loading, dropdown) {
    loading.classList.remove("show")

    if (results.length === 0) {
      container.innerHTML = `
        <li class="no-results" style="padding: 1rem; text-align: center; color: var(--text-muted);">
          No institutions found. Try a different search term.
        </li>
      `
      return
    }

    container.innerHTML = results
      .map(
        (inst, index) => `
      <li data-index="${index}" data-name="${inst.name}">
        <div class="inst-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
            <path d="M6 12v5c3 3 9 3 12 0v-5"/>
          </svg>
        </div>
        <div class="inst-info">
          <div class="inst-name">${inst.name}</div>
          <div class="inst-meta">
            <span>${inst.country || inst.countryCode || ''}</span>
            ${inst.whedId ? `<span>• ${inst.whedId}</span>` : ""}
          </div>
        </div>
        ${inst.is_partner || inst.partnerStatus ? '<span class="partner-badge">Partner</span>' : ""}
      </li>
    `,
      )
      .join("")

    // Add click handlers
    container.querySelectorAll("li").forEach((item) => {
      item.addEventListener("click", () => {
        const name = item.dataset.name
        document.getElementById("accred-institution-input").value = name
        dropdown.classList.remove("show")
        searchAccreditation(name)
      })
    })

    selectedResultIndex = -1
  }

  function updateAutocompleteSelection(items) {
    items.forEach((item, index) => {
      if (index === selectedResultIndex) {
        item.style.background = "var(--bg-secondary)"
      } else {
        item.style.background = ""
      }
    })
  }

  async function searchByFilters(filters) {
    const searchBtn = document.getElementById("adv-search-btn") || document.getElementById("accred-search-btn")
    const resultsList = document.getElementById("accreditation-results-list")
    const resultsGrid = document.getElementById("results-grid")
    const resultsCount = document.getElementById("results-count")
    const accreditationResultElement = document.getElementById("accreditation-result")

    if (searchBtn) {
      searchBtn.disabled = true
      searchBtn.innerHTML = '<span class="spinner"></span> Searching...'
    }

    try {
      // Get CSRF token
      const csrfToken = getCSRFToken()
      
      // Use the same API endpoint with available filters
      // Note: Advanced filters like yearFrom, yearTo, accredBody, degreeLevel
      // may need backend support - for now we use basic filters
      const response = await fetch('/api/public/accreditation/search/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || '',
          'X-CSRF-Token': csrfToken || ''  // Some Django versions expect this format
        },
        body: JSON.stringify({
          institution_name: filters.name || '',
          country: filters.country || '',
          institution_type: filters.type || ''
        })
      })

      const data = await response.json()

      if (data.success) {
        let results = []
        
        // Combine institutions and WHED records
        if (data.institutions && data.institutions.length > 0) {
          results = results.concat(data.institutions)
        }
        if (data.whed_records && data.whed_records.length > 0) {
          results = results.concat(data.whed_records)
        }

        // Apply client-side filters that aren't supported by API yet
        if (filters.city) {
          const cityQuery = filters.city.toLowerCase()
          results = results.filter((inst) => (inst.city || '').toLowerCase().includes(cityQuery))
        }

        if (filters.partnerOnly) {
          results = results.filter((inst) => inst.is_partner === true)
        }

        if (filters.accreditedOnly) {
          results = results.filter((inst) => {
            const status = inst.accreditation_status || ''
            return status.toLowerCase().includes('accredited') || 
                   status.toLowerCase().includes('verified') ||
                   inst.is_verified === true
          })
        }

        currentSearchResults = results

        // Display results
        if (results.length === 1) {
          displayAccreditationResult(results[0], results[0].name)
          if (resultsList) resultsList.classList.add("hidden")
          if (accreditationResultElement) accreditationResultElement.classList.remove("hidden")
          const backBtn = document.getElementById("back-to-results")
          if (backBtn) backBtn.classList.add("hidden")
        } else if (results.length > 1) {
          displayResultsList(results, resultsGrid, resultsCount)
          if (resultsList) resultsList.classList.remove("hidden")
          if (accreditationResultElement) accreditationResultElement.classList.add("hidden")
          const backBtn = document.getElementById("back-to-results")
          if (backBtn) backBtn.classList.add("hidden")
        } else {
          displayAccreditationResult(null, filters.name || "your search")
          if (resultsList) resultsList.classList.add("hidden")
          if (accreditationResultElement) accreditationResultElement.classList.remove("hidden")
        }
      } else {
        showToast(data.error || 'Failed to search institutions', "error")
        displayAccreditationResult(null, filters.name || "your search")
      }
    } catch (error) {
      console.error('Filter search error:', error)
      showToast("An error occurred while searching. Please try again.", "error")
      displayAccreditationResult(null, filters.name || "your search")
    } finally {
      // Reset button
      if (searchBtn) {
        searchBtn.disabled = false
        searchBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
          Search Database
        `
      }
    }
  }

  function displayResultsList(results, container, countElement) {
    countElement.textContent = `${results.length} institution${results.length !== 1 ? "s" : ""} found`

    container.innerHTML = results
      .map(
        (inst) => `
      <div class="result-card" data-name="${inst.name.toLowerCase()}">
        <div class="inst-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
            <path d="M6 12v5c3 3 9 3 12 0v-5"/>
          </svg>
        </div>
        <div class="inst-details">
          <div class="inst-name">${inst.name}</div>
          <div class="inst-location">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            ${inst.city}, ${inst.country}
          </div>
          <div class="inst-badges">
            <span class="badge ${inst.accredited ? "badge-success" : "badge-error"}">${inst.accredited ? "Accredited" : "Not Accredited"}</span>
            ${inst.partnerStatus ? '<span class="badge badge-primary">CertChain Partner</span>' : ""}
            ${inst.whedId ? `<span class="badge badge-secondary">${inst.whedId}</span>` : ""}
          </div>
        </div>
        <div class="result-arrow">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </div>
      </div>
    `,
      )
      .join("")

    // Add click handlers
    container.querySelectorAll(".result-card").forEach((card) => {
      card.addEventListener("click", () => {
        const institutionData = card.dataset.institution
        if (institutionData) {
          try {
            const institution = JSON.parse(institutionData)
            displayAccreditationResult(institution, institution.name)
            document.getElementById("accreditation-results-list").classList.add("hidden")
            document.getElementById("back-to-results").classList.remove("hidden")
            document.getElementById("accreditation-result").classList.remove("hidden")
          } catch (e) {
            console.error('Error parsing institution data:', e)
          }
        }
      })
    })
  }

  function filterResults(filter) {
    let filtered = currentSearchResults

    if (filter === "accredited") {
      filtered = currentSearchResults.filter((inst) => inst.accredited)
    } else if (filter === "partner") {
      filtered = currentSearchResults.filter((inst) => inst.partnerStatus)
    }

    displayResultsList(filtered, document.getElementById("results-grid"), document.getElementById("results-count"))
  }

  function displayAccreditationResult(institution, searchTerm) {
    const resultElement = elements.accreditationResult
    if (!resultElement) return

    const resultIcon = document.getElementById("accred-result-icon")
    const resultTitle = document.getElementById("accred-result-title")
    const resultSubtitle = document.getElementById("accred-result-subtitle")
    const resultBadge = document.getElementById("accred-result-badge")
    const resultDetails = document.getElementById("accred-details")
    const guidance = document.getElementById("accred-guidance")
    const timeline = document.getElementById("accred-timeline")
    const programsList = document.getElementById("programs-list")
    const backToResults = document.getElementById("back-to-results")

    resultElement.classList.remove("hidden")

    // Reset tabs to overview
    document.querySelectorAll(".inst-tab").forEach((t) => t.classList.remove("active"))
    document.querySelectorAll(".inst-tab-content").forEach((c) => c.classList.remove("active"))
    document.querySelector('.inst-tab[data-tab="overview"]')?.classList.add("active")
    document.getElementById("tab-overview")?.classList.add("active")

    if (institution) {
      resultIcon.className = `accred-result-icon ${institution.accredited ? "accredited" : "unaccredited"}`
      resultIcon.innerHTML = institution.accredited
        ? '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 12 2 2 4-4"/><circle cx="12" cy="12" r="10"/></svg>'
        : '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" x2="9" y1="9" y2="15"/><line x1="9" x2="15" y1="9" y2="15"/></svg>'

      resultTitle.textContent = institution.name
      resultSubtitle.textContent = institution.accredited
        ? "This institution is accredited and recognized"
        : "This institution is NOT accredited - Exercise caution"

      resultBadge.className = `badge ${institution.accredited ? "badge-success" : "badge-error"}`
      resultBadge.textContent = institution.accredited ? "Accredited" : "Not Accredited"

      // Overview details
      resultDetails.innerHTML = `
        <div class="accred-detail-item">
          <div class="accred-detail-label">Country</div>
          <div class="accred-detail-value">${institution.country}</div>
        </div>
        <div class="accred-detail-item">
          <div class="accred-detail-label">City</div>
          <div class="accred-detail-value">${institution.city}</div>
        </div>
        <div class="accred-detail-item">
          <div class="accred-detail-label">Type</div>
          <div class="accred-detail-value">${institution.type}</div>
        </div>
        <div class="accred-detail-item">
          <div class="accred-detail-label">Founded</div>
          <div class="accred-detail-value">${institution.founded || "N/A"}</div>
        </div>
        <div class="accred-detail-item">
          <div class="accred-detail-label">UNESCO WHED ID</div>
          <div class="accred-detail-value">${institution.whedId || "Not Listed"}</div>
        </div>
        <div class="accred-detail-item">
          <div class="accred-detail-label">Students</div>
          <div class="accred-detail-value">${institution.studentCount?.toLocaleString() || "N/A"}</div>
        </div>
        <div class="accred-detail-item" style="grid-column: span 2;">
          <div class="accred-detail-label">Recognition</div>
          <div class="accred-detail-value">${institution.recognition}</div>
        </div>
        <div class="accred-detail-item" style="grid-column: span 2;">
          <div class="accred-detail-label">Accreditation Bodies</div>
          <div class="accred-detail-value">${institution.accreditationBodies?.join(", ") || "None"}</div>
        </div>
        <div class="accred-detail-item" style="grid-column: span 2;">
          <div class="accred-detail-label">Degrees Offered</div>
          <div class="accred-detail-value">${institution.degrees?.join(", ") || "None"}</div>
        </div>
        <div class="accred-detail-item" style="grid-column: span 2;">
          <div class="accred-detail-label">CertChain Partner</div>
          <div class="accred-detail-value">${institution.partnerStatus ? '<span style="color: var(--success);"><strong>Yes</strong> - Blockchain verification available</span>' : '<span style="color: var(--warning);">No - Manual verification required</span>'}</div>
        </div>
      `

      // Accreditation timeline
      if (timeline && institution.accreditationHistory && institution.accreditationHistory.length > 0) {
        timeline.innerHTML = institution.accreditationHistory
          .map(
            (event) => `
          <div class="timeline-item ${event.status}">
            <div class="timeline-date">${event.date}</div>
            <div class="timeline-title">${event.event}</div>
          </div>
        `,
          )
          .join("")
        document.getElementById("accred-timeline-section").classList.remove("hidden")
      } else {
        document.getElementById("accred-timeline-section").classList.add("hidden")
      }

      // Programs list
      if (programsList && institution.programs && institution.programs.length > 0) {
        programsList.innerHTML = institution.programs
          .map(
            (prog) => `
          <div class="program-card">
            <div class="program-info">
              <h4>${prog.name}</h4>
              <p>Duration: ${prog.duration}</p>
            </div>
            <span class="program-level">${prog.level}</span>
          </div>
        `,
          )
          .join("")
        document.getElementById("accred-programs-section").classList.remove("hidden")
      } else {
        document.getElementById("accred-programs-section").classList.add("hidden")
      }

      // Verification guidance
      if (!institution.partnerStatus) {
        guidance.innerHTML = `
          <h4>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
            How to Verify Credentials from This Institution
          </h4>
          <ul>
            <li>Contact the institution's registrar office directly at <strong>${institution.verificationContact || "N/A"}</strong></li>
            <li>Visit their official website: <strong>${institution.website || "N/A"}</strong></li>
            <li>Request official verification through their alumni services</li>
            <li>Check with the ${institution.recognition} for degree recognition</li>
            <li>Request transcript verification through the national student clearinghouse (if applicable)</li>
          </ul>
        `
      } else {
        guidance.innerHTML = `
          <h4>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 12 2 2 4-4"/><circle cx="12" cy="12" r="10"/>
            </svg>
            Blockchain Verification Available
          </h4>
          <ul>
            <li><strong>This institution is a CertChain partner</strong></li>
            <li>Credentials can be verified instantly using our verification portal</li>
            <li>All credentials are secured on the blockchain with IPFS backup</li>
            <li>Verification takes less than 30 seconds</li>
            <li>QR codes on certificates link directly to blockchain records</li>
          </ul>
          <a href="#page-verify" class="btn btn-teal" style="margin-top: 1rem;" onclick="navigateTo('verify')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 12 2 2 4-4"/><circle cx="12" cy="12" r="10"/>
            </svg>
            Verify a Credential Now
          </a>
        `
      }

      showToast(`Found: ${institution.name}`, "success")
    } else {
      // Not found
      resultIcon.className = "accred-result-icon not-found"
      resultIcon.innerHTML =
        '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M16 16s-1.5-2-4-2-4 2-4 2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/></svg>'
      resultTitle.textContent = "Institution Not Found"
      resultSubtitle.textContent = `"${searchTerm}" was not found in our database`
      resultBadge.className = "badge badge-warning"
      resultBadge.textContent = "Not Found"

      resultDetails.innerHTML = `
        <div class="accred-detail-item" style="grid-column: span 2;">
          <div class="accred-detail-label">Search Tips</div>
          <div class="accred-detail-value">
            <ul style="margin: 0; padding-left: 1.25rem; color: var(--text-secondary);">
              <li>Check the spelling of the institution name</li>
              <li>Try using the full official name</li>
              <li>Search by country to browse institutions</li>
              <li>The institution may not be in UNESCO WHED</li>
              <li>Use advanced search for more options</li>
            </ul>
          </div>
        </div>
      `

      if (timeline) timeline.innerHTML = ""
      if (programsList) programsList.innerHTML = ""
      document.getElementById("accred-timeline-section").classList.add("hidden")
      document.getElementById("accred-programs-section").classList.add("hidden")

      guidance.innerHTML = `
        <h4>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          Warning: Unverified Institution
        </h4>
        <ul>
          <li><strong>Exercise extreme caution</strong> with credentials from unverified institutions</li>
          <li>Visit the UNESCO WHED database directly for comprehensive search</li>
          <li>Contact the relevant national education ministry</li>
          <li>Check if the institution appears on any diploma mill lists</li>
          <li>Request additional documentation from the credential holder</li>
        </ul>
      `

      showToast("Institution not found in database", "warning")
    }

    // Hide back button if coming from single search or results list is empty/single
    if (backToResults) {
      if (currentSearchResults.length <= 1) {
        backToResults.classList.add("hidden")
      } else {
        backToResults.classList.remove("hidden")
      }
    }
  }

  // Tab Switching
    function switchTab(tabId) {
    // Update tab buttons
    elements.verifyTabs.forEach((tab) => {
      tab.classList.toggle("active", tab.dataset.tab === tabId)
    })

    // Update tab panels
    document.querySelectorAll('[id^="tab-"]').forEach((content) => {
      const isActive = content.id === `tab-${tabId}`
      if (isActive) {
        content.classList.remove("hidden")
      } else {
        content.classList.add("hidden")
      }
    })

    // Stop QR scanner if switching away from QR tab
    if (tabId !== 'qr' && qrScannerInstance) {
      stopQRScanner()
    }
  }

  // Authentication
  function handleLogin(email, password) {
    if (!email || !password) {
      showToast("Please fill in all fields", "error")
      return
    }

    const submitBtn = document.getElementById("login-submit-btn")
    const btnText = submitBtn?.querySelector(".btn-text")
    const btnSpinner = submitBtn?.querySelector(".btn-spinner")
    const errorDiv = document.getElementById("login-error")
    
    // Show loading state
    if (submitBtn) {
      submitBtn.disabled = true
      if (btnText) btnText.style.display = "none"
      if (btnSpinner) btnSpinner.style.display = "inline-block"
    }
    if (errorDiv) errorDiv.style.display = "none"

    // Get CSRF token
    const csrfToken = getCSRFToken()

    fetch("/login/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({
        email: email,
        password: password
      }),
      credentials: 'include'  // Include cookies for session
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => {
          throw new Error(JSON.stringify(err))
        })
      }
      return response.json()
    })
    .then(data => {
      if (data.tokens && data.user) {
        // Store tokens
        localStorage.setItem("access_token", data.tokens.access)
        localStorage.setItem("refresh_token", data.tokens.refresh)
        localStorage.setItem("user", JSON.stringify(data.user))
        
        // Update state
        state.isLoggedIn = true
        state.user = data.user
        
        // Close modal and show success
        closeAllModals()
        showToast(data.message || "Welcome back! You are now signed in.", "success")
        updateNavbarForLoggedIn()
        updateWalletView()
        
        // Redirect to dashboard
        setTimeout(() => {
          window.location.href = "/dashboard"
        }, 1000)
      } else {
        throw new Error(data.error || data.message || "Login failed")
      }
    })
    .catch(error => {
      // Suppress browser extension errors
      if (error.message && error.message.includes('message channel')) {
        return
      }
      
      console.error("Login error:", error)
      let errorMessage = "Invalid email or password. Please try again."
      
      try {
        const errorData = JSON.parse(error.message)
        if (errorData.email) {
          errorMessage = Array.isArray(errorData.email) ? errorData.email[0] : errorData.email
        } else if (errorData.password) {
          errorMessage = Array.isArray(errorData.password) ? errorData.password[0] : errorData.password
        } else if (errorData.non_field_errors) {
          errorMessage = Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors
        } else if (typeof errorData === 'object') {
          errorMessage = Object.values(errorData)[0] || errorMessage
        }
      } catch (e) {
        errorMessage = error.message || errorMessage
      }
      
      showToast(errorMessage, "error")
      if (errorDiv) {
        errorDiv.textContent = errorMessage
        errorDiv.style.display = "block"
      }
    })
    .finally(() => {
      // Reset button state
      if (submitBtn) {
        submitBtn.disabled = false
        if (btnText) btnText.style.display = "inline"
        if (btnSpinner) btnSpinner.style.display = "none"
      }
    })
  }

  // Handle role change in signup form
  function handleRoleChange(role) {
    const institutionGroup = document.getElementById("signup-institution-group")
    const employerGroup = document.getElementById("signup-employer-group")
    const institutionSelect = document.getElementById("signup-institution")
    const institutionHint = document.getElementById("signup-institution-hint")
    
    // Hide all conditional groups first
    if (institutionGroup) institutionGroup.style.display = "none"
    if (employerGroup) employerGroup.style.display = "none"
    if (institutionSelect) institutionSelect.required = false
    
    // Show relevant group based on role
    if (role === "student" || role === "institution_admin") {
      if (institutionGroup) institutionGroup.style.display = "block"
      if (institutionSelect) institutionSelect.required = true
      
      // Update hint text
      if (institutionHint) {
        if (role === "student") {
          institutionHint.textContent = "Only partner institutions are available for students"
        } else {
          institutionHint.textContent = "Search and select the institution you belong to"
        }
      }
      
      // Initialize Select2 with AJAX (with small delay to ensure modal is ready)
      setTimeout(() => {
        initializeInstitutionSelect2(role === "student")
      }, 100)
    } else if (role === "employer") {
      if (employerGroup) employerGroup.style.display = "block"
      const companyNameInput = document.getElementById("signup-company-name")
      if (companyNameInput) companyNameInput.required = true
      
      // Destroy Select2 if it was initialized
      if (institutionSelect && $(institutionSelect).hasClass("select2-hidden-accessible")) {
        $(institutionSelect).select2('destroy')
      }
    }
  }
  
  // Initialize Select2 with AJAX for institution selection
  function initializeInstitutionSelect2(partnerOnly = false) {
    const institutionSelect = document.getElementById("signup-institution")
    if (!institutionSelect) return
    
    // Wait for jQuery and Select2 to be available
    if (typeof $ === 'undefined' || typeof $.fn.select2 === 'undefined') {
      console.error('jQuery or Select2 not loaded. Retrying in 500ms...')
      setTimeout(() => {
        initializeInstitutionSelect2(partnerOnly)
      }, 500)
      return
    }
    
    // Destroy existing Select2 instance if it exists
    if ($(institutionSelect).hasClass("select2-hidden-accessible")) {
      $(institutionSelect).select2('destroy')
    }
    
    // Clear the select
    institutionSelect.innerHTML = '<option value="">Search and select your institution...</option>'
    
    // Get the modal element for dropdownParent
    const signupModal = document.getElementById("signup-modal")
    const dropdownParent = signupModal ? $(signupModal) : $('body')
    
    // Initialize Select2 with AJAX
    $(institutionSelect).select2({
      theme: 'bootstrap-5',
      placeholder: 'Search and select your institution...',
      allowClear: true,
      dropdownParent: dropdownParent, // Important: attach dropdown to modal
      ajax: {
        url: '/api/v1/institutions/',
        dataType: 'json',
        delay: 250,
        headers: {
          'Accept': 'application/json'
        },
        data: function (params) {
          var query = {
            page: params.page || 1
          }
          
          // Add search parameter only if there's a search term
          if (params.term && params.term.trim().length > 0) {
            query.search = params.term.trim() // DRF SearchFilter expects 'search'
          }
          
          // Only add is_partner filter if partnerOnly is true
          if (partnerOnly) {
            query.is_partner = 'true'
          }
          
          return query
        },
        processResults: function (data, params) {
          params.page = params.page || 1
          
          // Handle both paginated and non-paginated responses
          let institutions = []
          if (data && data.results && Array.isArray(data.results)) {
            // Paginated response (DRF default)
            institutions = data.results
          } else if (data && Array.isArray(data)) {
            // Non-paginated response
            institutions = data
          }
          
          // Map institutions to Select2 format
          const mappedResults = institutions.map(function(inst) {
            return {
              id: inst.id,
              text: inst.name + (inst.country ? ` (${inst.country})` : ''),
              name: inst.name,
              country: inst.country || ''
            }
          })
          
          return {
            results: mappedResults,
            pagination: {
              // Check if there are more pages (DRF pagination)
              more: (data && data.next) ? true : false
            }
          }
        },
        error: function(xhr, status, error) {
          console.error('Select2 AJAX Error:', {
            status: status,
            error: error,
            response: xhr.responseText
          })
        },
        cache: false // Disable cache to ensure fresh results
      },
      minimumInputLength: 1,
      language: {
        inputTooShort: function () {
          return 'Please enter at least 1 character to search'
        },
        searching: function () {
          return 'Searching...'
        },
        noResults: function () {
          return 'No institutions found'
        }
      }
    })
  }

  function handleSignup(role, firstName, lastName, email, phone, password, passwordConfirm, institutionId, companyName, companyAddress, companyPhone) {
    if (!role || !firstName || !lastName || !email || !password || !passwordConfirm) {
      showToast("Please fill in all required fields", "error")
      return
    }

    if (password !== passwordConfirm) {
      showToast("Passwords do not match", "error")
      return
    }
    
    // Validate role-specific fields
    if ((role === "student" || role === "institution_admin") && !institutionId) {
      showToast("Please select an institution", "error")
      return
    }
    
    if (role === "employer" && !companyName) {
      showToast("Please enter your company/office name", "error")
      return
    }

    const submitBtn = document.getElementById("signup-submit-btn")
    const btnText = submitBtn?.querySelector(".btn-text")
    const btnSpinner = submitBtn?.querySelector(".btn-spinner")
    const errorDiv = document.getElementById("signup-error")
    
    // Show loading state
    if (submitBtn) {
      submitBtn.disabled = true
      if (btnText) btnText.style.display = "none"
      if (btnSpinner) btnSpinner.style.display = "inline-block"
    }
    if (errorDiv) errorDiv.style.display = "none"

    // Get CSRF token
    const csrfToken = getCSRFToken()
    
    // Build request body
    const requestBody = {
      email: email,
      password: password,
      password_confirm: passwordConfirm,
      first_name: firstName,
      last_name: lastName,
      phone: phone || "",
      role: role
    }
    
    // Add role-specific fields
    if (role === "student" || role === "institution_admin") {
      if (institutionId) {
        requestBody.institution_id = institutionId
      }
    }
    
    if (role === "employer") {
      requestBody.company_name = companyName || ""
      requestBody.company_address = companyAddress || ""
      requestBody.company_phone = companyPhone || ""
    }

    fetch("/register/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify(requestBody),
      credentials: 'include'  // Include cookies for session
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => {
          throw new Error(JSON.stringify(err))
        })
      }
      return response.json()
    })
    .then(data => {
      if (data.tokens && data.user) {
        // Store tokens
        localStorage.setItem("access_token", data.tokens.access)
        localStorage.setItem("refresh_token", data.tokens.refresh)
        localStorage.setItem("user", JSON.stringify(data.user))
        
        // Update state
        state.isLoggedIn = true
        state.user = data.user
        
        // Close modal and show success
        closeAllModals()
        showToast(data.message || "Account created successfully! Welcome to CertChain.", "success")
        updateNavbarForLoggedIn()
        updateWalletView()
        
        // Reload page to update UI
        setTimeout(() => {
          window.location.reload()
        }, 1000)
      } else {
        throw new Error(data.error || data.message || "Registration failed")
      }
    })
    .catch(error => {
      // Suppress browser extension errors
      if (error.message && error.message.includes('message channel')) {
        return
      }
      
      console.error("Signup error:", error)
      let errorMessage = "Registration failed. Please try again."
      
      try {
        const errorData = JSON.parse(error.message)
        if (errorData.email) {
          errorMessage = Array.isArray(errorData.email) ? errorData.email[0] : errorData.email
        } else if (errorData.password) {
          errorMessage = Array.isArray(errorData.password) ? errorData.password[0] : errorData.password
        } else if (errorData.password_confirm) {
          errorMessage = Array.isArray(errorData.password_confirm) ? errorData.password_confirm[0] : errorData.password_confirm
        } else if (errorData.institution_id) {
          errorMessage = Array.isArray(errorData.institution_id) ? errorData.institution_id[0] : errorData.institution_id
        } else if (errorData.company_name) {
          errorMessage = Array.isArray(errorData.company_name) ? errorData.company_name[0] : errorData.company_name
        } else if (errorData.non_field_errors) {
          errorMessage = Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors
        } else if (typeof errorData === 'object') {
          errorMessage = Object.values(errorData)[0] || errorMessage
        }
      } catch (e) {
        errorMessage = error.message || errorMessage
      }
      
      showToast(errorMessage, "error")
      if (errorDiv) {
        errorDiv.textContent = errorMessage
        errorDiv.style.display = "block"
      }
    })
    .finally(() => {
      // Reset button state
      if (submitBtn) {
        submitBtn.disabled = false
        if (btnText) btnText.style.display = "inline"
        if (btnSpinner) btnSpinner.style.display = "none"
      }
    })
  }

  // QR Scanner
  let qrScannerInstance = null
  function startQRScanner() {
    const scannerPlaceholder = document.getElementById("qr-scanner")
    const startBtn = document.getElementById("start-qr-scan")
    if (!scannerPlaceholder) return

    // Check if QR scanner library is available
    if (typeof QrScanner !== 'undefined') {
      // Use real QR scanner library
      try {
        QrScanner.hasCamera().then(hasCamera => {
          if (!hasCamera) {
            scannerPlaceholder.innerHTML = `
              <div style="text-align: center; padding: 2rem;">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5" style="margin-bottom: 1rem;">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                  <circle cx="12" cy="13" r="4"/>
                </svg>
                <p style="color: var(--text-muted); margin-bottom: 1rem;">Camera not available</p>
                <button class="btn btn-secondary" onclick="uploadQRImage()">Upload QR Image Instead</button>
              </div>
            `
            return
          }

          // Create video element
          const video = document.createElement('video')
          video.style.width = '100%'
          video.style.height = '100%'
          video.style.objectFit = 'cover'
          video.style.borderRadius = 'var(--radius-md)'
          scannerPlaceholder.innerHTML = ''
          scannerPlaceholder.appendChild(video)

          // Create scanner overlay
          const overlay = document.createElement('div')
          overlay.style.position = 'absolute'
          overlay.style.top = '0'
          overlay.style.left = '0'
          overlay.style.width = '100%'
          overlay.style.height = '100%'
          overlay.style.pointerEvents = 'none'
          overlay.innerHTML = `
            <div style="border: 2px solid var(--accent-primary); width: 200px; height: 200px; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); border-radius: 8px;">
              <div style="position: absolute; top: -2px; left: -2px; width: 20px; height: 20px; border-top: 3px solid var(--accent-primary); border-left: 3px solid var(--accent-primary);"></div>
              <div style="position: absolute; top: -2px; right: -2px; width: 20px; height: 20px; border-top: 3px solid var(--accent-primary); border-right: 3px solid var(--accent-primary);"></div>
              <div style="position: absolute; bottom: -2px; left: -2px; width: 20px; height: 20px; border-bottom: 3px solid var(--accent-primary); border-left: 3px solid var(--accent-primary);"></div>
              <div style="position: absolute; bottom: -2px; right: -2px; width: 20px; height: 20px; border-bottom: 3px solid var(--accent-primary); border-right: 3px solid var(--accent-primary);"></div>
            </div>
          `
          scannerPlaceholder.style.position = 'relative'
          scannerPlaceholder.appendChild(overlay)

          // Create stop button
          const stopBtn = document.createElement('button')
          stopBtn.className = 'btn btn-secondary'
          stopBtn.style.position = 'absolute'
          stopBtn.style.bottom = '1rem'
          stopBtn.style.left = '50%'
          stopBtn.style.transform = 'translateX(-50%)'
          stopBtn.style.zIndex = '10'
          stopBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="6" y="6" width="12" height="12" rx="2"/>
            </svg>
            Stop Camera
          `
          stopBtn.onclick = () => stopQRScanner()
          scannerPlaceholder.appendChild(stopBtn)

          // Initialize scanner
          qrScannerInstance = new QrScanner(
            video,
            result => {
              // Extract credential ID from QR code
              let credentialId = null
              
              // Try to match verification URL pattern
              const urlMatch = result.match(/\/credentials\/verify\/([A-Z0-9-]+)/) ||
                              result.match(/\/v\/([A-Z0-9-]+)/) ||
                              result.match(/verify\/([A-Z0-9-]+)/)
              if (urlMatch) {
                credentialId = urlMatch[1]
              } else {
                // Try to match credential ID pattern directly
                const idMatch = result.match(/(CERT-[A-Z0-9-]+)/i)
                if (idMatch) {
                  credentialId = idMatch[1]
                } else if (result.match(/^CERT-/i)) {
                  credentialId = result
                }
              }
              
              if (credentialId) {
                stopQRScanner()
                verifyCredential(credentialId)
                showToast("QR Code scanned successfully!", "success")
              } else {
                showToast("Could not extract credential ID from QR code", "error")
              }
            },
            {
              returnDetailedScanResult: true,
              highlightScanRegion: false
            }
          )

          qrScannerInstance.start().then(() => {
            if (startBtn) {
              startBtn.style.display = 'none'
            }
          }).catch(err => {
            console.error('QR Scanner error:', err)
            showToast("Failed to start camera. Please check permissions.", "error")
            scannerPlaceholder.innerHTML = `
              <div style="text-align: center; padding: 2rem;">
                <p style="color: var(--error); margin-bottom: 1rem;">Camera access denied or unavailable</p>
                <button class="btn btn-secondary" onclick="uploadQRImage()">Upload QR Image Instead</button>
              </div>
            `
          })
        })
      } catch (error) {
        console.error('QR Scanner initialization error:', error)
        showToast("QR scanner not available. Please enter credential ID manually.", "warning")
      }
    } else {
      // Fallback: Show upload option
      scannerPlaceholder.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
          <p style="color: var(--text-muted); margin-bottom: 1rem;">QR Scanner library not loaded</p>
          <input type="file" id="qr-file-input" accept="image/*" style="display: none;" onchange="handleQRFileUpload(event)">
          <button class="btn btn-secondary" onclick="document.getElementById('qr-file-input').click()">Upload QR Image</button>
        </div>
      `
    }
  }

  function stopQRScanner() {
    if (qrScannerInstance) {
      qrScannerInstance.stop()
      qrScannerInstance.destroy()
      qrScannerInstance = null
    }
    const scannerPlaceholder = document.getElementById("qr-scanner")
    const startBtn = document.getElementById("start-qr-scan")
    if (scannerPlaceholder) {
      scannerPlaceholder.innerHTML = `
        <div style="text-align: center;">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5">
            <rect width="5" height="5" x="3" y="3" rx="1"/>
            <rect width="5" height="5" x="16" y="3" rx="1"/>
            <rect width="5" height="5" x="3" y="16" rx="1"/>
            <path d="M21 16h-3a2 2 0 0 0-2 2v3"/>
          </svg>
          <p style="margin-top: 1rem; font-size: 0.875rem; color: var(--text-muted);">Click to start camera</p>
        </div>
      `
    }
    if (startBtn) {
      startBtn.style.display = 'block'
    }
  }

  // Upload QR image handler
  window.uploadQRImage = function() {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.onchange = handleQRFileUpload
    input.click()
  }

  function handleQRFileUpload(event) {
    const file = event.target.files[0]
    if (!file) return

    if (typeof QrScanner !== 'undefined') {
      QrScanner.scanImage(file)
        .then(result => {
          // Extract credential ID from QR code
          let credentialId = null
          
          const urlMatch = result.match(/\/credentials\/verify\/([A-Z0-9-]+)/) ||
                         result.match(/\/v\/([A-Z0-9-]+)/) ||
                         result.match(/verify\/([A-Z0-9-]+)/)
          if (urlMatch) {
            credentialId = urlMatch[1]
          } else {
            const idMatch = result.match(/(CERT-[A-Z0-9-]+)/i)
            if (idMatch) {
              credentialId = idMatch[1]
            } else if (result.match(/^CERT-/i)) {
              credentialId = result
            }
          }
          
          if (credentialId) {
            verifyCredential(credentialId)
            showToast("QR Code scanned successfully!", "success")
          } else {
            showToast("Could not extract credential ID from QR code. Please enter manually.", "error")
          }
        })
        .catch(error => {
          console.error('QR scan error:', error)
          showToast("Could not read QR code. Please try a clearer image or enter credential ID manually.", "error")
        })
    } else {
      showToast("QR scanner library not available. Please enter credential ID manually.", "warning")
    }
  }

  // Load institutions for search dropdown
  async function loadInstitutionsForSearch() {
    const institutionSelect = document.getElementById("search-institution")
    if (!institutionSelect) return

    try {
      const response = await fetch('/api/public/institutions/list/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      const data = await response.json()

      if (data.success && data.institutions && data.institutions.length > 0) {
        // Clear existing options except the first one
        institutionSelect.innerHTML = '<option value="">Select institution...</option>'
        
        // Add institutions from database
        data.institutions.forEach(inst => {
          const option = document.createElement('option')
          option.value = inst.name.toLowerCase().replace(/\s+/g, '-')
          option.textContent = inst.name
          option.dataset.institutionName = inst.name
          institutionSelect.appendChild(option)
        })
        
        // Add "Other" option
        const otherOption = document.createElement('option')
        otherOption.value = 'other'
        otherOption.textContent = 'Other (Global Search)'
        institutionSelect.appendChild(otherOption)
      }
    } catch (error) {
      console.error('Error loading institutions:', error)
      // Keep default options if API fails
    }
  }

  // Animated Counters
  function animateCounters() {
    const counters = document.querySelectorAll(".counter")

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const counter = entry.target
            const target = Number.parseInt(counter.dataset.target)
            const duration = 2000
            const step = target / (duration / 16)
            let current = 0

            const updateCounter = () => {
              current += step
              if (current < target) {
                counter.textContent = Math.floor(current).toLocaleString()
                requestAnimationFrame(updateCounter)
              } else {
                counter.textContent = target.toLocaleString()
              }
            }

            updateCounter()
            observer.unobserve(counter)
          }
        })
      },
      { threshold: 0.5 },
    )

    counters.forEach((counter) => observer.observe(counter))
  }

  // Activity Feed - Fetch from API
  async function populateActivityFeed() {
    if (!elements.activityList) return

    try {
      const response = await fetch('/api/public/live-activities/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      const data = await response.json()

      if (data.success && data.activities && data.activities.length > 0) {
        elements.activityList.innerHTML = data.activities
          .map(
            (activity) => `
          <div class="activity-item">
            <div class="activity-dot ${activity.type}"></div>
            <div class="activity-text">${activity.text}</div>
            <div class="activity-time">${activity.time}</div>
          </div>
        `,
          )
          .join("")
      } else {
        // Fallback if no activities
        elements.activityList.innerHTML = `
          <div class="activity-item">
            <div class="activity-dot success"></div>
            <div class="activity-text">System is ready for verifications</div>
            <div class="activity-time">Just now</div>
          </div>
        `
      }
    } catch (error) {
      console.error('Error fetching activities:', error)
      // Fallback on error
      elements.activityList.innerHTML = `
        <div class="activity-item">
          <div class="activity-dot info"></div>
          <div class="activity-text">Loading verification activities...</div>
          <div class="activity-time">Just now</div>
        </div>
      `
    }
  }

  // Password Toggle Functions
  function initPasswordToggles() {
    // Login password toggle
    const loginPasswordToggle = document.getElementById("login-password-toggle")
    const loginPasswordInput = document.getElementById("login-password")
    const loginPasswordEye = document.getElementById("login-password-eye")
    const loginPasswordEyeOff = document.getElementById("login-password-eye-off")
    
    if (loginPasswordToggle && loginPasswordInput) {
      loginPasswordToggle.addEventListener("click", () => {
        const isPassword = loginPasswordInput.type === "password"
        loginPasswordInput.type = isPassword ? "text" : "password"
        if (loginPasswordEye) loginPasswordEye.style.display = isPassword ? "none" : "block"
        if (loginPasswordEyeOff) loginPasswordEyeOff.style.display = isPassword ? "block" : "none"
      })
    }

    // Signup password toggle
    const signupPasswordToggle = document.getElementById("signup-password-toggle")
    const signupPasswordInput = document.getElementById("signup-password")
    const signupPasswordEye = document.getElementById("signup-password-eye")
    const signupPasswordEyeOff = document.getElementById("signup-password-eye-off")
    
    if (signupPasswordToggle && signupPasswordInput) {
      signupPasswordToggle.addEventListener("click", () => {
        const isPassword = signupPasswordInput.type === "password"
        signupPasswordInput.type = isPassword ? "text" : "password"
        if (signupPasswordEye) signupPasswordEye.style.display = isPassword ? "none" : "block"
        if (signupPasswordEyeOff) signupPasswordEyeOff.style.display = isPassword ? "block" : "none"
      })
    }

    // Signup password confirm toggle
    const signupPasswordConfirmToggle = document.getElementById("signup-password-confirm-toggle")
    const signupPasswordConfirmInput = document.getElementById("signup-password-confirm")
    const signupPasswordConfirmEye = document.getElementById("signup-password-confirm-eye")
    const signupPasswordConfirmEyeOff = document.getElementById("signup-password-confirm-eye-off")
    
    if (signupPasswordConfirmToggle && signupPasswordConfirmInput) {
      signupPasswordConfirmToggle.addEventListener("click", () => {
        const isPassword = signupPasswordConfirmInput.type === "password"
        signupPasswordConfirmInput.type = isPassword ? "text" : "password"
        if (signupPasswordConfirmEye) signupPasswordConfirmEye.style.display = isPassword ? "none" : "block"
        if (signupPasswordConfirmEyeOff) signupPasswordConfirmEyeOff.style.display = isPassword ? "block" : "none"
      })
    }
  }

  // Event Listeners
  function initEventListeners() {
    // Navigation
    elements.navLinks.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault()
        const pageId = link.dataset.page
        if (pageId) navigateTo(pageId)
      })
    })

    // Action buttons
    elements.actionButtons.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault()
        const action = btn.dataset.action
        if (action === "login") {
          closeAllModals()
          openModal("login-modal")
        } else if (action === "signup") {
          closeAllModals()
          openModal("signup-modal")
        } else if (action === "logout") {
          handleLogout()
        }
      })
    })

    // Logout button (separate listener in case it's not in actionButtons)
    const logoutBtn = document.getElementById("logout-btn")
    if (logoutBtn) {
      logoutBtn.addEventListener("click", (e) => {
        e.preventDefault()
        handleLogout()
      })
    }

    // Theme toggle
    if (elements.themeToggle) {
      elements.themeToggle.addEventListener("click", toggleTheme)
    }

    // Notification panel
    if (elements.notificationBtn) {
      elements.notificationBtn.addEventListener("click", () => {
        elements.notificationPanel?.classList.toggle("show")
      })
    }

    // Close notification panel when clicking outside
    document.addEventListener("click", (e) => {
      if (
        elements.notificationPanel &&
        !e.target.closest(".notification-btn") &&
        !e.target.closest(".notification-panel")
      ) {
        elements.notificationPanel.classList.remove("show")
      }
    })

    // Mobile menu
    if (elements.mobileMenuBtn) {
      elements.mobileMenuBtn.addEventListener("click", () => {
        elements.navbarLinks?.classList.toggle("show")
      })
    }

    // Modal close buttons
    elements.closeModalBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const modal = btn.closest(".modal-overlay")
        closeModal(modal)
      })
    })

    // Close modal on overlay click
    document.querySelectorAll(".modal-overlay").forEach((overlay) => {
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) {
          closeModal(overlay)
        }
      })
    })

    // Verify tabs
    elements.verifyTabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        switchTab(tab.dataset.tab)
      })
    })

    // Verification buttons
    const verifyByIdBtn = document.getElementById("verify-by-id-btn")
    if (verifyByIdBtn) {
      verifyByIdBtn.addEventListener("click", () => {
        const input = document.getElementById("verify-id-input")
        if (input?.value) {
          verifyCredential(input.value)
        } else {
          showToast("Please enter a credential ID", "error")
        }
      })
    }

    const quickVerifyBtn = document.getElementById("quick-verify-btn")
    if (quickVerifyBtn) {
      quickVerifyBtn.addEventListener("click", () => {
        const input = document.getElementById("quick-verify-input")
        if (input?.value) {
          verifyCredential(input.value)
        } else {
          showToast("Please enter a credential ID", "error")
        }
      })
    }

    const employerVerifyBtn = document.getElementById("employer-verify-btn")
    if (employerVerifyBtn) {
      employerVerifyBtn.addEventListener("click", () => {
        const input = document.getElementById("employer-verify-input")
        if (input?.value) {
          verifyCredential(input.value)
        } else {
          showToast("Please enter a credential ID", "error")
        }
      })
    }

    // QR Scanner
    const startQRScanBtn = document.getElementById("start-qr-scan")
    if (startQRScanBtn) {
      startQRScanBtn.addEventListener("click", startQRScanner)
    }

    // Verify by Hash
    const verifyByHashBtn = document.getElementById("verify-by-hash-btn")
    if (verifyByHashBtn) {
      verifyByHashBtn.addEventListener("click", async () => {
        const hashInput = document.getElementById("verify-hash-input")
        const hash = hashInput?.value.trim()
        
        if (!hash) {
          showToast("Please enter a blockchain hash", "error")
          return
        }

        const btn = verifyByHashBtn
        const originalHTML = btn.innerHTML
        btn.disabled = true
        btn.innerHTML = '<span class="spinner"></span> Verifying...'

        try {
          const csrfToken = getCSRFToken()
          const response = await fetch('/api/v1/credentials/verify/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken || ''
            },
            credentials: 'include',
            body: JSON.stringify({
              blockchain_hash: hash
            })
          })

          // Check if response is JSON before parsing
          const contentType = response.headers.get('content-type')
          let data
          if (contentType && contentType.includes('application/json')) {
            data = await response.json()
          } else {
            // Handle non-JSON responses (like HTML error pages)
            const text = await response.text()
            console.error('Non-JSON response:', text.substring(0, 200))
            throw new Error(`Server returned ${response.status}: ${response.statusText}`)
          }

          if (response.ok && data.valid !== undefined) {
            const credential = {
              credential_id: data.credential?.credential_id || '',
              holder: data.credential?.holder_name || '',
              institution: data.credential?.institution?.name || data.credential?.institution || '',
              degree: data.credential?.degree_level || '',
              program: data.credential?.program_name || '',
              grade: data.credential?.grade || '',
              issued: data.credential?.issue_date || data.credential?.completion_date || '',
              hash: data.credential?.blockchain_hash || hash,
              ipfsHash: data.credential?.ipfs_hash || '',
              valid: data.valid,
              status: data.status || (data.valid ? 'Verified' : 'Revoked'),
              revokedReason: data.credential?.revocation_reason || null,
              timeline: data.credential?.timeline || []
            }

            state.lastVerifiedCredential = credential
            displayVerificationResult(credential, true)
            if (credential.timeline && credential.timeline.length > 0) {
              displayCredentialTimeline(credential)
            } else {
              hideCredentialTimeline()
            }
            showToast(
              credential.valid ? "Credential verified successfully!" : "Credential found but has been revoked",
              credential.valid ? "success" : "error",
            )
          } else {
            displayVerificationResult(null, false)
            hideCredentialTimeline()
            const errorMsg = data.error || data.message || "Credential not found in our records"
            showToast(errorMsg, "error")
          }
        } catch (error) {
          console.error('Hash verification error:', error)
          displayVerificationResult(null, false)
          hideCredentialTimeline()
          
          // Provide more specific error messages
          let errorMessage = "An error occurred while verifying the credential. Please try again."
          if (error.message && error.message.includes('403')) {
            errorMessage = "Authentication error. Please refresh the page and try again."
          } else if (error.message && error.message.includes('CSRF')) {
            errorMessage = "Session expired. Please refresh the page and try again."
          } else if (error.message) {
            errorMessage = error.message
          }
          
          showToast(errorMessage, "error")
        } finally {
          btn.disabled = false
          btn.innerHTML = originalHTML
        }
      })
    }

    // Search Credentials by Name/Institution/Year
    const searchBtn = document.getElementById("search-btn")
    if (searchBtn) {
      searchBtn.addEventListener("click", async () => {
        const nameInput = document.getElementById("search-name")
        const institutionSelect = document.getElementById("search-institution")
        const yearInput = document.getElementById("search-year")
        
        const holderName = nameInput?.value.trim() || ''
        const institutionValue = institutionSelect?.value || ''
        const year = yearInput?.value.trim() || ''

        if (!holderName && !institutionValue && !year) {
          showToast("Please enter at least one search criteria", "error")
          return
        }

        // Get actual institution name from selected option
        let institution = institutionValue
        if (institutionSelect && institutionValue) {
          const selectedOption = institutionSelect.options[institutionSelect.selectedIndex]
          if (selectedOption && selectedOption.dataset.institutionName) {
            institution = selectedOption.dataset.institutionName
          } else if (institutionValue === 'other') {
            institution = 'other'
          }
        }

        const btn = searchBtn
        const originalHTML = btn.innerHTML
        btn.disabled = true
        btn.innerHTML = '<span class="spinner"></span> Searching...'

        try {
          const csrfToken = getCSRFToken()
          const response = await fetch('/api/public/credentials/search/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken || ''
            },
            body: JSON.stringify({
              holder_name: holderName,
              institution: institution,
              year: year
            })
          })

          const data = await response.json()

          if (data.success && data.credentials && data.credentials.length > 0) {
            // Display search results
            if (data.credentials.length === 1) {
              // If only one result, verify it directly
              verifyCredential(data.credentials[0].credential_id)
            } else {
              // Show multiple results - create a results list
              showSearchResults(data.credentials)
            }
          } else {
            showToast("No credentials found matching your search criteria", "info")
          }
        } catch (error) {
          console.error('Search error:', error)
          showToast("An error occurred while searching. Please try again.", "error")
        } finally {
          btn.disabled = false
          btn.innerHTML = originalHTML
        }
      })
    }

    // Accreditation search
    const accredSearchBtn = document.getElementById("accred-search-btn")
    if (accredSearchBtn) {
      accredSearchBtn.addEventListener("click", () => {
        const input = document.getElementById("accred-institution-input")
        if (input?.value) {
          searchAccreditation(input.value)
        } else {
          showToast("Please enter an institution name", "error")
        }
      })
    }

    // Demo wallet link
    const demoWalletLink = document.getElementById("demo-wallet-link")
    if (demoWalletLink) {
      demoWalletLink.addEventListener("click", (e) => {
        e.preventDefault()
        state.showDemoWallet = true
        updateWalletView()
        showToast("Viewing demo wallet", "info")
      })
    }

    // Wallet action buttons
    const downloadAllBtn = document.getElementById("wallet-download-all-btn")
    if (downloadAllBtn) {
      downloadAllBtn.addEventListener("click", async () => {
        if (!state.isLoggedIn && !state.showDemoWallet) {
          showToast("Please log in to download credentials", "error")
          return
        }

        const credentials = document.querySelectorAll(".wallet-credential-card[data-credential-id]")
        if (credentials.length === 0) {
          showToast("No credentials to download", "info")
          return
        }

        showToast("Opening all credentials for download...", "info")
        credentials.forEach((card, index) => {
          setTimeout(() => {
            const credentialId = card.dataset.credentialId
            if (credentialId) {
              downloadCredential(credentialId)
            }
          }, index * 500) // Stagger downloads
        })
      })
    }

    const requestNewBtn = document.getElementById("wallet-request-new-btn")
    if (requestNewBtn) {
      requestNewBtn.addEventListener("click", () => {
        if (!state.isLoggedIn) {
          showToast("Please log in to request a new credential", "error")
          openModal("login-modal")
          return
        }

        // Navigate to contact or request page
        showToast("Please contact your institution to request a new credential", "info")
        // You could also open a modal or navigate to a request page here
      })
    }

    // Copy share link
    const copyShareLinkBtn = document.getElementById("copy-share-link")
    if (copyShareLinkBtn) {
      copyShareLinkBtn.addEventListener("click", () => {
        const input = document.getElementById("share-link-input")
        if (input) {
          navigator.clipboard.writeText(input.value)
          showToast("Link copied to clipboard!", "success")
        }
      })
    }

    // Share credential button
    const shareCredentialBtn = document.getElementById("share-credential-btn")
    if (shareCredentialBtn) {
      shareCredentialBtn.addEventListener("click", () => {
        if (state.lastVerifiedCredential) {
          const credentialId = state.lastVerifiedCredential.credential_id
          const shareUrl = `${window.location.origin}/credentials/verify/${credentialId}/`
          
          // Copy to clipboard
          navigator.clipboard.writeText(shareUrl).then(() => {
            showToast("Verification link copied to clipboard!", "success")
          }).catch(() => {
            // Fallback: show in modal
            openModal("share-modal")
          })
        } else {
          openModal("share-modal")
        }
      })
    }

    // Download PDF button
    const downloadCertBtn = document.getElementById("download-cert-btn")
    if (downloadCertBtn) {
      downloadCertBtn.addEventListener("click", async () => {
        if (!state.lastVerifiedCredential) {
          showToast("No credential to download", "error")
          return
        }

        const credentialId = state.lastVerifiedCredential.credential_id
        try {
          // Open verification page in new tab for printing
          const verifyUrl = `/credentials/verify/${credentialId}/`
          window.open(verifyUrl, '_blank')
          showToast("Opening verification page for download...", "info")
        } catch (error) {
          console.error('Download error:', error)
          showToast("Failed to download. Please try again.", "error")
        }
      })
    }

    // Verify another button
    const verifyAnotherBtn = document.getElementById("verify-another-btn")
    if (verifyAnotherBtn) {
      verifyAnotherBtn.addEventListener("click", () => {
        elements.verifyResult?.classList.remove("show")
        hideCredentialTimeline()
        const input = document.getElementById("verify-id-input")
        if (input) {
          input.value = ""
          input.focus()
        }
        // Clear hash input too
        const hashInput = document.getElementById("verify-hash-input")
        if (hashInput) {
          hashInput.value = ""
        }
        // Clear search inputs
        const searchName = document.getElementById("search-name")
        const searchInstitution = document.getElementById("search-institution")
        const searchYear = document.getElementById("search-year")
        if (searchName) searchName.value = ""
        if (searchInstitution) searchInstitution.value = ""
        if (searchYear) searchYear.value = ""
      })
    }

    // Load institutions for search dropdown
    loadInstitutionsForSearch()

    // Login form
    const loginForm = document.getElementById("login-form")
    if (loginForm) {
      loginForm.addEventListener("submit", (e) => {
        e.preventDefault()
        const email = document.getElementById("login-email")?.value
        const password = document.getElementById("login-password")?.value
        handleLogin(email, password)
      })
    }

    // Signup form
    const signupForm = document.getElementById("signup-form")
    const signupModal = document.getElementById("signup-modal")
    
    // Listen for modal open to ensure Select2 works
    if (signupModal) {
      // Use MutationObserver to detect when modal is shown
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.attributeName === 'class') {
            const isShown = signupModal.classList.contains('show')
            if (isShown) {
              // Modal is now visible, check if Select2 needs initialization
              const institutionSelect = document.getElementById("signup-institution")
              const role = document.getElementById("signup-role")?.value
              if (institutionSelect && (role === "student" || role === "institution_admin")) {
                // Reinitialize Select2 if needed
                setTimeout(() => {
                  if (!$(institutionSelect).hasClass("select2-hidden-accessible")) {
                    initializeInstitutionSelect2(role === "student")
                  }
                }, 200)
              }
            }
          }
        })
      })
      observer.observe(signupModal, { attributes: true, attributeFilter: ['class'] })
    }
    
    if (signupForm) {
      // Handle role change to show/hide conditional fields
      const signupRole = document.getElementById("signup-role")
      if (signupRole) {
        signupRole.addEventListener("change", (e) => {
          handleRoleChange(e.target.value)
        })
      }
      
      signupForm.addEventListener("submit", (e) => {
        e.preventDefault()
        const role = document.getElementById("signup-role")?.value
        const firstName = document.getElementById("signup-first-name")?.value
        const lastName = document.getElementById("signup-last-name")?.value
        const email = document.getElementById("signup-email")?.value
        const phone = document.getElementById("signup-phone")?.value
        const password = document.getElementById("signup-password")?.value
        const passwordConfirm = document.getElementById("signup-password-confirm")?.value
        // Get institution ID from Select2 (use jQuery if available, otherwise native)
        const institutionSelect = document.getElementById("signup-institution")
        const institutionId = (typeof $ !== 'undefined' && $(institutionSelect).hasClass("select2-hidden-accessible")) 
          ? $(institutionSelect).val() 
          : institutionSelect?.value
        const companyName = document.getElementById("signup-company-name")?.value
        const companyAddress = document.getElementById("signup-company-address")?.value
        const companyPhone = document.getElementById("signup-company-phone")?.value
        handleSignup(role, firstName, lastName, email, phone, password, passwordConfirm, institutionId, companyName, companyAddress, companyPhone)
      })
    }

    // Enter key for inputs
    document.querySelectorAll("input, textarea").forEach((input) => {
      input.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          const id = input.id
          if (id === "verify-id-input") {
            document.getElementById("verify-by-id-btn")?.click()
          } else if (id === "quick-verify-input") {
            document.getElementById("quick-verify-btn")?.click()
          } else if (id === "employer-verify-input") {
            document.getElementById("employer-verify-btn")?.click()
          } else if (id === "accred-institution-input") {
            document.getElementById("accred-search-btn")?.click()
          } else if (id === "verify-hash-input") {
            document.getElementById("verify-by-hash-btn")?.click()
          } else if (id === "search-name" || id === "search-year") {
            document.getElementById("search-btn")?.click()
          }
        }
      })
    })
  }

  // Initialize
  function init() {
    initTheme()
    initPasswordToggles() // Initialize password visibility toggles
    initEventListeners()
    animateCounters()
    populateActivityFeed()
    loadInstitutionsForSearch() // Load institutions for search dropdown
    initAccreditationSearch() // Initialize accreditation search functionality
    
    // Check login state after a small delay to ensure DOM is fully rendered
    setTimeout(() => {
      checkLoginState() // Check if user is already logged in
    }, 100)
  }

  // Run on DOM ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init)
  } else {
    init()
  }
  
  // Expose a helper function to force show login buttons (for debugging)
  window.forceShowLoginButtons = function() {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("user")
    state.isLoggedIn = false
    state.user = null
    
    const loginBtn = document.getElementById("login-btn")
    const signupBtn = document.getElementById("signup-btn")
    
    if (loginBtn) {
      loginBtn.style.cssText = "display: inline-block !important; visibility: visible !important; opacity: 1 !important;"
    }
    if (signupBtn) {
      signupBtn.style.cssText = "display: inline-block !important; visibility: visible !important; opacity: 1 !important;"
    }
    
    console.log("Login buttons forced to be visible. If they still don't show, they may not exist in the DOM (user might be authenticated in Django session).")
  }
})()
