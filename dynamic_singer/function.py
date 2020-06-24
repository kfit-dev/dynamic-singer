import re
import os
import fcntl
import time
import logging

logger = logging.getLogger()


def parse_name(f):
    f = re.sub(r'[ ]+', ' ', f.lower()).strip()
    f = f.replace('-', '_').replace('.', '_').replace(' ', '_')
    return f


def log_subprocess_output(pipe, graceful_shutdown = 30):
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
            if graceful_shutdown > 0:
                logger.error(e)
                time.sleep(graceful_shutdown)
                os._exit(1)
            else:
                raise Exception(error)


def non_block_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.readline()
    except:
        return ''
