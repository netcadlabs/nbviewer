from abc import ABC, abstractmethod


class SchedulerProvider(ABC):

    def __init__(self, log):
        self.log = log

    @abstractmethod
    def add_notebook_job(self, notebook):
        pass

    @abstractmethod
    def add_notebook_jobs(self, notebooks):
        pass

    @abstractmethod
    def remove_notebook_job(self, notebook_code: str):
        pass

    @abstractmethod
    def get_notebook_jobs(self):
        pass
