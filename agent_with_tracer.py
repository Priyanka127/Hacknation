import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from tracer import AgentTracer


# --- MOCK TOOLS ---
def lookup_order(order_id):
    # Pretend to lookup order in DB
    return {"order_id": order_id, "status": "shipped", "expected_delivery": "2025-08-20"}

def send_invoice(order_id, email):
    # Pretend to send invoice email
    return {"order_id": order_id, "email": email, "status": "sent"}

# --- MOCK KB RETRIEVAL ---
def retrieve_kb_documents(query):
    # Pretend to retrieve relevant docs from KB
    return [
        {"title": "Return Policy", "content": "You can return items within 30 days."},
        {"title": "Shipping Info", "content": "Orders ship within 2 business days."}
    ]

# --- Main Agent Logic ---
def assistant_agent_run(user_message):
    tracer = AgentTracer()
    tracer.start_trace("OpenAI_Assistant_Email_Chat_Agent")

    tracer.log_step("Received user message", {"message": user_message})

    # Step 1: Retrieve KB docs relevant to user message
    kb_docs = retrieve_kb_documents(user_message)
    tracer.log_step("Retrieved KB documents", {"kb_docs": kb_docs})

    # Step 2: Construct the prompt for the OpenAI API
    # The prompt will include the user's message and the retrieved documents as context.
    system_prompt = "You are a helpful customer service assistant. Use the provided knowledge base documents to answer the user's questions. If the user asks for an order lookup or to send an invoice, use the available tools."

    context = ""
    for doc in kb_docs:
        context += f"### {doc['title']}\n{doc['content']}\n\n"

    prompt = f"{system_prompt}\n\n--- Knowledge Base ---\n{context}\n--- User Message ---\n{user_message}"

    tracer.log_step("Constructed prompt", {"prompt": prompt})

    # Step 3: Call the OpenAI API
    try:
        response = client.completions.create(model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7)
        tracer.log_step("OpenAI API call successful", {"response": response})

        # Step 4: Extract the response text
        assistant_response = response.choices[0].text.strip()
        tracer.log_step("Extracted assistant response", {"assistant_response": assistant_response})

        # Step 5: Check for tool usage (this is a simplified example)
        # In a real-world scenario, you would use function calling
        # or more sophisticated parsing to detect tool usage.
        if "lookup_order" in user_message:
            # Assume we can extract an order ID from the message
            order_id = "12345" # Mocking a hardcoded order ID
            tracer.log_step("Detected tool usage: lookup_order", {"order_id": order_id})
            order_info = lookup_order(order_id)
            tracer.log_step("Tool execution result", {"result": order_info})

            final_response = f"Your order status is: {order_info['status']}. It's expected to be delivered on {order_info['expected_delivery']}."

        elif "send_invoice" in user_message:
            # Assume we can extract an order ID and email from the message
            order_id = "12345"
            email = "user@example.com"
            tracer.log_step("Detected tool usage: send_invoice", {"order_id": order_id, "email": email})
            invoice_status = send_invoice(order_id, email)
            tracer.log_step("Tool execution result", {"result": invoice_status})

            final_response = f"An invoice for order {invoice_status['order_id']} has been sent to {invoice_status['email']}."
        else:
            final_response = assistant_response

        tracer.log_step("Final response", {"response": final_response})
        tracer.end_trace("Trace finished successfully")
        return final_response

    except Exception as e:
        tracer.log_step("OpenAI API call failed", {"error": str(e)})
        tracer.end_trace()
        return "Sorry, I'm having trouble processing your request right now. Please try again later."

# Example usage:
# print(assistant_agent_run("What is your return policy?"))
# print(assistant_agent_run("Where is my order?")) # Simplified to trigger tool

if __name__ == "__main__":
    print("--- Test 1: Asking about return policy ---")
    response1 = assistant_agent_run("What is your return policy?")
    print(f"Assistant: {response1}\n")

    print("--- Test 2: Simulating a request for order lookup ---")
    # This will trigger the mock `lookup_order` tool
    response2 = assistant_agent_run("I need to check the status of my order.")
    print(f"Assistant: {response2}\n")

    print("--- Test 3: Simulating a request to send an invoice ---")
    # This will trigger the mock `send_invoice` tool
    response3 = assistant_agent_run("Can you send me an invoice for my order?")
    print(f"Assistant: {response3}\n")

    print("--- Test 4: A general question not in the KB ---")
    response4 = assistant_agent_run("What is the meaning of life?")
    print(f"Assistant: {response4}\n")