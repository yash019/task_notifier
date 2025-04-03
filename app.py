# app.py
from flask import Flask, render_template, request, redirect
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
tasks = {}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "new_task" in request.form:
            task_name = request.form["new_task"].strip()
            property_manager = request.form["property_manager"].strip()
            manager_email = request.form["property_manager_email"].strip()
            property_name = request.form["property_name"].strip()
            emails = request.form.getlist("task_email")
            notes = request.form.get("notes", "").strip()
            date_created = datetime.now().strftime("%Y-%m-%d %H:%M")

            if task_name and emails and task_name not in tasks:
                tasks[task_name] = {
                    "done": False,
                    "emails": emails,
                    "property_manager": property_manager,
                    "manager_email": manager_email,
                    "property_name": property_name,
                    "notes": notes,
                    "date": date_created,
                    "subtasks": []
                }

        elif "task_done" in request.form:
            task = request.form["task_done"]
            extra = request.form.get("extra_info", "")
            tasks[task]["done"] = True
            tasks[task]["notes"] = extra
            recipients = tasks[task]["emails"] + [tasks[task]["manager_email"]]
            for email in recipients:
                send_email(task, email, done=True, extra=extra)

        elif "remind_task" in request.form:
            task = request.form["remind_task"]
            custom_msg = request.form.get("custom_reminder_msg", "")
            task_data = tasks[task]
            note = task_data["notes"]
            subtasks_details = "\n\nSubtasks:\n"
            for st in task_data["subtasks"]:
                subtasks_details += f"- {st['name']} (Status: {st['status']}, Created: {st['date']})\n"
            message = note + "\n" + custom_msg + subtasks_details
            recipients = task_data["emails"] + [task_data["manager_email"]]
            for email in recipients:
                send_email(task, email, done=False, extra=message)

        elif "new_subtask" in request.form:
            parent = request.form["task_parent"]
            subtask_name = request.form["new_subtask"].strip()
            date_created = datetime.now().strftime("%Y-%m-%d %H:%M")
            if subtask_name:
                tasks[parent]["subtasks"].append({"name": subtask_name, "status": "Started", "date": date_created})

        elif "subtask_status" in request.form:
            parent = request.form["task_parent"]
            subtask_name = request.form["subtask_name"]
            new_status = request.form["subtask_status"]
            for st in tasks[parent]["subtasks"]:
                if st["name"] == subtask_name:
                    st["status"] = new_status
                    recipients = tasks[parent]["emails"] + [tasks[parent]["manager_email"]]
                    for email in recipients:
                        send_email(f"Subtask '{subtask_name}' in Task '{parent}'", email, done=False, extra=f"Updated to: {new_status}")
                    break

        elif "edit_subtask_name" in request.form:
            parent = request.form["task_parent"]
            old_name = request.form["edit_subtask_name"]
            new_name = request.form["edited_name"]
            for st in tasks[parent]["subtasks"]:
                if st["name"] == old_name:
                    st["name"] = new_name
                    break

        return redirect("/")

    return render_template("index.html", tasks=tasks)

def send_email(task, recipient, done=False, extra=""):
    sender = "yashbhojwani67@gmail.com"
    password = "xonc mpje dtzu ivsk"
    subject = "Task Completed ✅" if done else "Task Reminder 🔔"
    body = f"{task} is {'completed ✅' if done else 'pending ⏳'}\n"
    if extra:
        body += f"\nAdditional Info:\n{extra}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

if __name__ == "__main__":
    app.run(debug=True)
