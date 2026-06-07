
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

class Application(BaseModel):
    company: str
    role: str
    status: str

class Recruiter(BaseModel):
    name: str
    company: str
    email: str

class Interview(BaseModel):
    company: str
    round: str
    date: str
    status: str

class Task(BaseModel):
    task_name: str
    status: str
    due_date: str
    priority: str

class FollowUp(BaseModel):
    company: str
    date: str
    notes: str
    status: str
    type: str

class UpdateApplication(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None

app = FastAPI()
@app.get("/")
def home():
    return {"message": "Crm is running!"}   


applications = [
    {"id": 1, "company": "Microsoft", "role": "SDE Intern", "status": "Applied"},
    {"id": 2, "company": "Google", "role": "Backend Intern", "status": "Interview"},
]

@app.get("/applications")
def get_applications():
    return applications

@app.post("/applications")
def add_application(app_data: Application):
    new_application = {
        "id": len(applications) + 1,
        "company": app_data.company,
        "role": app_data.role,
        "status": app_data.status
    }
    applications.append(new_application)
    return new_application

@app.put("/applications/{application_id}")
def update_application(application_id: int, updated_data: UpdateApplication):
    for app in applications:
        if app["id"] == application_id:
            if updated_data.company is not None:
                app["company"] = updated_data.company
            if updated_data.role is not None:
                app["role"] = updated_data.role
            if updated_data.status is not None:
                app["status"] = updated_data.status
            return app
    return {"error": "Application not found"}

@app.delete("/applications/{application_id}")
def delete_application(application_id: int):
    for index, app in enumerate(applications):
        if app["id"] == application_id:
            applications.pop(index)
            return {"message": f"Application {application_id} deleted"}
    return {"error": "Application not found"}

recruiters = [
    {"id": 1, "name": "Rahul Sharma", "company": "Microsoft", "email": "rahul@microsoft.com"},
    {"id": 2, "name": "Priya Mehta", "company": "Google", "email": "priya@google.com"},
]

@app.get("/recruiters")
def get_recruiters():
    return recruiters

@app.post("/recruiters")
def add_recruiter(rec_data: Recruiter):
    new_recruiter = {
        "id": len(recruiters) + 1,
        "name": rec_data.name,
        "company": rec_data.company,
        "email": rec_data.email
    }
    recruiters.append(new_recruiter)
    return new_recruiter

@app.put("/recruiters/{recruiter_id}")
def update_recruiter(recruiter_id: int, updated_data: Recruiter):
    for rec in recruiters:
        if rec["id"] == recruiter_id:
            rec["name"] = updated_data.name
            rec["company"] = updated_data.company
            rec["email"] = updated_data.email
            return rec
    return {"error": "Recruiter not found"}

@app.delete("/recruiters/{recruiter_id}")
def delete_recruiter(recruiter_id: int):
    for index, rec in enumerate(recruiters):
        if rec["id"] == recruiter_id:
            recruiters.pop(index)
            return {"message": f"Recruiter {recruiter_id} deleted"}
    return {"error": "Recruiter not found"}

interviews = [
    {"id": 1, "company": "Microsoft", "round": "Interview", "date": "2024-07-15", "status": "Scheduled"},
    {"id": 2, "company": "Google", "round": "Technical Round", "date": "2024-07-20", "status": "Scheduled"},
]

@app.get("/interviews")
def get_interviews():
    return interviews   

@app.post("/interviews")
def add_interview(interview_data: Interview):
    new_interview = {
        "id": len(interviews) + 1,
        "company": interview_data.company,
        "round": interview_data.round,
        "date": interview_data.date,
        "status": interview_data.status
    }
    interviews.append(new_interview)
    return new_interview

@app.put("/interviews/{interview_id}")
def update_interview(interview_id: int, updated_data: Interview):
    for interview in interviews:
        if interview["id"] == interview_id:
            interview["company"] = updated_data.company
            interview["round"] = updated_data.round
            interview["date"] = updated_data.date
            interview["status"] = updated_data.status
            return interview
    return {"error": "Interview not found"}

@app.delete("/interviews/{interview_id}")
def delete_interview(interview_id: int):
    for index, interview in enumerate(interviews):
        if interview["id"] == interview_id:
            interviews.pop(index)
            return {"message": f"Interview {interview_id} deleted"}
    return {"error": "Interview not found"}

tasks = [
    {"id": 1, "task_name": "Prepare for Microsoft interview", "status": "Pending", "due_date": "2024-07-10", "priority": "High"},
    {"id": 2, "task_name": "Follow up with Google recruiter", "status": "Completed", "due_date": "2024-07-15", "priority": "Medium"},
]

@app.get("/tasks")
def get_tasks():
    return tasks

@app.post("/tasks")
def add_task(task_data: Task):
    new_task = {
        "id": len(tasks) + 1,
        "task_name": task_data.task_name,
        "status": task_data.status,
        "due_date": task_data.due_date,
        "priority": task_data.priority
    }
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_data: Task):
    for task in tasks:
        if task["id"] == task_id:
            task["task_name"] = updated_data.task_name
            task["status"] = updated_data.status
            task["due_date"] = updated_data.due_date
            task["priority"] = updated_data.priority
            return task
    return {"error": "Task not found"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return {"message": f"Task {task_id} deleted"}
    return {"error": "Task not found"}

followups = [
    {"id": 1, "company": "Microsoft", "date": "2024-07-12", "notes": "Send thank you email after interview", "status": "Pending","type": "Email"}, 
    {"id": 2, "company": "Google", "date": "2024-07-18", "notes": "Follow up on application status", "status": "Pending","type": "Call"},
] 

@app.get("/followups")
def get_follow_ups():
    return followups

@app.post("/followups")
def add_follow_up(followup_data: FollowUp):
    new_followup = {
        "id": len(followups) + 1,
        "company": followup_data.company,
        "date": followup_data.date,
        "notes": followup_data.notes,
        "status": followup_data.status,
        "type": followup_data.type
    }
    followups.append(new_followup)
    return new_followup

@app.put("/followups/{followup_id}")
def update_follow_up(followup_id: int, updated_data: FollowUp):
    for followup in followups:
        if followup["id"] == followup_id:
            followup["company"] = updated_data.company
            followup["date"] = updated_data.date
            followup["notes"] = updated_data.notes
            followup["status"] = updated_data.status
            followup["type"] = updated_data.type
            return followup
    return {"error": "Follow-up not found"}

@app.delete("/followups/{followup_id}")
def delete_follow_up(followup_id: int):
    for index, followup in enumerate(followups):
        if followup["id"] == followup_id:
            followups.pop(index)
            return {"message": f"Follow-up {followup_id} deleted"}
    return {"error": "Follow-up not found"}
