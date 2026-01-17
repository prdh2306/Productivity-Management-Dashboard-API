# 🚀 Enterprise Task Management & Productivity API

A high-performance, secure RESTful API designed to streamline personal and team productivity. This system implements industry-standard design patterns, including JWT authentication, asynchronous background workers, and real-time data aggregation.

## 🎯 Project Overview
This project serves as a robust backend solution for task orchestration. It moves beyond simple CRUD operations by incorporating automated task lifecycles (recurring logic) and analytical insights to provide users with actionable productivity metrics.

## 🛠️ Technical Architecture
- **Backend Framework**: Flask (Python 3.x)
- **Database Layer**: SQLite with SQLAlchemy ORM for type-safe database interactions
- **Security**: JWT (JSON Web Tokens) for stateless authentication and Role-Based Access Control (RBAC)
- **Background Processing**: APScheduler for cron-based task automation
- **Standardization**: Strictly follows RESTful architectural constraints for endpoint scalability

## ✨ Key Features
- **Secure RBAC**: Comprehensive user registration and login system with automated Admin-elevation for the primary root user.
- **Advanced Task Engine**: Support for priority queuing, categorical organization, and real-time "Overdue" status computation.
- **Automation Layer**: Background cron jobs that handle Daily and Weekly recurring task clones upon completion.
- **Analytical Dashboard**:
    - **Performance Metrics**: Average lead time from task creation to completion.
    - **Resource Trends**: Statistical analysis of task priority distribution.
    - **Aggregated Summaries**: Real-time completion rates and overdue volume tracking.

## 🚦 Getting Started

### Prerequisites
- Python 3.8+
- Virtual Environment (Recommended)

### Installation & Setup
1. **Initialize Environment**:
 python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
Install Dependencies:
pip install flask flask-sqlalchemy flask-jwt-extended flask-apscheduler
Launch Service:
python file1.py
API 
/registerPOSTRegister a new identity (First user defaults to Admin)
/loginPOSTExchange credentials for a Bearer Token
   
 
