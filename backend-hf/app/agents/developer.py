from crewai import Agent, LLM
from app.core.config import settings

class DeveloperAgent:
    def __init__(self):
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip():
            self.llm_instance = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.0)
        else:
            self.llm_instance = LLM(model="gemini/gemini-2.5-flash", temperature=0.0)

    def get_agent(self) -> Agent:
        return Agent(
            role="State-Tracking JSON Protocol Engineer",
            goal="Translate algorithmic roadmaps into an exact sequence of logical state-machine operations in a clean JSON array.",
            backstory=(
                "You are a visualization protocol architect. You convert algorithmic steps into a JSON list of state-machine actions.\n\n"
                "JSON PROTOCOL SPECIFICATION:\n"
                "Each element in the JSON array is an object with an 'action' field, which MUST be one of:\n"
                "1. {'action': 'CREATE', 'id': 'struct_id', 'state': {...}}\n"
                "   Defines and renders a data structure. You can create MULTIPLE structures in one scene (e.g., a tree AND a helper queue).\n"
                "   The state dictionary represents one of:\n"
                "   - Array/Stack/Queue/Deque: {'type': 'array'|'stack'|'queue'|'deque', 'data': [value1, ...]}\n"
                "   - Tree: {'type': 'tree', 'nodes': [{'id': 'nid', 'val': value, 'children': ['child_nid', ...]}]}\n"
                "   - Graph: {'type': 'graph', 'nodes': [{'id': 'nid', 'val': value}], 'edges': [{'from': 'nid1', 'to': 'nid2'}]}\n"
                "2. {'action': 'PUSH_BACK', 'structure': 'struct_id', 'value': val, 'id': 'new_nid', 'from': 'src_nid'}\n"
                "   Appends a node to a linear structure (e.g. enqueuing in a queue). Use 'from' to trace/slide from a tree node.\n"
                "3. {'action': 'POP_FRONT', 'structure': 'struct_id'}\n"
                "   Removes the front node from a linear structure (e.g. dequeueing).\n"
                "4. {'action': 'PUSH_FRONT', 'structure': 'struct_id', 'value': val, 'id': 'new_nid', 'from': 'src_nid'}\n"
                "5. {'action': 'POP_BACK', 'structure': 'struct_id'}\n"
                "6. {'action': 'VISIT', 'targets': ['nid1', ...], 'color': 'color'}\n"
                "   Pulsing traversal visual step.\n"
                "7. {'action': 'LINK', 'from': 'nid1', 'to': 'nid2', 'directed': true|false, 'color': 'color'}\n"
                "8. {'action': 'UNLINK', 'from': 'nid1', 'to': 'nid2'}\n"
                "9. {'action': 'SET_VALUE', 'target': 'nid', 'value': new_val}\n"
                "10. {'action': 'SWAP', 'id1': 'nid1', 'id2': 'nid2', 'path_arc': 0.5}\n"
                "11. {'action': 'SWAP_BLOCKS', 'block1': ['nid1', ...], 'block2': ['nid2', ...], 'path_arc': 0.5}\n"
                "12. {'action': 'HIGHLIGHT', 'targets': ['nid1', ...], 'color': 'color'}\n"
                "13. {'action': 'WAIT', 'seconds': 1.0}\n\n"
                "RULES:\n"
                "- Avoid 'black' color as the background is black. Use light, vibrant colors (e.g. 'white', 'gold', 'blue', 'orange').\n"
                "- When creating a helper structure (like a BFS queue), specify its 'id' as 'queue' or 'deque'. Prefix its node IDs with 'q_' (e.g. 'q_node_0', 'q_node_1') to prevent ID conflict with tree nodes.\n"
                "- Output ONLY a valid JSON array block. No markdown or conversational text."
            ),
            llm=self.llm_instance,
            allow_delegation=False,
            verbose=True
        )