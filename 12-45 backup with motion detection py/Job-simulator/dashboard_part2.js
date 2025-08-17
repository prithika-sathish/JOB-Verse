// Display tasks in the table
async function displayTasks() {
    try {
        const tasksTableBody = document.getElementById('tasksTableBody');
        const tasksRef = db.collection('tasks');
        const snapshot = await tasksRef.get();

        tasksTableBody.innerHTML = '';

        snapshot.forEach(doc => {
            const task = doc.data();
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${task.taskName}</td>
                <td>${task.description}</td>
                <td>${task.priority}</td>
                <td>${task.timeEstimate}</td>
                <td>${task.deadline}</td>
                <td>${task.requiredFiles || 'No files required'}</td>
                <td>
                    <input type="file" id="file-${doc.id}" class="file-input">
                    <button class="upload-btn" onclick="handleFileUpload('${doc.id}')">
                        ${task.uploadedFile ? 'Update File' : 'Upload File'}
                    </button>
                    ${task.uploadedFile ? `
                        <div class="file-info">
                            <a href="${task.uploadedFile.url}" target="_blank">${task.uploadedFile.name}</a>
                        </div>
                    ` : ''}
                </td>
            `;
            tasksTableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error displaying tasks:', error);
    }
}

// Handle file upload
async function handleFileUpload(taskId) {
    const fileInput = document.getElementById(`file-${taskId}`);
    fileInput.click();

    fileInput.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            // Create a reference to the file in Firebase Storage
            const storageRef = storage.ref();
            const fileRef = storageRef.child(`task-files/${taskId}/${file.name}`);

            // Upload the file
            await fileRef.put(file);

            // Get the download URL
            const downloadURL = await fileRef.getDownloadURL();

            // Update the task document in Firestore
            await db.collection('tasks').doc(taskId).update({
                uploadedFile: {
                    name: file.name,
                    url: downloadURL,
                    uploadedAt: firebase.firestore.FieldValue.serverTimestamp()
                }
            });

            // Refresh the display
            displayTasks();
        } catch (error) {
            console.error('Error uploading file:', error);
            alert('Error uploading file. Please try again.');
        }
    };
}

// Set up navigation functionality
function setupNavigation() {
    // Logout functionality
    document.getElementById('logoutBtn').addEventListener('click', async () => {
        try {
            await firebase.auth().signOut();
            window.location.href = 'index.html';
        } catch (error) {
            console.error('Error signing out:', error);
        }
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
            // Remove active class from all buttons and sections
            navButtons.forEach(btn => btn.classList.remove('active'));
            contentSections.forEach(section => section.classList.remove('active'));

            // Add active class to clicked button and corresponding section
            button.classList.add('active');
            const sectionId = button.dataset.section;
            document.getElementById(sectionId)?.classList.add('active');
        });
    });
}
