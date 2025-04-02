from flask import Flask, render_template, request, redirect
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
tasks = {}  # {"Task name": {"done": False, "email": "someone@example.com"}}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "new_task" in request.form:
            new_task = request.form["new_task"].strip()
            task_email = request.form["task_email"].strip()
            if new_task and task_email and new_task not in tasks:
                tasks[new_task] = {"done": False, "email": task_email}
        elif "task_done" in request.form:
            task = request.form["task_done"]
            extra = request.form.get("extra_info", "")
            tasks[task]["done"] = True
            send_email(task, tasks[task]["email"], done=True, extra=extra)
        elif "remind_task" in request.form:
            task = request.form["remind_task"]
            send_email(task, tasks[task]["email"], done=False)
        return redirect("/")
    return render_template("index.html", tasks=tasks)

def send_email(task, recipient, done=False, extra=""):
    sender = "yashbhojwani67@gmail.com"
    password = "xonc mpje dtzu ivsk"

    subject = "Task Completed ✅" if done else "Task Reminder 🔔"
    body = f"{task} is {'completed ✅' if done else 'pending ⏳'}.\n"
    if extra and done:
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
