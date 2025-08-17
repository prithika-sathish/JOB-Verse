// Firebase is now available globally through the compat version
document.addEventListener('DOMContentLoaded', async () => {
    // Wait for Firebase Auth to initialize
    await new Promise(resolve => {
        const unsubscribe = firebase.auth().onAuthStateChanged(user => {
            unsubscribe();
            resolve();
        });
    });

    // Create admin account if it doesn't exist
    try {
        const signInMethods = await firebase.auth().fetchSignInMethodsForEmail('admin@gmail.com');
        if (signInMethods.length === 0) {
            // Email doesn't exist, create admin account
            const userCredential = await firebase.auth().createUserWithEmailAndPassword('admin@gmail.com', 'admin123');
            
            // Save admin data
            const adminData = {
                email: 'admin@gmail.com',
                role: 'admin',
                createdAt: new Date().toISOString()
            };
            
            // Save to both databases
            await firebase.firestore().collection('users').doc(userCredential.user.uid).set(adminData);
            await firebase.database().ref('users/' + userCredential.user.uid).set(adminData);
            
            console.log('Admin account created successfully');
        }
    } catch (error) {
        console.error('Error handling admin account:', error);
    }

    // Typing animation
    setTimeout(() => {
        const line2 = document.querySelector('.hero h1 .line2');
        if (line2) line2.classList.add('typing');
    }, 2000);

    // Get Started button functionality
    const ctaButton = document.querySelector('.cta-button');
    if (ctaButton) {
        ctaButton.addEventListener('click', (e) => {
            e.preventDefault();
            const loginModal = document.querySelector('#login');
            if (loginModal) {
                loginModal.style.display = 'block';
            }
        });
    }
});

// Theme toggle functionality
document.getElementById('themeToggle')?.addEventListener('click', () => {
    document.body.classList.toggle('light-mode');
    document.body.classList.toggle('dark-mode');
});

// Modal functionality
document.querySelectorAll('.modal').forEach(modal => {
    // Close button
    modal.querySelector('.close')?.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Click outside to close
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});

// Handle login form submission
document.querySelector('.login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = e.target.querySelector('input[type="email"]').value;
    const password = e.target.querySelector('input[type="password"]').value;

    // Disable submit button and show loading state
    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'Logging in...';

    try {
        // Sign in user
        const userCredential = await firebase.auth().signInWithEmailAndPassword(email, password);
        console.log('Login successful, checking credentials...');

        // Check if admin
        if (email === 'admin@gmail.com' && password === 'admin123') {
            window.location.href = 'admin.html';
            return;
        }
        
        // For regular users, check quiz results in Realtime Database
        try {
            const quizRef = firebase.database().ref('quiz_results')
                .orderByChild('email')
                .equalTo(email)
                .limitToLast(1);
            
            const snapshot = await quizRef.once('value');
            if (snapshot.exists()) {
                const results = [];
                snapshot.forEach(childSnapshot => {
                    results.push({
                        ...childSnapshot.val(),
                        id: childSnapshot.key
                    });
                });

                const latestResult = results[0];
                const score = latestResult.score;
                const totalQuestions = latestResult.totalQuestions;
                const percentage = Math.round((score / totalQuestions) * 100);

                // If user passed (>= 70%), redirect to dashboard
                if (percentage >= 70) {
                    window.location.href = 'dashboard.html';
                } else {
                    window.location.href = 'screening.html';
                }
            } else {
                // If no results in Realtime Database, try Firestore
                const querySnapshot = await firebase.firestore()
                    .collection('quiz_results')
                    .where('email', '==', email)
                    .get();

                if (!querySnapshot.empty) {
                    // Find the latest result manually
                    let latestResult = querySnapshot.docs[0].data();
                    let latestTimestamp = latestResult.timestamp;

                    querySnapshot.docs.forEach(doc => {
                        const data = doc.data();
                        if (data.timestamp > latestTimestamp) {
                            latestResult = data;
                            latestTimestamp = data.timestamp;
                        }
                    });

                    const score = latestResult.score;
                    const totalQuestions = latestResult.totalQuestions;
                    const percentage = Math.round((score / totalQuestions) * 100);

                    // If user passed (>= 70%), redirect to dashboard
                    if (percentage >= 70) {
                        window.location.href = 'dashboard.html';
                    } else {
                        window.location.href = 'screening.html';
                    }
                } else {
                    // If no test results found in either database, redirect to screening
                    window.location.href = 'screening.html';
                }
            }
        } catch (error) {
            console.error('Error checking quiz results:', error);
            // If we can't check quiz results, default to screening
            window.location.href = 'screening.html';
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed: ' + error.message);
    } finally {
        // Always re-enable the submit button and reset its text
        submitButton.disabled = false;
        submitButton.textContent = 'Login';
    }
});

