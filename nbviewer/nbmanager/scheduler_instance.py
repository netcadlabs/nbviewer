import os

from nbviewer.nbmanager.scheduler.cron_tabs_scheduler_provider import CronTabsSchedulerProvider
from nbviewer.nbmanager.scheduler.quartz_scheduler_provider import QuartzSchedulerProvider


class SchedulerInstance:
    __instance = None

    @staticmethod
    def get(log: any = None) -> 'SchedulerProvider':
        if SchedulerInstance.__instance is None:

            SCHEDULER_TYPE = os.getenv('SCHEDULER_TYPE', 'crontab')

            if SCHEDULER_TYPE == 'crontab':
                username = os.getenv('CRON_USERNAME', None)
                if username is None:
                    username = os.getlogin()
                SchedulerInstance.__instance = CronTabsSchedulerProvider(log=log, user=username)
            elif SCHEDULER_TYPE == 'quartz':
                quartz_service_url = os.getenv('QUARTZ_SERVICE', None)
                SchedulerInstance.__instance = QuartzSchedulerProvider(log=log, url=quartz_service_url)
            else:
                raise ValueError('%s is not known database provider type'.format(SCHEDULER_TYPE))
        return SchedulerInstance.__instance
