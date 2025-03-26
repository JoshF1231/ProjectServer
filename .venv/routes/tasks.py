from zipfile import error

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from server import mysql
from MySQLdb.cursors import DictCursor  # Import DictCursor

bp = Blueprint('tasks', __name__)

@bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    try:
        current_user = get_jwt_identity()
        cur = mysql.connection.cursor(DictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s", (current_user,))
        user_data = cur.fetchone()
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        cur.execute("SELECT * FROM tasks WHERE user_id = %s", (user_data['id'],))
        tasks = cur.fetchall()
        cur.close()
        if tasks:
            return jsonify(tasks)
        else:
            return jsonify({"message":"No tasks found"}),200
    except Exception as error:
        return jsonify({"error":f"Couldn't find tasks for this user error:{error}"}),500

@bp.route('/tasks', methods=['POST'])
@jwt_required()
def add_task():
    try:
        current_user = get_jwt_identity()
        task_data = request.json
        if not task_data or 'title' not in task_data:
            return jsonify({"error":"Title is required"}),400

        cur = mysql.connection.cursor(DictCursor)

        cur.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        user_data = cur.fetchone()
        if not user_data:
            return jsonify({"error":"User not found"}),404
        user_id = user_data['id']
        cur.execute(
            "INSERT INTO tasks (user_id, title, description, status) VALUES (%s, %s, %s, %s)",
            (user_id, task_data['title'], task_data.get('description', ''), 'pending')
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({"message":"User registered successfully"}),201
    except (error):
        return jsonify({"error":f"Couldn't add task error: {error}"}),500

@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        current_user = get_jwt_identity()
        cur = mysql.connection.cursor(DictCursor)
        cur.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        user_data = cur.fetchone()
        if not user_data:
            return jsonify({"error":"Could not find user"})
        user_id = user_data['id']

        cur.execute("SELECT * FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
        task = cur.fetchone()
        if not task:
            return jsonify({"error": "Task not found or you're not authorized to delete this task"}), 404

        # Delete the task
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message":"Task deleted successfuly"}), 200
    except Exception as error:
        return jsonify({"error":f"Couldn't delete task, error: {error}"}),500

@bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        current_user = get_jwt_identity()
        task_data = request.json
        if not task_data:
            return jsonify({"error":"No data provided for update"}),400
        cur = mysql.connection.cursor(DictCursor)
        cur.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        user_data = cur.fetchone()
        if not user_data:
            return jsonify({"error": "Could not find user"})
        user_id = user_data['id']
        cur.execute("SELECT * FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
        task = cur.fetchone()
        if not task:
            return jsonify({"error": "Task not found or you're not authorized to delete this task"}), 404
        update_data = {
            'title' : task_data.get('title',task['title']),
            'description' : task_data.get('description',task['description']),
            'status' : task_data.get('status',task['status']),
            'due_date' : task_data.get('due_date',task['due_date'])
        }
        cur.execute("""
                    UPDATE tasks
                    SET title = %s, description = %s, status = %s, due_date = %s
                    WHERE id = %s
                    """,(update_data['title'],update_data['description'],update_data['status'],update_data['due_date'],task_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message":"Task successfuly updated"}),200
    except Exception as error:
        return jsonify({"error":f"Could not update task, error:{error}"}),500