from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta
from sqlalchemy import func
import os

app = Flask(__name__)
scheduler = APScheduler()

# --- Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productivity.db'
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.config['SCHEDULER_API_ENABLED'] = True
db = SQLAlchemy(app)
jwt = JWTManager(app)
scheduler.init_app(app)
scheduler.start()

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Pending')
    deadline = db.Column(db.DateTime)
    category = db.Column(db.String(50), default='General')
    is_recurring = db.Column(db.String(20), default='none')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    completed_at = db.Column(db.DateTime)

with app.app_context():
    db.create_all()

# --- Background Worker: Recurring Tasks ---
@scheduler.task('cron', id='recurring_tasks', hour=0)
def handle_recurring():
    with app.app_context():
        tasks = Task.query.filter(Task.is_recurring != 'none', Task.status == 'Completed').all()
        for task in tasks:
            new_deadline = task.deadline + timedelta(days=1 if task.is_recurring == 'daily' else 7)
            new_task = Task(
                title=task.title, description=task.description, priority=task.priority,
                deadline=new_deadline, category=task.category, is_recurring=task.is_recurring,
                user_id=task.user_id
            )
            db.session.add(new_task)
        db.session.commit()

# --- Auth ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    role = 'admin' if User.query.count() == 0 else 'user'
    new_user = User(username=data['username'], password=data['password'], role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"User created as {role}"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        return jsonify(access_token=create_access_token(identity=str(user.id)), role=user.role)
    return jsonify({"message": "Invalid credentials"}), 401

# --- Task Management (CRUD + SEARCH + FILTER) ---
@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    u_id = get_jwt_identity()
    query = Task.query.filter_by(user_id=u_id)
    
    # 🔎 Search & Filter Logic
    if request.args.get('search'):
        s = request.args.get('search')
        query = query.filter((Task.title.contains(s)) | (Task.description.contains(s)))
    if request.args.get('priority'):
        query = query.filter_by(priority=request.args.get('priority'))
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))

    tasks = query.all()
    output = []
    for t in tasks:
        # 🕒 Auto-Overdue Logic
        display_status = t.status
        if t.deadline < datetime.now() and t.status != 'Completed':
            display_status = 'Overdue'
        
        output.append({
            "id": t.id, "title": t.title, "priority": t.priority, 
            "status": display_status, "deadline": t.deadline.strftime('%Y-%m-%d'),
            "category": t.category, "recurring": t.is_recurring
        })
    return jsonify(output)

@app.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    u_id = get_jwt_identity()
    data = request.get_json()
    new_task = Task(
        title=data['title'], description=data.get('description', ''),
        priority=data.get('priority', 'Medium'),
        deadline=datetime.strptime(data['deadline'], '%Y-%m-%d'),
        category=data.get('category', 'General'),
        is_recurring=data.get('recurring', 'none'),
        user_id=u_id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created"}), 201

@app.route('/tasks/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def update_delete_task(id):
    task = Task.query.filter_by(id=id, user_id=get_jwt_identity()).first()
    if not task: return jsonify({"message": "Not found"}), 404
    
    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Deleted"})

    data = request.get_json()
    if 'status' in data:
        task.status = data['status']
        if data['status'] == 'Completed': task.completed_at = datetime.now()
    db.session.commit()
    return jsonify({"message": "Updated"})

# --- Dashboard (Basic + Brownie Analytics) ---
@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    u_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=u_id).all()
    
    total = len(tasks)
    completed = len([t for t in tasks if t.status == 'Completed'])
    overdue = len([t for t in tasks if t.deadline < datetime.now() and t.status != 'Completed'])
    
    # Brownie Points Math
    total_time = sum([(t.completed_at - t.created_at).total_seconds() for t in tasks if t.completed_at])
    avg_hours = (total_time / completed / 3600) if completed > 0 else 0
    common_p = db.session.query(Task.priority, func.count(Task.id)).filter_by(user_id=u_id).group_by(Task.priority).order_by(func.count(Task.id).desc()).first()

    return jsonify({
        "basic": {"total": total, "completed": completed, "overdue": overdue, "rate": f"{round(completed/total*100, 1) if total > 0 else 0}%"},
        "advanced": {"avg_completion_hours": round(avg_hours, 2), "top_priority": common_p[0] if common_p else "N/A"}
    })

if __name__ == '__main__':
    app.run(debug=True)