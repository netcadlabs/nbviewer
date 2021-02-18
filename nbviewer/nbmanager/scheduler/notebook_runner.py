import asyncio
import threading
from datetime import datetime

from nbviewer.nbmanager.runner import NotebookRunner


def notebook_converter_thread(args=()):
    now = datetime.now()
    print("{} - About to run thread for {}".format(now.strftime("%D %H:%M:%S"), args[0]))
    _thread = threading.Thread(target=notebook_converter_job, args=args)
    _thread.start()
    # _thread = threading.Thread(target=asyncio.run, args=(notebook_converter_job(args),))


def notebook_converter_job(*args):
    notebook = args[0]

    tenant_id = notebook.get('tenant_id', None)
    code = notebook.get('code', None)
    path = notebook.get('path', None)
    timeout = notebook.get('timeout', 5000)

    now = datetime.now()
    print("DEBUG {} - I'm working on {}".format(now.strftime("%D %H:%M:%S"), code))
    runner = NotebookRunner()
    # asyncio.run(runner.run_no_db(notebook))
    asyncio.run(runner.run_w(notebook))
    print("DEBUG {} - I'm done with {}".format(now.strftime("%D %H:%M:%S"), code))
