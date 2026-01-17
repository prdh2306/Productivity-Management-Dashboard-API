#  Productivity Management Dashboard API

A professional-grade Backend API built for the GDG Recruitment Challenge. This system manages tasks with real-time analytics, recurring logic, and secure authentication.

## ✨ Features
- **Security**: JWT-based Authentication with Role-Based Access Control (Admin vs. User).
- **Task Management**: Full CRUD operations with Search and Filtering (Priority, Status, Category).
- **Automation**: Background worker (APScheduler) for recurring tasks (Daily/Weekly).
- **Smart Analytics**: 
    - Average task completion time calculation.
    - Automatic overdue task identification.
    - Most common task priority trends.
    - Productivity stats (completed tasks per day).

## 🛠️ Tech Stack
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-JWT-Extended
- **Scheduling**: Flask-APScheduler
- **Standards**: RESTful API Design

## 🏁 How to Run

1. **Setup Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install flask flask-sqlalchemy flask-jwt-extended flask-apscheduler
   📡 API Endpoints
Run Server:
python file1.py
🔐 Auth
POST /register - Create account (First user is Admin)

POST /login - Receive JWT Bearer Token

📝 Tasks (Requires Token)
GET /tasks - Retrieve tasks (Supports ?search=, ?priority=, ?status=)

POST /tasks - Create task (Supports "recurring": "daily")

PUT /tasks/<id> - Update status/details

DELETE /tasks/<id> - Remove task

📊 Analytics
GET /dashboard - Basic summary (Total, Completed, Overdue)

GET /dashboard/advanced - Brownie Point metrics (Avg completion time, trends)

🛡️ Error Handling
The API implements proper HTTP status codes:

201: Created

400: Bad Request / User Exists

401: Unauthorized (Missing/Expired Token)

403: Forbidden (Admin only routes)

404: Not Found