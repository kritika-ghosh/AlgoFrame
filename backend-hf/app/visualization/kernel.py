# app/visualization/kernel.py
from manim import *
import numpy as np

class DataNode(VGroup):
    def __init__(self, node_id, value, shape_type="square", size=1.0, color=BLUE, fill_opacity=0.6, label_color=WHITE):
        super().__init__()
        self.node_id = node_id
        self.value = value
        self.shape_type = shape_type
        
        # Color mapping to handle standard color strings safely
        color_val = self._resolve_color(color)
        
        if shape_type == "circle":
            self.shape = Circle(radius=size/2, color=color_val, stroke_width=4)
        elif shape_type == "rounded_rectangle":
            self.shape = RoundedRectangle(width=size*1.2, height=size, corner_radius=0.1, color=color_val, stroke_width=4)
        else: # Default is "square"
            self.shape = Square(side_length=size, color=color_val, stroke_width=4)
            
        self.shape.set_fill(color_val, opacity=fill_opacity)
        self.label = Text(str(value), color=label_color)
        self.label.scale_to_fit_width(size * 0.6)
        self.label.move_to(self.shape.get_center())
        
        self.add(self.shape, self.label)
        
    def _resolve_color(self, color):
        if isinstance(color, str):
            c_upper = color.upper()
            import manim
            if hasattr(manim, c_upper):
                return getattr(manim, c_upper)
                
            if c_upper == "AMBER":
                return ORANGE
            elif c_upper == "TEAL":
                return BLUE_D
            elif c_upper == "GOLD":
                return YELLOW_D
            elif c_upper == "ORANGE":
                return ORANGE
            else:
                try:
                    return ManimColor(color)
                except:
                    return BLUE
        return color

    def set_value(self, new_value):
        self.value = new_value
        old_center = self.label.get_center()
        self.remove(self.label)
        self.label = Text(str(new_value), color=self.label.color)
        self.label.scale_to_fit_width(self.shape.width * 0.6)
        self.label.move_to(old_center)
        self.add(self.label)

    def set_highlight(self, color, fill_opacity=0.8):
        color_val = self._resolve_color(color)
        self.shape.set_color(color_val)
        self.shape.set_fill(color_val, opacity=fill_opacity)


class DataEdge(VGroup):
    def __init__(self, start_node: DataNode, end_node: DataNode, directed=True, color=WHITE, stroke_width=4):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.directed = directed
        self.color = color
        self.stroke_width = stroke_width
        self.update_arrow_or_line()
        
    def update_arrow_or_line(self):
        self.submobjects = []
        start_pt = self.start_node.shape.get_center()
        end_pt = self.end_node.shape.get_center()
        
        direction = end_pt - start_pt
        length = np.linalg.norm(direction)
        if length > 0.001:
            unit_dir = direction / length
            start_radius = self.start_node.shape.width / 2.0
            end_radius = self.end_node.shape.width / 2.0
            start_pt = start_pt + unit_dir * start_radius
            end_pt = end_pt - unit_dir * end_radius
            
        if self.directed:
            self.line = Arrow(start_pt, end_pt, color=self.color, stroke_width=self.stroke_width, buff=0)
        else:
            self.line = Line(start_pt, end_pt, color=self.color, stroke_width=self.stroke_width)
        self.add(self.line)


class RendererFactory:
    @staticmethod
    def create_node(node_id, value, shape_type="square", size=0.8, color=BLUE, fill_opacity=0.3, label_color=WHITE) -> DataNode:
        return DataNode(
            node_id=node_id,
            value=value,
            shape_type=shape_type,
            size=size,
            color=color,
            fill_opacity=fill_opacity,
            label_color=label_color
        )


# --- Visual Layout Adapters ---

class LinearAdapter:
    @staticmethod
    def get_positions(data_list, spacing=1.2, vertical=False, x_offset=0.0, y_offset=0.0):
        positions = {}
        n = len(data_list)
        total_len = (n - 1) * spacing
        start = -total_len / 2.0
        for i, val in enumerate(data_list):
            node_id = f"node_{i}"
            if vertical:
                positions[node_id] = np.array([x_offset, -start - i * spacing + y_offset, 0])
            else:
                positions[node_id] = np.array([start + i * spacing + x_offset, y_offset, 0])
        return positions


