import json
from datetime import datetime

class AgentTracer:
    def __init__(self, save_path="trace_log.json"):
        self.save_path = save_path
        self.trace_data = []
        self.active_trace = None

    def start_trace(self, agent_name):
        self.active_trace = {
            "agent": agent_name,
            "start_time": datetime.utcnow().isoformat(),
            "steps": []
        }
        print(f"[TRACE] Started trace for agent: {agent_name}")

    def log_step(self, step_description, metadata=None):
        if self.active_trace is None:
            raise RuntimeError("No active trace. Call start_trace() first.")
        step = {
            "timestamp": datetime.utcnow().isoformat(),
            "description": step_description,
            "metadata": metadata or {}
        }
        self.active_trace["steps"].append(step)
        print(f"[TRACE] Step logged: {step_description}")

    def end_trace(self):
        if self.active_trace is None:
            raise RuntimeError("No active trace to end.")
        self.active_trace["end_time"] = datetime.utcnow().isoformat()
        self.trace_data.append(self.active_trace)
        with open(self.save_path, "w") as f:
            json.dump(self.trace_data, f, indent=2)
        print(f"[TRACE] Trace ended. Saved to {self.save_path}")
        self.active_trace = None
