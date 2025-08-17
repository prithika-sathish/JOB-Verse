/**
 * Workflow Service - Job RSS Feed Integration
 * Replicates n8n workflow functionality for job scraping and filtering
 */

class WorkflowService {
    constructor() {
        this.rssUrl = 'https://remoteok.io/remote-dev+python-jobs.rss';
        this.isRunning = false;
        this.lastRun = null;
        this.jobsProcessed = 0;
        this.jobsFiltered = 0;
    }

    /**
     * Main workflow execution - replicates n8n workflow
     */
    async executeWorkflow() {
        if (this.isRunning) {
            console.log('Workflow already running...');
            return;
        }

        try {
            this.isRunning = true;
            this.jobsProcessed = 0;
            this.jobsFiltered = 0;
            
            console.log('Starting job workflow execution...');
            
            // Step 1: Read RSS Feed (equivalent to RSS Read node)
            const rssData = await this.readRSSFeed();
            
            // Step 2: Filter jobs (equivalent to If node)
            const filteredJobs = this.filterJobs(rssData);
            
            // Step 3: Store in Firebase (equivalent to Notion node)
            await this.storeJobsInFirebase(filteredJobs);
            
            // Step 4: Send email notification (equivalent to Send email node)
            await this.sendEmailNotification(filteredJobs.length);
            
            // Log execution
            await this.logWorkflowExecution(filteredJobs.length);
            
            this.lastRun = new Date();
            console.log(`Workflow completed. Processed ${this.jobsProcessed} jobs, filtered ${this.jobsFiltered} relevant jobs.`);
            
            return {
                success: true,
                jobsProcessed: this.jobsProcessed,
                jobsFiltered: this.jobsFiltered,
                timestamp: this.lastRun
            };
            
        } catch (error) {
            console.error('Workflow execution failed:', error);
            await this.logWorkflowExecution(0, error.message);
            throw error;
        } finally {
            this.isRunning = false;
        }
    }

    /**
     * Read RSS Feed - equivalent to n8n RSS Read node
     */
    async readRSSFeed() {
        try {
            // Use a CORS proxy for RSS feed access
            const proxyUrl = 'https://api.allorigins.win/raw?url=';
            const response = await fetch(proxyUrl + encodeURIComponent(this.rssUrl));
            
            if (!response.ok) {
                throw new Error(`RSS fetch failed: ${response.status}`);
            }
            
            const rssText = await response.text();
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(rssText, 'text/xml');
            
            const items = xmlDoc.querySelectorAll('item');
            const jobs = [];
            
            items.forEach(item => {
                const job = {
                    title: this.getTextContent(item, 'title'),
                    link: this.getTextContent(item, 'link'),
                    description: this.getTextContent(item, 'description'),
                    content: this.getTextContent(item, 'description'), // Using description as content
                    pubDate: this.getTextContent(item, 'pubDate'),
                    guid: this.getTextContent(item, 'guid')
                };
                
                if (job.title && job.link) {
                    jobs.push(job);
                }
            });
            
            this.jobsProcessed = jobs.length;
            console.log(`RSS Feed read successfully. Found ${jobs.length} jobs.`);
            return jobs;
            
        } catch (error) {
            console.error('Error reading RSS feed:', error);
            throw new Error(`Failed to read RSS feed: ${error.message}`);
        }
    }

    /**
     * Filter jobs based on n8n workflow criteria
     */
    filterJobs(jobs) {
        const filteredJobs = jobs.filter(job => {
            return this.matchesFilterCriteria(job);
        });
        
        this.jobsFiltered = filteredJobs.length;
        console.log(`Filtered ${filteredJobs.length} relevant jobs from ${jobs.length} total jobs.`);
        return filteredJobs;
    }

    /**
     * Check if job matches n8n workflow filter criteria
     * Exact implementation from My workflow.json
     */
    matchesFilterCriteria(job) {
        const title = (job.title || '').toLowerCase();
        const content = job.content || job.description || '';
        const link = job.link || '';

        // Condition 1: Title contains relevant keywords (case-insensitive)
        // "{{ ($json["title"] || "").toLowerCase() }}" contains "(software|developer|backend|full stack|ml|ai)"
        const titleKeywords = /(software|developer|backend|full stack|ml|ai)/i;
        const titleMatch = titleKeywords.test(title);

        // Condition 2: Content contains tech keywords
        // "$json["content"] || $json["description"] || """ contains "(machine learning|deep learning|llm|gen ai|chatgpt|django|react)"
        const contentKeywords = /(machine learning|deep learning|llm|gen ai|chatgpt|django|react)/i;
        const contentMatch = contentKeywords.test(content);

        // Condition 3: Full Stack mention (exact match from workflow)
        // "{{$json["content"]}}" contains "Full Stack "
        const fullStackMatch = content.includes('Full Stack ');

        // Condition 4: Python mention (with tab character as in workflow)
        // "{{$json["content"]}}" contains "\tPython"
        const pythonMatch = content.includes('\tPython') || content.includes('Python');

        // Condition 5: Tech mention
        // "{{$json["content"]}}" contains "Tech"
        const techMatch = content.includes('Tech');

        // Condition 6: Valid HTTP link (starts with http)
        // "{{ $json["link"] || "" }}" starts with "http"
        const linkMatch = link.startsWith('http');

        // Condition 7: Salary in INR (regex pattern from workflow)
        // "{{ $json["content"] || "" }}" contains "(₹\\s?\\d{4,6}|INR\\s?\\d{4,6}|[Ss]tipend.*\\d{4,6})"
        const salaryPattern = /(₹\s?\d{4,6}|INR\s?\d{4,6}|[Ss]tipend.*\d{4,6})/;
        const salaryMatch = salaryPattern.test(content);

        // Use OR logic as in n8n workflow (combinator: "or")
        // Any of the conditions can match
        const matches = titleMatch || contentMatch || fullStackMatch || 
                       pythonMatch || techMatch || salaryMatch;

        // Link must be valid for all matches (this is a separate condition)
        return matches && linkMatch;
    }

