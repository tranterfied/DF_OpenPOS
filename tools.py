import json
import config
import os
from datetime import datetime

"""
Here we will define any convenience functions that we may write
"""

def load_settings(file_path='./config.json'):
    # load the file
    f = open('./config.json', 'r')

    # read the text out of the file
    text = ''
    for line in f:
        text += line

    # close the file
    f.close()

    # use the json loader to get what we need
    json_settings = json.loads(text)

    # set the settings
    config.settings = json_settings

# any operations that we want to perform when debugging
def debug_operations():
    os.remove('./pos_db.sqlite')

# function that will perform the logging functionality
def logger(text):
    # if the log file is not open lets open it
    if config.log_file is None:
        f = open('./logs/main_log.txt', 'a+')
        config.log_file = f

    log_text = '[%s]: ' % datetime.now().strftime('%Y-%m-%d-%H:%M:%S.%f')
    log_text += text

    # if it is open then lets write what we meant to
    if config.log_file is not None:
        config.log_file.write(log_text + '\n')

    if config.settings.get('debug', False):
        print log_text