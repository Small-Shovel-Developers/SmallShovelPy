class Pipeline:
    def __init__(self, name):
        self.name = name
        self.tasks = []

    def add_task(self, task):
        # @TODO: Add parameters for a task name and the option to specify a Python file to run and an environment to run it in. Make it to where you must specify at least either task or file but not both.

        if callable(task):
            self.tasks.append(task)
        else:
            raise ValueError("Task must be callable.")

    def execute(self):
        # @TODO: Make execute() able to accept parameters for each task/file in a dictionary, than add any such specified parameters to the arguments when running that task/file. Also add a parameter propogate_params that accepts either a list of task names or a True, and if specified will pass the output of each task in the list to the next task as paramters, or True to do this for every task.
        for task in self.tasks:
            try:
                # @TODO: Add logging
                print()
                task()
            except:
                # @TODO: Add logging
                print()

    def __repr__(self):
        return f"Pipeline(name={self.name}, tasks={len(self.tasks)})"
