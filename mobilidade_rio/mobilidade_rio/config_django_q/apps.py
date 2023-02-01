import types
from django.apps import AppConfig
from django.db import connection
from django.utils import timezone


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

    # TODO: opção para que schedules rodem a cada X segundos
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

        # Config schedules

        from django_q.models import Schedule, OrmQ, Task
        from mobilidade_rio.config_django_q import tasks as dq_tasks

        use_schedules = [
            {
                "func": dq_tasks.generate_prediction,
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
            Schedule.objects.update_or_create(**dic)


        # Validate schedules

        # Remove all not in use
        Schedule.objects.exclude(name__in=func_names).delete()
        # remove duplicates
        unique_name = Schedule.objects.values_list('name', flat=True).distinct()
        for name in unique_name:
            for schedule in Schedule.objects.filter(name=name).order_by('-pk')[1:]:
                schedule.delete()
        
        # empty other tables
        OrmQ.objects.all().delete()
        Task.objects.all().delete()
