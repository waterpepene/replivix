import time
import threading

def run_for(seconds: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            while time.time() - start_time < seconds:
                func(*args, **kwargs)
        return wrapper
    return decorator


@run_for(2)
def print_hello():
    print("Hello")

if __name__ == '__main__':
    print_hello()