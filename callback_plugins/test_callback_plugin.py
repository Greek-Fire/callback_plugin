# written for python2.7
# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import requests
import json
from ansible.plugins.callback import CallbackBase
from ansible import constants as C
from __main__ import cli

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

DOCUMENTATION = '''
    callback: test_callback_plugin
    type: notification
    short_description: Send callback on various runners to an API endpoint.
    description:
      - On ansible runner calls report state and task output to an API endpoint.
      - Configuration via callback_config.ini, place the file in the same directory
        as the plugin.
    requirements:
      - python requests library
    '''

class CallbackModule(CallbackBase):

    '''
    Callback to API endpoints on ansible runner calls.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'test_callback_plugin'

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__()

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook
        print(playbook.__dict__)

    def v2_playbook_on_play_start(self, play):
        self.play = play
        self.extra_vars = self.play.get_variable_manager().extra_vars
        self.callback_url = self.extra_vars['callback_url']

    def v2_runner_on_failed(self, result, ignore_errors=False):
        ### change payload
        payload = {'host_name': result._host.name,
                   'task_name': result.task_name,
                   'task_output_message' : result._result['msg']
                  }

        requests.post(self.callback_url),data=payload).json()
        pass

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        host_dict = {}
        for h in hosts:
            t = stats.summarize(h)
            if t['failures'] > 0:
                host_dict[h] = 'Fail'
            elif t['unreachable'] > 0:
                host_dict[h] = 'Unreachable'
            else: 
                host_dict[h] = 'Success'
        host_dict = json.dumps(host_dict)
        
        ### change paylod
        payload = {'final_output': host_dict,
                   }
        requests.post(self.callback_url),data=payload).json()
        pass
