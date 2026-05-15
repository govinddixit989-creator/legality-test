from fastapi import FastAPI
from routers import nodes, edges, routes

app = FastAPI(title="Network Route Optimization API")

app.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
app.include_router(edges.router, prefix="/edges", tags=["edges"])
app.include_router(routes.router, prefix="/routes", tags=["routes"])
