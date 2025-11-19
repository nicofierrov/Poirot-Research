"""Graph visualization using Plotly."""

import plotly.graph_objects as go
import networkx as nx
from typing import Optional, Dict, List, Tuple
import math


class GraphVisualizer:
    """
    Visualizer for knowledge graphs using Plotly.

    Creates interactive visualizations with nodes sized by importance
    and edges colored by relationship strength.
    """

    def __init__(self, knowledge_graph):
        """
        Initialize graph visualizer.

        Args:
            knowledge_graph: KnowledgeGraph instance
        """
        self.kg = knowledge_graph

    def create_interactive_graph(self,
                                title: str = "Knowledge Graph",
                                layout: str = "spring",
                                highlight_entities: Optional[List[str]] = None,
                                show_edge_labels: bool = False) -> go.Figure:
        """
        Create an interactive Plotly visualization of the knowledge graph.

        Args:
            title: Graph title
            layout: Layout algorithm ('spring', 'circular', 'kamada_kawai')
            highlight_entities: List of entities to highlight
            show_edge_labels: Whether to show edge labels

        Returns:
            Plotly Figure object
        """
        # Get graph positions using NetworkX layout
        G = self.kg.graph.to_undirected()

        if len(G.nodes()) == 0:
            # Empty graph
            fig = go.Figure()
            fig.update_layout(title="Empty Knowledge Graph")
            return fig

        # Choose layout algorithm
        if layout == "spring":
            pos = nx.spring_layout(G, k=1, iterations=50)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        else:
            pos = nx.spring_layout(G)

        # Create edge traces
        edge_traces = self._create_edge_traces(pos, show_edge_labels)

        # Create node trace
        node_trace = self._create_node_trace(pos, highlight_entities)

        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])

        # Update layout
        fig.update_layout(
            title=title,
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            height=700
        )

        return fig

    def _create_edge_traces(self, pos: Dict, show_labels: bool = False) -> List[go.Scatter]:
        """
        Create edge traces for the graph.

        Args:
            pos: Node positions dictionary
            show_labels: Whether to show edge labels

        Returns:
            List of Plotly Scatter traces for edges
        """
        edge_traces = []

        # Group edges by weight range for coloring
        edges_by_weight = {
            'weak': [],
            'moderate': [],
            'strong': [],
            'very_strong': []
        }

        for u, v, data in self.kg.graph.edges(data=True):
            weight = data.get('weight', 0.5)

            if weight <= 0.3:
                category = 'weak'
            elif weight <= 0.6:
                category = 'moderate'
            elif weight <= 0.8:
                category = 'strong'
            else:
                category = 'very_strong'

            edges_by_weight[category].append((u, v, weight, data))

        # Create traces for each weight category
        colors = {
            'weak': 'rgba(180, 180, 180, 0.3)',
            'moderate': 'rgba(100, 150, 200, 0.5)',
            'strong': 'rgba(50, 100, 200, 0.7)',
            'very_strong': 'rgba(0, 50, 200, 0.9)'
        }

        widths = {
            'weak': 1,
            'moderate': 2,
            'strong': 3,
            'very_strong': 4
        }

        for category, edges in edges_by_weight.items():
            if not edges:
                continue

            edge_x = []
            edge_y = []

            for u, v, weight, data in edges:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=widths[category], color=colors[category]),
                hoverinfo='none',
                mode='lines',
                name=f'{category} connections'
            )

            edge_traces.append(edge_trace)

        return edge_traces

    def _create_node_trace(self, pos: Dict,
                          highlight_entities: Optional[List[str]] = None) -> go.Scatter:
        """
        Create node trace for the graph.

        Args:
            pos: Node positions dictionary
            highlight_entities: Entities to highlight

        Returns:
            Plotly Scatter trace for nodes
        """
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []

        highlight_set = set(highlight_entities) if highlight_entities else set()

        for node in self.kg.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # Get node connections for sizing
            relationships = self.kg.get_entity_relationships(node)
            num_connections = (len(relationships['outgoing']) +
                             len(relationships['incoming']))

            # Calculate node size based on connections
            size = 20 + min(num_connections * 5, 50)
            node_size.append(size)

            # Highlight specified entities
            if node in highlight_set:
                node_color.append('red')
            else:
                node_color.append('lightblue')

            # Create hover text
            hover_text = f"<b>{node}</b><br>"
            hover_text += f"Connections: {num_connections}<br>"

            if relationships['outgoing']:
                hover_text += "<br><b>Connected to:</b><br>"
                for target, weight, rel_type in relationships['outgoing'][:5]:
                    hover_text += f"  → {target} ({weight:.2f})<br>"

            node_text.append(hover_text)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[node for node in self.kg.graph.nodes()],
            textposition="top center",
            textfont=dict(size=10),
            hovertext=node_text,
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white'),
                colorbar=dict(
                    thickness=15,
                    title='Node Importance',
                    xanchor='left',
                    titleside='right'
                )
            )
        )

        return node_trace

    def visualize_path(self, path: List[str],
                      title: str = "Path Visualization") -> go.Figure:
        """
        Visualize a specific path in the graph.

        Args:
            path: List of entities forming the path
            title: Visualization title

        Returns:
            Plotly Figure object
        """
        # Create subgraph with path nodes and their immediate neighbors
        path_set = set(path)
        nodes_to_include = set(path)

        # Add immediate neighbors of path nodes
        for entity in path:
            if entity in self.kg:
                neighbors = self.kg.get_neighbors(entity, order=1)
                nodes_to_include.update(list(neighbors)[:3])  # Limit neighbors

        # Create subgraph
        subgraph = self.kg.graph.subgraph(nodes_to_include)

        # Get positions
        pos = nx.spring_layout(subgraph.to_undirected(), k=1, iterations=50)

        # Create visualization highlighting the path
        fig = self.create_interactive_graph(
            title=title,
            highlight_entities=path
        )

        return fig

    def create_neighborhood_visualization(self, entity: str,
                                         max_order: int = 2,
                                         title: Optional[str] = None) -> go.Figure:
        """
        Visualize the neighborhood of an entity.

        Args:
            entity: Central entity
            max_order: Maximum neighborhood order to include
            title: Visualization title

        Returns:
            Plotly Figure object
        """
        if title is None:
            title = f"Neighborhood of {entity}"

        # Get all neighbors up to max_order
        all_neighbors = set([entity])
        for order in range(1, max_order + 1):
            neighbors = self.kg.get_neighbors(entity, order)
            all_neighbors.update(neighbors)

        # Create subgraph
        if len(all_neighbors) > 1:
            subgraph = self.kg.graph.subgraph(all_neighbors)
            pos = nx.spring_layout(subgraph.to_undirected(), k=1, iterations=50)
        else:
            return go.Figure().update_layout(title=f"{entity} has no neighbors")

        # Create visualization highlighting the central entity
        return self.create_interactive_graph(
            title=title,
            highlight_entities=[entity]
        )

    def save_html(self, fig: go.Figure, filename: str):
        """
        Save visualization to HTML file.

        Args:
            fig: Plotly Figure object
            filename: Output filename
        """
        fig.write_html(filename)

    def create_weight_distribution_chart(self) -> go.Figure:
        """
        Create a histogram of relationship weights.

        Returns:
            Plotly Figure object
        """
        relationships = self.kg.get_relationships()
        weights = [data.get('weight', 0.5) for _, _, data in relationships]

        fig = go.Figure(data=[go.Histogram(
            x=weights,
            nbinsx=20,
            marker_color='lightblue',
            marker_line_color='darkblue',
            marker_line_width=1
        )])

        fig.update_layout(
            title='Distribution of Relationship Weights',
            xaxis_title='Weight',
            yaxis_title='Count',
            showlegend=False
        )

        return fig

    def create_degree_distribution_chart(self) -> go.Figure:
        """
        Create a bar chart of node degree distribution.

        Returns:
            Plotly Figure object
        """
        entities = self.kg.get_entities()
        degrees = []

        for entity in entities:
            relationships = self.kg.get_entity_relationships(entity)
            degree = len(relationships['outgoing']) + len(relationships['incoming'])
            degrees.append((entity, degree))

        # Sort by degree
        degrees.sort(key=lambda x: x[1], reverse=True)

        # Take top 20
        top_entities = degrees[:20]

        fig = go.Figure(data=[go.Bar(
            x=[e[0] for e in top_entities],
            y=[e[1] for e in top_entities],
            marker_color='lightgreen',
            marker_line_color='darkgreen',
            marker_line_width=1
        )])

        fig.update_layout(
            title='Top 20 Entities by Connection Count',
            xaxis_title='Entity',
            yaxis_title='Number of Connections',
            showlegend=False
        )

        return fig
