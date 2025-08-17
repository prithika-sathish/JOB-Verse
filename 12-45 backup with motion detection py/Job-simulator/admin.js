document.addEventListener('DOMContentLoaded', async () => {
    // Wait for Firebase Auth to initialize and check state
    await new Promise(resolve => {
        const unsubscribe = firebase.auth().onAuthStateChanged(async user => {
            if (!user || user.email !== 'admin@gmail.com') {
                window.location.href = 'index.html';
                return;
            }

            // Display admin email
            document.getElementById('userEmail').textContent = user.email;
            unsubscribe();
            resolve();
        });
    });

    // Sidebar toggle functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    sidebarToggle?.addEventListener('click', () => {
        sidebar?.classList.toggle('collapsed');
    });

    // Navigation functionality
    const navButtons = document.querySelectorAll('.nav-btn');
    const contentSections = document.querySelectorAll('.content-section');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            navButtons.forEach(btn => btn.classList.remove('active'));
            contentSections.forEach(section => section.classList.remove('active'));
            button.classList.add('active');
            const sectionId = button.dataset.section;
            
            if (sectionId === 'timesheet') {
                window.location.href = 'erp_timesheet.html';
                return;
            }
            
            document.getElementById(sectionId)?.classList.add('active');
        });
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

    // Employee search functionality
    const employeeSearch = document.getElementById('employeeSearch');
    employeeSearch?.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        filterEmployees(searchTerm);
    });

    // Add employee button functionality
    const addEmployeeBtn = document.querySelector('.add-employee-btn');
    addEmployeeBtn?.addEventListener('click', () => {
        // TODO: Implement add employee functionality
        console.log('Add employee clicked');
    });

    // Initialize employee list
    await loadEmployees();

    // Initialize timesheet filters
    initializeTimesheetFilters();

    // Initialize payroll filters
    initializePayrollFilters();

    // Initialize task management
    initTaskManagement();
});

// Load employees from Firebase
async function loadEmployees() {
    try {
        const employeeList = document.querySelector('.employee-list');
        if (!employeeList) return;

        // Clear existing list
        employeeList.innerHTML = '';

        // Get all users from Firebase
        const usersSnapshot = await firebase.firestore().collection('users').get();
        
        usersSnapshot.forEach(doc => {
            const userData = doc.data();
            const employeeCard = createEmployeeCard(userData, doc.id);
            employeeList.appendChild(employeeCard);
        });
    } catch (error) {
        console.error('Error loading employees:', error);
    }
}

