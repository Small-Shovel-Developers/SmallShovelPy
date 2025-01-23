import sys
import functools
from io import StringIO
from datetime import datetime
import time

class DualOutput:
    """
    """
    def __init__(self, capture_prefix="", stdout_prefix=""):
        self.capture_prefix = capture_prefix
        self.stdout_prefix = stdout_prefix
        self.buffer = StringIO()
        self.original_stdout = sys.stdout

    def write(self, message):

        if message == "" or not message.strip():
            stdout_message = message
            capture_message = message
        else:
            if "Captured Error: " in message:
                message = message.replace("Captured Error: ","")
                prefix = f"{datetime.now()} - ERROR - "
            else:
                prefix = f"{datetime.now()} - INFO  - "
            stdout_message = prefix + self.stdout_prefix + message
            capture_message = prefix + self.stdout_prefix + message

        self.original_stdout.write(stdout_message)
        self.original_stdout.flush()
        self.buffer.write(capture_message)

    def flush(self):
        self.original_stdout.flush()

    def getvalue(self):
        return self.buffer.getvalue()


class Logger2:
    """
    """
    
    def __init__(self, filename):
        if filename.endswith('.log'):
            self.filename = filename
        else:
            self.filename = f"{filename}.log"
    
    def write(self, message):
        self.file = open(self.filename, "a+")
        self.file.write(message)
        self.file.close()

    def capture_output(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_ = ', '.join(args)
            kwargs_ = ', '.join(kwargs)
            header = f"{datetime.now()} - INFO  - {func.__name__}: Args({args_}), kwargs({kwargs_})\n"

            dual_output = DualOutput(capture_prefix="    ", stdout_prefix="    ")
            old_stdout = sys.stdout
            sys.stdout = dual_output

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                print(f"Captured Error: {e}")
                result = None
            finally:
                sys.stdout = old_stdout

            captured_output = dual_output.getvalue()
            self.write(header)
            self.write(captured_output)

            return result
        return wrapper