# Network Route Optimization API

A FastAPI application that models a network of servers (nodes) connected by links (edges) with associated latency costs, and finds the shortest (lowest-latency) path between any two nodes using Dijkstra's algorithm. All data is stored in-memory — no database required.

---

## What It Does

| Capability | Description |
|---|---|
| Add/list/delete nodes | Register named servers in the network |
| Add/list/delete edges | Connect two servers with a measured latency |
| Find shortest route | Compute the minimum-latency path between two servers |
| Query history | Retrieve a log of all past route queries with optional filters |

---

## Project Structure

```
legality/
├── main.py           # App entry point — creates FastAPI app and registers routers
├── models.py         # Pydantic schemas for all request and response bodies
├── store.py          # In-memory data store (nodes, edges, adjacency list, history)
├── graph.py          # Dijkstra's shortest-path algorithm
├── routers/
│   ├── nodes.py      # POST /nodes, GET /nodes, DELETE /nodes/{id}
│   ├── edges.py      # POST /edges, GET /edges, DELETE /edges/{id}
│   └── routes.py     # POST /routes/shortest, GET /routes/history
├── pyproject.toml    # Project metadata and dependencies
└── uv.lock           # Pinned dependency versions (managed by uv)
```

---

## How Everything Is Connected

```
main.py
  └── creates FastAPI app
  └── registers 3 routers (prefix: /nodes, /edges, /routes)
        │
        ├── routers/nodes.py   ──► store.py  (add_node, delete_node)
        ├── routers/edges.py   ──► store.py  (add_edge, delete_edge)
        └── routers/routes.py  ──► store.py  (get_adjacency_snapshot, add_history, query_history)
                               ──► graph.py  (shortest_path)

models.py  ◄── imported by all routers for request validation and response serialization
store.py   ◄── single module-level singleton `store = NetworkStore()` shared across all routers
graph.py   ◄── pure function, no imports from the project, fully independent
```

### Data Flow: Shortest Path Request

1. Client sends `POST /routes/shortest` with `{"source": "ServerA", "destination": "ServerC"}`
2. `routers/routes.py` validates both node names exist in the store
3. Calls `store.get_adjacency_snapshot()` — gets a copy of the current graph
4. Passes it to `graph.shortest_path()` — returns `(total_latency, path)` or `None`
5. Saves the result (including failed attempts) to history via `store.add_history()`
6. Returns `RouteResponse` or raises HTTP 404 if no path exists

---

## API Reference

### Nodes

#### `POST /nodes`
Create a new node (server).

**Request:**
```json
{ "name": "ServerA" }
```
**Response `201`:**
```json
{ "id": 1, "name": "ServerA" }
```
**Errors:** `400` if name is missing or already exists.

---

#### `GET /nodes`
List all nodes.

**Response `200`:**
```json
[
  { "id": 1, "name": "ServerA" },
  { "id": 2, "name": "ServerB" }
]
```

---

#### `DELETE /nodes/{id}`
Delete a node and all edges connected to it.

**Response:** `204 No Content`
**Errors:** `404` if node not found.

---

### Edges

#### `POST /edges`
Connect two nodes with a latency value.

**Request:**
```json
{ "source": "ServerA", "destination": "ServerB", "latency": 12.5 }
```
**Response `201`:**
```json
{ "id": 1, "source": "ServerA", "destination": "ServerB", "latency": 12.5 }
```
**Errors:**
- `400` if either node does not exist or the edge already exists
- `422` if latency is <= 0

---

#### `GET /edges`
List all edges.

---

#### `DELETE /edges/{id}`
Delete an edge.

**Response:** `204 No Content`
**Errors:** `404` if edge not found.

---

### Routes

#### `POST /routes/shortest`
Find the lowest-latency path between two nodes.

**Request:**
```json
{ "source": "ServerA", "destination": "ServerD" }
```
**Response `200`:**
```json
{
  "total_latency": 23.4,
  "path": ["ServerA", "ServerB", "ServerD"]
}
```
**Errors:**
- `400` if either node does not exist
- `404` if no path exists between the two nodes

> Every call (including failed ones) is recorded in history.

---

#### `GET /routes/history`
Retrieve past route queries.

**Query parameters (all optional):**

| Parameter | Type | Description |
|---|---|---|
| `source` | string | Filter by source node name |
| `destination` | string | Filter by destination node name |
| `limit` | integer | Max records to return (default: 100) |
| `date_from` | datetime | Filter records created at or after this time |
| `date_to` | datetime | Filter records created at or before this time |

**Response `200`:**
```json
[
  {
    "id": 1,
    "source": "ServerA",
    "destination": "ServerD",
    "total_latency": 23.4,
    "path": ["ServerA", "ServerB", "ServerD"],
    "created_at": "2026-02-20T14:32:00Z"
  }
]
```
> `total_latency` and `path` are `null` for queries where no path was found.

---

## Key Implementation Details

### In-Memory Store (`store.py`)
The `NetworkStore` class holds all state in plain Python dicts:

- `nodes` — maps `id -> {id, name}`
- `node_names` — maps `name -> id` for O(1) duplicate checks
- `edges` — maps `id -> {id, source, destination, latency}`
- `adjacency` — maps `node_name -> [(neighbor_name, latency), ...]` — the graph used by Dijkstra
- `history` — ordered list of all route query results

Deleting a node automatically prunes all edges that reference it and updates the adjacency list, keeping the graph consistent.

### Dijkstra's Algorithm (`graph.py`)
Uses Python's `heapq` (min-heap) from the standard library. The function:
- Takes a snapshot of the adjacency list so live mutations don't affect an in-flight query
- Treats the graph as **undirected** — each edge is traversable in both directions
- Returns `(total_latency, path_list)` or `None` if the destination is unreachable
- Handles disconnected graphs and self-loops correctly

### Pydantic Validation (`models.py`)
- Empty node names are rejected with `422`
- Latency <= 0 is rejected with `422` via a `field_validator`
- Business-logic errors (duplicate names, missing nodes) return `400` via explicit `HTTPException`

---

## Running the Project

**Install dependencies:**
```bash
uv add "fastapi[standard]"
```

**Start the server:**
```bash
uv run uvicorn main:app --reload
```

**Interactive API docs:**
Open http://localhost:8000/docs in your browser.

---

## Quick Example

```bash
# Add servers
curl -X POST http://localhost:8000/nodes -H "Content-Type: application/json" -d '{"name":"ServerA"}'
curl -X POST http://localhost:8000/nodes -H "Content-Type: application/json" -d '{"name":"ServerB"}'
curl -X POST http://localhost:8000/nodes -H "Content-Type: application/json" -d '{"name":"ServerC"}'

# Connect them: A-B=10ms, B-C=5ms, A-C=20ms
curl -X POST http://localhost:8000/edges -H "Content-Type: application/json" -d '{"source":"ServerA","destination":"ServerB","latency":10}'
curl -X POST http://localhost:8000/edges -H "Content-Type: application/json" -d '{"source":"ServerB","destination":"ServerC","latency":5}'
curl -X POST http://localhost:8000/edges -H "Content-Type: application/json" -d '{"source":"ServerA","destination":"ServerC","latency":20}'

# Find shortest path A -> C
# Expected: 15ms via ServerB (not the direct 20ms edge)
curl -X POST http://localhost:8000/routes/shortest -H "Content-Type: application/json" -d '{"source":"ServerA","destination":"ServerC"}'
# -> {"total_latency": 15.0, "path": ["ServerA", "ServerB", "ServerC"]}
```

