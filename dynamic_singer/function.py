import re
import os
import fcntl
import time


def parse_name(f):
    f = re.sub(r'[ ]+', ' ', f.lower()).strip()
    f = f.replace('-', '_').replace('.', '_').replace(' ', '_')
    return f


def log_subprocess_output(pipe, time_sleep = 30):
    error = '\n'.join(
        [line.decode().strip() for line in iter(pipe.readline, b'')]
    )
    if len(error):
        print(error)
        if (
            'Traceback ' in error
            or 'During handling of the above exception' in error
            or 'another exception occurred' in error
        ):
            time.sleep(time_sleep)
            raise Exception(error)


def non_block_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.readline()
    except:
        return ''
