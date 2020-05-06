import re
import os
import fcntl


def parse_name(f):
    f = re.sub(r'[ ]+', ' ', f.lower()).strip()
    f = f.replace('-', '_').replace('.', '_').replace(' ', '_')
    return f


def log_subprocess_output(pipe):
    error = '\n'.join(
        [line.decode().strip() for line in iter(pipe.readline, b'')]
    )
    if len(error):
        # raise Exception(error)
        print(error)


def non_block_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.readline()
    except:
        return ''
