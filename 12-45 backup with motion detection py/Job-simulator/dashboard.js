document.addEventListener('DOMContentLoaded', function() {
    // Initialize back button
    let backBtn = document.getElementById('backButton');
    if (backBtn) {
        backBtn.style.display = 'none';
        backBtn.addEventListener('click', () => window.history.back());
    }

    // Add click handler to all Choose File buttons
    document.querySelectorAll('.choose-file').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const fileInput = this.closest('.file-upload-container').querySelector('input[type="file"]');
            fileInput.click();
        });
    });

    // Add change handler to all file inputs
    document.querySelectorAll('.file-upload-container input[type="file"]').forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            if (fileName) {
                const button = this.closest('.file-upload-container').querySelector('.choose-file');
                button.textContent = fileName;
            }
        });
    });

    // Add click handler to sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }

    // Handle chat button clicks
    const chatButtons = document.querySelectorAll('.chat-btn');
    chatButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            const buttonText = button.textContent.trim();
            
            if (buttonText === 'Chat with Mr. Raze') {
                window.location.href = 'bossbot.html';
            } else if (buttonText === 'Chat with Alex') {
                window.location.href = 'juniordev-bot.html';
            } else if (buttonText === 'Chat with Sarah') {
                window.location.href = 'careerguide-bot.html';
            }
        });
    });

    // Add click handlers to nav buttons
    document.querySelectorAll('.nav-btn').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const sectionId = this.dataset.section;

            if (sectionId === 'tech-upskilling' || sectionId === 'soft-upskilling' || sectionId === 'switch-prep' || sectionId === 'colleagues' || sectionId === 'erp' || sectionId === 'job-finder' || sectionId === 'code-lab' || sectionId === 'network-shop' || sectionId === 'spin2solve' || sectionId === 'decision-lab' || sectionId === 'flashcards' || sectionId === 'career-twin' || sectionId === 'workflow-management') {
                if (backBtn) {
                    backBtn.style.display = 'flex';
                }
                
                if (sectionId === 'tech-upskilling') {
                    window.location.href = 'soft-skills.html';
                } else if (sectionId === 'soft-upskilling') {
                    window.location.href = 'task_management.html';
                } else if (sectionId === 'switch-prep') {
                    window.location.href = 'mock_interview.html';
                } else if (sectionId === 'erp') {
                    window.location.href = 'erp_timesheet.html';
                } else if (sectionId === 'job-finder') {
                    window.location.href = 'job_finder.html';
                } else if (sectionId === 'code-lab') {
                    window.location.href = 'code_editor.html';
                } else if (sectionId === 'network-shop') {
                    window.location.href = 'networking.html';
                } else if (sectionId === 'spin2solve') {
                    window.location.href = 'spin_the_wheel.html';
                } else if (sectionId === 'decision-lab') {
                    window.location.href = 'scenario_sim.html';
                } else if (sectionId === 'flashcards') {
                    window.location.href = 'flashcards.html';
                } else if (sectionId === 'career-twin') {
                    window.location.href = 'guidance.html';
                } else if (sectionId === 'colleagues') {
                    document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
                    document.getElementById(sectionId)?.classList.add('active');
                    
                    const sarahCard = document.querySelector('.colleague-card:nth-child(3)');
                    if (sarahCard) {
                        sarahCard.addEventListener('click', function(e) {
                            if (!e.target.closest('.chat-btn')) {
                                window.location.href = 'task_management.html';
                            }
                        });
                    }
                    return;
                } else if (sectionId === 'workflow-management') {
                    document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
                    document.getElementById(sectionId)?.classList.add('active');
                    initializeWorkflowManagement();
                    return;
                }
                return;
            }
            
            document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
            document.getElementById(sectionId)?.classList.add('active');
            
            if (backBtn) {
                backBtn.style.display = 'none';
            }
        });
    });

    // Initialize Firebase Auth listener
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            // Set up single listener for tasks
            const tasksRef = firebase.firestore().collection('tasks')
                .where('userId', '==', user.uid);

            tasksRef.onSnapshot((snapshot) => {
                updateTasksTable(snapshot);
            }, (error) => {
                console.error("Error listening to tasks:", error);
            });
        }
    });

    // Handle starter file downloads
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('download-btn') && e.target.textContent === 'Download Starter File') {
            downloadStarterFile();
        }
    });
});

