class Task:
    def __init__(self, task_id, pick_node, drop_node):
        self.task_id = task_id
        self.pick_node = pick_node
        self.drop_node = drop_node
        self.state = "PENDING" # PENDING, IN_PROGRESS_PICK, IN_PROGRESS_DROP, COMPLETED
