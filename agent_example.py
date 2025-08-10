# agent_example.py
import os
from tracer import Tracer
from decorators import traced_step

PG_DSN = "dbname=test user=postgres password=postgres host=localhost port=5432"

# Fake model & tool for demo
def fake_llm(prompt):
    return f"Echo: {prompt}"

def fake_tool_lookup(order_id):
    return {"order_id": order_id, "status": "shipped"}

def run_agent(user_input):
    tracer = Tracer(PG_DSN, "customer_support_agent", "user_42", {"model": "fake_llm_v1"})

    # Model call
    @traced_step(tracer, "model_call", meta={"model": "fake_llm"})
    def call_model(prompt):
        return fake_llm(prompt)

    # Tool call
    @traced_step(tracer, "tool_call", meta={"tool": "order_lookup"})
    def lookup_order(order_id):
        return fake_tool_lookup(order_id)

    tracer.log_step("user_input", input_data={"text": user_input})

    response = call_model(f"User said: {user_input}")
    order_info = lookup_order("987")

    tracer.log_step("final_response", output_data={"llm": response, "order": order_info})

    tracer.save()
    print("Run saved with ID:", tracer.run.run_id)

if __name__ == "__main__":
    run_agent("Where is my order?")
