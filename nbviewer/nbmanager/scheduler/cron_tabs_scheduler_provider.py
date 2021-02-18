import os

from crontab import CronTab

from nbviewer.nbmanager.api.scheduler_provider import SchedulerProvider


class CronTabsSchedulerProvider(SchedulerProvider):

    def print_cron(self, code: str):
        pass

    def __init__(self, log: any, user: str = 'root'):
        super().__init__(log)
        self.user = user
        self.cron = CronTab(user=self.user)
        self.cron_runner = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cronner.py')

    def __get_notebook_command(self, nb):
        params = {'cron_runner': self.cron_runner, 'tenant_id': nb['tenant_id'], 'code': nb['code']}
        command = "python3 {cron_runner} {tenant_id} {code}".format(**params)

        return command

    def add_notebook_job(self, notebook):
        command = self.__get_notebook_command(notebook)
        job = self.cron.new(command=command, comment=notebook['code'])
        self.cron.write()

    def add_notebook_jobs(self, notebooks: list):
        remove_list = []
        for job in self.cron:
            remove_list.append(job)
        for job in remove_list:
            self.cron.remove(job)

        for nb in notebooks:
            self.cron.remove_all(comment=nb['code'])

        if notebooks is not None:
            for nb in notebooks:
                command = self.__get_notebook_command(nb)
                # tab = "* * * * * {}".format(command)
                job = self.cron.new(command=command, comment=nb['code'])
                # job.minute.every(2)

        self.cron.write()

    def remove_notebook_job(self, notebook_code: str):
        jobs = self.cron.find_comment(notebook_code)
        self.cron.remove(jobs)
        self.cron.write()

    def get_notebook_jobs(self):
        print('printing cron for {}'.format(self.user))
        for job in self.cron.crons:
            print(job)
        print('printing done!')

    # def update_notebook_job(self, code: str, cron_tab: str):
    #     job = self.cron.find_comment(code)
    #     self.cron.remove(job)
    #     command = self.__get_notebook_command({'code': code, 'cron': cron_tab})
    #     self.cron.append(updated_job)
    #     command = job['command']
