"""Relationship analyzer for knowledge graphs."""

from typing import List, Dict, Tuple, Optional, Set
from .knowledge_graph import KnowledgeGraph
from .search_engine import SearchEngine


class RelationshipAnalyzer:
    """
    Analyzer for discovering and evaluating relationships in a knowledge graph.
    """

    def __init__(self, knowledge_graph: KnowledgeGraph,
                 search_engine: Optional[SearchEngine] = None):
        """
        Initialize relationship analyzer.

        Args:
            knowledge_graph: KnowledgeGraph instance
            search_engine: Optional SearchEngine for discovering new relationships
        """
        self.kg = knowledge_graph
        self.search_engine = search_engine or SearchEngine()

    def build_graph_from_entities(self, entities: List[str],
                                  context: str = "",
                                  threshold: float = 0.2) -> KnowledgeGraph:
        """
        Build a knowledge graph from a list of entities.

        Args:
            entities: List of entity names
            context: Context for relationship analysis
            threshold: Minimum weight threshold for including relationships

        Returns:
            The updated knowledge graph
        """
        # Add all entities to the graph
        for entity in entities:
            if entity not in self.kg:
                # Get entity information
                entity_info = self.search_engine.search_entity_info(entity, context)
                self.kg.add_entity(entity, entity_info)

        # Analyze relationships between all pairs
        print(f"Analyzing relationships between {len(entities)} entities...")
        relationships = self.search_engine.batch_analyze_relationships(entities, context)

        # Add relationships to graph
        for rel in relationships:
            if rel.get('weight', 0) >= threshold:
                self.kg.add_relationship(
                    rel['entity1'],
                    rel['entity2'],
                    rel['weight'],
                    rel.get('relationship_type', 'related_to'),
                    {
                        'description': rel.get('description', ''),
                        'confidence': rel.get('confidence', 0.5)
                    }
                )

                # Add reverse relationship if bidirectional
                if rel.get('bidirectional', False):
                    self.kg.add_relationship(
                        rel['entity2'],
                        rel['entity1'],
                        rel['weight'],
                        rel.get('relationship_type', 'related_to'),
                        {
                            'description': rel.get('description', ''),
                            'confidence': rel.get('confidence', 0.5)
                        }
                    )

        return self.kg

    def expand_graph(self, seed_entities: List[str],
                    context: str = "",
                    expansion_order: int = 1,
                    max_per_entity: int = 3,
                    threshold: float = 0.2) -> KnowledgeGraph:
        """
        Expand the knowledge graph by discovering related entities.

        Args:
            seed_entities: Initial entities to start from
            context: Context for analysis
            expansion_order: How many levels to expand
            max_per_entity: Max related entities per entity
            threshold: Minimum weight threshold

        Returns:
            The expanded knowledge graph
        """
        # Discover new entities
        print(f"Expanding network from {len(seed_entities)} seed entities...")
        all_entities = self.search_engine.expand_entity_network(
            seed_entities,
            context,
            expansion_order,
            max_per_entity
        )

        print(f"Discovered {len(all_entities)} total entities")

        # Build graph with all entities
        return self.build_graph_from_entities(all_entities, context, threshold)

    def find_strongest_connections(self, entity: str,
                                  n: int = 5) -> List[Tuple[str, float, str]]:
        """
        Find the strongest connections for an entity.

        Args:
            entity: Source entity
            n: Number of connections to return

        Returns:
            List of tuples (connected_entity, weight, relationship_type)
        """
        if entity not in self.kg:
            return []

        relationships = self.kg.get_entity_relationships(entity)

        # Combine outgoing and incoming
        all_connections = []
        for target, weight, rel_type in relationships['outgoing']:
            all_connections.append((target, weight, rel_type, 'outgoing'))
        for source, weight, rel_type in relationships['incoming']:
            all_connections.append((source, weight, rel_type, 'incoming'))

        # Sort by weight
        all_connections.sort(key=lambda x: x[1], reverse=True)

        return [(conn[0], conn[1], conn[2]) for conn in all_connections[:n]]

    def find_connection_paths(self, entity1: str, entity2: str,
                            max_paths: int = 5,
                            max_length: int = 4) -> List[Dict]:
        """
        Find connection paths between two entities.

        Args:
            entity1: First entity
            entity2: Second entity
            max_paths: Maximum number of paths to return
            max_length: Maximum path length

        Returns:
            List of path dictionaries with path and average weight
        """
        paths = self.kg.find_all_paths(entity1, entity2, max_length)

        # Calculate weights for each path
        path_info = []
        for path in paths[:max_paths]:
            avg_weight = self.kg.get_average_path_weight(path)
            weights = self.kg.get_path_weights(path)

            path_info.append({
                'path': path,
                'length': len(path) - 1,
                'average_weight': avg_weight,
                'weights': weights,
                'strength': avg_weight / len(path) if len(path) > 0 else 0
            })

        # Sort by strength (higher is better)
        path_info.sort(key=lambda x: x['strength'], reverse=True)

        return path_info

    def get_entity_influence_score(self, entity: str) -> float:
        """
        Calculate an influence score for an entity based on its connections.

        Args:
            entity: Entity to score

        Returns:
            Influence score (0-1)
        """
        if entity not in self.kg:
            return 0.0

        relationships = self.kg.get_entity_relationships(entity)

        # Sum of all connection weights
        total_weight = sum(w for _, w, _ in relationships['outgoing'])
        total_weight += sum(w for _, w, _ in relationships['incoming'])

        # Number of connections
        num_connections = len(relationships['outgoing']) + len(relationships['incoming'])

        if num_connections == 0:
            return 0.0

        # Average weight * log(number of connections) for scaling
        import math
        avg_weight = total_weight / num_connections
        influence = avg_weight * (1 + math.log(num_connections + 1) / 10)

        return min(1.0, influence)

    def rank_entities_by_influence(self, n: int = 10) -> List[Tuple[str, float]]:
        """
        Rank all entities by their influence score.

        Args:
            n: Number of top entities to return

        Returns:
            List of tuples (entity, influence_score)
        """
        entities = self.kg.get_entities()
        scores = [(entity, self.get_entity_influence_score(entity))
                 for entity in entities]

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:n]

    def get_relationship_summary(self) -> Dict:
        """
        Get a summary of relationships in the graph.

        Returns:
            Dictionary with relationship statistics
        """
        relationships = self.kg.get_relationships()

        if not relationships:
            return {
                'total_relationships': 0,
                'average_weight': 0.0,
                'weight_distribution': {},
                'relationship_types': {}
            }

        weights = [data.get('weight', 0.5) for _, _, data in relationships]
        rel_types = [data.get('relationship_type', 'unknown')
                    for _, _, data in relationships]

        # Weight distribution
        weight_ranges = {
            'weak (0-0.3)': sum(1 for w in weights if w <= 0.3),
            'moderate (0.3-0.6)': sum(1 for w in weights if 0.3 < w <= 0.6),
            'strong (0.6-0.8)': sum(1 for w in weights if 0.6 < w <= 0.8),
            'very_strong (0.8-1.0)': sum(1 for w in weights if w > 0.8)
        }

        # Relationship type counts
        type_counts = {}
        for rt in rel_types:
            type_counts[rt] = type_counts.get(rt, 0) + 1

        return {
            'total_relationships': len(relationships),
            'average_weight': sum(weights) / len(weights),
            'min_weight': min(weights),
            'max_weight': max(weights),
            'weight_distribution': weight_ranges,
            'relationship_types': type_counts
        }
