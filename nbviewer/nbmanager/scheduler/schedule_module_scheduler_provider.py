import json
import threading
import time

import schedule

from nbviewer.nbmanager.api.scheduler_provider import SchedulerProvider
from nbviewer.nbmanager.scheduler.notebook_runner import notebook_converter_thread


class ScheduleModuleSchedulerProvider(SchedulerProvider):

    def __init__(self, log: any):
        super().__init__(log)
        self.__main_job_runner = JobRunner()
        self.__main_job_runner.start()

    def add_notebook_job(self, notebook):
        self.__main_job_runner.add_job_data(notebook)

    def add_notebook_jobs(self, notebooks):
        for nb in notebooks:
            self.add_notebook_job(nb)

    def remove_notebook_job(self, notebook_code: str):
        self.__main_job_runner.remove_job(notebook_code)

    def get_notebook_jobs(self):
        return self.__main_job_runner.job_list


class JobRunner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.job_list = {}

    def add_job_data(self, notebook: any = {}):
        tenant_id = notebook.get('tenant_id', None)
        code = notebook.get('code', None)
        cron = notebook.get('cron', None)

        if code is None or tenant_id is None:
            return

        if cron is None or cron == '':
            print('Schedule cron definition for: {}'.format(code))
            return
        print('Scheduling notebook code : {}'.format(code))

        try:
            scheduler_instance = None

            cron_def: dict = json.loads(cron)
            interval_type = cron_def.get('interval_type', None)

            if interval_type == 'every':
                interval = cron_def.get('every_interval', None)
                if not isinstance(interval_type, int):
                    interval = int(interval)

                if interval > 0:
                    every_type = cron_def.get('every_type', None)
                    if every_type == 'minutes':
                        scheduler_instance = schedule.every(interval).minutes
                    elif every_type == 'hours':
                        scheduler_instance = schedule.every(interval).hours
                    elif every_type == 'weeks':
                        scheduler_instance = schedule.every(interval).weeks
                    # elif every_type == 'seconds': # USE FOR DEV TESTS ONLY
                    #     scheduler_instance = schedule.every(interval).seconds
            # elif interval_type == 'each':
            #     TODO
            else:
                return

            if scheduler_instance is None:
                return

            scheduler_instance.do(notebook_converter_thread, (notebook,)).tag(code, )
            self.job_list[code] = {
                'schedule': None,
                'cron': cron
            }
        except Exception as e:
            print(e)

    def remove_job(self, code):
        schedule.clear(code)
        del self.job_list[code]

    def run(self):
        while True:
            time.sleep(1)
            schedule.run_pending()
