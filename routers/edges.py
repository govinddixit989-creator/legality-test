from fastapi import APIRouter, HTTPException
from models import EdgeCreate, EdgeResponse
from store import store

router = APIRouter()


@router.post("", response_model=EdgeResponse, status_code=201)
def add_edge(body: EdgeCreate):
    try:
        edge = store.add_edge(body.source, body.destination, body.latency)
    except LookupError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return edge


@router.get("", response_model=list[EdgeResponse])
def list_edges():
    return list(store.edges.values())


@router.delete("/{edge_id}", status_code=204)
def delete_edge(edge_id: int):
    try:
        store.delete_edge(edge_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Edge not found")