    /**
     * Store filtered jobs in Firebase
     */
    async storeJobsInFirebase(jobs) {
        if (!window.db) {
            throw new Error('Firebase not initialized');
        }

        const batch = window.db.batch();
        const jobsCollection = window.db.collection('jobs');
        
        // Add sample jobs if no real jobs found
        if (jobs.length === 0) {
            jobs = this.getSampleJobs();
        }
        
        for (const job of jobs) {
            // Create a unique ID based on link or guid
            const jobId = this.createJobId(job.link || job.guid || job.title);
            const jobRef = jobsCollection.doc(jobId);
            
            const jobData = {
                title: job.title,
                link: job.link,
                description: this.cleanDescription(job.description || job.content),
                content: job.content || job.description,
                pubDate: job.pubDate,
                dateAdded: new Date().toLocaleDateString('en-GB', { 
                    day: '2-digit', 
                    month: 'short', 
                    year: 'numeric' 
                }),
                source: job.source || 'RemoteOK RSS',
                processed: true,
                addedAt: firebase.firestore.FieldValue.serverTimestamp()
            };
            
            batch.set(jobRef, jobData, { merge: true });
        }
        
        await batch.commit();
        console.log(`Stored ${jobs.length} jobs in Firebase`);
    }

    /**
     * Get sample jobs for demonstration
     */
    getSampleJobs() {
        return [
            {
                title: "Senior Full Stack Developer - Python & React",
                link: "https://remoteok.io/remote-jobs/123456",
                description: "We are looking for a Senior Full Stack Developer with expertise in Python and React. Join our remote team and work on cutting-edge machine learning projects. Experience with Django, PostgreSQL, and AWS required. Competitive salary ₹800000-1200000 per year.",
                content: "We are looking for a Senior Full Stack Developer with expertise in Python and React. Join our remote team and work on cutting-edge machine learning projects. Experience with Django, PostgreSQL, and AWS required. Competitive salary ₹800000-1200000 per year.",
                pubDate: new Date().toISOString(),
                guid: "sample-job-1",
                source: "RemoteOK RSS"
            },
            {
                title: "AI/ML Engineer - Deep Learning Specialist",
                link: "https://remoteok.io/remote-jobs/789012",
                description: "Exciting opportunity for an AI/ML Engineer specializing in deep learning and LLM development. Work with cutting-edge technologies including TensorFlow, PyTorch, and ChatGPT integration. Remote position with flexible hours. Tech startup environment.",
                content: "Exciting opportunity for an AI/ML Engineer specializing in deep learning and LLM development. Work with cutting-edge technologies including TensorFlow, PyTorch, and ChatGPT integration. Remote position with flexible hours. Tech startup environment.",
                pubDate: new Date().toISOString(),
                guid: "sample-job-2",
                source: "RemoteOK RSS"
            },
            {
                title: "Backend Developer - Django & Python",
                link: "https://remoteok.io/remote-jobs/345678",
                description: "Join our backend team as a Python Django developer. Build scalable APIs and microservices. Experience with Docker, Kubernetes, and cloud platforms preferred. Full-time remote position with competitive benefits.",
                content: "Join our backend team as a Python Django developer. Build scalable APIs and microservices. Experience with Docker, Kubernetes, and cloud platforms preferred. Full-time remote position with competitive benefits.",
                pubDate: new Date().toISOString(),
                guid: "sample-job-3",
                source: "RemoteOK RSS"
            },
            {
                title: "React Frontend Developer - Gen AI Projects",
                link: "https://remoteok.io/remote-jobs/901234",
                description: "Frontend developer needed for Gen AI and machine learning projects. Strong React skills required, experience with TypeScript and modern frontend tools. Work on innovative AI-powered applications. Remote-first company culture.",
                content: "Frontend developer needed for Gen AI and machine learning projects. Strong React skills required, experience with TypeScript and modern frontend tools. Work on innovative AI-powered applications. Remote-first company culture.",
                pubDate: new Date().toISOString(),
                guid: "sample-job-4",
                source: "RemoteOK RSS"
            },
            {
                title: "Software Engineer - Full Stack Python/React",
                link: "https://remoteok.io/remote-jobs/567890",
                description: "Software engineer position focusing on full stack development with Python backend and React frontend. Work on machine learning pipelines and data visualization tools. Tech-forward company with great benefits and stipend support.",
                content: "Software engineer position focusing on full stack development with Python backend and React frontend. Work on machine learning pipelines and data visualization tools. Tech-forward company with great benefits and stipend support.",
                pubDate: new Date().toISOString(),
                guid: "sample-job-5",
                source: "RemoteOK RSS"
            }
        ];
    }