class TreeAdapter:
    @staticmethod
    def get_positions(nodes, vertical_spacing=1.5, initial_width=6.0, y_offset=0.0):
        adj = {}
        node_ids = set()
        
        for n in nodes:
            nid = str(n.get("id"))
            node_ids.add(nid)
            adj[nid] = [str(c) for c in (n.get("children") or [])]
            
        # Find root node(s) - nodes with no parents
        children_ids = set()
        for nid, children in adj.items():
            for c in children:
                children_ids.add(c)
        roots = list(node_ids - children_ids)
        if not roots:
            roots = [list(node_ids)[0]] if node_ids else []
            
        positions = {}
        
        def assign_positions(nid, x, y, width):
            if not nid:
                return
            positions[nid] = np.array([x, y + y_offset, 0])
            children = adj.get(nid, [])
            if not children:
                return
            
            num_children = len(children)
            if num_children == 1:
                assign_positions(children[0], x, y - vertical_spacing, width)
            else:
                step = width / (num_children - 1) if num_children > 1 else width
                start_x = x - width / 2.0
                for idx, child in enumerate(children):
                    child_x = start_x + idx * step
                    assign_positions(child, child_x, y - vertical_spacing, width / 2.0)
                    
        num_roots = len(roots)
        if num_roots == 1:
            assign_positions(roots[0], 0, 2.5, initial_width)
        else:
            step = initial_width / (num_roots - 1)
            start_x = -initial_width / 2.0
            for idx, root in enumerate(roots):
                assign_positions(root, start_x + idx * step, 2.5, initial_width / num_roots)
                
        return positions


class GraphAdapter:
    @staticmethod
    def get_positions(nodes, radius=2.2, y_offset=0.0):
        positions = {}
        n = len(nodes)
        if n == 0:
            return positions
            
        for i, node in enumerate(nodes):
            nid = str(node.get("id"))
            theta = (2.0 * np.pi * i) / n
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            positions[nid] = np.array([x, y + y_offset, 0])
            
        return positions


