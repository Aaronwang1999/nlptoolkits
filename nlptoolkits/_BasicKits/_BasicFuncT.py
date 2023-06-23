import functools
import signal
import socket
import time
import os
import shutil
from urllib.parse import urlparse

"""The lowest level of package"""


def threads_interrupt_initiator():
    """
    Function for multiprocessing.Pool(initializer=threads_interrupt_initiator())
    Each pool process will execute this as part of its initialization.
    Use this to keep safe for multiprocessing...and gracefully interrupt by keyboard
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def check_server(url, timeout: int):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)  # You can adjust timeout as needed
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    except socket.gaierror:
        return False
    finally:
        # close what ever happens
        sock.close()


def timer_wrapper(func):
    """Wrapper for function running timing"""

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        time_start = time.time()
        result = func(*args, **kwargs)
        time_end = time.time()
        time_spend = time_end - time_start
        print('%s cost time: %.5f s' % (func.__name__, time_spend))
        return result

    return decorated


def delete_whole_dir(directory):
    """delete the whole dir..."""
    if os.path.exists(directory) and os.path.isdir(directory):
        shutil.rmtree(directory)


def check_is_list_of_dicts(obj):
    """check is it a list of dict"""

    if not isinstance(obj, list):
        return False

    for element in obj:
        if not isinstance(element, dict):
            return False

    return True