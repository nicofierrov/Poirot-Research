#!/usr/bin/env python3
"""
Example usage of the Deep Search Knowledge Graph application.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.knowledge_graph import KnowledgeGraph
from core.search_engine import SearchEngine
from core.relationship_analyzer import RelationshipAnalyzer
from core.path_analyzer import PathAnalyzer
from visualization.graph_visualizer import GraphVisualizer
from analysis.statistics import GraphStatistics


def example_basic_usage():
    """Example of basic knowledge graph usage."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Knowledge Graph Usage")
    print("=" * 70)

    # Create a knowledge graph
    kg = KnowledgeGraph()

    # Add entities
    entities = ["Python", "JavaScript", "TypeScript", "Django", "React"]
    for entity in entities:
        kg.add_entity(entity)

    # Add relationships with weights
    kg.add_relationship("Python", "Django", weight=0.9, relationship_type="framework_of")
    kg.add_relationship("JavaScript", "React", weight=0.9, relationship_type="library_of")
    kg.add_relationship("JavaScript", "TypeScript", weight=0.8, relationship_type="superset")
    kg.add_relationship("Python", "JavaScript", weight=0.6, relationship_type="similar_to")
    kg.add_relationship("Django", "React", weight=0.5, relationship_type="works_with")

    print(f"\nGraph contains {len(kg)} entities and {len(kg.get_relationships())} relationships")

    # Analyze neighborhoods
    path_analyzer = PathAnalyzer(kg)
    neighborhoods = path_analyzer.analyze_neighborhood_orders("Python", max_order=2)

    print("\nPython's neighborhood analysis:")
    for order, data in neighborhoods.items():
        print(f"  Order {order}: {data['count']} entities - {', '.join(data['entities'][:5])}")

    # Find paths
    paths = path_analyzer.find_all_connecting_paths("Python", "React", max_length=3)
    print(f"\nPaths from Python to React: {len(paths)}")
    if paths:
        print(f"  Strongest path: {' → '.join(paths[0]['path'])}")
        print(f"  Average weight: {paths[0]['average_weight']:.2f}")

    # Save graph
    kg.save_to_file("example_graph.json")
    print("\nGraph saved to example_graph.json")


def example_with_search():
    """Example using the search engine to build a graph."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Building Graph with Search Engine")
    print("=" * 70)

    # Note: This requires ANTHROPIC_API_KEY to be set
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("\nSkipping this example - ANTHROPIC_API_KEY not set")
        return

    # Create components
    kg = KnowledgeGraph()
    search_engine = SearchEngine(api_key)
    analyzer = RelationshipAnalyzer(kg, search_engine)

    # Define entities to analyze
    entities = ["OpenAI", "Anthropic", "Google AI"]
    context = "AI companies and their relationships"

    print(f"\nAnalyzing relationships between: {', '.join(entities)}")
    print(f"Context: {context}")

    # Build the graph
    analyzer.build_graph_from_entities(entities, context, threshold=0.3)

    print(f"\nGraph built with {len(kg)} entities")

    # Find strongest connections
    for entity in entities:
        strongest = analyzer.find_strongest_connections(entity, n=3)
        print(f"\nStrongest connections for {entity}:")
        for connected, weight, rel_type in strongest:
            print(f"  → {connected}: {weight:.2f} ({rel_type})")


def example_visualization():
    """Example of graph visualization."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Graph Visualization")
    print("=" * 70)

    # Create a sample graph
    kg = KnowledgeGraph()

    # Add tech companies and products
    entities = {
        "Apple": {},
        "iPhone": {},
        "MacBook": {},
        "Microsoft": {},
        "Windows": {},
        "Azure": {},
        "Google": {},
        "Android": {},
        "Cloud Computing": {}
    }

    for entity in entities:
        kg.add_entity(entity, entities[entity])

    # Add relationships
    relationships = [
        ("Apple", "iPhone", 0.95, "produces"),
        ("Apple", "MacBook", 0.95, "produces"),
        ("Microsoft", "Windows", 0.95, "produces"),
        ("Microsoft", "Azure", 0.9, "produces"),
        ("Google", "Android", 0.95, "produces"),
        ("Microsoft", "Cloud Computing", 0.8, "works_in"),
        ("Google", "Cloud Computing", 0.8, "works_in"),
        ("Azure", "Cloud Computing", 0.9, "part_of"),
        ("Apple", "Microsoft", 0.6, "competes_with"),
        ("Apple", "Google", 0.7, "competes_with"),
        ("Android", "iPhone", 0.8, "competes_with"),
    ]

    for source, target, weight, rel_type in relationships:
        kg.add_relationship(source, target, weight, rel_type)

    # Create visualizer
    visualizer = GraphVisualizer(kg)

    # Create interactive graph
    fig = visualizer.create_interactive_graph(
        title="Tech Companies Knowledge Graph",
        highlight_entities=["Apple", "Microsoft", "Google"]
    )

    # Save to HTML
    os.makedirs("output", exist_ok=True)
    visualizer.save_html(fig, "output/example_visualization.html")

    print("\nVisualization saved to output/example_visualization.html")
    print("Open this file in your browser to view the interactive graph!")


def example_statistics():
    """Example of statistical analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Statistical Analysis")
    print("=" * 70)

    # Load the graph from example 3
    kg = KnowledgeGraph()

    # Add a more complex network
    entities = ["A", "B", "C", "D", "E", "F", "G", "H"]
    for entity in entities:
        kg.add_entity(entity)

    # Create a network structure
    edges = [
        ("A", "B", 0.9), ("A", "C", 0.8), ("B", "D", 0.7),
        ("C", "D", 0.6), ("D", "E", 0.8), ("E", "F", 0.7),
        ("F", "G", 0.6), ("G", "H", 0.5), ("H", "A", 0.4),
        ("B", "E", 0.5), ("C", "F", 0.6)
    ]

    for source, target, weight in edges:
        kg.add_relationship(source, target, weight)

    # Analyze statistics
    stats = GraphStatistics(kg)

    print("\nNetwork Summary:")
    summary = stats.get_network_summary()

    print(f"  Nodes: {summary['basic_stats']['num_nodes']}")
    print(f"  Edges: {summary['basic_stats']['num_edges']}")
    print(f"  Density: {summary['basic_stats']['density']:.3f}")
    print(f"  Avg Clustering: {summary['clustering']['avg_clustering_coefficient']:.3f}")

    print("\nTop entities by PageRank:")
    for entity, score in summary['centrality']['top_pagerank'][:5]:
        print(f"  {entity}: {score:.4f}")

    print("\nCommunities detected:")
    communities = stats.detect_communities()
    for i, community in enumerate(communities, 1):
        print(f"  Community {i}: {', '.join(community)}")


def main():
    """Run all examples."""
    print("\nDeep Search Knowledge Graph - Examples\n")

    try:
        example_basic_usage()
        example_with_search()
        example_visualization()
        example_statistics()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
