import re


def parse_name(f):
    if '--config' in f:
        f = f.split('--config')[0]
    elif '-c' in f:
        f = f.split('-c')[0]
    f = re.sub(r'[ ]+', ' ', f.lower()).strip()
    f = f.replace('-', '_').replace('.', '_')
    return f


def log_subprocess_output(pipe):
    error = '\n'.join(
        [line.decode().strip() for line in iter(pipe.readline, b'')]
    )
    if len(error):
        raise Exception(error)
