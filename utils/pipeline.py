# pipeline_config.py
class PipelineConfig:
    def __init__(self, root_dir, input, reporting, storage, cache, workflows):
        self.root_dir = root_dir
        self.input = input
        self.reporting = reporting
        self.storage = storage
        self.cache = cache
        self.workflows = workflows

    def run(self):
        for workflow in self.workflows:
            workflow()