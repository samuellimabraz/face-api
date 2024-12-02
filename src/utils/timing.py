import time
from functools import wraps
from typing import Any, Callable
from src.utils.logging import logger

def timer(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if hasattr(result, 'inference_time'):
            result.inference_time = execution_time
        
        logger.debug(f"{func.__name__} took {execution_time:.4f} seconds")
        return result
    return wrapper