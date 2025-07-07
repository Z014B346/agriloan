from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from io import StringIO
import csv
from typing import List

from loan_logic import LoanInput, calculate_amortization_schedule  # Your loan logic module

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/form-result", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    principal: float = Form(...),
    annual_interest_rate: float = Form(...),
    term_years: int = Form(...),
    payments_per_year: int = Form(...),
    interest_only_years: int = Form(0),
    seasonal_months: str = Form("")  # e.g., "3,10"
):
    # Parse seasonal months string to a list of ints
    months = [int(m.strip()) for m in seasonal_months.split(",") if m.strip().isdigit()]

    input_data = LoanInput(
        principal=principal,
        annual_interest_rate=annual_interest_rate,
        term_years=term_years,
        payments_per_year=payments_per_year,
        seasonal_months=months,
        interest_only_years=interest_only_years
    )

    schedule, total_interest, total_paid = calculate_amortization_schedule(input_data)

    # Pass all form data for redisplay & download form
    form_data = {
        "principal": principal,
        "annual_interest_rate": annual_interest_rate,
        "term_years": term_years,
        "payments_per_year": payments_per_year,
        "interest_only_years": interest_only_years,
        "seasonal_months": seasonal_months
    }

    return templates.TemplateResponse("result.html", {
        "request": request,
        "total_interest": total_interest,
        "total_paid": total_paid,
        "schedule": schedule,
        "form_data": form_data
    })


@app.post("/download-csv")
async def download_csv(
    principal: float = Form(...),
    annual_interest_rate: float = Form(...),
    term_years: int = Form(...),
    payments_per_year: int = Form(...),
    interest_only_years: int = Form(0),
    seasonal_months: str = Form("")
):
    months = [int(m.strip()) for m in seasonal_months.split(",") if m.strip().isdigit()]

    input_data = LoanInput(
        principal=principal,
        annual_interest_rate=annual_interest_rate,
        term_years=term_years,
        payments_per_year=payments_per_year,
        seasonal_months=months,
        interest_only_years=interest_only_years
    )

    schedule, _, _ = calculate_amortization_schedule(input_data)

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=schedule[0].model_dump().keys())
    writer.writeheader()
    for row in schedule:
        writer.writerow(row.model_dump())

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=loan_schedule.csv"}
    )

@app.post("/calculate-json")
async def calculate_json(
    principal: float = Form(...),
    annual_interest_rate: float = Form(...),
    term_years: int = Form(...),
    payments_per_year: int = Form(...),
    interest_only_years: int = Form(...),
    seasonal_months: str = Form(...)
):
    months = [int(m.strip()) for m in seasonal_months.split(",") if m.strip().isdigit()]

    input_data = LoanInput(
        principal=principal,
        annual_interest_rate=annual_interest_rate,
        term_years=term_years,
        payments_per_year=payments_per_year,
        seasonal_months=months,
        interest_only_years=interest_only_years
    )

    schedule, total_interest, total_paid = calculate_amortization_schedule(input_data)

    return JSONResponse(content={
        "total_interest": total_interest,
        "total_paid": total_paid,
        "schedule": [row.model_dump() for row in schedule]
    })
