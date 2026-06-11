from datetime import datetime
from fastapi import APIRouter, HTTPException

from app.models import RechargeRecord, Student
from app.schemas import RechargeCreate, RechargeRead, StudentCreate, StudentRead
from app.store import next_id, recharge_records, students

router = APIRouter()


@router.get("", response_model=list[StudentRead])
def list_students() -> list[Student]:
    return list(students.values())


@router.post("", response_model=StudentRead, status_code=201)
def create_student(payload: StudentCreate) -> Student:
    student = Student(id=next_id("student"), **payload.model_dump())
    students[student.id] = student
    return student


@router.post("/{student_id}/recharge", response_model=RechargeRead, status_code=201)
def recharge_student(student_id: int, payload: RechargeCreate) -> RechargeRecord:
    student = students.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    remaining_before = student.remaining_hours
    remaining_after = remaining_before + payload.hours
    student.remaining_hours = remaining_after
    record = RechargeRecord(
        id=next_id("recharge"),
        student_id=student_id,
        hours=payload.hours,
        remaining_before=remaining_before,
        remaining_after=remaining_after,
        remark=payload.remark,
        created_at=datetime.now(),
    )
    recharge_records[record.id] = record
    return record


@router.get("/{student_id}/recharges", response_model=list[RechargeRead])
def list_recharges(student_id: int) -> list[RechargeRecord]:
    if student_id not in students:
        raise HTTPException(status_code=404, detail="学员不存在")
    return [r for r in recharge_records.values() if r.student_id == student_id]
