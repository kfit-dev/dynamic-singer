import re


def parse_name(f):
    f = f.split('-c')[0]
    f = re.sub(r'[ ]+', ' ', f.lower()).strip()
    f = f.replace('-', '_').replace('.', '_')
    return f
