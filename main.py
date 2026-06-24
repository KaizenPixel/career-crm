from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional


# ----- Allowed values -----

ApplicationStatus = Literal[
    "Applied",
    "Viewed",
    "Under Review",
    "Shortlisted",
    "Interview Scheduled",
    "Selected",
    "Rejected",
]

ActivityType = Literal[
    "notification",
    "status_update",
    "interview_confirmation",
    "task",
    "follow_up",
    "reminder",
]

ActivityStatus = Literal["open", "completed", "cancelled"]
Audience = Literal["candidate", "recruiter", "both", "internal"]
InterviewFormat = Literal["online", "offline"]


# ----- Request models -----

class ApplicationCreate(BaseModel):
    company: str
    role: str
    candidate_id: Optional[int] = None
    job_id: Optional[int] = None


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    note: Optional[str] = None


class InterviewScheduleRequest(BaseModel):
    date: str
    time: str
    format: InterviewFormat
    interviewer: str
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None


class ActivityCreate(BaseModel):
    activity_type: ActivityType = "notification"
    title: str
    message: str
    audience: Audience = "both"
    due_date: Optional[str] = None


class ActivityUpdate(BaseModel):
    status: Optional[ActivityStatus] = None
    message: Optional[str] = None


# ----- App and sample data -----

app = FastAPI(title="Career CRM - Scheduling and Communication Pod")

applications = [
    {
        "id": 1,
        "candidate_id": 101,
        "job_id": 201,
        "company": "Microsoft",
        "role": "SDE Intern",
        "status": "Applied",
        "interview": None,
    },
    {
        "id": 2,
        "candidate_id": 102,
        "job_id": 202,
        "company": "Google",
        "role": "Backend Intern",
        "status": "Shortlisted",
        "interview": None,
    },
]

activities = [
    {
        "id": 1,
        "application_id": 1,
        "activity_type": "notification",
        "title": "Application submitted",
        "message": "Your application for Microsoft has been received.",
        "audience": "candidate",
        "status": "open",
        "due_date": None,
    },
    {
        "id": 2,
        "application_id": 2,
        "activity_type": "status_update",
        "title": "Candidate shortlisted",
        "message": "Google moved this candidate to the shortlisted stage.",
        "audience": "both",
        "status": "open",
        "due_date": None,
    },
]


# ----- Helper functions -----

def get_next_id(records):
    return max((record["id"] for record in records), default=0) + 1


def find_application_or_404(application_id: int):
    for application in applications:
        if application["id"] == application_id:
            return application

    raise HTTPException(status_code=404, detail="Application not found")


def find_activity_or_404(activity_id: int):
    for activity in activities:
        if activity["id"] == activity_id:
            return activity

    raise HTTPException(status_code=404, detail="Activity not found")


def create_activity_record(
    application_id: int,
    activity_type: ActivityType,
    title: str,
    message: str,
    audience: Audience = "both",
    due_date: Optional[str] = None,
    status: ActivityStatus = "open",
):
    activity = {
        "id": get_next_id(activities),
        "application_id": application_id,
        "activity_type": activity_type,
        "title": title,
        "message": message,
        "audience": audience,
        "status": status,
        "due_date": due_date,
    }
    activities.append(activity)
    return activity


def build_interview_record(application, data: InterviewScheduleRequest):
    return {
        "application_id": application["id"],
        "company": application["company"],
        "role": application["role"],
        "date": data.date,
        "time": data.time,
        "format": data.format,
        "interviewer": data.interviewer,
        "location": data.location,
        "meeting_link": data.meeting_link,
        "notes": data.notes,
        "status": "Scheduled",
    }


def is_visible_to_audience(activity, audience: Optional[Audience]):
    if audience is None:
        return True

    if activity["audience"] == "both":
        return audience in ("candidate", "recruiter", "both")

    return activity["audience"] == audience


def filter_activity_records(
    application_id: Optional[int] = None,
    activity_type: Optional[ActivityType] = None,
    activity_status: Optional[ActivityStatus] = None,
    audience: Optional[Audience] = None,
):
    results = activities

    if application_id is not None:
        results = [
            activity
            for activity in results
            if activity["application_id"] == application_id
        ]

    if activity_type is not None:
        results = [
            activity
            for activity in results
            if activity["activity_type"] == activity_type
        ]

    if activity_status is not None:
        results = [
            activity
            for activity in results
            if activity["status"] == activity_status
        ]

    return [
        activity
        for activity in results
        if is_visible_to_audience(activity, audience)
    ]


