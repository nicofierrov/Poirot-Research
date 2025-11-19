"""Path and neighborhood analysis for knowledge graphs."""

from typing import List, Dict, Set, Tuple, Optional
from .knowledge_graph import KnowledgeGraph


class PathAnalyzer:
    """
    Analyzer for paths and neighborhood analysis in knowledge graphs.

    Implements various graph traversal and analysis methods including
    neighborhood orders and path analysis.
    """

    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize path analyzer.

        Args:
            knowledge_graph: KnowledgeGraph instance
        """
        self.kg = knowledge_graph

    def analyze_neighborhood_orders(self, entity: str,
                                   max_order: int = 3) -> Dict[int, Dict]:
        """
        Analyze neighborhood at different orders for an entity.

        Args:
            entity: Source entity
            max_order: Maximum order to analyze

        Returns:
            Dictionary mapping order to neighborhood analysis
        """
        if entity not in self.kg:
            return {}

        analysis = {}

        for order in range(1, max_order + 1):
            neighbors = self.kg.get_neighbors(entity, order)

            # Get connection details for direct neighbors (order 1)
            if order == 1:
                relationships = self.kg.get_entity_relationships(entity)
                neighbor_details = []

                for target, weight, rel_type in relationships['outgoing']:
                    neighbor_details.append({
                        'entity': target,
                        'weight': weight,
                        'relationship_type': rel_type,
                        'direction': 'outgoing'
                    })

                for source, weight, rel_type in relationships['incoming']:
                    neighbor_details.append({
                        'entity': source,
                        'weight': weight,
                        'relationship_type': rel_type,
                        'direction': 'incoming'
                    })

                analysis[order] = {
                    'count': len(neighbors),
                    'entities': list(neighbors),
                    'details': neighbor_details,
                    'average_weight': sum(d['weight'] for d in neighbor_details) / len(neighbor_details) if neighbor_details else 0
                }
            else:
                analysis[order] = {
                    'count': len(neighbors),
                    'entities': list(neighbors)
                }

        return analysis

    def find_multi_hop_paths(self, source: str, target: str,
                           min_hops: int = 1,
                           max_hops: int = 4) -> Dict[int, List[Dict]]:
        """
        Find paths of different lengths between two entities.

        Args:
            source: Source entity
            target: Target entity
            min_hops: Minimum path length
            max_hops: Maximum path length

        Returns:
            Dictionary mapping hop count to list of path info
        """
        paths_by_length = {}

        for hop_count in range(min_hops, max_hops + 1):
            paths = self.kg.find_all_paths(source, target, max_length=hop_count)

            # Filter to exact length
            exact_length_paths = [p for p in paths if len(p) - 1 == hop_count]

            if exact_length_paths:
                path_infos = []
                for path in exact_length_paths:
                    weights = self.kg.get_path_weights(path)
                    avg_weight = sum(weights) / len(weights) if weights else 0

                    path_infos.append({
                        'path': path,
                        'weights': weights,
                        'average_weight': avg_weight,
                        'min_weight': min(weights) if weights else 0,
                        'max_weight': max(weights) if weights else 0
                    })

                # Sort by average weight
                path_infos.sort(key=lambda x: x['average_weight'], reverse=True)
                paths_by_length[hop_count] = path_infos

        return paths_by_length

    def find_all_connecting_paths(self, entity1: str, entity2: str,
                                 max_length: int = 5) -> List[Dict]:
        """
        Find all paths connecting two entities with detailed analysis.

        Args:
            entity1: First entity
            entity2: Second entity
            max_length: Maximum path length

        Returns:
            List of path dictionaries with analysis
        """
        # Find paths in both directions
        paths_1_to_2 = self.kg.find_all_paths(entity1, entity2, max_length)
        paths_2_to_1 = self.kg.find_all_paths(entity2, entity1, max_length)

        all_path_infos = []

        # Analyze paths from entity1 to entity2
        for path in paths_1_to_2:
            weights = self.kg.get_path_weights(path)
            all_path_infos.append({
                'path': path,
                'direction': f'{entity1} → {entity2}',
                'length': len(path) - 1,
                'weights': weights,
                'average_weight': sum(weights) / len(weights) if weights else 0,
                'strength_score': self._calculate_path_strength(path)
            })

        # Analyze paths from entity2 to entity1
        for path in paths_2_to_1:
            weights = self.kg.get_path_weights(path)
            all_path_infos.append({
                'path': path,
                'direction': f'{entity2} → {entity1}',
                'length': len(path) - 1,
                'weights': weights,
                'average_weight': sum(weights) / len(weights) if weights else 0,
                'strength_score': self._calculate_path_strength(path)
            })

        # Sort by strength score
        all_path_infos.sort(key=lambda x: x['strength_score'], reverse=True)

        return all_path_infos

    def _calculate_path_strength(self, path: List[str]) -> float:
        """
        Calculate overall strength of a path.

        Considers both average weight and path length.
        Shorter, higher-weight paths are stronger.

        Args:
            path: List of entities in the path

        Returns:
            Strength score (0-1)
        """
        if len(path) < 2:
            return 0.0

        weights = self.kg.get_path_weights(path)
        if not weights:
            return 0.0

        avg_weight = sum(weights) / len(weights)
        path_length = len(path) - 1

        # Penalize longer paths
        length_penalty = 1 / (1 + (path_length - 1) * 0.2)

        return avg_weight * length_penalty

    def find_common_neighbors(self, entity1: str, entity2: str,
                             order: int = 1) -> Set[str]:
        """
        Find common neighbors between two entities at a given order.

        Args:
            entity1: First entity
            entity2: Second entity
            order: Neighborhood order

        Returns:
            Set of common neighbors
        """
        neighbors1 = self.kg.get_neighbors(entity1, order)
        neighbors2 = self.kg.get_neighbors(entity2, order)

        return neighbors1 & neighbors2

    def analyze_entity_connectivity(self, entity: str,
                                   max_order: int = 3) -> Dict:
        """
        Comprehensive connectivity analysis for an entity.

        Args:
            entity: Entity to analyze
            max_order: Maximum neighborhood order to analyze

        Returns:
            Dictionary with connectivity metrics
        """
        if entity not in self.kg:
            return {
                'entity': entity,
                'exists': False
            }

        # Get neighborhood analysis
        neighborhoods = self.analyze_neighborhood_orders(entity, max_order)

        # Calculate reachability
        total_reachable = set()
        for order in range(1, max_order + 1):
            if order in neighborhoods:
                total_reachable.update(neighborhoods[order]['entities'])

        # Get direct connections
        relationships = self.kg.get_entity_relationships(entity)
        total_connections = len(relationships['outgoing']) + len(relationships['incoming'])

        return {
            'entity': entity,
            'exists': True,
            'direct_connections': total_connections,
            'outgoing_connections': len(relationships['outgoing']),
            'incoming_connections': len(relationships['incoming']),
            'neighborhoods': neighborhoods,
            'total_reachable': len(total_reachable),
            'reachable_entities': list(total_reachable)
        }

    def find_bridges(self) -> List[Tuple[str, str]]:
        """
        Find bridge edges in the graph.

        Bridge edges are edges whose removal would disconnect the graph.

        Returns:
            List of bridge edges as tuples (source, target)
        """
        import networkx as nx

        # Convert to undirected for bridge detection
        undirected = self.kg.graph.to_undirected()

        # Find bridges
        bridges = list(nx.bridges(undirected))

        return bridges

    def find_critical_entities(self) -> List[Tuple[str, int]]:
        """
        Find critical entities whose removal would most impact connectivity.

        Returns:
            List of tuples (entity, number_of_components_if_removed)
        """
        import networkx as nx

        entities = self.kg.get_entities()
        undirected = self.kg.graph.to_undirected()

        # Current number of connected components
        current_components = nx.number_connected_components(undirected)

        critical_entities = []

        for entity in entities:
            # Create temporary graph without this entity
            temp_graph = undirected.copy()
            temp_graph.remove_node(entity)

            # Count components
            new_components = nx.number_connected_components(temp_graph)

            if new_components > current_components:
                critical_entities.append((entity, new_components))

        # Sort by impact (descending)
        critical_entities.sort(key=lambda x: x[1], reverse=True)

        return critical_entities

    def get_path_summary(self, entity1: str, entity2: str) -> Dict:
        """
        Get a comprehensive summary of paths between two entities.

        Args:
            entity1: First entity
            entity2: Second entity

        Returns:
            Dictionary with path summary
        """
        shortest_path = self.kg.find_shortest_path(entity1, entity2)
        all_paths = self.find_all_connecting_paths(entity1, entity2)

        if not all_paths and not shortest_path:
            return {
                'entity1': entity1,
                'entity2': entity2,
                'connected': False,
                'shortest_path': None,
                'path_count': 0
            }

        return {
            'entity1': entity1,
            'entity2': entity2,
            'connected': True,
            'shortest_path': shortest_path,
            'shortest_path_length': len(shortest_path) - 1 if shortest_path else None,
            'path_count': len(all_paths),
            'strongest_path': all_paths[0] if all_paths else None,
            'all_paths': all_paths[:10]  # Limit to top 10
        }
