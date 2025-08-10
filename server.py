import time
import json
import uuid
import requests
from datetime import datetime
from flask import Flask, Response, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for the React frontend

# In-memory "database" to store traces
# In a real application, this would be a persistent database like Firestore, SQLite, etc.
traces_db = {}

def generate_agent_trace(user_message):
    """
    This generator function simulates an agent's process, yields
    each step, and returns the complete trace.
    """
    session_id = str(uuid.uuid4())
    full_trace = {
        "session_id": session_id,
        "steps": []
    }
    
    # --- Step 1: Initial thought and tool selection ---
    step1 = {
        "timestamp": datetime.now().isoformat(),
        "description": "Initial agent thought and tool selection.",
        "visualization": {
            "type": "box",
            "title": "Agent Start",
            "content": f"User message: {user_message}"
        },
        "session_id": session_id
    }
    yield f"data: {json.dumps(step1)}\n\n"
    full_trace["steps"].append(step1)
    time.sleep(1.5)

    # --- Step 2: Call the LLM ---
    api_key = "AIzaSyAFAqlMu0DMQoxr2wY3T91e7ckcHT-fugk"  # The API key will be provided by the runtime
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json",
    }
    
    # Simulate a user request to the LLM
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"Respond to this message: {user_message}. If the message contains the word 'fail', respond with a specific error message about a tool failure."}]
            }
        ]
    }
    
    step2 = {
        "timestamp": datetime.now().isoformat(),
        "description": "Calling the LLM to generate a response.",
        "visualization": {
            "type": "box",
            "title": "LLM Call",
            "content": "Sending prompt to the Gemini API."
        },
        "session_id": session_id
    }
    yield f"data: {json.dumps(step2)}\n\n"
    full_trace["steps"].append(step2)
    time.sleep(2)

    # --- Step 3: Handle LLM response or simulated error ---
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes
        
        result = response.json()
        llm_response_text = result['candidates'][0]['content']['parts'][0]['text']

        if "fail" in user_message.lower():
            raise ValueError("Simulated tool failure based on user prompt.")

        step3 = {
            "timestamp": datetime.now().isoformat(),
            "description": "Processing LLM response.",
            "visualization": {
                "type": "box",
                "title": "LLM Output",
                "content": llm_response_text
            },
            "session_id": session_id
        }
        yield f"data: {json.dumps(step3)}\n\n"
        full_trace["steps"].append(step3)
        time.sleep(1)

        # --- Step 4: Final response generation (for a successful run) ---
        step4 = {
            "timestamp": datetime.now().isoformat(),
            "description": "Generating final response.",
            "visualization": {
                "type": "box",
                "title": "Final Response",
                "content": f"Agent's final answer: {llm_response_text}"
            },
            "session_id": session_id
        }
        yield f"data: {json.dumps(step4)}\n\n"
        full_trace["steps"].append(step4)

    except (requests.exceptions.RequestException, ValueError) as e:
        # --- Handle error state in the trace ---
        error_message = f"An error occurred: {e}"
        step_error = {
            "timestamp": datetime.now().isoformat(),
            "description": "Agent execution failed.",
            "status": "error",
            "error_message": error_message,
            "visualization": {
                "type": "box",
                "title": "Agent Error",
                "content": error_message
            },
            "session_id": session_id
        }
        yield f"data: {json.dumps(step_error)}\n\n"
        full_trace["steps"].append(step_error)
        
    traces_db[session_id] = full_trace

@app.route('/run_agent_stream', methods=['POST'])
def run_agent_stream():
    """
    API endpoint that streams the agent's trace data in real-time.
    """
    data = request.json
    user_message = data.get('message', 'default message')
    return Response(
        generate_agent_trace(user_message),
        mimetype='text/event-stream'
    )

@app.route('/replay_agent', methods=['POST'])
def replay_agent():
    """
    API endpoint to retrieve a saved trace by its session ID.
    """
    data = request.json
    session_id = data.get('sessionId')

    if session_id in traces_db:
        return jsonify(traces_db[session_id])
    else:
        return jsonify({"error": "Session ID not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)

