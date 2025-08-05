let currentRole = '';

// Role Selection
function selectRole(role, buttonElement) {
    currentRole = role;
    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.classList.remove('border-indigo-500', 'bg-indigo-50');
    });
    buttonElement.classList.add('border-indigo-500', 'bg-indigo-50');
    
    // Set default credentials
    const credentials = {
        admin: { email: 'admin@gmail.com', password: 'admin' },
        management: { email: 'management@gmail.com', password: 'management' },
        teacher: { email: 'teacher@gmail.com', password: 'teacher' },
        parent: { email: 'parent@gmail.com', password: 'parent' },
        driver: { email: 'driver@gmail.com', password: 'driver' },
        student: { email: 'student@gmail.com', password: 'student' }
    };
    
    document.getElementById('loginEmail').value = credentials[role].email;
    document.getElementById('loginPassword').value = credentials[role].password;
}

// Section Navigation (for index.html)
function showSection(sectionName) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
        section.style.display = 'none';
    });
    
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.style.display = 'block';
        targetSection.classList.add('active');
    }
}

// Logout function (used by all dashboards)
function logout() {
    localStorage.removeItem('currentUserRole'); // Clear stored role
    window.location.href = '{% url "student:logout" %}'; // Redirect to login page
}

// Function to load common navigation for dashboards
function loadDashboardNav() {
    const navHtml = `

    `;
    document.body.insertAdjacentHTML('afterbegin', navHtml);
}

// Notification badge style (can be moved to a common CSS file if preferred)
const commonStyles = `
    .notification-badge {
        background: #ef4444;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        font-size: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: absolute;
        top: -8px;
        right: -8px;
    }
    .poll-option {
        transition: all 0.3s ease;
    }
    .poll-option:hover {
        background-color: #f3f4f6;
    }
`;
const styleSheet = document.createElement("style");
styleSheet.type = "text/css";
styleSheet.innerText = commonStyles;
document.head.appendChild(styleSheet);

