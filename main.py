from fastapi import FastAPI
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

recruiters = [
    {"id": 1, "name": "Rahul Sharma", "company": "Microsoft", "email": "rahul@microsoft.com"},
    {"id": 2, "name": "Priya Mehta", "company": "Google", "email": "priya@google.com"},
]

@app.get("/recruiters")
def get_recruiters():
    return recruiters

interviews = [
    {"id": 1, "company": "Microsoft", "round": "Interview", "date": "2024-07-15", "status": "Scheduled"},
    {"id": 2, "company": "Google", "round": "Technical Round", "date": "2024-07-20", "status": "Scheduled"},
]

@app.get("/interviews")
def get_interviews():
    return interviews   

tasks = [
    {"id": 1, "task_name": "Prepare for Microsoft interview", "status": "Pending", "due_date": "2024-07-10", "priority": "High"},
    {"id": 2, "task_name": "Follow up with Google recruiter", "status": "Completed", "due_date": "2024-07-15", "priority": "Medium"},
]

@app.get("/tasks")
def get_tasks():
    return tasks

followups = [
    {"id": 1, "company": "Microsoft", "date": "2024-07-12", "notes": "Send thank you email after interview", "status": "Pending","type": "Email"}, 
    {"id": 2, "company": "Google", "date": "2024-07-18", "notes": "Follow up on application status", "status": "Pending","type": "Call"},
] 

@app.get("/followups")
def get_follow_ups():
    return followups

