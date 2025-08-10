from tracer import AgentTracer
from openai import OpenAI

tracer = AgentTracer()

client = OpenAI()

def run_agent():
    tracer.start_session()
    
    # Log an input
    tracer.record_step("User asks: What's the capital of France?")
    
    # Call the AI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "What's the capital of France?"}]
    )
    
    # Log the output
    tracer.record_step(f"AI responds: {response.choices[0].message.content}")
    
    tracer.end_session()

if __name__ == "__main__":
    run_agent()
