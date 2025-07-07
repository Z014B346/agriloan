from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from loan_logic import LoanInput, calculate_amortization_schedule

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# For JSON input
class LoanRequest(BaseModel):
    principal: float
    annual_interest_rate: float
    term_years: int
    payments_per_year: int
    interest_only_years: int
    seasonal_months: List[int]

# JSON endpoint
@app.post("/calculate-json")
async def calculate_loan_json(data: LoanRequest):
    input_data = LoanInput(
        principal=data.principal,
        annual_interest_rate=data.annual_interest_rate,
        term_years=data.term_years,
        payments_per_year=data.payments_per_year,
        interest_only_years=data.interest_only_years,
        seasonal_months=data.seasonal_months
    )

    schedule, total_interest, total_paid = calculate_amortization_schedule(input_data)

    return JSONResponse({
        "total_interest": total_interest,
        "total_paid": total_paid,
        "schedule": [entry.model_dump() for entry in schedule]
    })

# HTML form page
@app.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# HTML result page for form-data
@app.post("/form-result", response_class=HTMLResponse)
async def form_result(
    request: Request,
    principal: float = Form(...),
    annual_interest_rate: float = Form(...),
    term_years: int = Form(...),
    payments_per_year: int = Form(...),
    interest_only_years: int = Form(...),
    seasonal_months: str = Form(...),  # input like "3,10"
):
    seasonal_months_list = [int(m.strip()) for m in seasonal_months.split(",") if m.strip().isdigit()]
    input_data = LoanInput(
        principal=principal,
        annual_interest_rate=annual_interest_rate,
        term_years=term_years,
        payments_per_year=payments_per_year,
        interest_only_years=interest_only_years,
        seasonal_months=seasonal_months_list
    )

    schedule, total_interest, total_paid = calculate_amortization_schedule(input_data)

    return templates.TemplateResponse("results.html", {
        "request": request,
        "schedule": schedule,
        "total_interest": total_interest,
        "total_paid": total_paid,
        "form_data": {
            "principal": principal,
            "annual_interest_rate": annual_interest_rate,
            "term_years": term_years,
            "payments_per_year": payments_per_year,
            "interest_only_years": interest_only_years,
            "seasonal_months": seasonal_months
        }
    })

# CSV download
from fastapi.responses import StreamingResponse
import csv
from io import StringIO

@app.post("/download-csv")
async def download_csv(
    principal: float = Form(...),
    annual_interest_rate: float = Form(...),
    term_years: int = Form(...),
    payments_per_year: int = Form(...),
    interest_only_years: int = Form(...),
    seasonal_months: str = Form(...)
):
    seasonal_months_list = [int(m.strip()) for m in seasonal_months.split(",") if m.strip().isdigit()]
    input_data = LoanInput(
        principal=principal,
        annual_interest_rate=annual_interest_rate,
        term_years=term_years,
        payments_per_year=payments_per_year,
        interest_only_years=interest_only_years,
        seasonal_months=seasonal_months_list
    )

    schedule, _, _ = calculate_amortization_schedule(input_data)

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Year", "Month", "Payment", "Principal Paid", "Interest Paid", "Balance"])

    for entry in schedule:
        writer.writerow([
            entry.year,
            entry.month,
            entry.payment,
            entry.principal_paid,
            entry.interest_paid,
            entry.balance
        ])

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=amortization_schedule.csv"})
