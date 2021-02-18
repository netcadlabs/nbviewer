import os

from nbviewer.nbmanager.scheduler.cron_tabs_scheduler_provider import CronTabsSchedulerProvider
from nbviewer.nbmanager.scheduler.quartz_scheduler_provider import QuartzSchedulerProvider
from nbviewer.nbmanager.scheduler.schedule_module_scheduler_provider import ScheduleModuleSchedulerProvider


class SchedulerInstance:
    __instance = None

    @staticmethod
    def get(log: any = None) -> 'SchedulerProvider':
        if SchedulerInstance.__instance is None:

            SCHEDULER_TYPE = os.getenv('SCHEDULER_TYPE', 'scheduler')

            if SCHEDULER_TYPE == 'crontab':
                SchedulerInstance.__instance = CronTabsSchedulerProvider(log=log, user=os.getenv('CRON_USERNAME', os.getlogin()))
            elif SCHEDULER_TYPE == 'quartz':
                SchedulerInstance.__instance = QuartzSchedulerProvider(log=log, url=os.getenv('QUARTZ_SERVICE', None))
            elif SCHEDULER_TYPE == 'scheduler':
                SchedulerInstance.__instance = ScheduleModuleSchedulerProvider(log=log)
            else:
                raise ValueError('%s is not known database provider type'.format(SCHEDULER_TYPE))

        return SchedulerInstance.__instance
