import heapq
from math import inf


def shortest_path(
    adjacency: dict[str, list[tuple[str, float]]],
    source: str,
    destination: str,
) -> tuple[float, list[str]] | None:
    if source not in adjacency or destination not in adjacency:
        return None
    if source == destination:
        return 0.0, [source]

    dist: dict[str, float] = {source: 0.0}
    prev: dict[str, str] = {}
    heap: list[tuple[float, str]] = [(0.0, source)]

    while heap:
        cost, node = heapq.heappop(heap)
        if cost > dist.get(node, inf):
            continue
        if node == destination:
            path: list[str] = []
            cur = destination
            while cur != source:
                path.append(cur)
                cur = prev[cur]
            path.append(source)
            path.reverse()
            return cost, path
        for neighbor, weight in adjacency.get(node, []):
            new_cost = cost + weight
            if new_cost < dist.get(neighbor, inf):
                dist[neighbor] = new_cost
                prev[neighbor] = node
                heapq.heappush(heap, (new_cost, neighbor))

    return None
