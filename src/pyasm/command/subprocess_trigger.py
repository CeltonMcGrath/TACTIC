############################################################
#
#    Copyright (c) 2008, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

__all__ = ['SubprocessTrigger', 'QueueTrigger', 'ScriptTrigger']

import tacticenv

import sys
import subprocess
from subprocess import Popen

from pyasm.common import Config, Common, jsonloads, jsondumps
from pyasm.security import Site
from tactic_client_lib import TacticServerStub
from tactic_client_lib.interpreter import Handler

from trigger import Trigger
from command import Command



class SubprocessTrigger(Handler):
    '''Utility class that calls a trigger by external process'''
    def __init__(my):
        my.mode = "same process,new transaction"
        my.info = {}
        super(SubprocessTrigger,my).__init__()

    def set_data(my, data):
        my.data = data
        my.class_name = data.get("class_name")

        # Since the trigger will run separate somewhere else, we do not
        # know if the the workflow should stop of not.  The trigger
        # can define a result in the data
        kwargs = data.get("kwargs")
        if kwargs and kwargs.get("result"):
            my.info['result'] = kwargs.get("result")
        else:
            my.info['result'] = True




    def get_info(my):
        return my.info


    def get_class_name(my):
        return my.class_name

    def set_mode(my, mode):
        my.mode = mode

    def execute(my):
      
        input_data = my.get_input_data()
        data = my.data

        site = Site.get_site()
        if site and not data.get("site"):
            data['site'] = site



        # input data for the handler
        if my.mode == 'separate process,blocking':
            input_data_str = jsondumps(input_data)
            data_str = jsondumps(data)

            file = __file__
            py_exec = Config.get_value("services", "python")
            if not py_exec:
                py_exec = "python"


            retcode = subprocess.call([py_exec, file, data_str, input_data_str])



        elif my.mode == 'separate process,non-blocking':
            input_data_str = jsondumps(input_data)
            data_str = jsondumps(data)

            file = __file__
            py_exec = Config.get_value("services", "python")
            if not py_exec:
                py_exec = "python"

            retcode = subprocess.Popen([py_exec, file, data_str, input_data_str])


        elif my.mode == 'separate process,queued':

            kwargs = data.get("kwargs")
            priority = kwargs.get("priority") or 99999
            description = kwargs.get("description") or "Trigger"
            queue_type = kwargs.get("trigger") or "trigger"

            class_name = "pyasm.command.QueueTrigger"
            kwargs = {
                'input_data': input_data,
                'data': data,
            }

            from tactic.command import Queue
            queue_item = Queue.add(class_name, kwargs, queue_type=queue_type, priority=priority, description=description)


        elif my.mode == 'same process,new transaction':
            # run it inline
            trigger = ScriptTrigger()
            trigger.set_data(data)
            trigger.set_input(input_data)
            trigger.execute()


 
class QueueTrigger(Command):
    '''Simple command which is executed from a queue'''
    def execute(my):

        input_data = my.kwargs.get("input_data")
        data = my.kwargs.get("data")

        trigger = ScriptTrigger()
        trigger.set_input(input_data)
        trigger.set_data(data)

        trigger.execute()




class ScriptTrigger(Handler):
    '''Utility class that calls a trigger by external process'''
    # NOTE: this is not really a trigger'''

    def set_data(my, data):
        my.data = data

    def execute(my):
        #protocol = 'xmlrpc'


        protocol = 'local'
        if protocol == 'local':
            server = TacticServerStub.get()
        else:
            server = TacticServerStub(protocol=protocol,setup=False)
            TacticServerStub.set(server)

            project = my.data.get("project")
            ticket = my.data.get("ticket")
            assert project
            assert ticket
            server.set_server("localhost")
            server.set_project(project)
            server.set_ticket(ticket)

        my.class_name = my.data.get('class_name')
        assert my.class_name
        my.kwargs = my.data.get('kwargs')
        if not my.kwargs:
            my.kwags = {}


        #trigger = eval("%s(**my.kwargs)" % my.class_name)
        trigger = Common.create_from_class_path(my.class_name, kwargs=my.kwargs)

        input_data = my.get_input_data()
        trigger.set_input(input_data)
        trigger.execute()




#
# This main function is called from the SubprocessTrigger class defined in
# this module
#
if __name__ == '__main__':

    executable = sys.argv[0]
    args = sys.argv[1:]

    # load in the passed in data
    data_str = args[0]
    data = jsonloads(data_str)

    site = data.get("site")

    from pyasm.security import Batch
    project = data.get("project")
    assert project
    Batch(project_code=project, site=site)

    input_data_str = args[1]
    input_data = jsonloads(input_data_str)

    trigger = ScriptTrigger()
    trigger.set_data(data)
    trigger.set_input(input_data)
    trigger.execute()
    sys.exit(0)