// Function to update tasks table
function updateTasksTable(snapshot) {
    const tasksTableBody = document.getElementById('tasksTableBody');
    if (!tasksTableBody) return;

    // Keep track of existing tasks
    const existingTasks = new Set();
    
    snapshot.forEach(doc => {
        const task = doc.data();
        const taskId = doc.id;
        existingTasks.add(taskId);

        let row = document.querySelector(`[data-task-id="${taskId}"]`);
        
        if (!row) {
            // Create new row if it doesn't exist
            row = document.createElement('tr');
            row.setAttribute('data-task-id', taskId);
            tasksTableBody.appendChild(row);
        }

        // Update row content
        row.innerHTML = `
            <td><i class="fas ${getStatusIcon(task.status)}"></i></td>
            <td>${task.taskName}</td>
            <td>${task.description}</td>
            <td>${task.priority}</td>
            <td>${task.timeEstimate || '2 hours'}</td>
            <td>${task.deadline}</td>
            <td>
                <button class="download-btn">Download Starter File</button>
            </td>
            <td>
                <div class="file-upload-container">
                    <input type="file" accept="*/*" />
                    <small>Max file size: 1MB</small>
                    ${task.status === 'Completed' ? 
                        `<button class="download-btn">Download File ✓</button>
                         <div class="status">✓ Task completed</div>
                         <div class="status">Submitted</div>` :
                        `<button class="choose-file">Choose File</button>`}
                </div>
            </td>
        `;
    });

    // Remove rows for deleted tasks
    const rows = tasksTableBody.getElementsByTagName('tr');
    for (let i = rows.length - 1; i >= 0; i--) {
        const row = rows[i];
        const taskId = row.getAttribute('data-task-id');
        if (taskId && !existingTasks.has(taskId)) {
            row.remove();
        }
    }
}

// Helper function to get status icon
function getStatusIcon(status) {
    switch(status) {
        case 'Completed':
            return 'fa-check-circle';
        case 'Pending':
            return 'fa-clock';
        case 'Failed':
            return 'fa-times-circle';
        default:
            return 'fa-clock';
    }
}