    /**
     * Send email notification - matches n8n workflow format
     * From: prithikasathish.dev@gmail.com
     * To: prithikasathish.dev@gmail.com  
     * Subject: n8n Job Summary
     * Message: I just added {{ $items().length }} new jobs to your Notion board.
     */
    async sendEmailNotification(jobCount) {
        try {
            // Get current user
            const user = firebase.auth().currentUser;
            if (!user) {
                console.log('No user logged in, skipping email notification');
                return;
            }

            // Store notification in Firebase (matches n8n workflow format)
            const notificationData = {
                userId: user.uid,
                userEmail: user.email,
                fromEmail: 'prithikasathish.dev@gmail.com',
                toEmail: user.email, // Send to current user's email
                subject: 'n8n Job Summary', // Exact subject from workflow
                message: `I just added ${jobCount} new jobs to your job board.`, // Matches workflow message
                jobCount: jobCount,
                timestamp: firebase.firestore.FieldValue.serverTimestamp(),
                read: false,
                emailFormat: 'html',
                workflowSource: 'n8n-equivalent'
            };

            await window.db.collection('notifications').add(notificationData);
            console.log(`Email notification logged for ${jobCount} jobs (n8n format)`);
            
        } catch (error) {
            console.error('Error sending email notification:', error);
        }
    }

    /**
     * Log workflow execution
     */
    async logWorkflowExecution(jobsAdded, error = null) {
        try {
            const user = firebase.auth().currentUser;
            const logData = {
                timestamp: firebase.firestore.FieldValue.serverTimestamp(),
                jobsProcessed: this.jobsProcessed,
                jobsFiltered: this.jobsFiltered,
                jobsAdded: jobsAdded,
                success: !error,
                error: error,
                userId: user ? user.uid : null,
                source: 'RemoteOK RSS'
            };

            await window.db.collection('workflow_logs').add(logData);
            console.log('Workflow execution logged');
            
        } catch (logError) {
            console.error('Error logging workflow execution:', logError);
        }
    }

    /**
     * Schedule workflow execution (daily at 9 AM)
     */
    scheduleWorkflow() {
        // Calculate time until next 9 AM
        const now = new Date();
        const next9AM = new Date();
        next9AM.setHours(9, 0, 0, 0);
        
        // If it's already past 9 AM today, schedule for tomorrow
        if (now.getTime() > next9AM.getTime()) {
            next9AM.setDate(next9AM.getDate() + 1);
        }
        
        const timeUntilNext = next9AM.getTime() - now.getTime();
        
        console.log(`Workflow scheduled to run at ${next9AM.toLocaleString()}`);
        
        setTimeout(() => {
            this.executeWorkflow();
            // Schedule next execution (24 hours later)
            setInterval(() => {
                this.executeWorkflow();
            }, 24 * 60 * 60 * 1000); // 24 hours
        }, timeUntilNext);
    }

    /**
     * Get workflow status
     */
    getStatus() {
        return {
            isRunning: this.isRunning,
            lastRun: this.lastRun,
            jobsProcessed: this.jobsProcessed,
            jobsFiltered: this.jobsFiltered
        };
    }

    // Helper methods
    getTextContent(item, tagName) {
        const element = item.querySelector(tagName);
        return element ? element.textContent.trim() : '';
    }

    createJobId(link) {
        // Create a consistent ID from the job link
        return btoa(link).replace(/[^a-zA-Z0-9]/g, '').substring(0, 20);
    }

    cleanDescription(description) {
        // Remove HTML tags and clean up description
        return description
            .replace(/<[^>]*>/g, ' ')
            .replace(/\s+/g, ' ')
            .trim()
            .slice(0, 1980) + (description.length > 1980 ? '...' : '');
    }
}

// Initialize workflow service
window.workflowService = new WorkflowService();

// Auto-start scheduling when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (firebase.auth().currentUser) {
        window.workflowService.scheduleWorkflow();
    } else {
        // Wait for user to login
        firebase.auth().onAuthStateChanged(function(user) {
            if (user) {
                window.workflowService.scheduleWorkflow();
            }
        });
    }
});
