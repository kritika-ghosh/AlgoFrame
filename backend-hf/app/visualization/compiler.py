# app/visualization/compiler.py
import json

class ProtocolCompiler:
    @staticmethod
    def compile_json_to_manim(json_str: str, scene_class_name: str = "ArrayInitialization") -> str:
        """
        Parses JSON protocol and returns a fully executable Manim script string using the Visualization Kernel.
        """
        json_str = json_str.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
            
        try:
            operations = json.loads(json_str)
        except Exception as e:
            start_idx = json_str.find("[")
            end_idx = json_str.rfind("]")
            if start_idx != -1 and end_idx != -1:
                try:
                    operations = json.loads(json_str[start_idx:end_idx+1])
                except Exception as nested_e:
                    raise ValueError(f"Failed to parse JSON protocol: {str(e)}. Raw output was:\n{json_str}")
            else:
                raise ValueError(f"Failed to parse JSON protocol: {str(e)}. Raw output was:\n{json_str}")
            
        script = [
            "from manim import *",
            "from app.visualization.kernel import StateRegistry, DataNode, RendererFactory",
            "",
            f"class {scene_class_name}(Scene):",
            "    def construct(self):",
            "        registry = StateRegistry(self)"
        ]
        
        # Check if there are multiple structures
        create_ops = [op for op in operations if isinstance(op, dict) and op.get("action", "").upper() in ["CREATE", "CREATE_ARRAY"]]
        has_multiple = len(create_ops) > 1
        
        for op in operations:
            if not isinstance(op, dict):
                continue
            action = op.get("action", "").upper()
            if action in ["CREATE", "CREATE_ARRAY"]:
                if action == "CREATE_ARRAY" or "values" in op:
                    vals = op.get("values", [])
                    color = op.get("color", "BLUE")
                    shape = op.get("shape_type", "square")
                    spacing = op.get("spacing", 1.2)
                    state = {"type": "array", "data": vals, "color": color, "shape_type": shape, "spacing": spacing}
                else:
                    state = op.get("state", {})
                
                struct_id = op.get("id") or state.get("type", "main")
                y_offset = 0.0
                if has_multiple:
                    t = state.get("type", "")
                    if t in ["tree", "graph"]:
                        y_offset = 1.2
                    elif t in ["queue", "deque", "stack", "array"]:
                        y_offset = -2.5
                        
                script.append(f"        registry.create_structure({state}, struct_id={repr(struct_id)}, y_offset={y_offset})")
                script.append("        self.wait(1)")
            elif action in ["PUSH_BACK", "ENQUEUE"]:
                struct_id = op.get("structure") or op.get("struct_id") or "queue"
                val = op.get("value") or op.get("val")
                nid = op.get("id") or op.get("node_id")
                from_n = op.get("from") or op.get("from_node")
                script.append(f"        registry.push_back({repr(struct_id)}, {repr(val)}, node_id={repr(nid)}, from_node={repr(from_n)})")
                script.append("        self.wait(1)")
            elif action in ["POP_FRONT", "DEQUEUE"]:
                struct_id = op.get("structure") or op.get("struct_id") or "queue"
                script.append(f"        registry.pop_front({repr(struct_id)})")
                script.append("        self.wait(1)")
            elif action == "PUSH_FRONT":
                struct_id = op.get("structure") or op.get("struct_id") or "queue"
                val = op.get("value") or op.get("val")
                nid = op.get("id") or op.get("node_id")
                from_n = op.get("from") or op.get("from_node")
                script.append(f"        registry.push_front({repr(struct_id)}, {repr(val)}, node_id={repr(nid)}, from_node={repr(from_n)})")
                script.append("        self.wait(1)")
            elif action == "POP_BACK":
                struct_id = op.get("structure") or op.get("struct_id") or "queue"
                script.append(f"        registry.pop_back({repr(struct_id)})")
                script.append("        self.wait(1)")
            elif action == "VISIT":
                targets = op.get("targets", [])
                color = op.get("color", "ORANGE")
                script.append(f"        registry.visit({targets}, color='{color}')")
                script.append("        self.wait(1)")
            elif action == "LINK":
                u = op.get("from") or op.get("from_node")
                v = op.get("to") or op.get("to_node")
                directed = op.get("directed", True)
                color = op.get("color", "WHITE")
                script.append(f"        registry.link('{u}', '{v}', directed={directed}, color='{color}')")
                script.append("        self.wait(1)")
            elif action == "UNLINK":
                u = op.get("from") or op.get("from_node")
                v = op.get("to") or op.get("to_node")
                script.append(f"        registry.unlink('{u}', '{v}')")
                script.append("        self.wait(1)")
            elif action == "SET_VALUE":
                target = op.get("target") or op.get("target_id")
                val = op.get("value") or op.get("val")
                script.append(f"        registry.set_value('{target}', {repr(val)})")
                script.append("        self.wait(1)")
            elif action == "SWAP":
                id1 = op.get("id1")
                id2 = op.get("id2")
                arc = op.get("path_arc", 0.5)
                script.append(f"        registry.swap('{id1}', '{id2}', path_arc={arc})")
                script.append("        self.wait(1)")
            elif action == "SWAP_BLOCKS":
                block1 = op.get("block1", [])
                block2 = op.get("block2", [])
                arc = op.get("path_arc", 0.5)
                script.append(f"        registry.swap_blocks({block1}, {block2}, path_arc={arc})")
                script.append("        self.wait(1)")
            elif action == "HIGHLIGHT":
                targets = op.get("targets", [])
                color = op.get("color", "YELLOW")
                script.append(f"        registry.highlight({targets}, color='{color}')")
                script.append("        self.wait(1)")
            elif action == "WAIT":
                sec = op.get("seconds", 1)
                script.append(f"        self.wait({sec})")
                
        return "\n".join(script)
