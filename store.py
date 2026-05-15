from datetime import datetime


class NetworkStore:
    def __init__(self) -> None:
        self._node_counter = 0
        self._edge_counter = 0
        self._history_counter = 0

        self.nodes: dict[int, dict] = {}
        self.node_names: dict[str, int] = {}
        self.edges: dict[int, dict] = {}
        self.adjacency: dict[str, list[tuple[str, float]]] = {}
        self.history: list[dict] = []

    def add_node(self, name: str) -> dict:
        if name in self.node_names:
            raise ValueError("Node name already exists")
        self._node_counter += 1
        node = {"id": self._node_counter, "name": name}
        self.nodes[self._node_counter] = node
        self.node_names[name] = self._node_counter
        self.adjacency[name] = []
        return node

    def delete_node(self, node_id: int) -> None:
        if node_id not in self.nodes:
            raise KeyError(node_id)
        name = self.nodes[node_id]["name"]
        del self.nodes[node_id]
        del self.node_names[name]
        del self.adjacency[name]
        # remove edges referencing this node
        to_delete = [
            eid for eid, e in self.edges.items()
            if e["source"] == name or e["destination"] == name
        ]
        for eid in to_delete:
            edge = self.edges.pop(eid)
            src, dst = edge["source"], edge["destination"]
            if src in self.adjacency:
                self.adjacency[src] = [
                    (n, l) for n, l in self.adjacency[src] if n != dst
                ]
            if dst in self.adjacency:
                self.adjacency[dst] = [
                    (n, l) for n, l in self.adjacency[dst] if n != src
                ]

    def add_edge(self, source: str, destination: str, latency: float) -> dict:
        if source not in self.node_names:
            raise LookupError(f"Node '{source}' not found")
        if destination not in self.node_names:
            raise LookupError(f"Node '{destination}' not found")
        for e in self.edges.values():
            if (e["source"] == source and e["destination"] == destination) or \
               (e["source"] == destination and e["destination"] == source):
                raise ValueError("Edge already exists")
        self._edge_counter += 1
        edge = {
            "id": self._edge_counter,
            "source": source,
            "destination": destination,
            "latency": latency,
        }
        self.edges[self._edge_counter] = edge
        self.adjacency[source].append((destination, latency))
        self.adjacency[destination].append((source, latency))
        return edge

    def delete_edge(self, edge_id: int) -> None:
        if edge_id not in self.edges:
            raise KeyError(edge_id)
        edge = self.edges.pop(edge_id)
        src, dst, lat = edge["source"], edge["destination"], edge["latency"]
        self.adjacency[src] = [(n, l) for n, l in self.adjacency[src] if not (n == dst and l == lat)]
        self.adjacency[dst] = [(n, l) for n, l in self.adjacency[dst] if not (n == src and l == lat)]

    def get_adjacency_snapshot(self) -> dict[str, list[tuple[str, float]]]:
        return {k: list(v) for k, v in self.adjacency.items()}

    def add_history(self, entry: dict) -> None:
        self._history_counter += 1
        entry["id"] = self._history_counter
        self.history.append(entry)

    def query_history(
        self,
        source: str | None,
        destination: str | None,
        limit: int,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> list[dict]:
        results = self.history
        if source:
            results = [r for r in results if r["source"] == source]
        if destination:
            results = [r for r in results if r["destination"] == destination]
        if date_from:
            results = [r for r in results if r["created_at"] >= date_from]
        if date_to:
            results = [r for r in results if r["created_at"] <= date_to]
        return results[-limit:] if limit else results


store = NetworkStore()
