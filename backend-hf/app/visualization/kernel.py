# app/visualization/kernel.py
from manim import *
import numpy as np

class DataNode(VGroup):
    def __init__(self, node_id, value, shape_type="square", size=0.8, color=BLUE, fill_opacity=0.3, label_color=WHITE):
        super().__init__()
        self.node_id = node_id
        self.value = value
        self.shape_type = shape_type
        
        # Color mapping to handle lowercase standard colors safely
        color_val = self._resolve_color(color)
        
        if shape_type == "circle":
            self.shape = Circle(radius=size/2, color=color_val)
        elif shape_type == "rounded_rectangle":
            self.shape = RoundedRectangle(width=size*1.2, height=size, corner_radius=0.1, color=color_val)
        else: # Default is "square"
            self.shape = Square(side_length=size, color=color_val)
            
        self.shape.set_fill(color_val, opacity=fill_opacity)
        self.label = Text(str(value), color=label_color)
        self.label.scale_to_fit_width(size * 0.6)
        self.label.move_to(self.shape.get_center())
        
        self.add(self.shape, self.label)
        
    def _resolve_color(self, color):
        if isinstance(color, str):
            c_upper = color.upper()
            
            # Resolve standard manim colors from global scope
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
        self.clear()
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
            self.line = Arrow(start_pt, end_pt, color=self.color, stroke_width=self.stroke_width, buff=0.1)
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


class StateRegistry:
    def __init__(self, scene: Scene):
        self.scene = scene
        self.nodes = {}  # node_id -> DataNode
        self.edges = {}  # (start_id, end_id) -> DataEdge
        self.layout_type = "array"
        self.array_order = []
        
    def add_node(self, node: DataNode):
        self.nodes[node.node_id] = node
        
    def get_node(self, node_id) -> DataNode:
        return self.nodes.get(node_id)
        
    def create_array(self, values, shape_type="square", color="BLUE", spacing=1.0):
        self.layout_type = "array"
        self.array_order = []
        for i, val in enumerate(values):
            node_id = f"node_{i}"
            node = RendererFactory.create_node(node_id, val, shape_type=shape_type, color=color)
            self.add_node(node)
            self.array_order.append(node_id)
            
        self.array_group = VGroup(*[self.nodes[nid] for nid in self.array_order])
        self.array_group.arrange(RIGHT, buff=spacing - 0.8)
        self.scene.add(self.array_group)
        self.scene.play(FadeIn(self.array_group))
        
    def swap(self, id1, id2, path_arc=0.5):
        node1 = self.nodes.get(id1)
        node2 = self.nodes.get(id2)
        if not node1 or not node2:
            return
            
        pos1 = node1.get_center().copy()
        pos2 = node2.get_center().copy()
        
        self.scene.play(
            node1.animate.move_to(pos2),
            node2.animate.move_to(pos1),
            path_arc=path_arc
        )
        
        # Keep physical-to-logical index layout in sync
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
        
        # Keep physical-to-logical index layout in sync
        self.array_order.sort(key=lambda nid: self.nodes[nid].get_center()[0])

    def highlight(self, targets, color):
        anims = []
        for tid in targets:
            node = self.nodes.get(tid)
            if node:
                color_val = node._resolve_color(color)
                anims.append(node.shape.animate.set_color(color_val).set_fill(color_val, opacity=0.8))
        if anims:
            self.scene.play(*anims)

    def create_tree(self, node_data, edges_data, shape_type="circle", color="BLUE"):
        self.layout_type = "tree"
        for nd in node_data:
            node = RendererFactory.create_node(nd["id"], nd["value"], shape_type=shape_type, color=color)
            node.move_to(nd.get("pos", [0, 0, 0]))
            self.add_node(node)
            self.scene.add(node)
            
        for parent, child in edges_data:
            edge = self.add_edge(parent, child, directed=True)
            if edge:
                self.scene.add(edge)
                
        all_objs = list(self.nodes.values()) + list(self.edges.values())
        self.scene.play(FadeIn(VGroup(*all_objs)))

    def add_edge(self, start_id, end_id, directed=True, color=WHITE):
        start_node = self.get_node(start_id)
        end_node = self.get_node(end_id)
        if start_node and end_node:
            edge = DataEdge(start_node, end_node, directed=directed, color=color)
            self.edges[(start_id, end_id)] = edge
            return edge
        return None
