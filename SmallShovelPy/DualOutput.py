import sys
import functools
from datetime import datetime
import socket


class DualOutput:
    """
    Custom stream for dual output: real-time printing and buffer capture.
    """
    def __init__(self, capture_prefix="", stdout_prefix="", indent_level=0, log_as_stdout=None, logger=None):
        self.capture_prefix = capture_prefix
        self.stdout_prefix = stdout_prefix
        self.buffer = []
        self.original_stdout = sys.stdout
        self.indent_level = indent_level
        self.log_as_stdout = log_as_stdout
        self.logger = logger

    def write(self, message):
        current_time = f"{datetime.now()}"

        if message.strip():
            if "Captured Error: " in message:
                message = message.replace("Captured Error: ", "")
                level = " - ERROR - "
                prefix = f"{current_time} - ERROR - "
            else:
                prefix = f"{current_time} - INFO  - "
                level = " - INFO  - "

            # Apply indentation for sub-function output
            indent = "    " * self.indent_level
            stdout_message = f"{prefix}{self.stdout_prefix}{indent}{message}"

            capture_message = {
                "Time": current_time,
                "Message": f"{self.capture_prefix}{indent}{message}",
                "Level": level,
            }
            if capture_message['Message'].strip() not in self.logger.log_history:
                self.buffer.append(capture_message)
        else:
            stdout_message = message

        # Print to the real stdout
        if self.log_as_stdout and  stdout_message.strip() not in self.logger.log_history:
            self.original_stdout.write(stdout_message)
        else:
            self.original_stdout.write(message)
            
        self.original_stdout.flush()

    def flush(self):
        self.original_stdout.flush()

    def getvalue(self):
        out = self.buffer
        self.buffer = []
        return out