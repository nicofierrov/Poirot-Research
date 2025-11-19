"""Statistical analysis for knowledge graphs."""

import networkx as nx
from typing import Dict, List, Tuple, Any
import numpy as np


class GraphStatistics:
    """
    Statistical analysis toolkit for knowledge graphs.

    Provides various metrics including centrality measures,
    clustering coefficients, and community detection.
    """

    def __init__(self, knowledge_graph):
        """
        Initialize graph statistics analyzer.

        Args:
            knowledge_graph: KnowledgeGraph instance
        """
        self.kg = knowledge_graph

    def calculate_centrality_measures(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate various centrality measures for all nodes.

        Returns:
            Dictionary mapping centrality type to node scores
        """
        G = self.kg.graph
        undirected = G.to_undirected()

        centrality = {}

        # Degree centrality
        centrality['degree'] = nx.degree_centrality(G)

        # Betweenness centrality
        try:
            centrality['betweenness'] = nx.betweenness_centrality(G)
        except:
            centrality['betweenness'] = {node: 0 for node in G.nodes()}

        # Closeness centrality
        try:
            centrality['closeness'] = nx.closeness_centrality(G)
        except:
            centrality['closeness'] = {node: 0 for node in G.nodes()}

        # Eigenvector centrality
        try:
            centrality['eigenvector'] = nx.eigenvector_centrality(G, max_iter=100)
        except:
            centrality['eigenvector'] = {node: 0 for node in G.nodes()}

        # PageRank
        try:
            centrality['pagerank'] = nx.pagerank(G)
        except:
            centrality['pagerank'] = {node: 0 for node in G.nodes()}

        return centrality

    def get_top_central_nodes(self, metric: str = 'pagerank',
                             n: int = 10) -> List[Tuple[str, float]]:
        """
        Get the top N most central nodes by a specific metric.

        Args:
            metric: Centrality metric ('degree', 'betweenness', 'closeness',
                   'eigenvector', 'pagerank')
            n: Number of top nodes to return

        Returns:
            List of tuples (node, score)
        """
        centrality = self.calculate_centrality_measures()

        if metric not in centrality:
            return []

        scores = centrality[metric]
        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return sorted_nodes[:n]

    def calculate_clustering_coefficient(self) -> Dict[str, float]:
        """
        Calculate clustering coefficient for each node.

        Returns:
            Dictionary mapping node to clustering coefficient
        """
        undirected = self.kg.graph.to_undirected()

        try:
            return nx.clustering(undirected)
        except:
            return {node: 0 for node in undirected.nodes()}

    def get_average_clustering_coefficient(self) -> float:
        """
        Calculate the average clustering coefficient for the graph.

        Returns:
            Average clustering coefficient
        """
        clustering = self.calculate_clustering_coefficient()
        if not clustering:
            return 0.0

        return sum(clustering.values()) / len(clustering)

    def detect_communities(self) -> List[List[str]]:
        """
        Detect communities in the graph using Louvain method.

        Returns:
            List of communities, where each community is a list of nodes
        """
        try:
            import networkx.algorithms.community as nx_comm

            undirected = self.kg.graph.to_undirected()

            # Use Louvain method (greedy modularity)
            communities = nx_comm.louvain_communities(undirected)

            return [list(comm) for comm in communities]
        except Exception as e:
            print(f"Community detection failed: {e}")
            # Fallback to connected components
            undirected = self.kg.graph.to_undirected()
            components = nx.connected_components(undirected)
            return [list(comp) for comp in components]

    def calculate_graph_density(self) -> float:
        """
        Calculate the density of the graph.

        Returns:
            Graph density (0-1)
        """
        return nx.density(self.kg.graph)

    def get_connected_components(self) -> List[List[str]]:
        """
        Get all connected components in the graph.

        Returns:
            List of connected components
        """
        undirected = self.kg.graph.to_undirected()
        components = nx.connected_components(undirected)
        return [list(comp) for comp in components]

    def calculate_diameter(self) -> int:
        """
        Calculate the diameter of the graph (longest shortest path).

        Returns:
            Graph diameter, or -1 if graph is not connected
        """
        undirected = self.kg.graph.to_undirected()

        if not nx.is_connected(undirected):
            return -1

        try:
            return nx.diameter(undirected)
        except:
            return -1

    def calculate_average_path_length(self) -> float:
        """
        Calculate the average shortest path length in the graph.

        Returns:
            Average path length, or -1 if graph is not connected
        """
        undirected = self.kg.graph.to_undirected()

        if not nx.is_connected(undirected):
            # Calculate for largest component
            largest_cc = max(nx.connected_components(undirected), key=len)
            subgraph = undirected.subgraph(largest_cc)
            try:
                return nx.average_shortest_path_length(subgraph)
            except:
                return -1

        try:
            return nx.average_shortest_path_length(undirected)
        except:
            return -1

    def calculate_assortativity(self) -> float:
        """
        Calculate degree assortativity coefficient.

        Measures the tendency of nodes to connect to other nodes with similar degrees.

        Returns:
            Assortativity coefficient (-1 to 1)
        """
        try:
            return nx.degree_assortativity_coefficient(self.kg.graph)
        except:
            return 0.0

    def get_degree_distribution(self) -> Dict[int, int]:
        """
        Get the degree distribution of the graph.

        Returns:
            Dictionary mapping degree to count
        """
        degrees = dict(self.kg.graph.degree())
        degree_dist = {}

        for degree in degrees.values():
            degree_dist[degree] = degree_dist.get(degree, 0) + 1

        return degree_dist

    def calculate_reciprocity(self) -> float:
        """
        Calculate the reciprocity of the directed graph.

        Measures the proportion of mutual connections.

        Returns:
            Reciprocity score (0-1)
        """
        try:
            return nx.reciprocity(self.kg.graph)
        except:
            return 0.0

    def get_network_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of network statistics.

        Returns:
            Dictionary with various network metrics
        """
        # Basic stats
        num_nodes = len(self.kg.graph.nodes())
        num_edges = len(self.kg.graph.edges())

        # Centrality
        centrality = self.calculate_centrality_measures()
        top_pagerank = self.get_top_central_nodes('pagerank', 5)
        top_betweenness = self.get_top_central_nodes('betweenness', 5)

        # Clustering
        avg_clustering = self.get_average_clustering_coefficient()

        # Connectivity
        components = self.get_connected_components()
        is_connected = len(components) == 1

        # Communities
        communities = self.detect_communities()

        # Density
        density = self.calculate_graph_density()

        # Assortativity
        assortativity = self.calculate_assortativity()

        # Reciprocity
        reciprocity = self.calculate_reciprocity()

        # Average path length and diameter
        avg_path_length = self.calculate_average_path_length()
        diameter = self.calculate_diameter()

        # Degree distribution
        degree_dist = self.get_degree_distribution()
        avg_degree = sum(k * v for k, v in degree_dist.items()) / num_nodes if num_nodes > 0 else 0

        return {
            'basic_stats': {
                'num_nodes': num_nodes,
                'num_edges': num_edges,
                'avg_degree': avg_degree,
                'density': density
            },
            'connectivity': {
                'is_connected': is_connected,
                'num_components': len(components),
                'largest_component_size': len(components[0]) if components else 0,
                'diameter': diameter,
                'avg_path_length': avg_path_length
            },
            'centrality': {
                'top_pagerank': top_pagerank,
                'top_betweenness': top_betweenness
            },
            'clustering': {
                'avg_clustering_coefficient': avg_clustering,
                'num_communities': len(communities),
                'community_sizes': [len(c) for c in communities]
            },
            'structure': {
                'assortativity': assortativity,
                'reciprocity': reciprocity
            },
            'degree_distribution': degree_dist
        }

    def compare_entity_importance(self, entities: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Compare importance metrics for a list of entities.

        Args:
            entities: List of entity names

        Returns:
            Dictionary mapping entity to importance metrics
        """
        centrality = self.calculate_centrality_measures()
        clustering = self.calculate_clustering_coefficient()

        comparison = {}

        for entity in entities:
            if entity not in self.kg.graph:
                continue

            comparison[entity] = {
                'degree_centrality': centrality['degree'].get(entity, 0),
                'betweenness_centrality': centrality['betweenness'].get(entity, 0),
                'closeness_centrality': centrality['closeness'].get(entity, 0),
                'eigenvector_centrality': centrality['eigenvector'].get(entity, 0),
                'pagerank': centrality['pagerank'].get(entity, 0),
                'clustering_coefficient': clustering.get(entity, 0)
            }

        return comparison

    def find_influential_entities(self, threshold: float = 0.1) -> List[str]:
        """
        Find entities that are influential across multiple centrality measures.

        Args:
            threshold: Minimum average centrality score

        Returns:
            List of influential entity names
        """
        centrality = self.calculate_centrality_measures()

        # Calculate average centrality across metrics
        entities = self.kg.get_entities()
        influential = []

        for entity in entities:
            scores = [
                centrality['degree'].get(entity, 0),
                centrality['betweenness'].get(entity, 0),
                centrality['pagerank'].get(entity, 0)
            ]

            avg_score = sum(scores) / len(scores)

            if avg_score >= threshold:
                influential.append(entity)

        return influential
