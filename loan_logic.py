from typing import List, Tuple
from pydantic import BaseModel
import csv
from io import StringIO

class LoanInput(BaseModel):
    principal: float
    annual_interest_rate: float
    term_years: int
    payments_per_year: int
    seasonal_months: List[int]  # e.g. [3, 10]
    interest_only_years: int

class ScheduleEntry(BaseModel):
    year: int
    month: int
    payment: float
    principal_paid: float
    interest_paid: float
    balance: float

def npf_pmt(rate: float, nper: int, pv: float) -> float:
    if rate == 0:
        return pv / nper
    return rate * pv / (1 - (1 + rate) ** -nper)

def calculate_amortization_schedule(data: LoanInput) -> Tuple[List[ScheduleEntry], float, float]:
    total_months = data.term_years * 12
    payments_per_year = data.payments_per_year
    periodic_interest_rate = data.annual_interest_rate / 100 / payments_per_year


    balance = data.principal
    total_interest = 0.0
    schedule = []

    total_payments = data.term_years * payments_per_year
    interest_only_payments = data.interest_only_years * payments_per_year
    remaining_payments = total_payments - interest_only_payments

    # Calculate payment amount for amortization after interest-only period
    payment_amount = npf_pmt(periodic_interest_rate, remaining_payments, -data.principal) if remaining_payments > 0 else 0
    print(payment_amount)

    payments_made = 0

    for month_index in range(1, total_months + 1):
        year = (month_index - 1) // 12 + 1
        month = (month_index - 1) % 12 + 1

        if month not in data.seasonal_months:
            continue  # Skip months without payments

        payments_made += 1
        interest = -(balance * periodic_interest_rate)

        if payments_made <= interest_only_payments:
            principal_paid = 0.0
            actual_payment = interest
        else:
            principal_paid = payment_amount - interest
            actual_payment = payment_amount

        balance += principal_paid
        total_interest += interest

        schedule.append(ScheduleEntry(
            year=year,
            month=month,
            payment=round(actual_payment, 2),
            principal_paid=round(principal_paid, 2),
            interest_paid=round(interest, 2),
            balance=round(max(balance, 0), 2)
        ))

    total_paid = sum(entry.payment for entry in schedule)
    return schedule, round(abs(total_interest), 2), round(abs(total_paid), 2)


def schedule_to_csv(schedule: List[ScheduleEntry]) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=schedule[0].model_dump().keys())
    writer.writeheader()
    for entry in schedule:
        writer.writerow(entry.model_dump())
    return output.getvalue()
