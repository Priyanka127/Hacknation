# replay.py
import psycopg2, json

PG_DSN = "dbname=test user=postgres password=postgres host=localhost port=5432"

def load_run(run_id):
    with psycopg2.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT trace FROM agent_runs WHERE run_id=%s", (run_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Run not found")
            return json.loads(row[0])

if __name__ == "__main__":
    run_id = input("Enter run_id to replay: ")
    trace = load_run(run_id)
    for step in trace["steps"]:
        print(step["index"], step["step_type"], step.get("output"), step.get("error"))
