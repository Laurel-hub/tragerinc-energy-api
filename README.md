# TragerInc Energy Usage Insights API

## Overview

A production-style FastAPI backend that delivers customer energy usage insights, billing explanations, and data summaries.

This project simulates a real-world energy analytics service, transforming raw usage data into meaningful, actionable insights for both customers and business stakeholders.

---
## Live API
 https://tragerinc-energy-api.onrender.com

Interactive documentation:
https://tragerinc-energy-api.onrender.com/docs

---

## Key Features

* Customer-specific energy usage insights
* Billing explanation with month-over-month comparison
* Usage trend analysis with percentage change calculations
* Structured JSON responses for easy integration
* Robust error handling for missing or invalid data
* Fully deployed and accessible via cloud (Render)

---

## API Endpoints

### 1. Health Check

`GET /health`
Confirms API is running

---

### 2. Data Summary

`GET /data-summary`
Returns dataset overview:

* Number of customers
* Energy usage records
* Support tickets

---

### 3. Customer Insights

`GET /customer-insights/{customer_id}`

Provides:

* Latest vs average energy usage
* Usage classification (e.g. High usage)
* Percentage change analysis
* Personalised recommendations

Example:

```
/customer-insights/CUST000001
```

---

### 4. Billing Explanation

`GET /billing-explanation/{customer_id}`

Provides:

* Previous vs latest billing data
* Usage and charge differences
* Percentage changes
* Human-readable explanation of bill changes

---

## Tech Stack

* FastAPI
* Pandas
* Uvicorn
* Python

---

## Project Structure

```
tragerinc-energy-api/
│
├── app/
│   ├── main.py
│   ├── data_loader.py
│
├── data/
│   ├── tragerinc_customer_info.csv
│   ├── tragerinc_energy_usage.csv
│   ├── tragerinc_support_tickets.csv
│   ├── tragerinc_chatbot_interactions.csv
│
├── requirements.txt
└── README.md
```

---

## Running Locally

1. Clone the repository

```
git clone https://github.com/Laurel-hub/tragerinc-energy-api.git
cd tragerinc-energy-api
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Run the API

```
python -m uvicorn app.main:app --reload
```

4. Open in browser

```
http://127.0.0.1:8000/docs
```

---

## Error Handling

The API returns clear and structured error messages when:

* A customer ID does not exist
* Data is missing
* Invalid requests are made

Example:

```
{
  "detail": "No energy usage records found for customer ID: CUST999999"
}
```

---

## Future Improvements

* Separation of routes, services, and models
* Logging and monitoring
* Authentication and access control
* Frontend dashboard integration
* Automated testing

---

## Author

Oghenevurie Lauretta
MSc Artificial Intelligence | Healthcare-focused Data Analyst

