# pylint: disable=C0415


import logging

from django.apps import AppConfig
from django.db import DatabaseError, connection

logger = logging.getLogger("config_django_q")


def table_exists(table_name):
    """Check if table exists in database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = %s", [table_name])
            return cursor.fetchone()[0] == 1
    except DatabaseError as e:
        return False


class ConfigDjangoQConfig(AppConfig):
    """
    This class is used to add/update/delete schedules

    Features
    ---
        Do:
        - Add if not exists
        - Update if data is different
        - Delete if duplicated, renamed or not in module

        Dont:
        - Don't add if exists with the same data
            - It prevents re-adding the same schedule and increasing pk number every time

    How to use
    ---
    Follow the example in `Config schedules` section:
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mobilidade_rio.config_django_q'

    # custom class to

    def ready(self) -> None:
        """
        This method is called when the app is ready.

        Ignore the warning about `import outside top-level`, it only works here.

        This method won't start until django-q tables are in database, \
            preventing error when using Docker.
        """

        # Dont start until django-q tables are in database
        if not connection.introspection.table_names():
            return

        if not table_exists('django_q_schedule'):
            logger.error("django_q_schedule table not found, cornjob wont be initialized")
            return


        # Config schedules

        from django_q.models import OrmQ, Schedule, Task

        from mobilidade_rio.config_django_q import tasks as dq_tasks

        use_schedules = [
            {
                "func": dq_tasks.generate_prediction_sleep,
                "schedule": Schedule(
                    schedule_type=Schedule.MINUTES,
                    minutes=1,
                    repeats=-1,
                ),
            },
        ]

        # Run schedules

        func_names = []
        for schedule in use_schedules:
            # Create schedule with fields
            dic = schedule["schedule"].__dict__.copy()
            for field in ['_state', 'id']:
                del dic[field]
            if not dic["func"]:
                dic["func"] = f"{schedule['func'].__module__}.{schedule['func'].__name__}"
            if not dic["name"]:
                dic["name"] = dic["func"]
            func_names.append(dic["func"])

            # Add schedule
            Schedule.objects.update_or_create(**dic)  # pylint: disable=E1101


        # Validate schedules

        # Remove all not in use
        Schedule.objects.exclude(name__in=func_names).delete() # pylint: disable=E1101
        # remove duplicates
        unique_name = Schedule.objects.values_list('name', flat=True).distinct() # pylint: disable=E1101
        for name in unique_name:
            for schedule in Schedule.objects.filter(name=name).order_by('-pk')[1:]: # pylint: disable=E1101
                schedule.delete()
        # empty other tables
        OrmQ.objects.all().delete() # pylint: disable=E1101
        Task.objects.all().delete() # pylint: disable=E1101
