# written for python2.7
# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import requests
import json
from requests.auth import HTTPBasicAuth

from ansible.plugins.callback import CallbackBase
from ansible import constants as C
from ansible.utils.display import Display
from __main__ import cli
from ansible.utils.color import colorize, hostcolor


try:
    import configparser
except ImportError:
    import ConfigParser as configparser

DOCUMENTATION = '''
    callback: example_callback_plugin
    type: notification
    short_description: Send callback on various runners to an API endpoint.
    description:
      - On ansible runner calls report state and task output to an API endpoint.
      - Configuration via callback_config.ini, place the file in the same directory
        as the plugin.
    requirements:
      - python requests library
      - HTTPBasicAuth library from python requests.auth
      - ConfigParser for reading configuration file
    '''

class CallbackModule(CallbackBase):

    '''
    Callback to API endpoints on ansible runner calls.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'example_callback_plugin'

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__()

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook
        print(playbook.__dict__)

    def v2_playbook_on_play_start(self, play):
        self.play = play
        self.extra_vars = self.play.get_variable_manager().extra_vars
        self.callback_url = self.extra_vars['callback_url']
        self.username = self.extra_vars['username']
        self.password = self.extra_vars['password']

    def v2_runner_on_failed(self, result, ignore_errors=False):
        payload = {'host_name': result._host.name,
                   'task_name': result.task_name,
                   'task_output_message' : result._result['msg']
                  }

        requests.post(self.callback_url,auth=(self.username,self.password),data=payload).json()
        pass


    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        hostDict = {}
        for h in hosts:
            t = stats.summarize(h)
            if t['failures'] > 0:
                hostDict[h] = 'FAILED'
            elif t['unreachable'] > 0:
                hostDict[h] = 'UNREACHABLE'
            else: 
                hostDict[h] = 'SUCCEEDED'
        hostDict = json.dumps(hostDict)
        payload = {'final_output': hostDict,
                   }
        requests.post(self.callback_url,auth=(self.username,self.password),data=payload).json()
        pass
