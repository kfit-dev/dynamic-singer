import io
import sys
import json

def emit_state(state):
    if state is not None:
        line = json.dumps(state)
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()

input = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# raise Exception('haha')
f = open('output.txt', 'w')
for row in input:
    print('from b', row)
    print('from b', json.loads(row))
    f.write(row)
    emit_state(row)