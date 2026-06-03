# scratch_test.py
import subprocess
import os
from app.visualization.compiler import ProtocolCompiler

test_json = """
[
  {
    "action": "CREATE",
    "id": "tree",
    "state": {
      "type": "tree",
      "nodes": [
        {"id": "10", "val": 10, "children": ["5", "15"]},
        {"id": "5", "val": 5, "children": ["2", "7"]},
        {"id": "15", "val": 15, "children": ["12", "20"]},
        {"id": "2", "val": 2, "children": []},
        {"id": "7", "val": 7, "children": []},
        {"id": "12", "val": 12, "children": []},
        {"id": "20", "val": 20, "children": []}
      ]
    }
  },
  {
    "action": "CREATE",
    "id": "queue",
    "state": {
      "type": "queue",
      "data": []
    }
  },
  {
    "action": "PUSH_BACK",
    "structure": "queue",
    "value": 10,
    "id": "q_0",
    "from": "10"
  },
  {
    "action": "VISIT",
    "targets": ["10"],
    "color": "white"
  },
  {
    "action": "POP_FRONT",
    "structure": "queue"
  },
  {
    "action": "PUSH_BACK",
    "structure": "queue",
    "value": 5,
    "id": "q_1",
    "from": "5"
  },
  {
    "action": "PUSH_BACK",
    "structure": "queue",
    "value": 15,
    "id": "q_2",
    "from": "15"
  },
  {
    "action": "VISIT",
    "targets": ["5"],
    "color": "white"
  },
  {
    "action": "POP_FRONT",
    "structure": "queue"
  },
  {
    "action": "PUSH_BACK",
    "structure": "queue",
    "value": 2,
    "id": "q_3",
    "from": "2"
  },
  {
    "action": "PUSH_BACK",
    "structure": "queue",
    "value": 7,
    "id": "q_4",
    "from": "7"
  },
  {
    "action": "VISIT",
    "targets": ["15"],
    "color": "white"
  },
  {
    "action": "POP_FRONT",
    "structure": "queue"
  },
  {
    "action": "PUSH_BACK",
    "structure": "queue",
    "value": 12,
    "id": "q_5",
    "from": "12"
  },
  {
    "action": "PUSH_BACK",
    "structure": "queue",
    "value": 20,
    "id": "q_6",
    "from": "20"
  },
  {
    "action": "VISIT",
    "targets": ["2"],
    "color": "white"
  },
  {
    "action": "POP_FRONT",
    "structure": "queue"
  },
  {
    "action": "VISIT",
    "targets": ["7"],
    "color": "white"
  },
  {
    "action": "POP_FRONT",
    "structure": "queue"
  },
  {
    "action": "VISIT",
    "targets": ["12"],
    "color": "white"
  },
  {
    "action": "POP_FRONT",
    "structure": "queue"
  },
  {
    "action": "VISIT",
    "targets": ["20"],
    "color": "white"
  },
  {
    "action": "POP_FRONT",
    "structure": "queue"
  },
  {
    "action": "WAIT",
    "seconds": 1.0
  }
]
"""

compiled_code = ProtocolCompiler.compile_json_to_manim(test_json, scene_class_name="ArrayInitialization")
scene_filename = "scene_test.py"
with open(scene_filename, "w", encoding="utf-8") as f:
    f.write(compiled_code)

try:
    result = subprocess.run(["manim", "-ql", scene_filename, "ArrayInitialization"], capture_output=True, text=True)
    print("Return code:", result.returncode)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
finally:
    if os.path.exists(scene_filename):
        os.remove(scene_filename)
