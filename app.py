from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__)

# Ensure the tasks directory exists
if not os.path.exists('tasks'):
    os.makedirs('tasks')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/todo1')
def todo1():
    active_tasks, completed_tasks = read_tasks('todo1.txt')
    return render_template('todo.html', page_title="Todo List 1", active_tasks=active_tasks, completed_tasks=completed_tasks, page="todo1")

@app.route('/todo2')
def todo2():
    active_tasks, completed_tasks = read_tasks('todo2.txt')
    return render_template('todo.html', page_title="Todo List 2", active_tasks=active_tasks, completed_tasks=completed_tasks, page="todo2")

@app.route('/add_task/<string:page>', methods=['POST'])
def add_task(page):
    task = request.form.get('task')
    if task:
        append_task(f'{page}.txt', task)
    return redirect(url_for(page))

@app.route('/delete_task/<string:page>/<int:task_id>')
def delete_task(page, task_id):
    delete_task_by_id(f'{page}.txt', task_id)
    return redirect(url_for(page))

@app.route('/complete_task/<string:page>/<int:task_id>')
def complete_task(page, task_id):
    mark_task_completed(f'{page}.txt', task_id)
    return redirect(url_for(page))

@app.route('/rearrange_tasks/<string:page>', methods=['POST'])
def rearrange_tasks(page):
    new_order = request.form.getlist('task_order[]')
    rearrange_tasks_order(f'{page}.txt', new_order)
    return redirect(url_for(page))

def read_tasks(filename):
    active_tasks = []
    completed_tasks = []
    try:
        with open(f'tasks/{filename}', 'r') as f:
            for index, line in enumerate(f):
                task_data = line.strip().split('|')
                if len(task_data) == 3:
                    status, timestamp, task = task_data
                    if status == 'active':
                        active_tasks.append((index, task, timestamp))
                    elif status == 'completed':
                        completed_tasks.append((index, task, timestamp))
    except FileNotFoundError:
        pass
    return active_tasks, completed_tasks

def append_task(filename, task):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(f'tasks/{filename}', 'a') as f:
        f.write(f"active|{timestamp}|{task}\n")

def delete_task_by_id(filename, task_id):
    tasks = read_all_tasks(filename)
    if 0 <= task_id < len(tasks):
        del tasks[task_id]
        write_tasks(filename, tasks)

def mark_task_completed(filename, task_id):
    tasks = read_all_tasks(filename)
    if 0 <= task_id < len(tasks):
        status, timestamp, task = tasks[task_id].split('|')
        if status == 'active':
            completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tasks[task_id] = f"completed|{completion_time}|{task}\n"
            write_tasks(filename, tasks)

def rearrange_tasks_order(filename, new_order):
    tasks = read_all_tasks(filename)
    rearranged_tasks = [tasks[int(i)] for i in new_order if 0 <= int(i) < len(tasks)]
    active_tasks = [task for task in tasks if task.startswith('active')]
    completed_tasks = [task for task in tasks if task.startswith('completed')]
    
    # Rearrange only the active tasks
    rearranged_active_tasks = [active_tasks[int(i)] for i in new_order if 0 <= int(i) < len(active_tasks)]
    
    # Combine rearranged active tasks with completed tasks
    final_tasks = rearranged_active_tasks + completed_tasks
    
    write_tasks(filename, final_tasks)

def read_all_tasks(filename):
    try:
        with open(f'tasks/{filename}', 'r') as f:
            return f.readlines()
    except FileNotFoundError:
        return []

def write_tasks(filename, tasks):
    with open(f'tasks/{filename}', 'w') as f:
        f.writelines(tasks)

if __name__ == '__main__':
    app.run(debug=True)