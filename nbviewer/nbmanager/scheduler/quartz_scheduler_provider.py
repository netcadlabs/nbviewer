from nbviewer.nbmanager.api.scheduler_provider import SchedulerProvider


# TODO - https://www.quartz-scheduler.net/documentation
class QuartzSchedulerProvider(SchedulerProvider):

    def __init__(self, log: any, url: str):
        super().__init__(log)
        self.url = url

    def add_notebook_job(self, notebook):
        pass

    def add_notebook_jobs(self, notebooks):
        pass

    def remove_notebook_job(self, notebook_code: str):
        pass

    def get_notebook_jobs(self):
        pass
