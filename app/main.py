# pip install fastapi uvicorn pydantic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.chat_service import (
    generate_llm_response,
    build_customer_prompt
)

from app.data_loader import (
    load_customer_info,
    load_energy_usage,
    load_support_tickets,
    load_chatbot_interactions
)


app = FastAPI(
    title="TragerInc Energy Usage Insights API",
    description="Backend API for energy usage insights, billing explanations, support ticket checks, and chatbot responses.",
    version="1.0.0"
)


class UsageMetrics(BaseModel):
    latest_usage_kwh: float
    average_usage_kwh: float
    average_charge: float
    average_peak_demand_kwh: float


class UsageAnalysis(BaseModel):
    usage_flag: str
    usage_change_percent: float


class CustomerInsightResponse(BaseModel):
    customer_id: str
    metrics: UsageMetrics
    analysis: UsageAnalysis
    insight: str
    recommendation: str
    message: str


class MonthBillingData(BaseModel):
    date: str
    usage_kwh: float
    total_charge: float


class BillingChangeAnalysis(BaseModel):
    usage_change_kwh: float
    usage_change_percent: float
    charge_change: float
    charge_change_percent: float


class BillingExplanationResponse(BaseModel):
    customer_id: str
    previous_month: MonthBillingData
    latest_month: MonthBillingData
    change_analysis: BillingChangeAnalysis
    explanation: str
    message: str


class ChatRequest(BaseModel):
    customer_id: str
    user_message: Optional[str] = None
    message: Optional[str] = None


class ChatResponse(BaseModel):
    customer_id: str
    user_message: str
    ai_response: str


@app.get("/")
def root():
    return {
        "message": "Welcome to the TragerInc Energy Usage Insights API",
        "status": "API is running successfully"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "TragerInc Energy Usage Insights API"
    }


@app.get("/data-summary")
def data_summary():
    customer_df = load_customer_info()
    energy_df = load_energy_usage()
    tickets_df = load_support_tickets()

    return {
        "customers": len(customer_df),
        "energy_usage_records": len(energy_df),
        "support_tickets": len(tickets_df),
        "message": "Data loaded successfully"
    }


@app.get("/customer-insights/{customer_id}", response_model=CustomerInsightResponse)
def customer_insights(customer_id: str):
    energy_df = load_energy_usage()

    customer_energy = energy_df[energy_df["Customer_ID"] == customer_id]

    if customer_energy.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No energy usage records found for customer ID: {customer_id}"
        )

    latest_record = customer_energy.sort_values(by="Date").iloc[-1]

    avg_usage = customer_energy["Usage_kWh"].mean()
    avg_charge = customer_energy["Total_Charge"].mean()
    avg_peak = customer_energy["Peak_Demand_kWh"].mean()

    latest_usage = latest_record["Usage_kWh"]
    usage_change_pct = ((latest_usage - avg_usage) / avg_usage) * 100

    if latest_usage > avg_usage:
        usage_flag = "High usage"
        recommendation = "Your recent energy usage is higher than your average. Consider reducing appliance usage during peak hours."
    else:
        usage_flag = "Normal usage"
        recommendation = "Your energy usage is within your normal range. Keep maintaining efficient usage."

    return {
        "customer_id": customer_id,
        "metrics": {
            "latest_usage_kwh": round(latest_usage, 2),
            "average_usage_kwh": round(avg_usage, 2),
            "average_charge": round(avg_charge, 2),
            "average_peak_demand_kwh": round(avg_peak, 2)
        },
        "analysis": {
            "usage_flag": usage_flag,
            "usage_change_percent": round(usage_change_pct, 2)
        },
        "insight": f"Your recent energy usage is {round(usage_change_pct, 2)}% {'higher' if usage_change_pct > 0 else 'lower'} than your average.",
        "recommendation": recommendation,
        "message": "Customer energy insight generated successfully"
    }


