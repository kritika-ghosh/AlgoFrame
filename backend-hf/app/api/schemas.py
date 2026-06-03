# app/api/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal

class GenerationResponse(BaseModel):
    status: str = Field(..., description="Current status of the compilation pipeline (completed/failed)")
    video_url: str = Field(..., description="Direct access HTTP URL path to download or stream the .mp4 file")
    message: str = Field(..., description="Summary message of the compilation results")

# --- Polymorphic Data Structure Representation Schemas ---
class NodeSchema(BaseModel):
    id: str = Field(..., description="Unique ID for the node")
    val: Union[int, str] = Field(..., description="Visual display value")
    children: Optional[List[str]] = Field(default=None, description="IDs of child nodes (for hierarchical structures)")

class EdgeSchema(BaseModel):
    from_node: str = Field(..., alias="from", description="Source node ID")
    to_node: str = Field(..., alias="to", description="Target node ID")
    weight: Optional[Union[int, float]] = Field(default=None, description="Optional weight/label for the connection")

class ArrayState(BaseModel):
    type: Literal["array", "stack", "queue"]
    data: List[Union[int, str]]

class TreeState(BaseModel):
    type: Literal["tree"]
    nodes: List[NodeSchema]

class GraphState(BaseModel):
    type: Literal["graph"]
    nodes: List[NodeSchema]
    edges: List[EdgeSchema]

PolymorphicState = Union[ArrayState, TreeState, GraphState]