from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import STATE_RUNNING
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz
import time

class Client:
    def __init__(self):
        self.pipelines = {}
        self.scheduler = BackgroundScheduler()

    def add_pipeline(self, pipeline):
        if pipeline.name in self.pipelines:
            raise ValueError(f"Pipeline with name '{pipeline.name}' already exists.")
        self.pipelines[pipeline.name] = pipeline

    def schedule_pipeline(self, pipeline_name, trigger_type, **trigger_kwargs):
        if pipeline_name not in self.pipelines:
            raise ValueError(f"No pipeline with name '{pipeline_name}' found.")
        
        pipeline = self.pipelines[pipeline_name]

        if trigger_type == "cron":
            trigger = CronTrigger(**trigger_kwargs)
        elif trigger_type == "interval":
            trigger = IntervalTrigger(**trigger_kwargs)
        else:
            raise ValueError("Unsupported trigger type. Use 'cron' or 'interval'.")
        
        self.scheduler.add_job(pipeline.execute, trigger)
        print(f"Scheduled pipeline '{pipeline_name}' with {trigger_type} trigger.")

    def start_scheduler(self, independent=False):
        if self.is_scheduler_running():
            print("Scheduler running, restarting now...")
            self.stop_scheduler()
            self.scheduler.start()
        else:
            self.scheduler.start()

        if independent:
            try:
                while True:
                    time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                self.stop_scheduler()

    def stop_scheduler(self):
        self.scheduler.shutdown()

    def is_scheduler_running(self):
        return self.scheduler.state == STATE_RUNNING

    def __repr__(self):
        repr = f"Client(pipelines={list(self.pipelines.keys())})"
        return repr



"""

NEED:
    - Expand the "add_pipeline" and "schedule_pipeline" methods to save their code/schedule to a database
    - Expand the scheduler to read in this database before running
    - Need server set up to connect the client to the API server and subscribe to commands. Need this 

"""