# ----- Health and compatibility routes -----

@app.get("/")
def home():
    return {
        "message": "Scheduling and Communication pod is running",
        "docs": "/docs",
    }


@app.get("/applications")
def get_legacy_applications():
    return applications


# ----- Application lifecycle routes -----

@app.get("/api/v1/applications")
def get_applications():
    return applications


@app.post("/api/v1/applications")
def create_application(data: ApplicationCreate):
    application = {
        "id": get_next_id(applications),
        "candidate_id": data.candidate_id,
        "job_id": data.job_id,
        "company": data.company,
        "role": data.role,
        "status": "Applied",
        "interview": None,
    }
    applications.append(application)

    activity = create_activity_record(
        application["id"],
        "notification",
        "Application submitted",
        f"Application submitted for {data.company}.",
        "candidate",
    )

    return {"application": application, "activity": activity}


@app.get("/api/v1/applications/{application_id}")
def get_application(application_id: int):
    return find_application_or_404(application_id)


@app.post("/api/v1/applications/{application_id}/status")
def update_application_status(application_id: int, data: ApplicationStatusUpdate):
    application = find_application_or_404(application_id)
    old_status = application["status"]
    application["status"] = data.status

    message = data.note or f"Status changed from {old_status} to {data.status}."
    activity = create_activity_record(
        application_id,
        "status_update",
        "Application status updated",
        message,
        "both",
    )

    return {"application": application, "activity": activity}


# ----- Interview scheduling routes -----

@app.get("/api/v1/interviews")
def get_interviews():
    return [
        application["interview"]
        for application in applications
        if application["interview"]
    ]


@app.get("/api/v1/applications/{application_id}/interview")
def get_application_interview(application_id: int):
    application = find_application_or_404(application_id)

    if application["interview"] is None:
        raise HTTPException(status_code=404, detail="Interview not scheduled")

    return application["interview"]


@app.post("/api/v1/applications/{application_id}/interviews")
def schedule_interview(application_id: int, data: InterviewScheduleRequest):
    application = find_application_or_404(application_id)
    interview = build_interview_record(application, data)

    application["interview"] = interview
    application["status"] = "Interview Scheduled"

    activity = create_activity_record(
        application_id,
        "interview_confirmation",
        "Interview scheduled",
        f"{application['company']} interview scheduled on {data.date} at {data.time}.",
        "both",
    )

    return {"interview": interview, "confirmation": activity}


@app.put("/api/v1/applications/{application_id}/interviews")
def reschedule_interview(application_id: int, data: InterviewScheduleRequest):
    application = find_application_or_404(application_id)

    if application["interview"] is None:
        raise HTTPException(status_code=404, detail="Interview not scheduled")

    interview = build_interview_record(application, data)
    application["interview"] = interview

    activity = create_activity_record(
        application_id,
        "interview_confirmation",
        "Interview rescheduled",
        f"{application['company']} interview moved to {data.date} at {data.time}.",
        "both",
    )

    return {"interview": interview, "confirmation": activity}


@app.post("/api/v1/applications/{application_id}/interviews/cancel")
def cancel_interview(application_id: int):
    application = find_application_or_404(application_id)

    if application["interview"] is None:
        raise HTTPException(status_code=404, detail="Interview not scheduled")

    application["interview"]["status"] = "Cancelled"
    application["status"] = "Under Review"

    activity = create_activity_record(
        application_id,
        "notification",
        "Interview cancelled",
        f"{application['company']} interview has been cancelled.",
        "both",
    )

    return {"application": application, "notification": activity}


# ----- Activity, notification, and action item routes -----

@app.get("/api/v1/applications/{application_id}/activities")
def get_application_activities(application_id: int):
    find_application_or_404(application_id)
    return filter_activity_records(application_id=application_id)


@app.post("/api/v1/applications/{application_id}/activities")
def create_application_activity(application_id: int, data: ActivityCreate):
    find_application_or_404(application_id)
    return create_activity_record(
        application_id,
        data.activity_type,
        data.title,
        data.message,
        data.audience,
        data.due_date,
    )


