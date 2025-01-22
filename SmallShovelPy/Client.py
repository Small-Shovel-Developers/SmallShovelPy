from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import STATE_RUNNING
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz
import time
import pandas as pd
import socket
import threading
import json
import sys
import os
from SmallShovelPy import Pipeline

class Client:
    active_clients = []

    def __init__(self, client_name):
        self.client_name = client_name
        self.client_id = 0
        self.port = 5000
        self.pipelines = {}
        self.schedules = {}
        self.scheduler = BackgroundScheduler()
        self.active_clients = []
        self.client_ports = {}

    def add_pipeline(self, pipeline):
        if pipeline.name in self.pipelines:
            raise ValueError(f"Pipeline with name '{pipeline.name}' already exists.")
        self.pipelines[pipeline.name] = pipeline

    def show_pipelines(self):
        data = {
            "Pipeline Name": [],
            "Trigger Type": [],
            "Schedule Parameters": []
        }
        for s in self.pipelines:
            try:
                for schedict in self.schedules[s]:
                    data['Pipeline Name'].append(s)
                    data['Trigger Type'].append(schedict['trigger_type'])
                    schedule_args = schedict['schedule_args']
                    params = '\n'.join([f'{key}={value}' for key,value in schedule_args.items()])
                    # params += '\n-----------------------'
                    data['Schedule Parameters'].append(params)
            except:
                data['Trigger Type'].append('')
                data['Schedule Parameters'].append('')

        df = pd.DataFrame(data)
        return df.to_markdown(index=False)
    
    def run_pipeline(self, pipeline_name):
        pipeline = self.pipelines[pipeline_name]
        return pipeline.execute()

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
        
        job = self.scheduler.add_job(pipeline.execute, trigger)
        
        if pipeline_name in self.schedules:
            self.schedules[pipeline_name].append({
                "trigger_type": trigger_type,
                "schedule_args": trigger_kwargs,
                "job": job
            })
        else:
            self.schedules[pipeline_name] = [{
                "trigger_type": trigger_type,
                "schedule_args": trigger_kwargs,
                "job": job
            }]

        print(f"Scheduled pipeline '{pipeline_name}' with {trigger_type} trigger.")

    def remove_pipeline(self, pipeline_name):
        if pipeline_name not in self.pipelines:
            print(f"Pipeline '{pipeline_name}' does not exist.")
            return False
        else:
            # Remove the scheduled job if it exists
            if pipeline_name in self.schedules:
                job = self.schedules[pipeline_name].get('job')
                if job:
                    self.scheduler.remove_job(job.id)
                del self.schedules[pipeline_name]

            # Remove the pipeline from my records
            del self.pipelines[pipeline_name]
            print(f"Pipeline '{pipeline_name}' has been removed.")
            return True

    def unschedule_pipeline(self, pipeline_name):
        if pipeline_name not in self.pipelines:
            print(f"Pipeline '{pipeline_name}' does not exist.")
            return False
        else:
            # Remove the scheduled job if it exists
            if pipeline_name in self.schedules:
                job = self.schedules[pipeline_name].get('job')
                if job:
                    self.scheduler.remove_job(job.id)
                del self.schedules[pipeline_name]

            print(f"Pipeline '{pipeline_name}' has been unscheduled.")
            return True

    def start_scheduler(self, independent=False):
        try:
            if self.is_scheduler_running():
                print("Scheduler running, restarting now...")
                self.stop_scheduler()

            self.scheduler.start()

            if independent:
                print("Scheduler running independently. Press Ctrl+C to stop.")
                try:
                    while True:
                        time.sleep(1)
                except (KeyboardInterrupt, SystemExit):
                    print("Shutting down scheduler...")
                    self.stop_scheduler()
        except Exception as e:
            print(f"Error while starting scheduler: {e}")


    def stop_scheduler(self):
        self.scheduler.shutdown()

    def is_scheduler_running(self):
        return self.scheduler.state == STATE_RUNNING

    def __repr__(self):
        repr = f"Client(pipelines={list(self.pipelines.keys())})"
        return repr

    def run(self):
        self.running = True
        scheduler_thread = threading.Thread(target=self.start_scheduler, daemon=True)
        service_thread = threading.Thread(target=self.run_service, daemon=True)
        
        scheduler_thread.start()
        service_thread.start()

        try:
            while self.running:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print("Shutting down client...")
            self.stop()
            scheduler_thread.join()
            service_thread.join()

    def stop(self):
        """Stop the scheduler and service threads cleanly."""
        self.running = False
        self.stop_scheduler()

        # TODO: Send "exit" message to any other running clients

        print(f"Client {self.client_name} has been stopped.")
        sys.exit()

    def send_command(self, host, port, command):
        """Send a command to a specific client."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, port))
                client_socket.sendall(command.encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                return response
        except ConnectionRefusedError:
            return "Unable to connect to the client."
        except Exception as e:
            return f"Error: {e}"

    def run_service(self, host='127.0.0.1'):
        """Starts the client and listens for commands."""
        self.running = True

        # TODO: Find the next available port in the range 5000-5010
        port = 5000
        for i in range(11):
            port += i
            command = "show clients"
            resp = self.send_command(host='127.0.0.1', port=port, command=command)
            try:
                data = json.loads(resp)
                self.active_clients += data
                for client in data:
                    self.client_ports[client['name']] = client['port']
                
            except:
                self.port = port
                if self.client_name in self.client_ports.keys():
                    self.client_name = f"{self.client_name}-{self.port}"
                    print(f"Client of same name was already running. Client name has been updated to: {self.client_name}")

        # Add current instance to client list
        data = {
            "name": self.client_name,
            "id": self.client_id,
            "port": self.port
        }
        self.active_clients.append(data)

        command = f"welcome {json.dumps(data)}"
        for port in self.client_ports:
            self.send_command(host='127.0.0.1', port=port, command=command)

        def handle_client_connection(conn):
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    command = data.decode('utf-8').strip()
                    response = self.handle_command(command)
                    conn.sendall(response.encode('utf-8'))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((host, self.port))
            server_socket.listen()
            print(f"Client {self.client_name} listening on {host}:{self.port}")

            while self.running:
                conn, addr = server_socket.accept()
                threading.Thread(target=handle_client_connection, args=(conn,)).start()

    def handle_command(self, command):
        parts = command.split()
        if not parts:
            return "Invalid command."

        cmd = parts[0].lower()
        if cmd == "welcome" and len(parts) > 1:
            data = dict(parts[1])
            self.active_clients.append(data)

        elif cmd == "show" and len(parts) > 1 and parts[1] == "clients":
            return json.dumps(self.active_clients)

        elif cmd == "show" and len(parts) > 1 and parts[1] == "pipelines":
            return self.show_pipelines() or "No pipelines available."
        
        elif cmd == "run" and len(parts) > 2 and parts[1] == "pipeline":
            pipeline_name = parts[2]
            if pipeline_name in self.pipelines.keys():
                # @TODO: Check for successful pipeline run, adjust output as needed.
                # @TODO: Capture IO output from pipeline to return to user.
                output = self.run_pipeline(pipeline_name)
                return f"Pipeline {pipeline_name} executed. Output: {output}"
            else:
                return f"No pipeline with name {pipeline_name}"
        
        elif cmd == "update" and len(parts) > 2 and parts[1] == "pipeline":
            pipeline_name = parts[2]
            if pipeline_name in self.pipelines.keys():
                pipeline = self.pipelines[pipeline_name]

                if parts[3] == "schedule":
                    if parts[4] == "cron" or parts[4] == "interval":
                        trigger_kwargs = { arg.split('=')[0]: arg.split('=')[1] for arg in parts[5:]}
                        try:
                            self.schedule_pipeline(pipeline_name, parts[4], **trigger_kwargs)
                            return f"Scheduled {pipeline_name}"
                        except:
                            triggers = '\n    - '.join(parts[4:])
                            return f"Unable to schedule {pipeline_name} with triggers:\n{triggers}"

                elif parts[3] == "unschedule":
                    self.unschedule_pipeline(pipeline_name)
                    return f"{pipeline_name} has been unscheduled."
                
                elif parts[3] == "add_task":
                    if parts[4] == "file":
                        file =  ' '.join(parts[5:])
                        if os.path.isfile(file) and file.endswith('.py'):
                            pipeline.add_task(file=file)
                            return f"{pipeline_name} added {file} to tasks"
                        else:
                            return "Invalid file path or file type. Must be an existing Python file."

                    elif parts[4] == "command":
                        # @TODO: 
                        return "This task type is not currently supported."
                    
                    elif parts[4] == "func":
                        function_code =  ' '.join(parts[5:])
                        namespace = {}
                        exec(function_code, namespace)
                        func_name = function_code.split()[1].split("(")[0]
                        namespace[func_name].source_code = function_code
                        if func_name in namespace.keys():
                            return f"Please select a new function name, {func_name} is already in namespace."
                        else:
                            pipeline.add_task(func=namespace[func_name])
                            return f"{pipeline_name} added func {func_name} to tasks"
                    else:
                        return f"Unknown command part: {parts[4]}"
                else:
                    return f"Unknown command part: {parts[3]}"
            else:
                return f"No pipeline with name {pipeline_name}"
        
        elif command.startswith("create pipeline ") and len(parts) > 2:
            pipeline_name = parts[2]
            if pipeline_name in self.pipelines.keys():
                return f"Pipeline with name {pipeline_name} already exists"
            else:
                pipeline = Pipeline(name=pipeline_name)
                self.add_pipeline(pipeline)
                return self.show_pipelines()
        
        elif command.startswith("remove pipeline ") and len(parts) > 2:
            pipeline_name = parts[2]
            if pipeline_name in self.pipelines.keys():
                if self.remove_pipeline(pipeline_name):
                    return f"{pipeline_name} removed from {self.client_name}"
                else:
                    return f"Unable to remove {pipeline_name}"
            else:
                return f"No pipeline with name {pipeline_name}"
        
        elif cmd == "shutdown":
            print("Shutting down client by remote request...")
            self.stop()

        else:
            return "Unknown command."
        

if __name__ == "__main__":

    from Pipeline import Pipeline

    def sample():
        print("Task 1 complete.")
        return "Output of task 1"

    p1 = Pipeline(name="P1")
    p1.add_task(sample)

    client = Client("Client2")
    client.add_pipeline(p1)
    client.schedule_pipeline("P1", "cron", hour=13, minute=2, day_of_week="wed")
    client.run()