import json
import os.path
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import auto


@auto.cli
@auto.json(print_tasks=True)
def config():
    with open("../civgraph.json") as file:
        return json.loads(file.read())