// Create employee card element
function createEmployeeCard(userData, userId) {
    const card = document.createElement('div');
    card.className = 'employee-card';
    card.innerHTML = `
        <div class="employee-info">
            <h3>${userData.email}</h3>
            <p><strong>Domain:</strong> ${userData.domain}</p>
            <p><strong>Skill:</strong> ${userData.skill}</p>
            <p><strong>Experience:</strong> ${userData.monthsExperience} months</p>
        </div>
        <div class="employee-actions">
            <button class="edit-btn" data-id="${userId}">
                <i class="fas fa-edit"></i>
            </button>
            <button class="delete-btn" data-id="${userId}">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;

    // Add event listeners for edit and delete buttons
    card.querySelector('.edit-btn').addEventListener('click', () => {
        // TODO: Implement edit functionality
        console.log('Edit employee:', userId);
    });

    card.querySelector('.delete-btn').addEventListener('click', async () => {
        if (confirm('Are you sure you want to delete this employee?')) {
            try {
                await firebase.firestore().collection('users').doc(userId).delete();
                card.remove();
            } catch (error) {
                console.error('Error deleting employee:', error);
                alert('Failed to delete employee');
            }
        }
    });

    return card;
}

// Filter employees based on search term
function filterEmployees(searchTerm) {
    const employeeCards = document.querySelectorAll('.employee-card');
    employeeCards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(searchTerm) ? 'flex' : 'none';
    });
}

// Initialize timesheet filters
function initializeTimesheetFilters() {
    const employeeFilter = document.getElementById('employeeFilter');
    if (!employeeFilter) return;

    // Populate employee filter
    firebase.firestore().collection('users').get().then(snapshot => {
        snapshot.forEach(doc => {
            const userData = doc.data();
            const option = document.createElement('option');
            option.value = doc.id;
            option.textContent = userData.email;
            employeeFilter.appendChild(option);
        });
    });

    // Add event listeners for filters
    employeeFilter.addEventListener('change', updateTimesheet);
    document.getElementById('dateFilter')?.addEventListener('change', updateTimesheet);
}

// Update timesheet display
function updateTimesheet() {
    // TODO: Implement timesheet update logic
    console.log('Updating timesheet...');
}

// Initialize payroll filters
function initializePayrollFilters() {
    const monthFilter = document.getElementById('monthFilter');
    const yearFilter = document.getElementById('yearFilter');
    
    if (!monthFilter || !yearFilter) return;

    // Populate month filter
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December'];
    months.forEach((month, index) => {
        const option = document.createElement('option');
        option.value = index + 1;
        option.textContent = month;
        monthFilter.appendChild(option);
    });

    // Populate year filter
    const currentYear = new Date().getFullYear();
    for (let year = currentYear; year >= currentYear - 2; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearFilter.appendChild(option);
    }

    // Add event listeners for filters
    monthFilter.addEventListener('change', updatePayroll);
    yearFilter.addEventListener('change', updatePayroll);

    // Generate payroll button
    document.querySelector('.generate-payroll-btn')?.addEventListener('click', generatePayroll);
}

// Update payroll display
function updatePayroll() {
    // TODO: Implement payroll update logic
    console.log('Updating payroll...');
}

// Generate payroll report
function generatePayroll() {
    // TODO: Implement payroll generation logic
    console.log('Generating payroll report...');
}

// Task Management
let allTasks = [];
let allUsers = [];

// Initialize task management
function initTaskManagement() {
    // Always ensure we have a reference to Firestore
    if (!window.db) {
        window.db = firebase.firestore();
        console.log('Initialized db reference for task management');
    }
    
    loadUsers();
    loadTasks();
    setupTaskForm();
    setupTaskFilters();
    setupTaskReviewActions();
}

// Load all users for assignment
async function loadUsers() {
    try {
        // Use a different variable to avoid conflict with allUsers
        const usersSnapshot = await firebase.firestore().collection('users').get();
        allUsers = usersSnapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
        }));
        
        console.log('Loaded users:', allUsers);
        
        // Populate user dropdown in task form
        const userSelect = document.getElementById('taskUserSelect');
        const userFilter = document.getElementById('userFilter');
        
        if (userSelect) {
            userSelect.innerHTML = `<option value="">Select a user</option>`;
            allUsers.forEach(user => {
                userSelect.innerHTML += `<option value="${user.id}">${user.email}</option>`;
            });
        }
        
        if (userFilter) {
            userFilter.innerHTML = `<option value="">All Users</option>`;
            allUsers.forEach(user => {
                userFilter.innerHTML += `<option value="${user.id}">${user.email}</option>`;
            });
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showAdminNotification('Error loading users', 'error');
    }
}

// Load all tasks
async function loadTasks() {
    try {
        // Make sure we're using the global firebase object
        const tasksSnapshot = await firebase.firestore().collection('tasks')
            .orderBy('createdAt', 'desc')
            .get();
        
        console.log('Tasks snapshot:', tasksSnapshot.docs.length);
        
        allTasks = tasksSnapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
        }));
        
        console.log('Loaded tasks:', allTasks);
        
        renderTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
        showAdminNotification('Error loading tasks', 'error');
    }
}

// Setup task form
function setupTaskForm() {
    const taskForm = document.getElementById('taskForm');
    if (!taskForm) {
        console.error('Task form not found!');
        return;
    }
    
    taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const userId = document.getElementById('taskUserSelect').value;
        const taskName = document.getElementById('taskName').value;
        const description = document.getElementById('taskDescription').value;
        const priority = document.getElementById('taskPriority').value;
        const deadline = document.getElementById('taskDeadline').value;
        const starterFileInput = document.getElementById('starterFile');
        
        if (!userId || !taskName || !description || !priority || !deadline) {
            showAdminNotification('Please fill all required fields', 'error');
            return;
        }
        
        try {
            // Show loading state
            const submitBtn = taskForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Task...';
            submitBtn.disabled = true;
            
            let starterFile = null;
            
            if (starterFileInput.files.length > 0) {
                const file = starterFileInput.files[0];
                const reader = new FileReader();
                
                // Convert to Promise
                const fileContent = await new Promise((resolve, reject) => {
                    reader.onload = e => resolve(e.target.result);
                    reader.onerror = e => reject(e);
                    reader.readAsText(file);
                });
                
                starterFile = {
                    name: file.name,
                    content: fileContent
                };
            }
            
            const taskData = {
                userId,
                taskName,
                description,
                priority,
                deadline,
                status: 'Pending',
                createdAt: new Date().toISOString(),
                starterFile
            };
            
            // Get a direct reference to the Firestore database
            const db = firebase.firestore();
            await db.collection('tasks').add(taskData);
            
            // Reset form
            taskForm.reset();
            
            // Show success message
            showAdminNotification('Task created successfully!', 'success');
            
            // Reset button and reload tasks
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
            
            // Reload tasks
            loadTasks();
            
        } catch (error) {
            console.error('Error creating task:', error);
            showAdminNotification('Error creating task', 'error');
        }
    });
    
    // Setup file input
    const starterFileInput = document.getElementById('starterFile');
    const fileLabel = document.querySelector('label[for="starterFile"]');
    
    if (starterFileInput && fileLabel) {
        starterFileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileLabel.innerHTML = `<i class="fas fa-check"></i> ${this.files[0].name}`;
                fileLabel.classList.add('file-selected');
            } else {
                fileLabel.innerHTML = `<i class="fas fa-upload"></i> Upload Starter File (Optional)`;
                fileLabel.classList.remove('file-selected');
            }
        });
    }
}

// Setup task filters
function setupTaskFilters() {
    const statusFilter = document.getElementById('statusFilter');
    const userFilter = document.getElementById('userFilter');
    
    if (statusFilter) {
        statusFilter.addEventListener('change', renderTasks);
    }
    
    if (userFilter) {
        userFilter.addEventListener('change', renderTasks);
    }
}

// Setup task review actions
function setupTaskReviewActions() {
    document.addEventListener('click', async (e) => {
        // View submitted file
        if (e.target.closest('.view-submission-btn')) {
            const taskId = e.target.closest('.view-submission-btn').dataset.taskId;
            const task = allTasks.find(t => t.id === taskId);
            
            if (task && task.submittedFile) {
                viewSubmittedFile(task.submittedFile);
            }
        }
        
        // Approve task
        if (e.target.closest('.approve-task-btn')) {
            const taskId = e.target.closest('.approve-task-btn').dataset.taskId;
            const feedback = prompt('Add feedback for approval (optional):');
            await updateTaskStatus(taskId, 'Approved', feedback);
        }
        
        // Reject task
        if (e.target.closest('.reject-task-btn')) {
            const taskId = e.target.closest('.reject-task-btn').dataset.taskId;
            const feedback = prompt('Please provide feedback for rejection:');
            
            if (feedback) {
                await updateTaskStatus(taskId, 'Rejected', feedback);
            } else {
                showAdminNotification('Feedback is required for rejection', 'error');
            }
        }
    });
}

// Update task status
async function updateTaskStatus(taskId, status, feedback) {
    try {
        await firebase.firestore().collection('tasks').doc(taskId).update({
            status,
            feedback,
            reviewedAt: new Date().toISOString()
        });
        
        showAdminNotification(`Task ${status.toLowerCase()} successfully`, 'success');
        loadTasks();
    } catch (error) {
        console.error(`Error updating task status:`, error);
        showAdminNotification(`Error updating task status`, 'error');
    }
}

// View submitted file
function viewSubmittedFile(file) {
    // Create modal for viewing file content
    const modal = document.createElement('div');
    modal.className = 'file-view-modal';
    
    modal.innerHTML = `
        <div class="file-view-content">
            <div class="file-view-header">
                <h3><i class="fas fa-file-alt"></i> ${file.name}</h3>
                <button class="close-file-view"><i class="fas fa-times"></i></button>
            </div>
            <div class="file-view-body">
                <pre>${file.content}</pre>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add close functionality
    modal.querySelector('.close-file-view').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    // Close when clicking outside the content
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// Render tasks
function renderTasks() {
    const tasksTableBody = document.getElementById('tasksTableBody');
    if (!tasksTableBody) {
        console.error('Tasks table body not found!');
        return;
    }
    
    console.log('Rendering tasks, element found:', tasksTableBody);
    
    const statusFilter = document.getElementById('statusFilter')?.value || '';
    const userFilter = document.getElementById('userFilter')?.value || '';
    
    console.log('Filters:', { statusFilter, userFilter });
    console.log('All tasks available:', allTasks.length);
    
    // Filter tasks
    let filteredTasks = [...allTasks];
    
    if (statusFilter) {
        filteredTasks = filteredTasks.filter(task => task.status === statusFilter);
    }
    
    if (userFilter) {
        filteredTasks = filteredTasks.filter(task => task.userId === userFilter);
    }
    
    console.log('Filtered tasks:', filteredTasks.length);
    
    // Clear existing tasks
    tasksTableBody.innerHTML = '';
    
    if (filteredTasks.length === 0) {
        tasksTableBody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 2rem;">
                    <p style="color: var(--text-secondary);">No tasks found</p>
                </td>
            </tr>
        `;
        return;
    }
    
    // Render each task
    filteredTasks.forEach(task => {
        const user = allUsers.find(u => u.id === task.userId);
        const userName = user ? (user.displayName || user.email) : 'Unknown User';
        
        console.log('Rendering task:', task.taskName, 'for user:', userName);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${task.taskName}</td>
            <td>${userName}</td>
            <td><span class="priority-badge ${task.priority?.toLowerCase() || 'medium'}">${task.priority || 'Medium'}</span></td>
            <td>${new Date(task.deadline).toLocaleDateString()}</td>
            <td>
                <span class="status-badge ${task.status?.toLowerCase() || 'pending'}">${task.status || 'Pending'}</span>
            </td>
            <td>
                ${task.submittedFile ? 
                    `<div class="submission-status">
                        <i class="fas fa-check-circle"></i> Submitted
                        <button class="view-submission-btn" data-task-id="${task.id}">
                            <i class="fas fa-eye"></i> View
                        </button>
                    </div>` : 
                    `<div class="submission-status pending">
                        <i class="fas fa-hourglass-half"></i> Awaiting submission
                    </div>`
                }
            </td>
            <td>
                <div class="task-actions admin-actions">
                    ${task.status === 'Submitted' ? `
                        <button class="approve-task-btn" data-task-id="${task.id}">
                            <i class="fas fa-check"></i> Approve
                        </button>
                        <button class="reject-task-btn" data-task-id="${task.id}">
                            <i class="fas fa-times"></i> Reject
                        </button>
                    ` : ''}
                    <button class="delete-task-btn" data-task-id="${task.id}">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </td>
        `;
        
        tasksTableBody.appendChild(row);
    });
    
    // Setup delete task buttons
    document.querySelectorAll('.delete-task-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const taskId = this.dataset.taskId;
            if (confirm('Are you sure you want to delete this task?')) {
                try {
                    // Get the database reference and use it directly
                    const db = firebase.firestore();
                    await db.collection('tasks').doc(taskId).delete();
                    showAdminNotification('Task deleted successfully', 'success');
                    loadTasks();
                } catch (error) {
                    console.error('Error deleting task:', error);
                    showAdminNotification('Error deleting task', 'error');
                }
            }
        });
    });
}

