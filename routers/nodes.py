from fastapi import APIRouter, HTTPException
from models import NodeCreate, NodeResponse
from store import store

router = APIRouter()


@router.post("", response_model=NodeResponse, status_code=201)
def add_node(body: NodeCreate):
    try:
        node = store.add_node(body.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return node


@router.get("", response_model=list[NodeResponse])
def list_nodes():
    return list(store.nodes.values())


@router.delete("/{node_id}", status_code=204)
def delete_node(node_id: int):
    try:
        store.delete_node(node_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Node not found")
