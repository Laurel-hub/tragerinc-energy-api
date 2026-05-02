# TragerInc Energy Usage Insights API

FastAPI backend for customer energy usage insights, billing explanations, and support efficiency.

## Endpoints
- `/`
- `/health`
- `/data-summary`
- `/customer-insights/{customer_id}`
- `/billing-explanation/{customer_id}`

## Run locally
pip install -r requirements.txt
python -m uvicorn app.main:app --reload