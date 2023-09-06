#!/usr/bin/env python
# Tested on Python 3.10.12

'''
CI/Seedy
'''

import sys
import signal
import json
import uuid
import os
import shutil
import base64
import subprocess


# Constants

UNLOCK_CODE = open('/unlock_code.txt', 'r').read().strip()


# Utilities

def pprint(data, endl=b'\n'):
    '''Standardise writes as byte buffers.
    '''
    if type(data) is str:
        data = data.encode('utf-8')
    else:
        data = str(data).encode('utf-8')
    if type(endl) is str:
        endl = endl.encode('utf-8')
    sys.stdout.buffer.write(data + endl)
    sys.stdout.flush()


def readline(prompt=None):
    '''Reads a line from the user with optional prompt.
    '''
    if prompt:
        pprint(prompt, endl=b'')

    data = sys.stdin.readline()
    return data


# Build Functions

def process(data):
    '''Processes input from the user.
    '''
    # Validate the input.
    if not isinstance(data, dict):
        return False, 'data is not a dict'
    lang = data.get('lang', None)
    user_input = data.get('input', None)
    unlock_code = data.get('unlock', None)
    if lang is None or user_input is None:
        return False, 'lang or input is missing'

    # Decode the user data.
    try:
        user_input = base64.b64decode(user_input)
    except:
        return False, "cannot decode base64"


    # Select the processor.
    status, result = False, None
    processors = {
        'c': (process_c, False),
        'java': (process_java, True),
        'python': (process_python, True),
    }
    processor, locked = processors.get(lang, (None, False))
    if locked and unlock_code != UNLOCK_CODE:
        return False, 'please purchase a valid license key'

    # Generate a working directory for the build.
    working_dir = "/tmp/builds/{}".format(str(uuid.uuid4()))
    os.mkdir(working_dir)

    # Run the processor.
    if processor:
        success = processor(user_input, working_dir)
        status, result = True, "{} compile {}".format(lang, "success" if success else "failed")
    else:
        status, result = False, 'unknown language'

    # Clean up the working directory.
    shutil.rmtree(working_dir)

    return status, result

def process_c(user_input, working_dir):
    # Write the user input to main.c
    main_c = "{}/main.c".format(working_dir)
    open(main_c, 'wb').write(user_input)

    # Test if building the file with gcc suceeds.
    code = subprocess.call(["gcc", "-Wl,--fatal-warnings", "-o", "/dev/null", main_c],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    return code == 0

def process_java(user_input, working_dir):
    # Write the user input to main.zip
    main_zip = "{}/main.zip".format(working_dir)
    open(main_zip, 'wb').write(user_input)

    # Unzip the file containing the Java sources.
    code = subprocess.call(["unzip", "-d", working_dir, main_zip],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    if code != 0:
        return False

    # Test if building the file with javac succeeds.
    main_java = "{}/Main.java".format(working_dir)
    classpath = "{}/*".format(working_dir)
    code = subprocess.call(["javac", "-cp", classpath, main_java],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    return code == 0

def process_python(user_input, working_dir):
    # Test if building the Python bytecode succeeds.
    try:
        compile(user_input, 'build.py', 'exec')
        return True
    except:
        return False

def response(status, result):
    return {'status': status, 'result': result}

def main():
    # Setup some limit on how long a player can stay connected.
    # 8 Hours
    seconds = 60 * 60 * 8
    signal.alarm(seconds)

    # Print the banner.
    pprint('CI/Seedy v.0.2.4 - Simple CI/CD for Everyone. API ready.')

    # Start the loop.
    while True:
        line = readline()
        try:
            data = json.loads(line)
            status, result = process(data)
            resp = response(status, result)
        except:
            resp = response(False, 'unable to parse JSON or there was a fatal error')
        pprint(json.dumps(resp))


# Run Main as a Script

if __name__ == '__main__':
    main()