// Show notification
function showAdminNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `admin-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Diagnostic function to help debug issues
// This can be run from the browser console
function diagnoseTaskIssues() {
    console.group('Task Management Diagnostics');
    
    // Check DOM elements
    const taskForm = document.getElementById('taskForm');
    const taskUserSelect = document.getElementById('taskUserSelect');
    const tasksTableBody = document.getElementById('tasksTableBody');
    
    console.log('Task Form Found:', !!taskForm);
    console.log('User Select Found:', !!taskUserSelect);
    console.log('Tasks Table Body Found:', !!tasksTableBody);
    
    // Check data
    console.log('Users Loaded:', allUsers.length);
    console.log('Tasks Loaded:', allTasks.length);
    
    // Check Firebase instance
    console.log('Firebase Auth Available:', !!firebase?.auth);
    console.log('Firebase Firestore Available:', !!firebase?.firestore);
    
    // Check global references
    console.log('Global DB Reference:', !!window.db);
    console.log('Global Auth Reference:', !!window.auth);
    
    console.groupEnd();
    
    return {
        elementsFound: {
            taskForm: !!taskForm,
            taskUserSelect: !!taskUserSelect,
            tasksTableBody: !!tasksTableBody
        },
        dataLoaded: {
            users: allUsers.length,
            tasks: allTasks.length
        }
    };
}

// Make the function available globally
window.diagnoseTaskIssues = diagnoseTaskIssues;
window.reloadTasks = loadTasks;
window.reloadUsers = loadUsers;
