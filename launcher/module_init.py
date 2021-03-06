import subprocess
import threading
import logging
import os
import sys
import config

import web_control
import time
proc_handler = {}


current_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath( os.path.join(current_path, os.pardir))
if root_path not in sys.path:
    sys.path.append(root_path)

def start(module):

    try:
        #config.load()
        if not module in config.config["modules"]:
            logging.error("module not exist %s", module)
            raise

        if module in proc_handler:
            logging.error("module %s is running", module)
            return "module is running"


        #script_path = os.path.abspath( os.path.join(current_path, os.pardir, os.pardir, module, version, 'start.py'))
        #proc_handler[module] = subprocess.Popen([sys.executable, script_path], shell=False)

        if module not in proc_handler:
            proc_handler[module] = {}

            #script_path = os.path.abspath( os.path.join(current_path, os.pardir, module))
            #sys.path.insert(0, script_path)
            proc_handler[module]["imp"] = __import__(module, globals(), locals(), ['local', 'start'], -1)

        _start = proc_handler[module]["imp"].start
        p = threading.Thread(target = _start.main)
        p.daemon = True
        p.start()
        proc_handler[module]["proc"] = p

        while not _start.client.ready:
            time.sleep(0.1)

        logging.info("%s started", module)

    except Exception as e:
        logging.exception("start module %s fail:%s", module, e)
        return "Except:%s" % e
    return "start success."

def stop(module):
    try:
        if not module in proc_handler:
            logging.error("module %s not running", module)
            return

        #proc_handler[module].terminate()  # Sends SIGTERM
        #proc_handler[module].wait()
        _start = proc_handler[module]["imp"].start
        _start.client.config.keep_run = False
        logging.debug("module %s stopping", module)
        while _start.client.ready:
            time.sleep(0.1)

        del proc_handler[module]

        logging.info("module %s stopped", module)
    except Exception as e:
        logging.exception("stop module %s fail:%s", module, e)
        return "Except:%s" % e
    return "stop success."

def start_all_auto():
    #config.load()
    for module in config.config["modules"]:
        if module == "launcher":
            continue
        if "auto_start" in config.config['modules'][module] and config.config['modules'][module]["auto_start"]:
            start_time = time.time()
            start(module)
            #web_control.confirm_module_ready(config.get(["modules", module, "control_port"], 0))
            finished_time = time.time()
            logging.info("start %s time cost %d", module, (finished_time - start_time) * 1000)

def stop_all():
    running_modules = [k for k in proc_handler]
    for module in running_modules:
        stop(module)