@app.get("/billing-explanation/{customer_id}", response_model=BillingExplanationResponse)
def billing_explanation(customer_id: str):
    energy_df = load_energy_usage()

    customer_energy = energy_df[energy_df["Customer_ID"] == customer_id].sort_values(by="Date")

    if customer_energy.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No energy usage records found for customer ID: {customer_id}"
        )

    if len(customer_energy) < 2:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough historical records to compare billing changes for customer ID: {customer_id}"
        )

    latest = customer_energy.iloc[-1]
    previous = customer_energy.iloc[-2]

    usage_change = latest["Usage_kWh"] - previous["Usage_kWh"]
    charge_change = latest["Total_Charge"] - previous["Total_Charge"]

    usage_change_pct = (usage_change / previous["Usage_kWh"]) * 100
    charge_change_pct = (charge_change / previous["Total_Charge"]) * 100

    if charge_change > 0:
        explanation = (
            f"Your latest bill is higher because your total charge increased by "
            f"{charge_change_pct:.1f}% compared with the previous month. "
            f"Your energy usage also changed by {usage_change_pct:.1f}%."
        )
    elif charge_change < 0:
        explanation = (
            f"Your latest bill is lower because your total charge decreased by "
            f"{abs(charge_change_pct):.1f}% compared with the previous month. "
            f"Your energy usage changed by {usage_change_pct:.1f}%."
        )
    else:
        explanation = (
            "Your latest bill is the same as the previous month. "
            f"Your energy usage changed by {usage_change_pct:.1f}%."
        )

    return {
        "customer_id": customer_id,
        "previous_month": {
            "date": str(previous["Date"].date()),
            "usage_kwh": round(previous["Usage_kWh"], 2),
            "total_charge": round(previous["Total_Charge"], 2)
        },
        "latest_month": {
            "date": str(latest["Date"].date()),
            "usage_kwh": round(latest["Usage_kWh"], 2),
            "total_charge": round(latest["Total_Charge"], 2)
        },
        "change_analysis": {
            "usage_change_kwh": round(usage_change, 2),
            "usage_change_percent": round(usage_change_pct, 2),
            "charge_change": round(charge_change, 2),
            "charge_change_percent": round(charge_change_pct, 2)
        },
        "explanation": explanation,
        "message": "Billing explanation generated successfully"
    }


def get_customer_chat_context(customer_id: str):
    energy_df = load_energy_usage()

    customer_energy = energy_df[energy_df["Customer_ID"] == customer_id].sort_values(by="Date")

    if customer_energy.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No energy usage records found for customer ID: {customer_id}"
        )

    latest_record = customer_energy.iloc[-1]

    avg_usage = customer_energy["Usage_kWh"].mean()
    avg_charge = customer_energy["Total_Charge"].mean()
    avg_peak = customer_energy["Peak_Demand_kWh"].mean()

    latest_usage = latest_record["Usage_kWh"]
    latest_charge = latest_record["Total_Charge"]
    latest_peak = latest_record["Peak_Demand_kWh"]

    usage_change_pct = ((latest_usage - avg_usage) / avg_usage) * 100

    context = {
        "customer_id": customer_id,
        "latest_date": str(latest_record["Date"].date()),
        "latest_usage_kwh": round(latest_usage, 2),
        "average_usage_kwh": round(avg_usage, 2),
        "latest_total_charge": round(latest_charge, 2),
        "average_total_charge": round(avg_charge, 2),
        "latest_peak_demand_kwh": round(latest_peak, 2),
        "average_peak_demand_kwh": round(avg_peak, 2),
        "usage_change_percent_vs_average": round(usage_change_pct, 2)
    }

    if len(customer_energy) >= 2:
        previous_record = customer_energy.iloc[-2]

        usage_change = latest_record["Usage_kWh"] - previous_record["Usage_kWh"]
        charge_change = latest_record["Total_Charge"] - previous_record["Total_Charge"]

        usage_change_pct_monthly = (usage_change / previous_record["Usage_kWh"]) * 100
        charge_change_pct_monthly = (charge_change / previous_record["Total_Charge"]) * 100

        context.update({
            "previous_date": str(previous_record["Date"].date()),
            "previous_usage_kwh": round(previous_record["Usage_kWh"], 2),
            "previous_total_charge": round(previous_record["Total_Charge"], 2),
            "monthly_usage_change_kwh": round(usage_change, 2),
            "monthly_usage_change_percent": round(usage_change_pct_monthly, 2),
            "monthly_charge_change": round(charge_change, 2),
            "monthly_charge_change_percent": round(charge_change_pct_monthly, 2)
        })

    return context


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    user_message = request.user_message or request.message

    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="Please provide a user_message for the chatbot."
        )

    customer_context = get_customer_chat_context(request.customer_id)

    prompt = build_customer_prompt(
        customer_id=request.customer_id,
        user_message=user_message,
        customer_context=customer_context
    )

    ai_response = generate_llm_response(prompt)

    return ChatResponse(
        customer_id=request.customer_id,
        user_message=user_message,
        ai_response=ai_response
    )