from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from models import RouteRequest, RouteResponse, HistoryEntry
from store import store
from graph import shortest_path

router = APIRouter()


@router.post("/shortest", response_model=RouteResponse)
def get_shortest_route(body: RouteRequest):
    if body.source not in store.node_names:
        raise HTTPException(status_code=400, detail=f"Node '{body.source}' not found")
    if body.destination not in store.node_names:
        raise HTTPException(status_code=400, detail=f"Node '{body.destination}' not found")

    adjacency = store.get_adjacency_snapshot()
    result = shortest_path(adjacency, body.source, body.destination)

    entry: dict = {
        "source": body.source,
        "destination": body.destination,
        "total_latency": result[0] if result else None,
        "path": result[1] if result else None,
        "created_at": datetime.now(timezone.utc),
    }
    store.add_history(entry)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No path exists between {body.source} and {body.destination}",
        )
    return RouteResponse(total_latency=result[0], path=result[1])


@router.get("/history", response_model=list[HistoryEntry])
def get_route_history(
    source: str | None = Query(default=None),
    destination: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
):
    return store.query_history(source, destination, limit, date_from, date_to)
