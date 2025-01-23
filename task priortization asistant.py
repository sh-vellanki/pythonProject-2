import sqlite3
import re
from datetime import datetime
import matplotlib.pyplot as plt


# Database setup
def initialize_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            due_date TEXT,
            priority INTEGER,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    return conn


# NLP-based priority calculation
def calculate_priority(description, due_date):
    priority = 0

    # Keywords for importance
    if any(word in description.lower() for word in ["urgent", "critical", "important"]):
        priority += 2

    # Proximity to deadline
    if due_date:
        days_left = (datetime.strptime(due_date, "%Y-%m-%d") - datetime.now()).days
        if days_left <= 1:
            priority += 3
        elif days_left <= 3:
            priority += 2
        elif days_left <= 7:
            priority += 1

    return priority


# Add a new task
def add_task(conn):
    description = input("Enter task description: ")
    due_date = input("Enter due date (YYYY-MM-DD) or leave blank: ")

    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Task not added.")
            return

    priority = calculate_priority(description, due_date)
    conn.execute("INSERT INTO tasks (description, due_date, priority) VALUES (?, ?, ?)",
                 (description, due_date, priority))
    conn.commit()
    print("Task added successfully!")


# View all tasks
def view_tasks(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE status='Pending' ORDER BY priority DESC, due_date ASC")
    tasks = cursor.fetchall()

    if tasks:
        print("\nYour tasks:")
        for task in tasks:
            print(f"ID: {task[0]}, Description: {task[1]}, Due Date: {task[2]}, Priority: {task[3]}, Status: {task[4]}")
    else:
        print("No tasks found.")


# Mark a task as completed
def complete_task(conn):
    task_id = input("Enter the ID of the task to mark as completed: ")
    conn.execute("UPDATE tasks SET status='Completed' WHERE id=?", (task_id,))
    conn.commit()
    print("Task marked as completed!")


# Visualize tasks
def visualize_tasks(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT description, priority FROM tasks WHERE status='Pending'")
    tasks = cursor.fetchall()

    if tasks:
        descriptions = [task[0] for task in tasks]
        priorities = [task[1] for task in tasks]

        plt.barh(descriptions, priorities, color='skyblue')
        plt.xlabel("Priority")
        plt.ylabel("Tasks")
        plt.title("Task Priority Visualization")
        plt.show()
    else:
        print("No tasks to visualize.")


# Main menu
def main():
    conn = initialize_db()

    while True:
        print("\nTask Prioritization Assistant")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Complete Task")
        print("4. Visualize Tasks")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_task(conn)
        elif choice == "2":
            view_tasks(conn)
        elif choice == "3":
            complete_task(conn)
        elif choice == "4":
            visualize_tasks(conn)
        elif choice == "5":
            print("Exiting... Goodbye!")
            conn.close()
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
