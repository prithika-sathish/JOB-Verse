document.addEventListener('DOMContentLoaded', () => {
    // Initialize UI elements
    const testSkill = document.getElementById('testSkill');
    const startTest = document.getElementById('startTest');
    const quizContainer = document.getElementById('quiz-container');
    const quizContent = document.getElementById('quiz-content');
    const domainSelection = document.getElementById('domain-selection');
    const results = document.getElementById('results');
    const submitAnswer = document.getElementById('submitAnswer');
    const retakeTest = document.getElementById('retakeTest');

    // Set up auth state listener
    firebase.auth().onAuthStateChanged(async user => {
        if (!user) {
            console.log('No user logged in, redirecting to index...');
            window.location.href = 'index.html';
            return;
        }

        console.log('User logged in:', user.email);
        document.getElementById('userEmail').textContent = user.email;

        try {
            // Get user's registered skill
            const userDataSnapshot = await firebase.database().ref('users/' + user.uid).once('value');
            if (userDataSnapshot.exists()) {
                const userData = userDataSnapshot.val();
                if (userData.skill === 'dsa' || userData.skill === 'full-stack-development') {
                    testSkill.value = userData.skill;
                }
            }

            // Check previous test results
            const quizRef = firebase.database().ref('quiz_results');
            const query = quizRef.orderByChild('email').equalTo(user.email);
            const snapshot = await query.once('value');
            
            if (snapshot.exists()) {
                let latestResult = null;
                let latestTimestamp = 0;

                snapshot.forEach(childSnapshot => {
                    const result = childSnapshot.val();
                    const timestamp = new Date(result.timestamp).getTime();
                    if (timestamp > latestTimestamp) {
                        latestResult = result;
                        latestTimestamp = timestamp;
                    }
                });

                if (latestResult && Math.round((latestResult.score / latestResult.totalQuestions) * 100) >= 70) {
                    console.log('User passed the test, redirecting to dashboard...');
                    window.location.href = 'dashboard.html';
                    return;
                }
            }

            // Show screening interface if user hasn't passed
            document.querySelector('.screening-container').style.display = 'block';
        } catch (error) {
            console.error('Error initializing screening:', error);
            // Show screening interface even on error, so user can still take the test
            document.querySelector('.screening-container').style.display = 'block';
        }
    });

    // Logout functionality
    document.getElementById('logoutBtn').addEventListener('click', async () => {
        try {
            await firebase.auth().signOut();
            window.location.href = 'index.html';
        } catch (error) {
            console.error('Error signing out:', error);
        }
    });

    // Start test button handler
    startTest.addEventListener('click', () => {
        if (!testSkill.value) {
            alert('Please select a skill to proceed');
            return;
        }

        // Initialize quiz based on selected skill
        const selectedSkill = testSkill.value;
        console.log('Starting test for skill:', selectedSkill);
        
        // Hide selection and show quiz
        domainSelection.style.display = 'none';
        quizContent.style.display = 'block';
        
        // Update quiz title
        document.getElementById('quiz-title').textContent = 
            selectedSkill === 'dsa' ? 'DSA (Data Structures & Algorithms) Test' : 'Full Stack Development Test';

        // Quiz questions and answers
        const quizzes = {
            'dsa': {
                questions: [
                    {
                        question: "Which data structure uses FIFO (First In First Out) principle?",
                        options: ["Stack", "Queue", "Tree", "Graph"],
                        correct: 1
                    },
                    {
                        question: "What is the time complexity of binary search in a sorted array?",
                        options: ["O(n)", "O(n log n)", "O(log n)", "O(1)"],
                        correct: 2
                    },
                    {
                        question: "Which data structure is best suited for implementing a recursive function stack?",
                        options: ["Queue", "Linked List", "Array", "Stack"],
                        correct: 3
                    },
                    {
                        question: "Which traversal method visits left subtree, root, then right subtree?",
                        options: ["Preorder", "Inorder", "Postorder", "Level Order"],
                        correct: 1
                    },
                    {
                        question: "In which case does a binary search tree (BST) become inefficient like a linked list?",
                        options: ["When balanced", "When it has both left and right children", "When nodes are inserted in sorted order", "When height is minimal"],
                        correct: 2
                    },
                    {
                        question: "What is the space complexity of a recursive implementation of binary search?",
                        options: ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                        correct: 1
                    },
                    {
                        question: "Which sorting algorithm has the best average-case time complexity?",
                        options: ["Bubble Sort", "Quick Sort", "Insertion Sort", "Selection Sort"],
                        correct: 1
                    },
                    {
                        question: "What is the main advantage of using a hash table?",
                        options: ["Ordered data storage", "O(1) average case for insertions and lookups", "Memory efficiency", "Sequential access"],
                        correct: 1
                    },
                    {
                        question: "Which data structure would you use to implement an undo feature?",
                        options: ["Queue", "Stack", "Linked List", "Binary Tree"],
                        correct: 1
                    },
                    {
                        question: "What is the time complexity of finding the height of a binary tree?",
                        options: ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                        correct: 2
                    }
                ]
            },
            'full-stack-development': {
                questions: [
                    {
                        question: "What is the primary purpose of CORS in web development?",
                        options: ["To encrypt API responses", "To allow or restrict cross-origin requests", "To manage user sessions", "To validate JWT tokens"],
                        correct: 1
                    },
                    {
                        question: "Which is true about SQL and NoSQL databases?",
                        options: ["SQL is schema-less and NoSQL is strictly structured", "SQL is best for unstructured data", "SQL uses fixed schemas; NoSQL offers flexible structures", "NoSQL can't store relationships"],
                        correct: 2
                    },
                    {
                        question: "What happens in the componentDidMount() method in React?",
                        options: ["Component is destroyed", "Component is updated", "DOM is created and API calls are made", "State is initialized"],
                        correct: 2
                    },
                    {
                        question: "How does JWT (JSON Web Token) authenticate users?",
                        options: ["By hashing the password and comparing it to a key", "By encoding user info in a token sent with requests", "By opening a socket connection", "By verifying cookies"],
                        correct: 1
                    },
                    {
                        question: "What is middleware used for in Express.js?",
                        options: ["Only to handle routes", "To set database schemas", "To intercept and process requests before they reach routes", "To render frontend components"],
                        correct: 2
                    },
                    {
                        question: "What is the purpose of Redux in React applications?",
                        options: ["To handle routing", "To manage global state", "To optimize performance", "To handle API calls"],
                        correct: 1
                    },
                    {
                        question: "Which HTTP method should be used for idempotent operations?",
                        options: ["POST", "PUT", "PATCH", "DELETE"],
                        correct: 1
                    },
                    {
                        question: "What is the main benefit of using Docker in development?",
                        options: ["Faster code execution", "Consistent development environments", "Better security", "Improved database performance"],
                        correct: 1
                    },
                    {
                        question: "What is the purpose of the virtual DOM in React?",
                        options: ["To improve security", "To optimize rendering performance", "To handle routing", "To manage state"],
                        correct: 1
                    },
                    {
                        question: "Which database indexing strategy is best for frequent range queries?",
                        options: ["Hash index", "B-tree index", "Bitmap index", "No index"],
                        correct: 1
                    }
                ]
            }
        };

        // Initialize quiz state
        let currentQuiz = quizzes[selectedSkill];
        let currentQuestionIndex = 0;
        let score = 0;
        let timeLeft = 180; // 3 minutes in seconds
        let timerInterval;

        function startTimer() {
            const timerElement = document.getElementById('timer');
            timerElement.innerHTML = '⏱ ' + formatTime(timeLeft);
            
            timerInterval = setInterval(() => {
                timeLeft--;
                timerElement.innerHTML = '⏱ ' + formatTime(timeLeft);
                
                if (timeLeft <= 30) {
                    timerElement.classList.add('warning');
                }
                
                if (timeLeft <= 0) {
                    clearInterval(timerInterval);
                    handleTestCompletion(score, currentQuiz.questions.length);
                }
            }, 1000);
        }

        function formatTime(seconds) {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        }

        function displayQuestion() {
            const question = currentQuiz.questions[currentQuestionIndex];
            document.getElementById('quiz-title').textContent = 
                selectedSkill === 'dsa' ? 'DSA (Data Structures & Algorithms) Test' : 'Full Stack Development Test';
            
            document.getElementById('question-text').textContent = question.question;
            
            const optionsContainer = document.getElementById('options-container');
            optionsContainer.innerHTML = '';
            
            question.options.forEach((option, index) => {
                const button = document.createElement('button');
                button.className = 'option-button';
                button.textContent = option;
                button.onclick = () => {
                    // Remove selected class from all options
                    optionsContainer.querySelectorAll('.option-button').forEach(btn => {
                        btn.classList.remove('selected');
                    });
                    // Add selected class to clicked option
                    button.classList.add('selected');
                    // Wait a brief moment before moving to next question
                    setTimeout(() => handleAnswer(index), 300);
                };
                optionsContainer.appendChild(button);
            });

            // Start timer on first question
            if (currentQuestionIndex === 0) {
                startTimer();
            }
        }

        function handleAnswer(selectedIndex) {
            const question = currentQuiz.questions[currentQuestionIndex];
            if (selectedIndex === question.correct) {
                score++;
            }

            currentQuestionIndex++;
            if (currentQuestionIndex < currentQuiz.questions.length) {
                displayQuestion();
            } else {
                clearInterval(timerInterval); // Stop timer when quiz is complete
                handleTestCompletion(score, currentQuiz.questions.length);
            }
        }

        // Start with first question
        displayQuestion();
    });

    // Handle test completion
    async function handleTestCompletion(score, totalQuestions) {
        const user = firebase.auth().currentUser;
        if (!user) {
            console.error('No user logged in');
            return;
        }

        const percentage = Math.round((score / totalQuestions) * 100);
        const timestamp = new Date().toISOString();
        
        const testData = {
            email: user.email,
            userId: user.uid,
            score: score,
            totalQuestions: totalQuestions,
            percentage: percentage,
            domain: 'tech', // Since we only have DSA and Full Stack Development
            skill: testSkill.value,
            timestamp: timestamp
        };
        
        try {
            console.log('Saving test results...');
            // Save to Realtime Database
            await firebase.database()
                .ref('quiz_results')
                .push(testData);

            // Save to Firestore
            await firebase.firestore()
                .collection('quiz_results')
                .add({
                    ...testData,
                    timestamp: new Date() // Firestore needs a Date object
                });

            console.log('Test results saved successfully');

            // Update UI
            document.getElementById('score').textContent = score;
            document.getElementById('correct-answers').textContent = score;
            document.getElementById('total-questions').textContent = totalQuestions;
            
            // Show results section
            quizContent.style.display = 'none';
            results.style.display = 'block';

            // If passed, show success modal and redirect to dashboard
            if (percentage >= 70) {
                console.log('User passed the test, showing success modal...');
                
                // Show success modal
                document.querySelector('.modal-overlay').style.display = 'block';
                document.querySelector('.success-modal').style.display = 'block';
                
                // Add event listener to the dashboard button in success modal
                document.querySelector('.success-modal button').onclick = () => {
                    window.location.href = 'dashboard.html';
                };
            } else {
                console.log('User did not pass, showing retake option');
                // Show retake option for failed attempts
                retakeTest.style.display = 'block';
            }
        } catch (error) {
            console.error('Error saving test results:', error);
            alert('Error saving test results. Please try again.');
        }
    }

    // Retake test button
    retakeTest.addEventListener('click', () => {
        results.style.display = 'none';
        domainSelection.style.display = 'block';
        testSkill.value = '';
    });

    // Initially hide the screening container until auth check is complete
    document.querySelector('.screening-container').style.display = 'none';
});
