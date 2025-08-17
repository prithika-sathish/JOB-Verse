// Task data
const tasks = [
    {
        "taskName": "Mobile Responsiveness Fix",
        "description": "Make the UI responsive across all devices using media queries and flexible layout techniques.",
        "priority": "High",
        "timeEstimate": "2 hours",
        "deadline": "2025-05-04",
        "requiredFiles": "",
        "uploadedFile": null
    },
    {
        "taskName": "Attendance Hour Fix (HR Module)",
        "description": "Correct logic for updating working hours on Half-Day or On-Duty status to avoid full-day errors.",
        "priority": "High",
        "timeEstimate": "3 hours",
        "deadline": "2025-05-05",
        "requiredFiles": "",
        "uploadedFile": null
    },
    {
        "taskName": "Convert Meeting Notes to Tasks",
        "description": "Analyze meeting discussion and extract clear, actionable tasks.",
        "priority": "Medium",
        "timeEstimate": "1 hour",
        "deadline": "2025-05-04",
        "requiredFiles": "",
        "uploadedFile": null
    }
];

// Initialize Firebase Auth listener
firebase.auth().onAuthStateChanged(async user => {
    if (!user) {
        window.location.href = 'index.html';
        return;
    }

    // Display user email
    document.getElementById('userEmail').textContent = user.email;

    try {
        // Initialize Firebase Storage
        const storage = firebase.storage();
        window.storage = storage;

        // Store tasks in Firestore if not present
        await initializeTasks();
        
        // Display tasks
        await displayTasks();

        // Set up navigation and UI handlers
        setupNavigation();
        
        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Error initializing dashboard:', error);
    }
});

// Initialize tasks in Firestore
async function initializeTasks() {
    try {
        const tasksRef = db.collection('tasks');
        const snapshot = await tasksRef.get();
        
        // Only add tasks if collection is empty
        if (snapshot.empty) {
            for (const task of tasks) {
                await tasksRef.add(task);
            }
            console.log('Tasks initialized in Firestore');
        }
    } catch (error) {
        console.error('Error initializing tasks:', error);
    }
}
