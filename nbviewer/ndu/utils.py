import json

from nbviewer.nbmanager.database_instance import DatabaseInstance


def get_argument_value(arguments: dict, name, default_value=''):
    if arguments and arguments.get(name, None) is not None:
        values = arguments.get(name)
        value = None
        if len(values) > 0:
            value = values[0]
            if isinstance(value, bytes):
                value = value.decode("utf-8")

        if value is not None:
            if default_value is not None and isinstance(default_value, int):
                value = int(value)
            return value

    return default_value


def extract_cron_obj(arguments: dict) -> str:
    result = {
        'interval_type': get_argument_value(arguments, 'interval_type', None),
        'every_type': get_argument_value(arguments, 'every_type', None),
        'every_interval': get_argument_value(arguments, 'every_interval', None),
        'each_type': get_argument_value(arguments, 'each_type', None),
        'each_time': get_argument_value(arguments, 'each_time', None),
    }

    return json.dumps(result)


def __get_notebook(tenant_id, code):
    notebook = DatabaseInstance.get().get_tenant_notebooks(tenant_id, code)
    return clean_data_for_ui(notebook)


def clean_data_for_ui(item: dict):
    remove_keys = ['path']
    for key in remove_keys:
        if key in item:
            item.pop(key)
    return item
