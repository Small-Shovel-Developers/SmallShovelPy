import os
import subprocess
import re

class Pipeline:
    def __init__(self, name):
        self.name = name
        self.tasks = []

    def add_task(self, func=None, file=None, shell=None, command=None):
        '''
        '''

        if func:
            if file:
                raise ValueError("Cannot specify func parameter and file at the same time.")
            elif shell or command:
                raise ValueError("Cannot specify func parameter and shell/command at the same time.")
            elif callable(func):
                self.tasks.append({'task_type': 'func', 'task': func})
            else:
                raise ValueError("Func must be a callable function.")
            
        if file:
            if func:
                raise ValueError("Cannot specify func parameter and file at the same time.")
            elif shell or command:
                raise ValueError("Cannot specify file parameter and shell/command at the same time.")
            if os.path.isfile(file) and file.endswith('.py'):
                self.tasks.append({'task_type': 'file', 'task': file})
            else:
                raise ValueError("Invalid file path or file type. Must be an existing Python file.")
            
        if shell or command:
            if shell and command:
                if func:
                    raise ValueError("Cannot specify func parameter and shell/command at the same time.")
                elif file:
                    raise ValueError("Cannot specify file parameter and shell/command at the same time.")
                else:
                    valid_shells = ['powershell', 'gitbash', 'bash', 'terminal', 'sh', 'cmd', 'command prompt']
                    if shell.lower() not in valid_shells:
                        raise ValueError(f"Unsupported shell type: {shell}. Supported types are: {valid_shells}")
                    
                    self.tasks.append({
                        'task_type': 'shell',
                        'task': {
                            'shell': shell,
                            'command': command
                        }
                    })
            else:
                raise ValueError("Must specify shell type and command to run together.")

    def remove_task(self, task_index):
        '''
        Method that removes a specified task from the `tasks` list
        '''
        try:
            self.tasks.remove(self.tasks[task_index])
        except ValueError:
            print(f"{task_index} is not in the task list")

    def execute(self, params=None):
        '''
        Executes all tasks in the pipeline, passing parameters between tasks if specified.
        '''
        outputs = []
        params = params or [{}]  # Ensure params is a list of dictionaries

        for i, task in enumerate(self.tasks):
            try:
                task_params = {}
                
                # Replace "outputs[n]" in params with actual outputs
                if i < len(params):
                    for key, value in params[i].items():
                        if isinstance(value, str) and value.startswith("outputs[") and value.endswith("]"):

                            pattern1 = r"\[[a-zA-Z0-9]+\]"
                            pattern2 = r"\['[a-zA-Z0-9]+\']"
                            pattern3 = r'\["[a-zA-Z0-9]+\"]'
                            matches = re.findall(pattern1, value)
                            matches += re.findall(pattern2, value)
                            matches += re.findall(pattern3, value)

                            selection = outputs

                            for match in matches:
                                sub_key = match.split('[')[1].split(']')[0]
                                if sub_key.isdigit():
                                    i = int(sub_key)
                                    selection = selection[i]
                                else:
                                    sub_key = sub_key.replace("'","").replace('"',"")
                                    selection = selection[sub_key]
                            task_params[key] = selection
                        else: 
                            task_params[key] = value

                if task['task_type'] == 'func':
                    output = task['task'](**task_params)
                    outputs.append(output)

                elif task['task_type'] == 'file':
                    command = ['python', task['task']]

                    def parse_cli_args(key, value):
                        if value == "":
                            return f"{key}"
                        elif "=" in value:
                            return f"{key}{value}"
                        else:
                            return f"{key} {value}"
                        
                    for key, value in task_params.items():
                        command.append(parse_cli_args(key, value))

                    result = subprocess.run(command, capture_output=True, text=True)
                    output = result.stdout if result.returncode == 0 else result.stderr
                    outputs.append(output)

                elif task['task_type'] == 'shell':
                    command = task['task']['command']

                    def parse_cli_args(key, value):
                        if value == "":
                            return f"{key}"
                        elif "=" in value:
                            return f"{key}{value}"
                        else:
                            return f"{key} {value}"
                    additional_params = " ".join(parse_cli_args(key, value) for key, value in task_params.items())
                    command = f"{command} {additional_params}"

                    shell = task['task']['shell'].lower()
                    if shell.lower() == 'powershell':
                        # Run in PowerShell
                        shell_command = ['powershell', '-Command', command]
                        
                    elif shell.lower() == 'gitbash':
                        # Run in GitBash
                        shell_command = ['bash', '-c', command]
                        
                    elif shell.lower() == 'bash':
                        # Run in GitBash
                        shell_command = ['bash', '-c', command]
                        
                    elif shell.lower() == 'terminal':
                        # Run in Terminal (Unix shell)
                        shell_command = ['sh', '-c', command]
                        
                    elif shell.lower() == 'sh':
                        # Run in Terminal (Unix shell)
                        shell_command = ['sh', '-c', command]

                    elif shell.lower() == 'command prompt':
                        # Run in Command Prompt
                        shell_command = ['cmd', '/c', command]

                    elif shell.lower() == 'cmd':
                        # Run in Command Prompt
                        shell_command = ['cmd', '/c', command]
                    else:
                        return "Error: Unsupported shell type."

                    result = subprocess.run(shell_command, capture_output=True, text=True)
                    output = result.stdout if result.returncode == 0 else result.stderr
                    outputs.append(output)

            except Exception as e:
                outputs.append(f"Task {i + 1} failed with error: {e}")

        return outputs


    def __repr__(self):
        return f"Pipeline(name={self.name}, tasks={len(self.tasks)})"
