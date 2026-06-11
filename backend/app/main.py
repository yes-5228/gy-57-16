from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.routes import appointments, coaches, dashboard, students
from app.store import seed_data


app = FastAPI(title="Driving School Booking API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for err in exc.errors():
        loc = err.get("loc", [])
        field = loc[-1] if loc else ""
        msg = err.get("msg", "")
        type_ = err.get("type", "")

        custom_msg = ""
        if field == "hours":
            if type_ == "int_parsing":
                custom_msg = "请输入有效的课时数字"
            elif "greater than" in msg:
                custom_msg = "课时数必须大于 0"
            elif "less than or equal" in msg or "le" in type_:
                custom_msg = "课时数不能超过 200，请输入 1-200 之间的数字"
            elif "greater than or equal" in msg or "gt" in type_ or "less than" in msg:
                custom_msg = "课时数必须在 1-200 之间"
            else:
                custom_msg = "课时数必须在 1-200 之间"
        elif field == "remark":
            custom_msg = "备注不能超过 200 字"
        elif field == "name":
            custom_msg = "姓名长度必须在 2-30 个字符之间"
        elif field == "phone":
            custom_msg = "电话号码长度必须在 7-20 个字符之间"
        elif field == "remaining_hours":
            custom_msg = "剩余课时必须在 0-200 之间"
        else:
            custom_msg = msg

        errors.append(custom_msg)

    detail = "；".join(errors) if errors else "参数校验失败"
    return JSONResponse(
        status_code=422,
        content={"detail": detail},
    )


@app.on_event("startup")
def startup() -> None:
    seed_data()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(coaches.router, prefix="/api/coaches", tags=["coaches"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
