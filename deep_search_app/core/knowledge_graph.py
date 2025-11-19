"""Knowledge Graph implementation using NetworkX."""

import networkx as nx
from typing import List, Dict, Tuple, Set, Optional, Any
import json


class KnowledgeGraph:
    """
    A knowledge graph for storing and analyzing entity relationships.

    Uses NetworkX for graph operations and supports weighted edges
    representing relationship strength (0-1 scale).
    """

    def __init__(self):
        """Initialize an empty directed graph."""
        self.graph = nx.DiGraph()
        self.entity_data = {}  # Store additional metadata for entities

    def add_entity(self, entity: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add an entity to the knowledge graph.

        Args:
            entity: Name of the entity
            metadata: Optional metadata dictionary for the entity
        """
        self.graph.add_node(entity)
        if metadata:
            self.entity_data[entity] = metadata

    def add_relationship(self, source: str, target: str,
                        weight: float = 0.5,
                        relationship_type: str = "related_to",
                        metadata: Optional[Dict[str, Any]] = None):
        """
        Add a weighted relationship between two entities.

        Args:
            source: Source entity
            target: Target entity
            weight: Relationship strength (0-1 scale)
            relationship_type: Type of relationship
            metadata: Optional metadata for the relationship
        """
        # Ensure weight is in valid range
        weight = max(0.0, min(1.0, weight))

        # Ensure both entities exist
        if source not in self.graph:
            self.add_entity(source)
        if target not in self.graph:
            self.add_entity(target)

        # Add edge with attributes
        self.graph.add_edge(
            source,
            target,
            weight=weight,
            relationship_type=relationship_type,
            metadata=metadata or {}
        )

    def get_entities(self) -> List[str]:
        """Get all entities in the graph."""
        return list(self.graph.nodes())

    def get_relationships(self) -> List[Tuple[str, str, Dict]]:
        """
        Get all relationships in the graph.

        Returns:
            List of tuples (source, target, attributes)
        """
        return [(u, v, data) for u, v, data in self.graph.edges(data=True)]

    def get_entity_relationships(self, entity: str) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get all relationships for a specific entity.

        Args:
            entity: Entity name

        Returns:
            Dict with 'outgoing' and 'incoming' relationships
        """
        if entity not in self.graph:
            return {'outgoing': [], 'incoming': []}

        outgoing = [
            (target, data.get('weight', 0.5), data.get('relationship_type', 'related_to'))
            for _, target, data in self.graph.out_edges(entity, data=True)
        ]

        incoming = [
            (source, data.get('weight', 0.5), data.get('relationship_type', 'related_to'))
            for source, _, data in self.graph.in_edges(entity, data=True)
        ]

        return {
            'outgoing': outgoing,
            'incoming': incoming
        }

    def get_neighbors(self, entity: str, order: int = 1) -> Set[str]:
        """
        Get neighbors at a specific order (distance) from an entity.

        Args:
            entity: Source entity
            order: Distance (1 = direct neighbors, 2 = neighbors of neighbors, etc.)

        Returns:
            Set of entities at the specified distance
        """
        if entity not in self.graph:
            return set()

        # Convert to undirected for neighbor analysis
        undirected = self.graph.to_undirected()

        if order == 1:
            return set(undirected.neighbors(entity))

        # For higher orders, use BFS
        current_level = {entity}
        visited = {entity}

        for _ in range(order):
            next_level = set()
            for node in current_level:
                neighbors = set(undirected.neighbors(node))
                next_level.update(neighbors - visited)
            visited.update(next_level)
            current_level = next_level

        return current_level

    def get_all_neighbors_up_to_order(self, entity: str, max_order: int = 3) -> Dict[int, Set[str]]:
        """
        Get neighbors at all orders up to max_order.

        Args:
            entity: Source entity
            max_order: Maximum distance to explore

        Returns:
            Dictionary mapping order to set of entities
        """
        neighbors_by_order = {}

        for order in range(1, max_order + 1):
            neighbors_by_order[order] = self.get_neighbors(entity, order)

        return neighbors_by_order

    def find_all_paths(self, source: str, target: str,
                      max_length: Optional[int] = None) -> List[List[str]]:
        """
        Find all simple paths between two entities.

        Args:
            source: Source entity
            target: Target entity
            max_length: Maximum path length (None for unlimited)

        Returns:
            List of paths, where each path is a list of entities
        """
        if source not in self.graph or target not in self.graph:
            return []

        try:
            if max_length:
                paths = nx.all_simple_paths(self.graph, source, target, cutoff=max_length)
            else:
                paths = nx.all_simple_paths(self.graph, source, target)
            return list(paths)
        except nx.NetworkXNoPath:
            return []

    def find_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find the shortest path between two entities.

        Args:
            source: Source entity
            target: Target entity

        Returns:
            Shortest path as list of entities, or None if no path exists
        """
        if source not in self.graph or target not in self.graph:
            return None

        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return None

    def get_path_weights(self, path: List[str]) -> List[float]:
        """
        Get the weights of edges along a path.

        Args:
            path: List of entities forming a path

        Returns:
            List of edge weights
        """
        weights = []
        for i in range(len(path) - 1):
            if self.graph.has_edge(path[i], path[i + 1]):
                weight = self.graph[path[i]][path[i + 1]].get('weight', 0.5)
                weights.append(weight)
        return weights

    def get_average_path_weight(self, path: List[str]) -> float:
        """
        Calculate the average weight along a path.

        Args:
            path: List of entities forming a path

        Returns:
            Average weight of the path
        """
        weights = self.get_path_weights(path)
        return sum(weights) / len(weights) if weights else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Export graph to dictionary format.

        Returns:
            Dictionary representation of the graph
        """
        return {
            'nodes': [
                {
                    'id': node,
                    'metadata': self.entity_data.get(node, {})
                }
                for node in self.graph.nodes()
            ],
            'edges': [
                {
                    'source': u,
                    'target': v,
                    'weight': data.get('weight', 0.5),
                    'relationship_type': data.get('relationship_type', 'related_to'),
                    'metadata': data.get('metadata', {})
                }
                for u, v, data in self.graph.edges(data=True)
            ]
        }

    def save_to_file(self, filename: str):
        """
        Save graph to JSON file.

        Args:
            filename: Path to output file
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeGraph':
        """
        Create a KnowledgeGraph from dictionary data.

        Args:
            data: Dictionary with 'nodes' and 'edges' keys

        Returns:
            New KnowledgeGraph instance
        """
        kg = cls()

        # Add nodes
        for node_data in data.get('nodes', []):
            kg.add_entity(node_data['id'], node_data.get('metadata'))

        # Add edges
        for edge_data in data.get('edges', []):
            kg.add_relationship(
                edge_data['source'],
                edge_data['target'],
                edge_data.get('weight', 0.5),
                edge_data.get('relationship_type', 'related_to'),
                edge_data.get('metadata')
            )

        return kg

    @classmethod
    def load_from_file(cls, filename: str) -> 'KnowledgeGraph':
        """
        Load graph from JSON file.

        Args:
            filename: Path to input file

        Returns:
            KnowledgeGraph instance
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __len__(self) -> int:
        """Return number of entities in the graph."""
        return len(self.graph.nodes())

    def __contains__(self, entity: str) -> bool:
        """Check if entity exists in graph."""
        return entity in self.graph
