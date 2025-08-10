# decorators.py
from functools import wraps

def traced_step(tracer, step_type, meta=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                tracer.log_step(step_type, input_data={"args": args, "kwargs": kwargs}, output_data=result, meta=meta)
                return result
            except Exception as e:
                tracer.log_step(step_type, input_data={"args": args, "kwargs": kwargs}, error=str(e), meta=meta)
                raise
        return wrapper
    return decorator
