import sys
import functools
from datetime import datetime
import socket
from DualOutput import DualOutput


class Logger:
    """
    Logger for capturing and formatting function output.
    """
    def __init__(self, filename, log_as_stdout=False, broadcast_logs=True, port=6000):
        if filename.endswith('.log'):
            self.filename = filename
        else:
            self.filename = f"{filename}.log"
        self.buffer = []
        self.call_stack = []
        self.log_as_stdout = log_as_stdout
        self.broadcast_logs = broadcast_logs
        self.port = port
        self.log_history = []

    def write(self, message):

        if not message.endswith('\n'):
            message = message + "\n"

        file = open(self.filename, "a+")
        file.write(message)
        file.close()

        if self.broadcast_logs:
            self.broadcast_message(message.strip('\n'))
        
        self.log_history.append(message)


    def broadcast_message(self, message):
        # Set up the broadcast socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        broadcast_address = ('<broadcast>', self.port)

        server_socket.sendto(message.encode(), broadcast_address)
        server_socket.close()


    def capture_output(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.call_stack.append(func.__name__)
            indent_level = len(self.call_stack) - 1

            # Log the function call
            args_str = ', '.join(map(str, args))
            kwargs_str = ', '.join(f"{k}={v}" for k, v in kwargs.items())
            header = {
                "Time": f"{datetime.now()}",
                "Message": f"{'    ' * indent_level}{func.__name__}: Args({args_str}), kwargs({kwargs_str})",
                "Level": " - INFO  - ",
            }
            if header in self.buffer:
                self.buffer.remove(header)
            if header not in self.buffer:
                self.buffer.append(header)

            dual_output = DualOutput(
                capture_prefix="    " * (indent_level+1),
                stdout_prefix="    " * (indent_level+1),
                indent_level=indent_level,
                log_as_stdout=self.log_as_stdout,
                logger=self
            )
            old_stdout = sys.stdout
            sys.stdout = dual_output

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                print(f"Captured Error: {e}")
                result = None
            finally:
                sys.stdout = old_stdout
                self.call_stack.pop()

            captured_output = dual_output.getvalue()
            self.buffer += captured_output

            # Write log
            for line in self.buffer:
                if line['Message'].strip() + "\n" not in self.log_history:
                    log_entry = f"{line['Time']}{line['Level']}{line['Message']}"
                    self.write(log_entry + "\n")
                # self.buffer.remove(line)

            # Clear the buffer
            self.buffer = []
            if len(self.call_stack) == 0:
                self.log_history = []

            return result
            self.buffer = []

        return wrapper