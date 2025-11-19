#!/usr/bin/env python3
"""
Basic test to verify the installation and core functionality.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from core.knowledge_graph import KnowledgeGraph
        from core.search_engine import SearchEngine
        from core.relationship_analyzer import RelationshipAnalyzer
        from core.path_analyzer import PathAnalyzer
        from visualization.graph_visualizer import GraphVisualizer
        from analysis.statistics import GraphStatistics
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_basic_graph():
    """Test basic graph operations."""
    print("\nTesting basic graph operations...")

    try:
        from core.knowledge_graph import KnowledgeGraph

        kg = KnowledgeGraph()
        kg.add_entity("A")
        kg.add_entity("B")
        kg.add_relationship("A", "B", weight=0.8)

        assert len(kg) == 2, "Should have 2 entities"
        assert len(kg.get_relationships()) == 1, "Should have 1 relationship"
        assert "A" in kg, "Should contain entity A"

        neighbors = kg.get_neighbors("A", order=1)
        assert "B" in neighbors, "B should be neighbor of A"

        print("✓ Basic graph operations work")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_path_analysis():
    """Test path analysis."""
    print("\nTesting path analysis...")

    try:
        from core.knowledge_graph import KnowledgeGraph
        from core.path_analyzer import PathAnalyzer

        kg = KnowledgeGraph()
        kg.add_entity("A")
        kg.add_entity("B")
        kg.add_entity("C")
        kg.add_relationship("A", "B", weight=0.8)
        kg.add_relationship("B", "C", weight=0.7)

        path_analyzer = PathAnalyzer(kg)
        path = kg.find_shortest_path("A", "C")

        assert path == ["A", "B", "C"], "Shortest path should be A->B->C"

        neighborhoods = path_analyzer.analyze_neighborhood_orders("A", max_order=2)
        assert 1 in neighborhoods, "Should have order 1 neighbors"
        assert 2 in neighborhoods, "Should have order 2 neighbors"

        print("✓ Path analysis works")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_statistics():
    """Test statistics calculation."""
    print("\nTesting statistics...")

    try:
        from core.knowledge_graph import KnowledgeGraph
        from analysis.statistics import GraphStatistics

        kg = KnowledgeGraph()
        for i in range(5):
            kg.add_entity(f"Node{i}")

        kg.add_relationship("Node0", "Node1", weight=0.8)
        kg.add_relationship("Node1", "Node2", weight=0.7)
        kg.add_relationship("Node2", "Node3", weight=0.9)
        kg.add_relationship("Node3", "Node4", weight=0.6)
        kg.add_relationship("Node0", "Node4", weight=0.5)

        stats = GraphStatistics(kg)
        centrality = stats.calculate_centrality_measures()

        assert 'pagerank' in centrality, "Should calculate PageRank"
        assert 'degree' in centrality, "Should calculate degree centrality"

        density = stats.calculate_graph_density()
        assert 0 <= density <= 1, "Density should be between 0 and 1"

        print("✓ Statistics calculation works")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization():
    """Test visualization creation."""
    print("\nTesting visualization...")

    try:
        from core.knowledge_graph import KnowledgeGraph
        from visualization.graph_visualizer import GraphVisualizer

        kg = KnowledgeGraph()
        kg.add_entity("A")
        kg.add_entity("B")
        kg.add_relationship("A", "B", weight=0.8)

        visualizer = GraphVisualizer(kg)
        fig = visualizer.create_interactive_graph()

        assert fig is not None, "Should create a figure"

        print("✓ Visualization creation works")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Deep Search Knowledge Graph - Basic Tests")
    print("=" * 60)

    tests = [
        test_imports,
        test_basic_graph,
        test_path_analysis,
        test_statistics,
        test_visualization
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)

    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)

    if all(results):
        print("\n✓ All tests passed! The application is ready to use.")
        print("\nTry running:")
        print('  python main.py -e "Python" "JavaScript" -c "Programming languages"')
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