class StateRegistry:
    def __init__(self, scene: Scene):
        self.scene = scene
        self.nodes = {}  # node_id -> DataNode
        self.edges = {}  # (start_id, end_id) -> DataEdge
        self.layout_type = "array"
        self.array_order = []
        self.structures = {}  # struct_id -> {"type": ..., "node_ids": [], "y_offset": ...}
        
    def add_node(self, node: DataNode):
        self.nodes[node.node_id] = node
        
    def get_node(self, node_id) -> DataNode:
        return self.nodes.get(str(node_id))
        
    def add_edge(self, start_id, end_id, directed=True, color=WHITE):
        start_node = self.get_node(start_id)
        end_node = self.get_node(end_id)
        if start_node and end_node:
            edge = DataEdge(start_node, end_node, directed=directed, color=color)
            self.edges[(str(start_id), str(end_id))] = edge
            return edge
        return None

    def create_array(self, values, shape_type="square", color="BLUE", spacing=1.2):
        self.create_structure({
            "type": "array",
            "data": values,
            "shape_type": shape_type,
            "color": color,
            "spacing": spacing
        })

    def create_structure(self, schema_data, struct_id=None, y_offset=0.0):
        layout_type = schema_data.get("type", "array")
        self.layout_type = layout_type
        
        if struct_id is None:
            struct_id = layout_type
            
        self.structures[struct_id] = {
            "type": layout_type,
            "node_ids": [],
            "y_offset": y_offset
        }
        
        if layout_type in ["array", "stack", "queue", "deque"]:
            vals = schema_data.get("data", [])
            positions = LinearAdapter.get_positions(vals, spacing=1.2, y_offset=y_offset)
            self.array_order = []
            for i, val in enumerate(vals):
                node_id = f"{struct_id}_{i}"
                pos = positions[f"node_{i}"]
                node = RendererFactory.create_node(node_id, val, shape_type="square", color=BLUE)
                node.move_to(pos)
                self.add_node(node)
                self.structures[struct_id]["node_ids"].append(node_id)
                self.array_order.append(node_id)
                
            self.array_group = VGroup(*[self.nodes[nid] for nid in self.structures[struct_id]["node_ids"]])
            self.scene.play(FadeIn(self.array_group))
            
        elif layout_type == "tree":
            nodes = schema_data.get("nodes", [])
            positions = TreeAdapter.get_positions(nodes, y_offset=y_offset)
            
            # Create nodes
            node_group = VGroup()
            for n in nodes:
                nid = str(n.get("id"))
                val = n.get("val")
                pos = positions.get(nid, np.array([0, 0, 0]))
                node = RendererFactory.create_node(nid, val, shape_type="circle", color=GOLD)
                node.move_to(pos)
                self.add_node(node)
                self.structures[struct_id]["node_ids"].append(nid)
                node_group.add(node)
                
            # Create edges
            edge_group = VGroup()
            for n in nodes:
                nid = str(n.get("id"))
                children = n.get("children") or []
                for c in children:
                    edge = self.add_edge(nid, str(c), directed=True, color=WHITE)
                    if edge:
                        edge_group.add(edge)
                        
            all_objs = VGroup(node_group, edge_group)
            self.scene.play(FadeIn(all_objs))
            
        elif layout_type == "graph":
            nodes = schema_data.get("nodes", [])
            edges = schema_data.get("edges", [])
            positions = GraphAdapter.get_positions(nodes, y_offset=y_offset)
            
            # Create nodes
            node_group = VGroup()
            for n in nodes:
                nid = str(n.get("id"))
                val = n.get("val")
                pos = positions.get(nid, np.array([0, 0, 0]))
                node = RendererFactory.create_node(nid, val, shape_type="circle", color=TEAL)
                node.move_to(pos)
                self.add_node(node)
                self.structures[struct_id]["node_ids"].append(nid)
                node_group.add(node)
                
            # Create edges
            edge_group = VGroup()
            for e in edges:
                u = str(e.get("from_node") or e.get("from"))
                v = str(e.get("to_node") or e.get("to"))
                edge = self.add_edge(u, v, directed=False, color=WHITE)
                if edge:
                    edge_group.add(edge)
                    
            all_objs = VGroup(node_group, edge_group)
            self.scene.play(FadeIn(all_objs))

    def push_back(self, struct_id, value, node_id=None, from_node=None):
        struct = self.structures.get(struct_id)
        if not struct: return
        
        if not node_id:
            node_id = f"{struct_id}_{len(struct['node_ids'])}"
            
        current_nodes = [self.get_node(nid) for nid in struct["node_ids"]]
        new_values = [n.value for n in current_nodes] + [value]
        
        new_positions = LinearAdapter.get_positions(new_values, y_offset=struct["y_offset"])
        
        anims = []
        for i, nid in enumerate(struct["node_ids"]):
            target_pos = new_positions[f"node_{i}"]
            anims.append(self.get_node(nid).animate.move_to(target_pos))
            
        new_node = RendererFactory.create_node(node_id, value, shape_type="square", color=BLUE)
        if from_node and self.get_node(from_node):
            start_pos = self.get_node(from_node).get_center()
        else:
            start_pos = new_positions[f"node_{len(current_nodes)}"] + np.array([1.5, 0, 0])
            
        new_node.move_to(start_pos)
        self.add_node(new_node)
        struct["node_ids"].append(node_id)
        
        self.scene.add(new_node)
        anims.append(new_node.animate.move_to(new_positions[f"node_{len(current_nodes)}"]))
        self.scene.play(*anims, run_time=0.6)

    def pop_front(self, struct_id):
        struct = self.structures.get(struct_id)
        if not struct or not struct["node_ids"]: return
        
        front_nid = struct["node_ids"].pop(0)
        front_node = self.get_node(front_nid)
        
        remaining_nodes = [self.get_node(nid) for nid in struct["node_ids"]]
        remaining_values = [n.value for n in remaining_nodes]
        
        new_positions = LinearAdapter.get_positions(remaining_values, y_offset=struct["y_offset"])
        
        anims = [FadeOut(front_node), front_node.animate.scale(0.1)]
        for i, nid in enumerate(struct["node_ids"]):
            target_pos = new_positions[f"node_{i}"]
            anims.append(self.get_node(nid).animate.move_to(target_pos))
            
        self.scene.play(*anims, run_time=0.6)
        if front_nid in self.nodes:
            del self.nodes[front_nid]

    def push_front(self, struct_id, value, node_id=None, from_node=None):
        struct = self.structures.get(struct_id)
        if not struct: return
        
        if not node_id:
            node_id = f"{struct_id}_{len(struct['node_ids'])}"
            
        current_nodes = [self.get_node(nid) for nid in struct["node_ids"]]
        new_values = [value] + [n.value for n in current_nodes]
        
        new_positions = LinearAdapter.get_positions(new_values, y_offset=struct["y_offset"])
        
        anims = []
        for i, nid in enumerate(struct["node_ids"]):
            target_pos = new_positions[f"node_{i+1}"]
            anims.append(self.get_node(nid).animate.move_to(target_pos))
            
        new_node = RendererFactory.create_node(node_id, value, shape_type="square", color=BLUE)
        if from_node and self.get_node(from_node):
            start_pos = self.get_node(from_node).get_center()
        else:
            start_pos = new_positions["node_0"] - np.array([1.5, 0, 0])
            
        new_node.move_to(start_pos)
        self.add_node(new_node)
        struct["node_ids"].insert(0, node_id)
        
        self.scene.add(new_node)
        anims.append(new_node.animate.move_to(new_positions["node_0"]))
        self.scene.play(*anims, run_time=0.6)

    def pop_back(self, struct_id):
        struct = self.structures.get(struct_id)
        if not struct or not struct["node_ids"]: return
        
        back_nid = struct["node_ids"].pop()
        back_node = self.get_node(back_nid)
        
        remaining_nodes = [self.get_node(nid) for nid in struct["node_ids"]]
        remaining_values = [n.value for n in remaining_nodes]
        
        new_positions = LinearAdapter.get_positions(remaining_values, y_offset=struct["y_offset"])
        
        anims = [FadeOut(back_node), back_node.animate.scale(0.1)]
        for i, nid in enumerate(struct["node_ids"]):
            target_pos = new_positions[f"node_{i}"]
            anims.append(self.get_node(nid).animate.move_to(target_pos))
            
        self.scene.play(*anims, run_time=0.6)
        if back_nid in self.nodes:
            del self.nodes[back_nid]

    def visit(self, targets, color="ORANGE"):
        for tid in targets:
            target_node = self.get_node(tid)
            if not target_node:
                continue
                
            color_val = target_node._resolve_color(color)
            
            # Find incoming edge from a parent
            parent_edge = None
            for (u, v), edge in self.edges.items():
                if str(v) == str(tid):
                    parent_edge = edge
                    break
                    
            # Animate the tracing dot along the edge if a parent exists
            if parent_edge:
                start_pt = parent_edge.start_node.shape.get_center()
                end_pt = parent_edge.end_node.shape.get_center()
                
                # Glowing tracing dot
                particle = Dot(start_pt, color=color_val, radius=0.08)
                self.scene.add(particle)
                
                self.scene.play(
                    particle.animate.move_to(end_pt),
                    run_time=0.4,
                    rate_func=smooth
                )
                self.scene.remove(particle)
                
            # Pulsing highlight of visited node
            self.scene.play(
                target_node.animate.scale(1.25).set_color(color_val),
                run_time=0.25
            )
            self.scene.play(
                target_node.animate.scale(1.0 / 1.25),
                run_time=0.2
            )

    def link(self, from_id, to_id, directed=True, color=WHITE):
        edge = self.add_edge(from_id, to_id, directed=directed, color=color)
        if edge:
            self.scene.play(Create(edge))

    def unlink(self, from_id, to_id):
        # Scan for edge key
        key1 = (str(from_id), str(to_id))
        key2 = (str(to_id), str(from_id))
        edge = self.edges.get(key1) or self.edges.get(key2)
        if edge:
            self.scene.play(FadeOut(edge))
            self.edges.pop(key1, None)
            self.edges.pop(key2, None)

    def set_value(self, target_id, new_value):
        node = self.get_node(target_id)
        if node:
            self.scene.play(Flash(node, color=YELLOW, flash_radius=0.6))
            node.set_value(new_value)

    def swap(self, id1, id2, path_arc=0.5):
        node1 = self.get_node(id1)
        node2 = self.get_node(id2)
        if not node1 or not node2:
            return
            
        pos1 = node1.get_center().copy()
        pos2 = node2.get_center().copy()
        
        self.scene.play(
            node1.animate.move_to(pos2),
            node2.animate.move_to(pos1),
            path_arc=path_arc
        )
        
        if self.array_order:
            self.array_order.sort(key=lambda nid: self.nodes[nid].get_center()[0])

    def swap_blocks(self, ids1, ids2, path_arc=0.5):
        group1 = VGroup(*[self.nodes[id] for id in ids1 if id in self.nodes])
        group2 = VGroup(*[self.nodes[id] for id in ids2 if id in self.nodes])
        if len(group1) == 0 or len(group2) == 0:
            return
            
        center1 = group1.get_center().copy()
        center2 = group2.get_center().copy()
        offset = center2 - center1
        
        anim_list = []
        for id in ids1:
            if id in self.nodes:
                anim_list.append(self.nodes[id].animate.shift(offset))
        for id in ids2:
            if id in self.nodes:
                anim_list.append(self.nodes[id].animate.shift(-offset))
                
        self.scene.play(*anim_list, path_arc=path_arc)
        
        if self.array_order:
            self.array_order.sort(key=lambda nid: self.nodes[nid].get_center()[0])

    def highlight(self, targets, color):
        anims = []
        for tid in targets:
            node = self.get_node(tid)
            if node:
                color_val = node._resolve_color(color)
                anims.append(node.shape.animate.set_color(color_val).set_fill(color_val, opacity=0.8))
        if anims:
            self.scene.play(*anims)