// Function to download starter file
async function downloadStarterFile() {
    try {
        // Read the faulty_ui_bug.html file
        const response = await fetch('faulty_ui_bug.html');
        const content = await response.text();
        
        // Create and trigger download
        const blob = new Blob([content], { type: 'text/html' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'faulty_ui_bug.html';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error("Error downloading starter file:", error);
    }
}

// Workflow Management Functions
async function initializeWorkflowManagement() {
    // Load workflow service if not already loaded
    if (!window.workflowService) {
        const script = document.createElement('script');
        script.src = 'workflow-service.js';
        document.head.appendChild(script);
        
        // Wait for script to load
        await new Promise(resolve => {
            script.onload = resolve;
        });
    }
    
    updateWorkflowStatus();
    loadRecentJobs();
    
    // Set up periodic status updates
    setInterval(updateWorkflowStatus, 10000); // Update every 10 seconds
}

function updateWorkflowStatus() {
    if (!window.workflowService) return;
    
    const status = window.workflowService.getStatus();
    const indicator = document.getElementById('workflow-status-indicator');
    const lastRunTime = document.getElementById('last-run-time');
    const jobsProcessed = document.getElementById('jobs-processed');
    const jobsAdded = document.getElementById('jobs-added');
    const runButton = document.getElementById('run-workflow-btn');
    
    if (indicator) {
        const dot = indicator.querySelector('.status-dot');
        const text = indicator.querySelector('.status-text');
        
        if (status.isRunning) {
            dot.style.backgroundColor = '#ff9800';
            text.textContent = 'Running...';
            runButton.disabled = true;
            runButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
        } else {
            dot.style.backgroundColor = '#4caf50';
            text.textContent = 'Ready';
            runButton.disabled = false;
            runButton.innerHTML = '<i class="fas fa-play"></i> Run Now';
        }
    }
    
    if (lastRunTime) {
        lastRunTime.textContent = status.lastRun ? 
            status.lastRun.toLocaleString() : 'Never';
    }
    
    if (jobsProcessed) {
        jobsProcessed.textContent = status.jobsProcessed || 0;
    }
    
    if (jobsAdded) {
        jobsAdded.textContent = status.jobsFiltered || 0;
    }
}

async function triggerWorkflow() {
    if (!window.workflowService) {
        showWorkflowMessage('Workflow service not loaded', 'error');
        return;
    }
    
    try {
        showWorkflowMessage('Starting workflow...', 'info');
        const result = await window.workflowService.executeWorkflow();
        showWorkflowMessage(`Workflow completed! Added ${result.jobsFiltered} new jobs.`, 'success');
        loadRecentJobs(); // Refresh recent jobs list
    } catch (error) {
        console.error('Workflow execution failed:', error);
        showWorkflowMessage(`Workflow failed: ${error.message}`, 'error');
    }
}

async function loadRecentJobs() {
    try {
        const recentJobsList = document.getElementById('recent-jobs-list');
        if (!recentJobsList || !window.db) return;
        
        const jobsSnapshot = await window.db.collection('jobs')
            .orderBy('addedAt', 'desc')
            .limit(5)
            .get();
        
        if (jobsSnapshot.empty) {
            recentJobsList.innerHTML = `
                <div class="no-jobs-message">
                    <i class="fas fa-briefcase"></i>
                    <p>No jobs added yet. Run the workflow to fetch new jobs.</p>
                </div>
            `;
            return;
        }
        
        let jobsHtml = '';
        jobsSnapshot.forEach(doc => {
            const job = doc.data();
            jobsHtml += `
                <div class="recent-job-item">
                    <div class="job-info">
                        <h4>${job.title || 'Untitled Position'}</h4>
                        <p>${job.source || 'Unknown Source'}</p>
                    </div>
                    <div class="job-time">
                        ${job.dateAdded || 'Recently'}
                    </div>
                </div>
            `;
        });
        
        recentJobsList.innerHTML = jobsHtml;
        
    } catch (error) {
        console.error('Error loading recent jobs:', error);
    }
}

async function viewWorkflowLogs() {
    try {
        if (!window.db) {
            showWorkflowMessage('Database not available', 'error');
            return;
        }
        
        const logsSnapshot = await window.db.collection('workflow_logs')
            .orderBy('timestamp', 'desc')
            .limit(10)
            .get();
        
        let logsHtml = '<h3>Recent Workflow Executions</h3>';
        
        if (logsSnapshot.empty) {
            logsHtml += '<p>No workflow logs found.</p>';
        } else {
            logsHtml += '<div class="logs-container">';
            logsSnapshot.forEach(doc => {
                const log = doc.data();
                const timestamp = log.timestamp ? log.timestamp.toDate().toLocaleString() : 'Unknown';
                const status = log.success ? 'Success' : 'Failed';
                const statusClass = log.success ? 'success' : 'error';
                
                logsHtml += `
                    <div class="log-entry ${statusClass}">
                        <div class="log-header">
                            <span class="log-status">${status}</span>
                            <span class="log-time">${timestamp}</span>
                        </div>
                        <div class="log-details">
                            Jobs Processed: ${log.jobsProcessed || 0} | 
                            Jobs Added: ${log.jobsAdded || 0}
                            ${log.error ? `<br>Error: ${log.error}` : ''}
                        </div>
                    </div>
                `;
            });
            logsHtml += '</div>';
        }
        
        // Create modal to show logs
        const modal = document.createElement('div');
        modal.className = 'workflow-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Workflow Logs</h2>
                    <button class="close-modal" onclick="this.closest('.workflow-modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${logsHtml}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('Error loading workflow logs:', error);
        showWorkflowMessage('Failed to load workflow logs', 'error');
    }
}

function showWorkflowMessage(message, type = 'info') {
    const colors = {
        success: '#4caf50',
        error: '#f44336',
        info: '#2196f3',
        warning: '#ff9800'
    };
    
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        z-index: 1001;
        font-weight: 500;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Add CSS for workflow management
const workflowStyles = document.createElement('style');
workflowStyles.textContent = `
    .workflow-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: auto auto;
        gap: 2rem;
        max-width: 1200px;
    }
    
    .workflow-status-card, .workflow-config-card, .recent-jobs-card {
        background: var(--card-dark);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    .recent-jobs-card {
        grid-column: 1 / -1;
    }
    
    .status-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #4caf50;
    }
    
    .status-details {
        margin-bottom: 1.5rem;
    }
    
    .status-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .status-item .label {
        color: rgba(255,255,255,0.7);
    }
    
    .status-item .value {
        font-weight: 600;
        color: var(--primary-dark);
    }
    
    .workflow-actions {
        display: flex;
        gap: 1rem;
    }
    
    .action-btn {
        flex: 1;
        padding: 0.75rem 1rem;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .action-btn.primary {
        background: var(--primary-dark);
        color: white;
    }
    
    .action-btn.secondary {
        background: transparent;
        color: var(--primary-dark);
        border: 1px solid var(--primary-dark);
    }
    
    .action-btn:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,255,213,0.3);
    }
    
    .action-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    .config-section {
        margin-bottom: 1.5rem;
    }
    
    .config-section h4 {
        margin-bottom: 0.75rem;
        color: var(--primary-dark);
    }
    
    .config-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        padding: 0.5rem 0;
    }
    
    .config-label {
        color: rgba(255,255,255,0.7);
    }
    
    .config-value {
        font-weight: 500;
        word-break: break-all;
    }
    
    .filter-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .filter-tag {
        background: rgba(0,255,213,0.1);
        color: var(--primary-dark);
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        border: 1px solid rgba(0,255,213,0.2);
    }
    
    .recent-job-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        margin-bottom: 0.5rem;
        background: var(--bg-dark);
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }
    
    .recent-job-item h4 {
        margin: 0 0 0.25rem 0;
        font-size: 1rem;
    }
    
    .recent-job-item p {
        margin: 0;
        color: rgba(255,255,255,0.6);
        font-size: 0.85rem;
    }
    
    .job-time {
        color: var(--primary-dark);
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .no-jobs-message {
        text-align: center;
        padding: 2rem;
        color: rgba(255,255,255,0.6);
    }
    
    .no-jobs-message i {
        font-size: 2rem;
        margin-bottom: 1rem;
        color: var(--primary-dark);
    }
    
    .workflow-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }
    
    .modal-content {
        background: var(--card-dark);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        max-width: 600px;
        max-height: 80vh;
        overflow-y: auto;
        width: 90%;
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .close-modal {
        background: none;
        border: none;
        color: var(--text-dark);
        font-size: 1.2rem;
        cursor: pointer;
    }
    
    .modal-body {
        padding: 1.5rem;
    }
    
    .log-entry {
        margin-bottom: 1rem;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    .log-entry.success {
        border-left-color: #4caf50;
        background: rgba(76,175,80,0.1);
    }
    
    .log-entry.error {
        border-left-color: #f44336;
        background: rgba(244,67,54,0.1);
    }
    
    .log-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .log-details {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.8);
    }
    
    @media (max-width: 768px) {
        .workflow-container {
            grid-template-columns: 1fr;
        }
        
        .workflow-actions {
            flex-direction: column;
        }
    }
`;
document.head.appendChild(workflowStyles);
