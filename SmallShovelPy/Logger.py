import logging
import datetime
import io
import sys

class Logger:
    """
    A logger class that saves log output to a file with the current datetime and a user defined title.

    ## Arguments:
    - `file`: specified filename
    - `level`: sets the log level for the instance of the class

    ***Log Levels***
    - `DEBUG`: Info for debugging purposes.
    - `INFO`: Confirmation that things are working as expected.
    - `WARNING`: An indication that something unexpected happened.
    - `ERRO`: A more serious problem that could impact the results of the opeation
    - `CRITICAL`: A serious error that results in a stoppage/failure.
    """
    
    def __init__(self, file, level):
        
        now = datetime.datetime.now()
        self.filename = f"{file}_{now.strftime('%Y%m%d_%H%M%S')}.log" 
        self.logger = logging.getLogger(file)
        self.logger.setLevel(level) 

        # Create a file handler
        file_handler = logging.FileHandler(self.filename)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Create a stream handler
        stream_handler = logging.StreamHandler()

        # Add the file handler to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def info(self, message):
        self.logger.info(message)
        
    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
    
    def log_io(self, func, verbose=False):
        """
        Decorator that logs any print statements and other IO within the wrapped function.
        
        ***Decorator Example Usage:***
            @Logger("example_logs", logging.INFO).log_io
        """
        def wrapper(*args, **kwargs):
            # Capture print statements and other IO
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout

            # Run the function and capture any exceptions
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                self.error(e)
                raise  # Re-raise the exception

            finally:
                sys.stdout = old_stdout
                captured_output = new_stdout.getvalue()
                if captured_output:
                    self.info(f"IO output from {func.__name__}: {captured_output}")
                else:
                    self.info(f"No IO output from {func.__name__}")

            return result
        return wrapper