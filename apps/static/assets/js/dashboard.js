// Dashboard JavaScript - Role-Based Dynamic Sidebar (Mobile-First Refactor)

;(() => {
  // Get user data from Django template or localStorage
  function getUserData() {
    // Try to get from Django template first
    if (window.DJANGO_USER_DATA && window.DJANGO_USER_DATA.isAuthenticated) {
      const djangoUser = window.DJANGO_USER_DATA
      // Map Django role to JavaScript role key
      const roleMap = {
        'super_admin': 'super-admin',
        'institution_admin': 'institution-admin',
        'student': 'student',
        'employer': 'employer'
      }
      return {
        name: djangoUser.fullName || `${djangoUser.firstName} ${djangoUser.lastName}`.trim() || djangoUser.email,
        role: djangoUser.roleDisplay || djangoUser.role,
        email: djangoUser.email,
        roleKey: roleMap[djangoUser.role] || djangoUser.role,
        avatar: djangoUser.avatar
      }
    }
    
    // Try to get from localStorage (JWT login)
    try {
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        const user = JSON.parse(storedUser)
        const roleMap = {
          'super_admin': 'super-admin',
          'institution_admin': 'institution-admin',
          'student': 'student',
          'employer': 'employer'
        }
        const roleDisplayMap = {
          'super_admin': 'Super Admin',
          'institution_admin': 'Institution Admin',
          'student': 'Student',
          'employer': 'Employer/Verifier'
        }
        return {
          name: user.full_name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email,
          role: roleDisplayMap[user.role] || user.role,
          email: user.email,
          roleKey: roleMap[user.role] || user.role,
          avatar: user.avatar || null
        }
      }
    } catch (e) {
      console.error('Error parsing user from localStorage:', e)
    }
    
    // Fallback to default
    return null
  }

  const actualUser = getUserData()
  
  // State
  const state = {
    currentRole: actualUser ? actualUser.roleKey : "super-admin",
    sidebarCollapsed: false,
    theme: localStorage.getItem("theme") || "light",
    currentSection: "overview",
    touchStartX: 0,
    touchEndX: 0,
    user: actualUser, // Store actual user data
  }

  // User data for different roles (fallback/demo data)
  const userData = {
    "super-admin": {
      name: "John Doe",
      role: "Super Admin",
      email: "john.doe@certchain.io",
    },
    "institution-admin": {
      name: "Dr. Sarah Bangura",
      role: "Institution Admin",
      email: "sarah.bangura@usl.edu.sl",
    },
    student: {
      name: "Aminata Kamara",
      role: "Student",
      email: "aminata.kamara@student.usl.edu.sl",
    },
    employer: {
      name: "Michael Johnson",
      role: "HR Manager",
      email: "m.johnson@techcorp.com",
    },
  }

  // Section mapping for each role
  const roleSections = {
    "super-admin": ["overview", "institutions", "users", "accreditation", "ledger", "analytics", "settings"],
    "institution-admin": [
      "inst-dashboard",
      "issue-credentials",
      "students",
      "verification-logs",
      "inst-profile",
      "inst-settings",
    ],
    student: ["wallet", "share-qr", "student-history", "student-profile"],
    employer: ["verify-credential", "scan-qr", "employer-accreditation", "employer-history", "employer-profile"],
  }

  // Section titles
  const sectionTitles = {
    overview: "System Overview",
    institutions: "Institutions",
    users: "Users",
    accreditation: "Global Accreditation",
    ledger: "Credentials Ledger",
    analytics: "Analytics",
    settings: "Settings",
    "inst-dashboard": "Dashboard",
    "issue-credentials": "Issue Credentials",
    students: "Students",
    "verification-logs": "Verification Logs",
    "inst-profile": "Profile",
    "inst-settings": "Settings",
    wallet: "My Credentials Wallet",
    "share-qr": "Download/Share QR",
    "student-history": "Verification History",
    "student-profile": "Profile Settings",
    "verify-credential": "Verify Credential",
    "scan-qr": "Scan QR Code",
    "employer-accreditation": "Accreditation Lookup",
    "employer-history": "Verification History",
    "employer-profile": "Profile",
  }

  // DOM Elements
  let elements = {}

  // Initialize
  function init() {
    elements = {
      sidebar: document.getElementById("sidebar"),
      sidebarToggle: document.getElementById("sidebar-toggle"),
      mobileMenuToggle: document.getElementById("mobile-menu-toggle"),
      roleSelector: document.getElementById("role-selector"),
      themeToggle: document.getElementById("theme-toggle"),
      userDropdownBtn: document.getElementById("user-dropdown-btn"),
      userDropdownMenu: document.getElementById("user-dropdown-menu"),
      currentSectionTitle: document.getElementById("current-section-title"),
      toastContainer: document.getElementById("toast-container"),
      sidebarOverlay: document.getElementById("sidebar-overlay"),
      sidebarCloseMobile: document.getElementById("sidebar-close-mobile"),
      contentWrapper: document.getElementById("content-wrapper"),
    }
    
    // If we have actual user data, set the role
    if (state.user) {
      state.currentRole = state.user.roleKey
      // In development mode (DEBUG=True), keep role selector visible for testing
      // Only hide it in production when not in debug mode
      const isDebugMode = window.DJANGO_USER_DATA && window.DJANGO_USER_DATA.debug !== false
      if (elements.roleSelector && !isDebugMode) {
        elements.roleSelector.style.display = 'none'
        const roleSelectorLabel = elements.roleSelector.closest('.role-selector')
        if (roleSelectorLabel) {
          roleSelectorLabel.style.display = 'none'
        }
      }
    }
    
    initTheme()
    initEventListeners()
    initMobileFeatures()
    // Update UI with actual user data (after elements are initialized)
    updateUserInterface()
    initNavigation()

    // Add escape key handler
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeMobileSidebar()
        closeUserDropdown()
      }
    })
  }

  // Theme Management
  function initTheme() {
    if (state.theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark")
    }
    updateThemeColor()
  }

  function updateThemeColor() {
    const themeColorMeta = document.querySelector('meta[name="theme-color"]')
    if (themeColorMeta) {
      themeColorMeta.content = state.theme === "dark" ? "#1e1b4b" : "#4f46e5"
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

    updateThemeColor()
    showToast(`Switched to ${state.theme} mode`, "info")
  }

  function initMobileFeatures() {
    initTouchGestures()
    checkMobileView()
    window.addEventListener("resize", debounce(checkMobileView, 150))
  }

  function debounce(func, wait) {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  }

  function checkMobileView() {
    const isMobile = window.innerWidth <= 1024
    document.body.classList.toggle("is-mobile", isMobile)

    if (!isMobile && elements.sidebar) {
      elements.sidebar.classList.remove("show")
      if (elements.sidebarOverlay) {
        elements.sidebarOverlay.classList.remove("show")
      }
      document.body.style.overflow = ""
    }
  }

  function initTouchGestures() {
    if (!elements.sidebar) return

    elements.sidebar.addEventListener("touchstart", handleTouchStart, { passive: true })
    elements.sidebar.addEventListener("touchmove", handleTouchMove, { passive: true })
    elements.sidebar.addEventListener("touchend", handleTouchEnd, { passive: true })

    document.addEventListener("touchstart", handleEdgeSwipeStart, { passive: true })
    document.addEventListener("touchmove", handleEdgeSwipeMove, { passive: true })
    document.addEventListener("touchend", handleEdgeSwipeEnd, { passive: true })
  }

  function handleTouchStart(e) {
    state.touchStartX = e.touches[0].clientX
  }

  function handleTouchMove(e) {
    state.touchEndX = e.touches[0].clientX
  }

  function handleTouchEnd() {
    const swipeDistance = state.touchStartX - state.touchEndX
    const minSwipeDistance = 50

    if (swipeDistance > minSwipeDistance && elements.sidebar.classList.contains("show")) {
      closeMobileSidebar()
    }
  }

  let edgeSwipeStartX = 0
  let isEdgeSwipe = false

  function handleEdgeSwipeStart(e) {
    const touchX = e.touches[0].clientX
    if (touchX < 20 && !elements.sidebar.classList.contains("show")) {
      edgeSwipeStartX = touchX
      isEdgeSwipe = true
    }
  }

  function handleEdgeSwipeMove(e) {
    if (!isEdgeSwipe) return
  }

  function handleEdgeSwipeEnd(e) {
    if (!isEdgeSwipe) return

    const touchEndX = e.changedTouches[0].clientX
    const swipeDistance = touchEndX - edgeSwipeStartX

    if (swipeDistance > 50) {
      openMobileSidebar()
    }

    isEdgeSwipe = false
  }

  // Event Listeners
  function initEventListeners() {
    if (elements.sidebarToggle) {
      elements.sidebarToggle.addEventListener("click", toggleSidebar)
    }

    if (elements.mobileMenuToggle) {
      elements.mobileMenuToggle.addEventListener("click", (e) => {
        e.preventDefault()
        e.stopPropagation()
        console.log("[v0] Mobile menu toggle clicked")
        openMobileSidebar()
      })
    }

    if (elements.sidebarCloseMobile) {
      elements.sidebarCloseMobile.addEventListener("click", (e) => {
        e.preventDefault()
        e.stopPropagation()
        console.log("[v0] Close mobile sidebar clicked")
        closeMobileSidebar()
      })
    }

    if (elements.sidebarOverlay) {
      elements.sidebarOverlay.addEventListener("click", (e) => {
        // Only close if clicking directly on the overlay, not on the sidebar or its children
        if (e.target === elements.sidebarOverlay) {
          e.preventDefault()
          console.log("[v0] Overlay clicked")
          closeMobileSidebar()
        }
      })
    }
    
    // Prevent sidebar clicks from bubbling to overlay
    if (elements.sidebar) {
      elements.sidebar.addEventListener("click", (e) => {
        // Stop propagation to prevent overlay from closing sidebar
        e.stopPropagation()
      })
    }

    // Role selector dropdown (in Dashboard section)
    const roleSelectorSelect = document.getElementById("role-selector-select")
    if (roleSelectorSelect) {
      roleSelectorSelect.addEventListener("change", (e) => {
        const newRole = e.target.value
        changeUserRole(newRole)
      })
    }
    
    // Legacy role selector (if exists)
    if (elements.roleSelector) {
      elements.roleSelector.addEventListener("change", (e) => {
        changeRole(e.target.value)
      })
    }

    if (elements.themeToggle) {
      elements.themeToggle.addEventListener("click", toggleTheme)
    }

    if (elements.userDropdownBtn) {
      elements.userDropdownBtn.addEventListener("click", toggleUserDropdown)
    }

    document.addEventListener("click", (e) => {
      if (elements.userDropdownMenu && !elements.userDropdownBtn.contains(e.target)) {
        elements.userDropdownMenu.classList.remove("show")
      }
    })

    document.querySelectorAll(".nav-item").forEach((item) => {
      item.addEventListener("click", (e) => {
        // Stop propagation to prevent sidebar from closing on mobile
        e.stopPropagation()
        
        // Only prevent default if there's a data-section attribute (for JavaScript navigation)
        // Otherwise, allow normal link navigation
        const section = item.dataset.section
        if (section) {
          e.preventDefault()
          navigateToSection(section)
        }
        // If no data-section, let the link navigate normally
        
        // Close sidebar on mobile after navigation (only for actual links, not selects)
        if (item.tagName === 'A' && window.innerWidth <= 768) {
          // Small delay to allow navigation to start
          setTimeout(() => {
            closeMobileSidebar()
          }, 300)
        }
      })
    })
    
    // Handle role selector - don't close sidebar when changing role
    document.querySelectorAll(".role-selector-select").forEach((select) => {
      select.addEventListener("click", (e) => {
        e.stopPropagation()
      })
      
      select.addEventListener("change", (e) => {
        e.stopPropagation()
      })
      
      select.addEventListener("mousedown", (e) => {
        e.stopPropagation()
      })
    })
    
    // Prevent all clicks inside sidebar from closing it
    if (elements.sidebar) {
      const sidebarNav = elements.sidebar.querySelector('.sidebar-nav')
      if (sidebarNav) {
        sidebarNav.addEventListener("click", (e) => {
          e.stopPropagation()
        })
      }
      
      const sidebarHeader = elements.sidebar.querySelector('.sidebar-header')
      if (sidebarHeader) {
        sidebarHeader.addEventListener("click", (e) => {
          // Allow close button to work
          if (!e.target.closest('.sidebar-close-mobile')) {
            e.stopPropagation()
          }
        })
      }
    }

    document.querySelectorAll(".verify-tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        const tabId = tab.dataset.tab
        switchVerifyTab(tabId)
      })
    })

    const employerVerifyBtn = document.getElementById("employer-verify-btn")
    if (employerVerifyBtn) {
      employerVerifyBtn.addEventListener("click", () => {
        const input = document.getElementById("employer-credential-input")
        if (input && input.value.trim()) {
          verifyCredential(input.value.trim())
        }
      })
    }

    const issueForm = document.getElementById("issue-credential-form")
    if (issueForm) {
      issueForm.addEventListener("submit", (e) => {
        e.preventDefault()
        showToast("Credential issued successfully and recorded on blockchain!", "success")
      })
    }

    // Bulk Upload Institutions Form
    const bulkUploadForm = document.getElementById("bulk-upload-form")
    if (bulkUploadForm) {
      bulkUploadForm.addEventListener("submit", handleBulkUpload)
    }

    window.addEventListener("popstate", () => {
      if (elements.sidebar.classList.contains("show")) {
        closeMobileSidebar()
      }
    })
  }

  // Sidebar Functions
  function toggleSidebar() {
    state.sidebarCollapsed = !state.sidebarCollapsed
    elements.sidebar.classList.toggle("collapsed", state.sidebarCollapsed)
  }

  function openMobileSidebar() {
    console.log("[v0] Opening mobile sidebar")
    console.log("[v0] Sidebar element:", elements.sidebar)
    console.log("[v0] Overlay element:", elements.sidebarOverlay)

    if (elements.sidebar) {
      elements.sidebar.classList.add("show")
      console.log("[v0] Added show class to sidebar")
    }
    if (elements.sidebarOverlay) {
      elements.sidebarOverlay.classList.add("show")
      console.log("[v0] Added show class to overlay")
    }
    document.body.style.overflow = "hidden"
  }

  function closeMobileSidebar() {
    console.log("[v0] Closing mobile sidebar")
    if (elements.sidebar) {
      elements.sidebar.classList.remove("show")
    }
    if (elements.sidebarOverlay) {
      elements.sidebarOverlay.classList.remove("show")
    }
    document.body.style.overflow = ""
  }

  // Change user role on backend
  async function changeUserRole(newRole) {
    // Get CSRF token
    const csrfToken = getCSRFToken()
    const accessToken = localStorage.getItem("access_token")
    
    try {
      // Show loading state
      const roleSelect = document.getElementById("role-selector-select")
      if (roleSelect) {
        roleSelect.disabled = true
      }
      
      // Call backend API to change role
      const response = await fetch("/change-role/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
          "Authorization": accessToken ? `Bearer ${accessToken}` : ""
        },
        credentials: 'include',
        body: JSON.stringify({
          role: newRole
        })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        // Update local state
        state.currentRole = newRole
        
        // Update user data if provided
        if (data.user) {
          // Update localStorage user data
          const userData = localStorage.getItem("user")
          if (userData) {
            try {
              const user = JSON.parse(userData)
              user.role = data.user.role
              localStorage.setItem("user", JSON.stringify(user))
            } catch (e) {
              console.error("Error updating user data:", e)
            }
          }
          
          // Update Django user data if available
          if (window.DJANGO_USER_DATA) {
            window.DJANGO_USER_DATA.role = data.user.role
            window.DJANGO_USER_DATA.roleDisplay = data.user.role
          }
        }
        
        // Update UI
        changeRole(newRole)
        
        // Show success message
        showToast(data.message || `Role changed to ${newRole}`, "success")
        
        // Reload page after a short delay to reflect changes
        setTimeout(() => {
          window.location.reload()
        }, 1500)
      } else {
        showToast(data.error || "Failed to change role", "error")
        // Revert select to previous value
        if (roleSelect && state.currentRole) {
          roleSelect.value = state.currentRole
        }
      }
    } catch (error) {
      console.error("Error changing role:", error)
      showToast("An error occurred while changing role", "error")
      // Revert select to previous value
      const roleSelect = document.getElementById("role-selector-select")
      if (roleSelect && state.currentRole) {
        roleSelect.value = state.currentRole
      }
    } finally {
      // Re-enable select
      const roleSelect = document.getElementById("role-selector-select")
      if (roleSelect) {
        roleSelect.disabled = false
      }
    }
  }
  
  // Get CSRF token helper
  function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value
    if (!token) {
      // Try to get from cookie as fallback
      const cookies = document.cookie.split(';')
      for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=')
        if (name === 'csrftoken') {
          return value
        }
      }
    }
    return token || ''
  }

  // Role Management (UI only - for view switching)
  function changeRole(role) {
    state.currentRole = role

    document.querySelectorAll(".nav-section").forEach((section) => {
      section.classList.add("hidden")
    })

    const activeNavSection = document.querySelector(`.nav-section[data-role="${role}"]`)
    if (activeNavSection) {
      activeNavSection.classList.remove("hidden")
    }

    document.querySelectorAll(".content-section").forEach((section) => {
      section.classList.remove("active")
    })

    const firstSection = roleSections[role][0]
    const firstContentSection = document.getElementById(`section-${firstSection}`)
    if (firstContentSection) {
      firstContentSection.classList.add("active")
      state.currentSection = firstSection
      updateBreadcrumb(firstSection)
    }

    updateActiveNavItem(firstSection)
    updateUserInterface()
    // Show toast in development mode or demo mode
    const isDebugMode = window.DJANGO_USER_DATA && window.DJANGO_USER_DATA.debug === true
    if (!state.user || isDebugMode) {
      const roleName = userData[role] ? userData[role].role : role
      showToast(`Switched to ${roleName} view`, "info")
    }
  }

  function updateUserInterface() {
    // Use actual user data if available, otherwise fall back to demo data
    const user = state.user || userData[state.currentRole]

    const sidebarUserName = document.querySelector(".sidebar-user-name")
    const sidebarUserRole = document.querySelector(".sidebar-user-role")
    if (sidebarUserName && user) sidebarUserName.textContent = user.name
    if (sidebarUserRole && user) sidebarUserRole.textContent = user.role

    const userName = document.querySelector(".user-name")
    const dropdownName = document.querySelector(".user-dropdown-name")
    const dropdownEmail = document.querySelector(".user-dropdown-email")
    if (userName && user) userName.textContent = user.name
    if (dropdownName && user) dropdownName.textContent = user.name
    if (dropdownEmail && user) dropdownEmail.textContent = user.email
    
    // Update sidebar avatar if user has one
    if (user && user.avatar) {
      const sidebarAvatar = document.querySelector(".sidebar-user-avatar img")
      if (sidebarAvatar) {
        sidebarAvatar.src = user.avatar
        sidebarAvatar.alt = user.name
      }
    }
  }

  // Navigation
  function navigateToSection(sectionId) {
    if (!roleSections[state.currentRole].includes(sectionId)) {
      const matchingSection = roleSections[state.currentRole].find(
        (s) => s.includes(sectionId.split("-").pop()) || sectionId.includes(s),
      )
      if (matchingSection) {
        sectionId = matchingSection
      } else {
        sectionId = roleSections[state.currentRole][0]
      }
    }

    document.querySelectorAll(".content-section").forEach((section) => {
      section.classList.remove("active")
    })

    const targetSection = document.getElementById(`section-${sectionId}`)
    if (targetSection) {
      targetSection.classList.add("active")
      state.currentSection = sectionId
      updateBreadcrumb(sectionId)
      updateActiveNavItem(sectionId)
    }

    if (window.innerWidth <= 1024) {
      closeMobileSidebar()
    }

    if (elements.contentWrapper) {
      elements.contentWrapper.scrollTop = 0
    }
  }

  // Make navigateToSection globally available for onclick handlers
  window.navigateToSection = navigateToSection

  function updateBreadcrumb(sectionId) {
    if (elements.currentSectionTitle) {
      elements.currentSectionTitle.textContent = sectionTitles[sectionId] || sectionId
    }
  }

  function updateActiveNavItem(sectionId) {
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.classList.remove("active")
    })

    const activeItem = document.querySelector(`.nav-item[data-section="${sectionId}"]`)
    if (activeItem) {
      activeItem.classList.add("active")
    }
  }

  // User Dropdown
  function toggleUserDropdown() {
    elements.userDropdownMenu.classList.toggle("show")
  }

  function closeUserDropdown() {
    if (elements.userDropdownMenu) {
      elements.userDropdownMenu.classList.remove("show")
    }
  }

  // Verify Tabs
  function switchVerifyTab(tabId) {
    document.querySelectorAll(".verify-tab").forEach((tab) => {
      tab.classList.remove("active")
      if (tab.dataset.tab === tabId) {
        tab.classList.add("active")
      }
    })

    document.querySelectorAll(".verify-panel").forEach((panel) => {
      panel.classList.remove("active")
    })
    const targetPanel = document.getElementById(`panel-${tabId}`)
    if (targetPanel) {
      targetPanel.classList.add("active")
    }
  }

  // Credential Verification
  function verifyCredential(credentialId) {
    const verifyBtn = document.getElementById("employer-verify-btn")
    const resultContainer = document.getElementById("employer-verify-result")

    if (verifyBtn) {
      verifyBtn.disabled = true
      verifyBtn.innerHTML = '<span class="spinner"></span> Verifying...'
    }

    setTimeout(() => {
      const credentials = {
        "CERT-2024-SL-001234": {
          valid: true,
          holder: "Aminata Kamara",
          institution: "University of Sierra Leone",
          degree: "Bachelor of Science",
          program: "Computer Science & Information Technology",
          grade: "First Class Honours",
          issued: "December 15, 2024",
        },
        "CERT-2024-NJ-005678": {
          valid: true,
          holder: "Mohamed Sesay",
          institution: "Njala University",
          degree: "Bachelor of Engineering",
          program: "Civil Engineering",
          grade: "Second Class Upper",
          issued: "November 20, 2024",
        },
        "CERT-2023-LK-009012": {
          valid: false,
          revoked: true,
          reason: "Credential revoked by issuing institution",
        },
      }

      const credential = credentials[credentialId.toUpperCase()]

      if (verifyBtn) {
        verifyBtn.disabled = false
        verifyBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.3-4.3"/>
          </svg>
          Verify
        `
      }

      if (resultContainer) {
        if (credential) {
          if (credential.valid) {
            resultContainer.innerHTML = `
              <div class="verify-success">
                <div class="verify-success-header">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="m9 12 2 2 4-4"/>
                    <circle cx="12" cy="12" r="10"/>
                  </svg>
                  <h3>Credential Verified</h3>
                </div>
                <div class="verify-details">
                  <div class="verify-detail-row">
                    <span class="verify-detail-label">Holder:</span>
                    <span class="verify-detail-value">${credential.holder}</span>
                  </div>
                  <div class="verify-detail-row">
                    <span class="verify-detail-label">Institution:</span>
                    <span class="verify-detail-value">${credential.institution}</span>
                  </div>
                  <div class="verify-detail-row">
                    <span class="verify-detail-label">Degree:</span>
                    <span class="verify-detail-value">${credential.degree}</span>
                  </div>
                  <div class="verify-detail-row">
                    <span class="verify-detail-label">Program:</span>
                    <span class="verify-detail-value">${credential.program}</span>
                  </div>
                  <div class="verify-detail-row">
                    <span class="verify-detail-label">Grade:</span>
                    <span class="verify-detail-value">${credential.grade}</span>
                  </div>
                  <div class="verify-detail-row">
                    <span class="verify-detail-label">Issued:</span>
                    <span class="verify-detail-value">${credential.issued}</span>
                  </div>
                </div>
              </div>
            `
            showToast("Credential verified successfully!", "success")
          } else {
            resultContainer.innerHTML = `
              <div class="verify-error">
                <div class="verify-error-header">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                  </svg>
                  <h3>Credential Revoked</h3>
                </div>
                <p>${credential.reason}</p>
              </div>
            `
            showToast("Warning: This credential has been revoked!", "error")
          }
        } else {
          resultContainer.innerHTML = `
            <div class="verify-not-found">
              <div class="verify-not-found-header">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 8v4"/>
                  <path d="M12 16h.01"/>
                </svg>
                <h3>Credential Not Found</h3>
              </div>
              <p>No credential found with ID: ${credentialId}</p>
            </div>
          `
          showToast("Credential not found in the system", "error")
        }
      }
    }, 1500)
  }

  // Toast Notifications
  function showToast(message, type = "info") {
    const toast = document.createElement("div")
    toast.className = `toast ${type}`

    const icons = {
      success: `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="m9 12 2 2 4-4"/>
        <circle cx="12" cy="12" r="10"/>
      </svg>`,
      error: `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
      </svg>`,
      info: `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 16v-4"/>
        <path d="M12 8h.01"/>
      </svg>`,
    }

    toast.innerHTML = `
      ${icons[type] || icons.info}
      <span class="toast-message">${message}</span>
    `

    if (elements.toastContainer) {
      elements.toastContainer.appendChild(toast)

      setTimeout(() => {
        toast.style.opacity = "0"
        toast.style.transform = "translateX(100%)"
        setTimeout(() => toast.remove(), 300)
      }, 4000)
    }
  }

  // Bulk Upload Institutions
  function handleBulkUpload(e) {
    e.preventDefault()
    
    const form = e.target
    const fileInput = document.getElementById("bulk-upload-file")
    const uploadBtn = document.getElementById("bulk-upload-btn")
    const btnText = uploadBtn?.querySelector(".btn-text")
    const btnSpinner = uploadBtn?.querySelector(".btn-spinner")
    const progressDiv = document.getElementById("upload-progress")
    const progressBar = document.getElementById("progress-bar")
    const progressPercent = document.getElementById("progress-percent")
    const resultsDiv = document.getElementById("upload-results")
    const summaryDiv = document.getElementById("upload-summary")
    const errorsDiv = document.getElementById("upload-errors")
    const errorsList = document.getElementById("errors-list")
    
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      showToast("Please select a JSON file to upload", "error")
      return
    }
    
    const file = fileInput.files[0]
    
    // Validate file type
    if (!file.name.endsWith('.json')) {
      showToast("Please upload a JSON file", "error")
      return
    }
    
    // Show loading state
    if (uploadBtn) {
      uploadBtn.disabled = true
      if (btnText) btnText.style.display = "none"
      if (btnSpinner) btnSpinner.style.display = "inline-block"
    }
    
    // Show progress
    if (progressDiv) progressDiv.style.display = "block"
    if (progressBar) progressBar.style.width = "10%"
    if (progressPercent) progressPercent.textContent = "10%"
    
    // Hide previous results
    if (resultsDiv) resultsDiv.style.display = "none"
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
    
    // Get JWT token from localStorage
    const accessToken = localStorage.getItem('access_token')
    
    // Create FormData
    const formData = new FormData()
    formData.append('file', file)
    
    // Build headers
    const headers = {
      "X-CSRFToken": csrfToken
    }
    
    // Add JWT token if available
    if (accessToken) {
      headers["Authorization"] = `Bearer ${accessToken}`
    }
    
    // Upload file
    fetch("/institutions/bulk-upload/", {
      method: "POST",
      headers: headers,
      body: formData,
      credentials: 'include'
    })
    .then(response => {
      if (progressBar) progressBar.style.width = "50%"
      if (progressPercent) progressPercent.textContent = "50%"
      
      if (!response.ok) {
        return response.json().then(err => {
          throw new Error(JSON.stringify(err))
        })
      }
      return response.json()
    })
    .then(data => {
      if (progressBar) progressBar.style.width = "100%"
      if (progressPercent) progressPercent.textContent = "100%"
      
      // Hide progress after a moment
      setTimeout(() => {
        if (progressDiv) progressDiv.style.display = "none"
      }, 1000)
      
      // Show results
      if (resultsDiv) resultsDiv.style.display = "block"
      
      const summary = data.summary || {}
      
      // Display summary
      if (summaryDiv) {
        summaryDiv.innerHTML = `
          <div style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 700; color: var(--accent-primary);">${summary.total_processed || 0}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">Total Processed</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 700; color: var(--success);">${summary.created || 0}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">Created</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 700; color: var(--info);">${summary.updated || 0}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">Updated</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 700; color: var(--warning);">${summary.skipped || 0}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">Skipped</div>
          </div>
          ${summary.errors > 0 ? `
          <div style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 700; color: var(--error);">${summary.errors}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">Errors</div>
          </div>
          ` : ''}
        `
      }
      
      // Display errors if any
      if (data.errors && data.errors.length > 0) {
        if (errorsDiv) errorsDiv.style.display = "block"
        if (errorsList) {
          errorsList.innerHTML = data.errors.slice(0, 20).map(err => `
            <div style="padding: 0.5rem; margin-bottom: 0.5rem; background: var(--bg-secondary); border-radius: var(--radius-sm); border-left: 3px solid var(--error);">
              <strong>Row ${err.index}:</strong> ${err.name}<br>
              <span style="color: var(--text-muted); font-size: 0.75rem;">${err.error}</span>
            </div>
          `).join('')
          
          if (data.errors.length > 20) {
            errorsList.innerHTML += `<p style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.5rem;">... and ${data.errors.length - 20} more errors</p>`
          }
        }
      } else {
        if (errorsDiv) errorsDiv.style.display = "none"
      }
      
      // Show success message
      showToast(
        `Bulk upload completed! Created: ${summary.created}, Updated: ${summary.updated}`,
        "success"
      )
      
      // Reset form
      form.reset()
    })
    .catch(error => {
      // Suppress browser extension errors
      if (error.message && error.message.includes('message channel')) {
        return
      }
      
      console.error("Bulk upload error:", error)
      
      let errorMessage = "Upload failed. Please try again."
      
      try {
        const errorData = JSON.parse(error.message)
        errorMessage = errorData.error || errorMessage
      } catch (e) {
        errorMessage = error.message || errorMessage
      }
      
      showToast(errorMessage, "error")
      
      // Hide progress
      if (progressDiv) progressDiv.style.display = "none"
    })
    .finally(() => {
      // Reset button state
      if (uploadBtn) {
        uploadBtn.disabled = false
        if (btnText) btnText.style.display = "inline"
        if (btnSpinner) btnSpinner.style.display = "none"
      }
    })
  }

  // Initialize on DOM ready
  function initNavigation() {
    // Placeholder for future navigation initialization
  }

  // Credential Share Functionality
  function initCredentialShare() {
    // Share credential buttons
    document.querySelectorAll('.share-credential-btn').forEach(btn => {
      btn.addEventListener('click', async function() {
        const credentialId = this.getAttribute('data-credential-id')
        const credentialName = this.getAttribute('data-credential-name') || 'Credential'
        
        if (!credentialId) {
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Credential ID not found'
          })
          return
        }

        // Show input dialog with all options
        const result = await Swal.fire({
          title: 'Share Credential',
          html: `
            <p>Generate a shareable link for this credential.</p>
            <div class="form-group" style="text-align: left; margin-top: 1rem;">
              <label for="share-email" class="form-label" style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Share with Email (Optional)</label>
              <input type="email" id="share-email" class="swal2-input" placeholder="recipient@example.com" style="width: 100%;">
            </div>
            <div class="form-group" style="text-align: left; margin-top: 1rem;">
              <label for="share-expires" class="form-label" style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Expires In (Days, Optional)</label>
              <input type="number" id="share-expires" class="swal2-input" value="30" min="1" style="width: 100%;">
            </div>
            <div class="form-group" style="text-align: left; margin-top: 1rem;">
              <label class="form-label" style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Privacy Settings</label>
              <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                <label class="checkbox-label" style="display: flex; align-items: center; gap: 0.5rem;">
                  <input type="checkbox" id="hide-grade" class="checkbox-input"> Hide Grade
                </label>
                <label class="checkbox-label" style="display: flex; align-items: center; gap: 0.5rem;">
                  <input type="checkbox" id="hide-student-id" class="checkbox-input"> Hide Student ID
                </label>
              </div>
            </div>
          `,
          showCancelButton: true,
          confirmButtonText: 'Generate Link',
          confirmButtonColor: '#4f46e5',
          cancelButtonText: 'Cancel',
          focusConfirm: false,
          preConfirm: () => {
            const email = Swal.getPopup().querySelector('#share-email').value;
            const expires_in_days = Swal.getPopup().querySelector('#share-expires').value;
            const hide_grade = Swal.getPopup().querySelector('#hide-grade').checked;
            const hide_student_id = Swal.getPopup().querySelector('#hide-student-id').checked;
            return { email, expires_in_days, hide_grade, hide_student_id };
          }
        })

        if (!result.isConfirmed) return // User cancelled
        const { email, expires_in_days, hide_grade, hide_student_id } = result.value

        try {
          // Get CSRF token
          const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                           document.cookie.match(/csrftoken=([^;]+)/)?.[1]

          // Get JWT token from localStorage
          const accessToken = localStorage.getItem('access_token')
          
          const headers = {
            'Content-Type': 'application/json',
          }
          
          if (csrftoken) {
            headers['X-CSRFToken'] = csrftoken
          }
          
          if (accessToken) {
            headers['Authorization'] = `Bearer ${accessToken}`
          }

          // Create share link via API
          const response = await fetch('/credentials/share/', {
            method: 'POST',
            headers: headers,
            credentials: 'include',
            body: JSON.stringify({
              credential: credentialId,
              shared_with_email: email || null,
              expires_in_days: expires_in_days ? parseInt(expires_in_days) : 30,
              max_views: 100,
              hide_grade: hide_grade,
              hide_student_id: hide_student_id
            })
          })

          if (!response.ok) {
            // Try to parse error response
            let errorData;
            try {
              errorData = await response.json();
            } catch (e) {
              // If response is not JSON (e.g., HTML error page), throw generic error
              throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }
            throw new Error(errorData.detail || errorData.error || `Failed to create share link: ${response.status}`);
          }

          const data = await response.json()

          if (data.share_token) {
            const shareUrl = `${window.location.origin}/credentials/share/${data.share_token}/`
            
            // Show success with share link
            Swal.fire({
              icon: 'success',
              title: 'Share Link Generated!',
              html: `
                <p>Copy this link to share your credential:</p>
                <div style="background: var(--bg-secondary, #f5f5f5); padding: 0.75rem; border-radius: 8px; display: flex; align-items: center; gap: 0.5rem; margin: 1rem 0;">
                  <input type="text" value="${shareUrl}" id="share-link-input" readonly style="flex-grow: 1; border: none; background: transparent; color: var(--text-primary, #333); font-family: monospace; font-size: 0.875rem;">
                  <button class="btn btn-sm btn-primary" id="copy-share-link-btn" style="padding: 0.5rem 1rem; background: #4f46e5; color: white; border: none; border-radius: 4px; cursor: pointer;">Copy</button>
                </div>
                ${data.expires_at ? `<p style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">Link expires: ${new Date(data.expires_at).toLocaleString()}</p>` : ''}
              `,
              confirmButtonText: 'Done',
              confirmButtonColor: '#4f46e5',
              allowOutsideClick: false,
              allowEscapeKey: false,
              didOpen: () => {
                document.getElementById('copy-share-link-btn')?.addEventListener('click', () => {
                  const input = document.getElementById('share-link-input')
                  if (input) {
                    input.select()
                    document.execCommand('copy')
                    navigator.clipboard.writeText(shareUrl).then(() => {
                      Swal.fire({
                        icon: 'success',
                        title: 'Copied!',
                        text: 'Share link copied to clipboard',
                        timer: 2000,
                        showConfirmButton: false
                      })
                    }).catch(() => {
                      // Fallback if clipboard API fails
                      Swal.fire({
                        icon: 'success',
                        title: 'Selected!',
                        text: 'Link selected - press Ctrl+C to copy',
                        timer: 2000,
                        showConfirmButton: false
                      })
                    })
                  }
                })
              }
            })
          } else {
            throw new Error(data.error || data.detail || 'Failed to create share link')
          }
        } catch (error) {
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message || 'Failed to create share link. Please try again.'
          })
        }
      })
    })

    // View QR buttons
    document.querySelectorAll('.view-qr-btn').forEach(btn => {
      btn.addEventListener('click', async function() {
        const credentialId = this.getAttribute('data-credential-id')
        const qrUrl = this.getAttribute('data-qr-url')
        const verificationUrl = this.getAttribute('data-verification-url')
        const credentialIdText = this.getAttribute('data-credential-id-text')
        
        if (!credentialId) {
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Credential ID not found'
          })
          return
        }

        // Show loading
        Swal.fire({
          title: 'Loading QR Code...',
          allowOutsideClick: false,
          allowEscapeKey: false,
          didOpen: () => {
            Swal.showLoading()
          }
        })

        try {
          // Get CSRF token
          const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                           document.cookie.match(/csrftoken=([^;]+)/)?.[1]
          
          // Get JWT token from localStorage
          const accessToken = localStorage.getItem('access_token')
          
          const headers = {
            'Content-Type': 'application/json',
          }
          
          if (csrftoken) {
            headers['X-CSRFToken'] = csrftoken
          }
          
          if (accessToken) {
            headers['Authorization'] = `Bearer ${accessToken}`
          }

          // Fetch QR code from API (will generate if not exists)
          const response = await fetch(`/credentials/${credentialId}/qr/`, {
            method: 'GET',
            headers: headers,
            credentials: 'include'
          })

          if (!response.ok) {
            let errorData
            try {
              errorData = await response.json()
            } catch (e) {
              throw new Error(`Server error: ${response.status} ${response.statusText}`)
            }
            throw new Error(errorData.error || errorData.detail || `Failed to get QR code: ${response.status}`)
          }

          const data = await response.json()
          let qrImageUrl = data.qr_code_url || qrUrl
          const verifyUrl = data.verification_url || verificationUrl || 
                           (credentialIdText ? `${window.location.origin}/credentials/verify/${credentialIdText}/` : null)

          // If no QR code image, generate one client-side using QR.js API
          if (!qrImageUrl && verifyUrl) {
            // Use QR.js API as fallback
            qrImageUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(verifyUrl)}`
          }

          // Close loading dialog
          Swal.close()

          // Show QR code
          Swal.fire({
            title: 'Credential QR Code',
            html: `
              <div style="text-align: center;">
                ${qrImageUrl ? `
                  <img src="${qrImageUrl}" alt="QR Code" style="max-width: 300px; margin: 1rem auto; display: block; border: 2px solid #e5e7eb; border-radius: 8px; padding: 1rem; background: white;">
                  <p style="font-size: 0.875rem; color: #666; margin-top: 1rem;">Scan this QR code to verify the credential</p>
                ` : `
                  <div style="text-align: center; padding: 2rem;">
                    <p style="color: #ef4444;">QR Code not available</p>
                    ${verifyUrl ? `<p style="font-size: 0.875rem; color: #666; margin-top: 1rem;">Verification URL:</p>
                    <div style="background: #f5f5f5; padding: 0.75rem; border-radius: 8px; margin: 1rem 0;">
                      <code style="word-break: break-all; font-size: 0.75rem; color: #333;">${verifyUrl}</code>
                    </div>` : ''}
                  </div>
                `}
                ${verifyUrl ? `
                  <div style="display: flex; gap: 0.5rem; justify-content: center; margin-top: 1rem;">
                    <button id="copy-verify-url-btn" class="btn btn-sm btn-outline" style="padding: 0.5rem 1rem;">Copy URL</button>
                    ${qrImageUrl ? `<button id="download-qr-btn" class="btn btn-sm btn-primary" style="padding: 0.5rem 1rem;">Download QR</button>` : ''}
                  </div>
                ` : ''}
              </div>
            `,
            showCancelButton: true,
            cancelButtonText: 'Close',
            confirmButtonText: 'Done',
            confirmButtonColor: '#4f46e5',
            didOpen: () => {
              if (verifyUrl) {
                document.getElementById('copy-verify-url-btn')?.addEventListener('click', () => {
                  navigator.clipboard.writeText(verifyUrl).then(() => {
                    Swal.fire({
                      icon: 'success',
                      title: 'Copied!',
                      text: 'Verification URL copied to clipboard',
                      timer: 2000,
                      showConfirmButton: false
                    })
                  }).catch(() => {
                    // Fallback
                    const input = document.createElement('input')
                    input.value = verifyUrl
                    document.body.appendChild(input)
                    input.select()
                    document.execCommand('copy')
                    document.body.removeChild(input)
                    Swal.fire({
                      icon: 'success',
                      title: 'Copied!',
                      text: 'Verification URL copied to clipboard',
                      timer: 2000,
                      showConfirmButton: false
                    })
                  })
                })
              }
              
              if (qrImageUrl) {
                document.getElementById('download-qr-btn')?.addEventListener('click', () => {
                  // Create download link
                  const link = document.createElement('a')
                  link.href = qrImageUrl
                  link.download = `qr_code_${data.credential_id || credentialIdText || 'credential'}.png`
                  document.body.appendChild(link)
                  link.click()
                  document.body.removeChild(link)
                  
                  Swal.fire({
                    icon: 'success',
                    title: 'Download Started!',
                    text: 'QR code download started',
                    timer: 2000,
                    showConfirmButton: false
                  })
                })
              }
            }
          })
        } catch (error) {
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message || 'Failed to load QR code. Please try again.'
          })
        }
      })
    })
  }

  // Initialize credential share on page load
  function initCredentialFeatures() {
    initCredentialShare()
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      init()
      initCredentialFeatures()
    })
  } else {
    init()
    initCredentialFeatures()
  }
})()