// Handle registration form submission
document.querySelector('.register-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        email: e.target.querySelector('input[name="email"]').value,
        password: e.target.querySelector('input[name="password"]').value,
        domain: document.getElementById('registerDomain').value,
        skill: document.getElementById('registerSkill').value,
        proficiency: e.target.querySelector('input[name="proficiency"]:checked').value,
        projectLinks: e.target.querySelector('input[name="projectLinks"]').value,
        monthsExperience: e.target.querySelector('input[name="monthsExperience"]').value
    };

    // Validate form data first
    if (!formData.email || !formData.password || !formData.domain || !formData.skill || !formData.proficiency) {
        alert('Please fill in all required fields');
        return;
    }

    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'Creating account...';

    try {
        console.log('Creating user account...');
        // Create user account
        const userCredential = await firebase.auth().createUserWithEmailAndPassword(formData.email, formData.password);
        
        console.log('Saving user data...');
        // Save to both Realtime Database and Firestore for redundancy
        const userData = {
            email: formData.email,
            domain: formData.domain,
            skill: formData.skill,
            proficiency: formData.proficiency,
            projectLinks: formData.projectLinks,
            monthsExperience: parseInt(formData.monthsExperience),
            createdAt: new Date().toISOString()
        };

        // Save to Realtime Database
        await firebase.database().ref('users/' + userCredential.user.uid).set(userData);
        
        // Save to Firestore
        await firebase.firestore().collection('users').doc(userCredential.user.uid).set(userData);

        console.log('User registered successfully, redirecting to screening...');
        // After successful registration, redirect directly to screening
        window.location.href = 'screening.html';
    } catch (error) {
        console.error('Registration error:', error);
        alert('Registration failed: ' + error.message);
        // If registration fails, keep the registration modal open
        document.querySelector('#register').style.display = 'block';
        document.querySelector('#login').style.display = 'none';
        // Reset button on failure
        submitButton.textContent = 'Create Account';
    } finally {
        // Re-enable the button
        submitButton.disabled = false;
    }
});

// Open modal on link click
document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const modalId = link.getAttribute('href');
        if (modalId === '#features' || modalId === '#about' || modalId === '#resources' || modalId === '#contact') {
            const section = document.querySelector(modalId);
            if (section) {
                section.scrollIntoView({ behavior: 'smooth' });
            }
            return;
        }
        const modal = document.querySelector(modalId);
        if (modal && modal.classList.contains('modal')) {
            modal.style.display = 'block';
        }
    });
});

// Domain-Skill mapping
const skillsByDomain = {
    tech: [
        'DSA (Data Structures & Algorithms)',
        'Full Stack Development',
        'Cybersecurity',
        'Machine Learning',
        'DevOps & Cloud',
        'Android/iOS Development',
        'Game Development'
    ],
    business: ['Project Management', 'Business Analysis', 'Marketing Strategy', 'Sales', 'Operations'],
    design: ['UI/UX Design', 'Graphic Design', 'Motion Design', 'Product Design', 'Brand Design'],
    finance: ['Investment Analysis', 'Risk Management', 'Financial Planning', 'Trading', 'Accounting']
};

// Update skills dropdown based on selected domain
document.getElementById('registerDomain')?.addEventListener('change', function() {
    const skillSelect = document.getElementById('registerSkill');
    const selectedDomain = this.value;
    
    if (!skillSelect) return;
    
    skillSelect.innerHTML = '<option value="">Select Skill</option>';
    
    if (selectedDomain) {
        skillSelect.removeAttribute('disabled');
        skillsByDomain[selectedDomain].forEach(skill => {
            const option = document.createElement('option');
            option.value = skill.toLowerCase().replace(/\s+/g, '-');
            option.textContent = skill;
            skillSelect.appendChild(option);
        });
    } else {
        skillSelect.setAttribute('disabled', true);
    }
});

// Handle newsletter subscription
document.querySelector('.newsletter-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = e.target.querySelector('input[type="email"]').value;

    try {
        const subscriptionData = {
            email: email,
            subscribedAt: new Date().toISOString()
        };

        // Save to both databases for redundancy
        await Promise.all([
            firebase.database().ref('newsletter_subscribers/' + email.replace(/[.#$[\]]/g, '_')).set(subscriptionData),
            firebase.firestore().collection('newsletter_subscribers').doc(email).set(subscriptionData)
        ]);

        alert('Thank you for subscribing!');
        e.target.reset();
    } catch (error) {
        alert('Subscription failed: ' + error.message);
    }
});
