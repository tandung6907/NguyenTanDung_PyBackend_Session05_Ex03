"""
PHÂN TÍCH VÀ THIẾT KẾ GIẢI PHÁP

1. PHÂN TÍCH BÀI TOÁN
Input API nhận:
    - student_id (int): mã học viên muốn đăng ký
    - course_id (int): mã khóa học muốn đăng ký

Output khi thành công (201 Created):
    - message: thông báo đăng ký thành công
    - data: bản ghi registration vừa được tạo (id, student_id, course_id)

Output khi thất bại (lỗi nghiệp vụ, dùng HTTPException):
    - student_id không tồn tại  -> 404, detail: "Student not found"
    - course_id không tồn tại   -> 404, detail: "Course not found"
    - đăng ký trùng khóa học    -> 400, detail: "Student already registered this course"
    - khóa học đã đủ sĩ số      -> 400, detail: "Course is full"


2. ĐỀ XUẤT GIẢI PHÁP
Hướng xử lý cho API POST /registrations, thực hiện tuần tự theo đúng
thứ tự ưu tiên để đảm bảo thông báo lỗi chính xác với nguyên nhân:

    Bước 1: Kiểm tra student_id có tồn tại trong danh sách students
            không. Nếu không -> raise HTTPException 404 "Student not found".

    Bước 2: Kiểm tra course_id có tồn tại trong danh sách courses
            không. Nếu không -> raise HTTPException 404 "Course not found".

    Bước 3: Kiểm tra trong danh sách registrations đã có bản ghi nào
            có cùng cặp (student_id, course_id) chưa (bẫy 1 - đăng ký
            trùng). Nếu có -> raise HTTPException 400
            "Student already registered this course".

    Bước 4: Đếm số lượng registrations hiện có của course_id, so sánh
            với capacity của khóa học (bẫy 2 - đủ sĩ số). Nếu số lượng
            đã đăng ký >= capacity -> raise HTTPException 400
            "Course is full".

    Bước 5: Nếu qua hết các bước kiểm tra trên mà không có lỗi, tạo
            bản ghi registration mới, thêm vào danh sách registrations,
            trả về status_code=201 Created cùng dữ liệu vừa tạo.

Lý do thứ tự kiểm tra như trên: cần xác thực dữ liệu đầu vào (student,
course có tồn tại hay không) trước khi kiểm tra các quy tắc nghiệp vụ
liên quan (trùng đăng ký, đủ sĩ số), tránh trường hợp báo sai lỗi khi
dữ liệu gửi lên không hợp lệ ngay từ đầu.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

students = [
    {"id": 1, "name": "Nguyen Van A"},
    {"id": 2, "name": "Tran Thi B"},
    {"id": 3, "name": "Le Van C"}
]

courses = [
    {"id": 1, "name": "FastAPI Basic", "capacity": 2},
    {"id": 2, "name": "Python OOP", "capacity": 2}
]

registrations = [
    {"id": 1, "student_id": 1, "course_id": 1},
    {"id": 2, "student_id": 2, "course_id": 1}
]


class RegistrationCreate(BaseModel):
    student_id: int
    course_id: int


@app.post("/registrations", status_code=status.HTTP_201_CREATED)
def create_registration(registration: RegistrationCreate):
    student = next((s for s in students if s["id"] == registration.student_id), None)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    course = next((c for c in courses if c["id"] == registration.course_id), None)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    # Kiểm tra đăng ký trùng khóa học (bẫy 1)
    already_registered = any(
        r["student_id"] == registration.student_id and r["course_id"] == registration.course_id
        for r in registrations
    )
    if already_registered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already registered this course"
        )

    # Kiểm tra khóa học đã đủ sĩ số chưa (bẫy 2)
    current_count = sum(1 for r in registrations if r["course_id"] == registration.course_id)
    if current_count >= course["capacity"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course is full")

    new_registration = {
        "id": len(registrations) + 1,
        "student_id": registration.student_id,
        "course_id": registration.course_id
    }
    registrations.append(new_registration)
    return {
        "message": "Register course successfully",
        "data": new_registration
    }