@app.patch("/api/v1/activities/{activity_id}")
def update_activity(activity_id: int, data: ActivityUpdate):
    activity = find_activity_or_404(activity_id)

    if data.status is not None:
        activity["status"] = data.status

    if data.message is not None:
        activity["message"] = data.message

    return activity


@app.get("/api/v1/activities")
def get_activities(
    application_id: Optional[int] = None,
    activity_type: Optional[ActivityType] = None,
    activity_status: Optional[ActivityStatus] = None,
    audience: Optional[Audience] = None,
):
    return filter_activity_records(
        application_id,
        activity_type,
        activity_status,
        audience,
    )


@app.get("/api/v1/notifications")
def get_notifications(audience: Optional[Audience] = None):
    return [
        activity
        for activity in filter_activity_records(audience=audience)
        if activity["activity_type"] in ("notification", "status_update")
    ]


@app.get("/api/v1/action-items")
def get_action_items(audience: Optional[Audience] = None):
    return [
        activity
        for activity in filter_activity_records(
            activity_status="open",
            audience=audience,
        )
        if activity["activity_type"] in ("task", "follow_up", "reminder")
    ]


@app.post("/api/v1/applications/{application_id}/tasks")
def create_task(application_id: int, data: ActivityCreate):
    find_application_or_404(application_id)
    return create_activity_record(
        application_id,
        "task",
        data.title,
        data.message,
        data.audience,
        data.due_date,
    )


@app.post("/api/v1/applications/{application_id}/follow-ups")
def create_follow_up(application_id: int, data: ActivityCreate):
    find_application_or_404(application_id)
    return create_activity_record(
        application_id,
        "follow_up",
        data.title,
        data.message,
        data.audience,
        data.due_date,
    )

# ----- Calendar / Availability -----

AvailabilityStatus = Literal["available", "confirmed", "cancelled"]

class AvailabilitySlot(BaseModel):
    date: str
    time: str
    format: InterviewFormat
    notes: Optional[str] = None

class ConfirmSlot(BaseModel):
    slot_index: int
    interviewer: str
    meeting_link: Optional[str] = None
    location: Optional[str] = None

availability_slots = {}

@app.post("/api/v1/applications/{application_id}/availability")
def add_availability(application_id: int, data: AvailabilitySlot):
    application = find_application_or_404(application_id)
    if application_id not in availability_slots:
        availability_slots[application_id] = []
    slot = {
        "index": len(availability_slots[application_id]),
        "date": data.date,
        "time": data.time,
        "format": data.format,
        "notes": data.notes,
        "status": "available"
    }
    availability_slots[application_id].append(slot)
    activity = create_activity_record(
        application_id,
        "notification",
        "Availability added",
        f"Candidate added availability slot on {data.date} at {data.time}.",
        "recruiter"
    )
    return {"slot": slot, "activity": activity}

@app.get("/api/v1/applications/{application_id}/availability")
def get_availability(application_id: int):
    find_application_or_404(application_id)
    return availability_slots.get(application_id, [])

@app.post("/api/v1/applications/{application_id}/availability/confirm")
def confirm_slot(application_id: int, data: ConfirmSlot):
    application = find_application_or_404(application_id)
    slots = availability_slots.get(application_id, [])
    if not slots or data.slot_index >= len(slots):
        raise HTTPException(status_code=404, detail="Slot not found")
    slot = slots[data.slot_index]
    slot["status"] = "confirmed"
    interview = {
        "application_id": application_id,
        "company": application["company"],
        "role": application["role"],
        "date": slot["date"],
        "time": slot["time"],
        "format": slot["format"],
        "interviewer": data.interviewer,
        "meeting_link": data.meeting_link,
        "location": data.location,
        "notes": slot["notes"],
        "status": "Scheduled"
    }
    application["interview"] = interview
    application["status"] = "Interview Scheduled"
    activity = create_activity_record(
        application_id,
        "interview_confirmation",
        "Interview confirmed",
        f"Interview confirmed on {slot['date']} at {slot['time']} with {data.interviewer}.",
        "both"
    )
    return {"interview": interview, "confirmation": activity}