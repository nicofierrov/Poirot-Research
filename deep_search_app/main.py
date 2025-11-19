#!/usr/bin/env python3
"""
Deep Search Knowledge Graph Application

Performs deep research using network analysis and knowledge graphs
to find relevant relationships between entities.
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Optional
from dotenv import load_dotenv
from colorama import init, Fore, Style

from core.knowledge_graph import KnowledgeGraph
from core.search_engine import SearchEngine
from core.relationship_analyzer import RelationshipAnalyzer
from core.path_analyzer import PathAnalyzer
from visualization.graph_visualizer import GraphVisualizer
from analysis.statistics import GraphStatistics


# Initialize colorama
init(autoreset=True)


class DeepSearchApp:
    """
    Main application for deep search knowledge graph analysis.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the deep search application.

        Args:
            api_key: Anthropic API key (optional)
        """
        self.kg = KnowledgeGraph()
        self.search_engine = SearchEngine(api_key)
        self.analyzer = RelationshipAnalyzer(self.kg, self.search_engine)
        self.path_analyzer = PathAnalyzer(self.kg)
        self.visualizer = GraphVisualizer(self.kg)
        self.statistics = GraphStatistics(self.kg)

    def deep_search(self,
                   entities: List[str],
                   context: str = "",
                   expand: bool = True,
                   expansion_order: int = 1,
                   max_per_entity: int = 3,
                   threshold: float = 0.2,
                   output_dir: str = "output") -> Dict:
        """
        Perform a deep search on the given entities.

        Args:
            entities: List of entities to analyze
            context: Additional context for the search
            expand: Whether to expand the network
            expansion_order: How many levels to expand
            max_per_entity: Max related entities per entity
            threshold: Minimum relationship weight threshold
            output_dir: Directory for output files

        Returns:
            Dictionary with search results
        """
        print(f"\n{Fore.CYAN}{'=' * 70}")
        print(f"{Fore.CYAN}DEEP SEARCH - Knowledge Graph Analysis")
        print(f"{Fore.CYAN}{'=' * 70}\n")

        print(f"{Fore.YELLOW}Entities to analyze: {Fore.WHITE}{', '.join(entities)}")
        print(f"{Fore.YELLOW}Context: {Fore.WHITE}{context or 'General analysis'}\n")

        # Step 1: Build or expand the knowledge graph
        if expand:
            print(f"{Fore.GREEN}[1/5] Expanding entity network (order={expansion_order})...")
            self.analyzer.expand_graph(
                entities,
                context,
                expansion_order,
                max_per_entity,
                threshold
            )
        else:
            print(f"{Fore.GREEN}[1/5] Building knowledge graph...")
            self.analyzer.build_graph_from_entities(entities, context, threshold)

        print(f"{Fore.WHITE}   ✓ Graph contains {len(self.kg)} entities and {len(self.kg.get_relationships())} relationships\n")

        # Step 2: Analyze neighborhoods
        print(f"{Fore.GREEN}[2/5] Analyzing neighborhood orders...")
        neighborhood_analysis = self._analyze_neighborhoods(entities)
        print(f"{Fore.WHITE}   ✓ Neighborhood analysis complete\n")

        # Step 3: Analyze paths
        print(f"{Fore.GREEN}[3/5] Analyzing connection paths...")
        path_analysis = self._analyze_paths(entities)
        print(f"{Fore.WHITE}   ✓ Path analysis complete\n")

        # Step 4: Calculate statistics
        print(f"{Fore.GREEN}[4/5] Calculating network statistics...")
        stats = self.statistics.get_network_summary()
        print(f"{Fore.WHITE}   ✓ Statistical analysis complete\n")

        # Step 5: Generate visualizations
        print(f"{Fore.GREEN}[5/5] Generating visualizations...")
        os.makedirs(output_dir, exist_ok=True)
        self._generate_visualizations(entities, output_dir)
        print(f"{Fore.WHITE}   ✓ Visualizations saved to {output_dir}/\n")

        # Generate conclusions
        conclusions = self._generate_conclusions(
            entities,
            neighborhood_analysis,
            path_analysis,
            stats
        )

        # Save results
        results = {
            'entities': entities,
            'context': context,
            'neighborhood_analysis': neighborhood_analysis,
            'path_analysis': path_analysis,
            'statistics': stats,
            'conclusions': conclusions,
            'graph_data': self.kg.to_dict()
        }

        results_file = os.path.join(output_dir, 'results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Save graph
        graph_file = os.path.join(output_dir, 'knowledge_graph.json')
        self.kg.save_to_file(graph_file)

        # Display results
        self._display_results(conclusions, stats)

        return results

    def _analyze_neighborhoods(self, entities: List[str]) -> Dict:
        """Analyze neighborhoods for each entity."""
        neighborhoods = {}

        for entity in entities:
            if entity in self.kg:
                neighborhoods[entity] = self.path_analyzer.analyze_neighborhood_orders(
                    entity,
                    max_order=3
                )

        return neighborhoods

    def _analyze_paths(self, entities: List[str]) -> Dict:
        """Analyze paths between all entity pairs."""
        paths = {}

        for i, entity1 in enumerate(entities):
            for entity2 in entities[i + 1:]:
                if entity1 in self.kg and entity2 in self.kg:
                    path_summary = self.path_analyzer.get_path_summary(entity1, entity2)
                    if path_summary['connected']:
                        paths[f"{entity1} <-> {entity2}"] = path_summary

        return paths

    def _generate_visualizations(self, entities: List[str], output_dir: str):
        """Generate and save visualizations."""
        # Main graph visualization
        fig = self.visualizer.create_interactive_graph(
            title="Knowledge Graph - Deep Search Results",
            highlight_entities=entities
        )
        self.visualizer.save_html(fig, os.path.join(output_dir, 'graph_interactive.html'))

        # Weight distribution
        fig_weights = self.visualizer.create_weight_distribution_chart()
        fig_weights.write_html(os.path.join(output_dir, 'weight_distribution.html'))

        # Degree distribution
        fig_degree = self.visualizer.create_degree_distribution_chart()
        fig_degree.write_html(os.path.join(output_dir, 'degree_distribution.html'))

    def _generate_conclusions(self,
                            entities: List[str],
                            neighborhoods: Dict,
                            paths: Dict,
                            stats: Dict) -> List[str]:
        """Generate conclusions from the analysis."""
        conclusions = []

        # Graph size conclusion
        num_entities = stats['basic_stats']['num_nodes']
        num_relationships = stats['basic_stats']['num_edges']
        conclusions.append(
            f"Analyzed a network of {num_entities} entities with {num_relationships} relationships"
        )

        # Connectivity conclusion
        if stats['connectivity']['is_connected']:
            conclusions.append(
                f"The network is fully connected with an average path length of {stats['connectivity']['avg_path_length']:.2f}"
            )
        else:
            conclusions.append(
                f"The network has {stats['connectivity']['num_components']} disconnected components"
            )

        # Relationship strength conclusion
        avg_weight = sum(
            data.get('weight', 0) for _, _, data in self.kg.get_relationships()
        ) / max(num_relationships, 1)

        if avg_weight >= 0.7:
            strength = "very strong"
        elif avg_weight >= 0.5:
            strength = "strong"
        elif avg_weight >= 0.3:
            strength = "moderate"
        else:
            strength = "weak"

        conclusions.append(
            f"Overall relationship strength is {strength} (average weight: {avg_weight:.2f})"
        )

        # Most influential entities
        top_entities = stats['centrality']['top_pagerank'][:3]
        if top_entities:
            influential = ", ".join([f"{e[0]} ({e[1]:.3f})" for e in top_entities])
            conclusions.append(
                f"Most influential entities: {influential}"
            )

        # Path analysis conclusion
        if paths:
            shortest_paths = [p for p in paths.values() if p.get('shortest_path_length')]
            if shortest_paths:
                avg_shortest = sum(p['shortest_path_length'] for p in shortest_paths) / len(shortest_paths)
                conclusions.append(
                    f"Query entities are connected with an average distance of {avg_shortest:.1f} hops"
                )

        # Community structure
        num_communities = stats['clustering']['num_communities']
        if num_communities > 1:
            conclusions.append(
                f"Detected {num_communities} distinct communities in the network"
            )

        # Clustering
        avg_clustering = stats['clustering']['avg_clustering_coefficient']
        if avg_clustering > 0.5:
            conclusions.append(
                f"High clustering coefficient ({avg_clustering:.2f}) indicates strong local connections"
            )

        return conclusions

    def _display_results(self, conclusions: List[str], stats: Dict):
        """Display results in the terminal."""
        print(f"\n{Fore.CYAN}{'=' * 70}")
        print(f"{Fore.CYAN}CONCLUSIONS")
        print(f"{Fore.CYAN}{'=' * 70}\n")

        for i, conclusion in enumerate(conclusions, 1):
            print(f"{Fore.GREEN}{i}. {Fore.WHITE}{conclusion}")

        print(f"\n{Fore.CYAN}{'=' * 70}")
        print(f"{Fore.CYAN}KEY STATISTICS")
        print(f"{Fore.CYAN}{'=' * 70}\n")

        print(f"{Fore.YELLOW}Network Structure:")
        print(f"  • Entities: {Fore.WHITE}{stats['basic_stats']['num_nodes']}")
        print(f"{Fore.YELLOW}  • Relationships: {Fore.WHITE}{stats['basic_stats']['num_edges']}")
        print(f"{Fore.YELLOW}  • Density: {Fore.WHITE}{stats['basic_stats']['density']:.3f}")
        print(f"{Fore.YELLOW}  • Avg Degree: {Fore.WHITE}{stats['basic_stats']['avg_degree']:.2f}")

        print(f"\n{Fore.YELLOW}Connectivity:")
        print(f"  • Connected: {Fore.WHITE}{stats['connectivity']['is_connected']}")
        if stats['connectivity']['avg_path_length'] > 0:
            print(f"{Fore.YELLOW}  • Avg Path Length: {Fore.WHITE}{stats['connectivity']['avg_path_length']:.2f}")
        if stats['connectivity']['diameter'] > 0:
            print(f"{Fore.YELLOW}  • Diameter: {Fore.WHITE}{stats['connectivity']['diameter']}")

        print(f"\n{Fore.YELLOW}Top Entities (PageRank):")
        for entity, score in stats['centrality']['top_pagerank'][:5]:
            print(f"  • {Fore.WHITE}{entity}: {score:.4f}")

        print(f"\n{Fore.YELLOW}Clustering:")
        print(f"  • Avg Coefficient: {Fore.WHITE}{stats['clustering']['avg_clustering_coefficient']:.3f}")
        print(f"{Fore.YELLOW}  • Communities: {Fore.WHITE}{stats['clustering']['num_communities']}")

        print(f"\n{Fore.GREEN}✓ Analysis complete! Check the output directory for detailed results and visualizations.\n")


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='Deep Search Knowledge Graph Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -e "Apple" "Microsoft" "Google" -c "Tech companies"
  python main.py -e "Python" "JavaScript" -e --expand --order 2
  python main.py --file entities.txt --context "Programming languages"
        """
    )

    parser.add_argument(
        '-e', '--entities',
        nargs='+',
        help='Entities to analyze (space-separated)'
    )

    parser.add_argument(
        '-f', '--file',
        help='File containing entities (one per line)'
    )

    parser.add_argument(
        '-c', '--context',
        default='',
        help='Context for the analysis'
    )

    parser.add_argument(
        '--expand',
        action='store_true',
        help='Expand the network by discovering related entities'
    )

    parser.add_argument(
        '--order',
        type=int,
        default=1,
        help='Expansion order (default: 1)'
    )

    parser.add_argument(
        '--max-per-entity',
        type=int,
        default=3,
        help='Max related entities per entity (default: 3)'
    )

    parser.add_argument(
        '--threshold',
        type=float,
        default=0.2,
        help='Minimum relationship weight threshold (default: 0.2)'
    )

    parser.add_argument(
        '-o', '--output',
        default='output',
        help='Output directory (default: output)'
    )

    parser.add_argument(
        '--api-key',
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Get entities
    entities = []
    if args.entities:
        entities.extend(args.entities)

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            entities.extend([line.strip() for line in f if line.strip()])

    if not entities:
        print(f"{Fore.RED}Error: No entities provided. Use -e or --file to specify entities.")
        parser.print_help()
        sys.exit(1)

    # Get API key
    api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print(f"{Fore.YELLOW}Warning: No API key provided. Some features may be limited.")
        print(f"{Fore.YELLOW}Set ANTHROPIC_API_KEY environment variable or use --api-key")

    # Run deep search
    try:
        app = DeepSearchApp(api_key)
        results = app.deep_search(
            entities,
            args.context,
            args.expand,
            args.order,
            args.max_per_entity,
            args.threshold,
            args.output
        )

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Analysis interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
