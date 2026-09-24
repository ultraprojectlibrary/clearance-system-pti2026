# clearance-system-pti2026
Development of a clearance system for final year students using PTI as case study for this project.

## About the Project
This project is a Django-based web application that digitizes the final year student clearance process. It streamlines the workflow for students to obtain necessary approvals from various university departments before graduation.

### Key Features
* **Multi-Role User System:** Custom dashboards for Students and Staff (HOD, Entrepreneurship/SUG, Sport Director, Library, Hostel, Student Affairs, Exams and Records).
* **Automated Clearance Workflow:** Students can upload required documents (receipts, results) for review.
* **Progress Tracking:** Students can track the approval status of their documents in real-time across all departments.
* **Digital Approvals:** Staff members can review student documents and approve them digitally.
* **Statement of Results:** Generating and issuing digital statements of results once clearance is completed.
* **Announcements & Reviews:** Integrated communication for sending announcements and review messages.

### Tech Stack
* **Backend:** Python, Django
* **Database:** SQLite (development)
* **Frontend:** HTML, CSS, JavaScript (Django Templates)

---

## IDE INSTALLATION & SETUP FOR CLEARANCE SYSTEM 2026
### STEP 1:
Download Python V3.12.7 from the official website (https://www.python.org/downloads/release/python-3127/) following the installation process carefully. Once it is done, click OK.

### STEP 2: 
Download VS Code from the official website (https://code.visualstudio.com/download) following the installation process carefully. Once it is done, click OK.

### STEP 3:
Open VS Code, click on extensions, search and install the following:
* Live Server
* Django (django-html)
* Python extension
* Django template extension

### STEP 4: 
Open the command prompt on your PC, type or copy this command to install the required packages:

```bash
pip install django pillow django-crispy-forms gunicorn whitenoise virtualenvwrapper-win
```

### Running the Application Locally
1. Clone the repository and navigate into the project directory.
2. Run database migrations: `python manage.py migrate`
3. Start the development server: `python manage.py runserver`
4. Access the application in your browser at `http://127.0.0.1:8000/`.
