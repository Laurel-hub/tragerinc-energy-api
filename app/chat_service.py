from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "google/flan-t5-small"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


def build_customer_prompt(customer_id: str, user_message: str, customer_context: dict) -> str:
    """
    Builds a customer-specific prompt using real usage and billing data.
    This makes the chatbot more dynamic instead of giving generic responses.
    """

    prompt = f"""
You are a helpful customer support assistant for TragerInc, an energy company.

Answer the customer's question using the customer-specific energy and billing data below.

Customer ID: {customer_id}

Customer energy and billing context:
{customer_context}

Customer question:
{user_message}

Instructions:
- Give a clear, friendly and professional response.
- Use the customer's actual data where relevant.
- Explain possible reasons for higher or lower usage or billing.
- Give practical energy-saving advice if appropriate.
- Do not invent numbers that are not in the customer context.
- If the available data is limited, say so politely.

Response:
"""
    return prompt


def generate_llm_response(prompt: str) -> str:
    """
    Sends the final prompt to the FLAN-T5 model and returns the generated response.
    """

    try:
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        outputs = model.generate(
            **inputs,
            max_new_tokens=180,
            do_sample=False
        )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.strip()

    except Exception as e:
        return f"Error generating response: {str(e)}"