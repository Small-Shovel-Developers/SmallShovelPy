<h1 style="text-align: center;">SmallShovelPy</h1>

# Installation
```bash
pip install git+https://github.com/Small-Shovel-Developers/SmallShovelPy.git
```

# Usage
lol wut

# Classes
## 1. Pipeline
The Pipeline class represents a sequence of tasks that can be executed as a unit. Pipelines are used to group related code blocks and define their execution order.

The Pipeline class constructor can be called by providing the pipeline name, as in the following example:

```python
from SmallShovelPy import Pipeline

# Create a pipeline
pipeline = Pipeline(name="Data Processing Pipeline")
```

Currently, the class supports the following methods:

- ***Pipeline().add_task()*** \  
    Adds a task (callable) to the pipeline. \  

    **Parameters**:
    - `task`: [ callable ]
      The callable (function or object) to add to the pipeline.

    **Returns**:
    - None

    **Examples**:
    ```python
    def clean_data():
        print("Data cleaned.")

    pipeline.add_task(clean_data)
    ```

- ***Pipeline().execute()*** \  
    Executes all tasks in the pipeline sequentially. \  

    **Parameters**:
    - None

    **Returns**:
    - None

    **Examples**:
    ```python
    pipeline.execute()
    # Output: Data cleaned.
    ```

## 2. Client
The Client class manages multiple pipelines and schedules them for execution using various triggers. The Client provides a unified interface to add pipelines, manage schedules, and monitor execution.

The Client class constructor can be called without any parameters:

```python
from SmallShovelPy import Client

# Create a client instance
client = Client()
```

Currently, the class supports the following methods:

- ***Client().add_pipeline()*** \  
    Adds a pipeline to the client’s collection. \  

    **Parameters**:
    - `pipeline`: [ Pipeline ]
      The Pipeline object to add to the client.

    **Returns**:
    - None

    **Examples**:
    ```python
    client.add_pipeline(pipeline)
    ```

- ***Client().schedule_pipeline()*** \  
    Schedules a pipeline for execution using a specified trigger. \  

    **Parameters**:
    - `pipeline_name`: [ str ]
      The name of the pipeline to schedule.
    - `trigger_type`: [ str ]
      The type of trigger to use ("cron" or "interval").
    - For cron triggers:
        - `year`: [ int | str ]
        Specific year(s) to trigger.
        - `month`: [ int | str ]
        Specific month(s) to trigger (1-12 or names).
        - `day`: [ int | str ]
        Specific day(s) of the month to trigger (1-31).
        - `day_of_week`: [ int | str ]
        Specific day(s) of the week to trigger (e.g., "mon", "tue").
        - `hour`: [ int | str ]
        Specific hour(s) to trigger (0-23).
        - `minute`: [ int | str ]
        Specific minute(s) to trigger (0-59).
        - `second`: [ int | str ]
        Specific second(s) to trigger (0-59).
        - `timezone`: [ pytz.timezone ]
        The timezone for the schedule.

    - For interval triggers:
        - `weeks`: [ int ]
        Interval in weeks.
        - `days`: [ int ]
        Interval in days.
        - `hours`: [ int ]
        Interval in hours.
        - `minutes`: [ int ]
        Interval in minutes.
        - `seconds`: [ int ]
        Interval in seconds.
        - `start_date`: [ datetime | str ]
        The start date/time for the interval.
        - `end_date`: [ datetime | str ]
        The end date/time for the interval.

    **Returns**:
    - None

    **Examples**:
    ```python
    # Schedule a pipeline to run at 6:30 AM on weekdays (Monday-Friday)
    client.schedule_pipeline("Data Processing Pipeline", "cron", hour=6, minute=30, day_of_week="mon-fri")

    # Schedule a pipeline to run every 2 days starting now
    client.schedule_pipeline("Data Processing Pipeline", "interval", days=2, start_date="2025-01-01 00:00:00")
    ```

- ***Client().start_scheduler()*** \  
    Starts the scheduler to enable pipeline execution. \  

    **Parameters**:
    - `independent`: [ bool ] - *default: False*
      Determines whethers or not to keep the parent script active independent of the `.run()` method.

    **Returns**:
    - None

    **Examples**:
    ```python
    client.start_scheduler()
    ```

- ***Client().stop_scheduler()*** \  
    Stops the scheduler and halts all scheduled jobs. \  

    **Parameters**:
    - None

    **Returns**:
    - None

    **Examples**:
    ```python
    client.stop_scheduler()
    ```

- ***Client().is_scheduler_running()*** \  
    Checks if the scheduler is currently running. \  

    **Parameters**:
    - None

    **Returns**:
    - [ bool ] - True if the scheduler is running, False otherwise.

    **Examples**:
    ```python
    if client.is_scheduler_running():
        print("Scheduler is active.")
    ```

