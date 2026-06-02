# app/visualization/compiler.py
import json

class ProtocolCompiler:
    @staticmethod
    def compile_json_to_manim(json_str: str, scene_class_name: str = "ArrayInitialization") -> str:
        """
        Parses JSON protocol and returns a fully executable Manim script string using the Visualization Kernel.
        """
        # Defensive block stripping
        json_str = json_str.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
            
        try:
            operations = json.loads(json_str)
        except Exception as e:
            # Let's try to extract JSON array if there is conversational noise
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
        
        for op in operations:
            if not isinstance(op, dict):
                continue
            action = op.get("action", "").upper()
            if action == "CREATE_ARRAY":
                vals = op.get("values", [])
                color = op.get("color", "BLUE")
                shape = op.get("shape_type", "square")
                spacing = op.get("spacing", 1.0)
                script.append(f"        registry.create_array({vals}, shape_type='{shape}', color='{color}', spacing={spacing})")
                script.append("        self.wait(1)")
            elif action == "HIGHLIGHT":
                targets = op.get("targets", [])
                color = op.get("color", "YELLOW")
                script.append(f"        registry.highlight({targets}, color='{color}')")
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
            elif action == "WAIT":
                sec = op.get("seconds", 1)
                script.append(f"        self.wait({sec})")
                
        return "\n".join(script)
