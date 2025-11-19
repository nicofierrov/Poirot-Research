"""Search engine for discovering entity relationships."""

import os
import re
import json
from typing import List, Dict, Tuple, Optional, Any
from anthropic import Anthropic


class SearchEngine:
    """
    Search engine for discovering relationships between entities.

    Uses web search and LLM analysis to find and extract relationships.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize search engine.

        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None

    def search_entity_info(self, entity: str, context: str = "") -> Dict[str, Any]:
        """
        Search for information about an entity.

        Args:
            entity: Entity to search for
            context: Additional context for the search

        Returns:
            Dictionary with entity information
        """
        if not self.client:
            return {
                'entity': entity,
                'description': f"Information about {entity}",
                'context': context
            }

        # Use Claude to search for entity information
        prompt = f"""Provide a concise summary about the following entity in 2-3 sentences:

Entity: {entity}
Context: {context if context else "General information"}

Focus on the most relevant and factual information."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            description = response.content[0].text

            return {
                'entity': entity,
                'description': description,
                'context': context
            }
        except Exception as e:
            return {
                'entity': entity,
                'description': f"Information about {entity}",
                'error': str(e)
            }

    def analyze_relationship(self, entity1: str, entity2: str,
                           context: str = "") -> Dict[str, Any]:
        """
        Analyze the relationship between two entities.

        Args:
            entity1: First entity
            entity2: Second entity
            context: Additional context

        Returns:
            Dictionary with relationship analysis including weight (0-1)
        """
        if not self.client:
            # Return default relationship
            return {
                'entity1': entity1,
                'entity2': entity2,
                'relationship_type': 'related_to',
                'weight': 0.5,
                'description': f"Relationship between {entity1} and {entity2}",
                'bidirectional': False
            }

        prompt = f"""Analyze the relationship between these two entities:

Entity 1: {entity1}
Entity 2: {entity2}
Context: {context if context else "General analysis"}

Provide your analysis in the following JSON format:
{{
  "relationship_exists": true/false,
  "relationship_type": "type of relationship (e.g., 'works_with', 'located_in', 'part_of', 'similar_to', 'competes_with', etc.)",
  "weight": 0.0-1.0 (0 = no relationship, 1 = very strong relationship),
  "description": "Brief description of the relationship",
  "bidirectional": true/false (whether the relationship goes both ways),
  "confidence": 0.0-1.0 (your confidence in this analysis)
}}

Be objective and base your analysis on factual connections. Weight guidelines:
- 0.0-0.2: Weak or tangential connection
- 0.3-0.5: Moderate connection
- 0.6-0.8: Strong connection
- 0.9-1.0: Very strong/direct connection

Only return the JSON, no additional text."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(result_text)

            return {
                'entity1': entity1,
                'entity2': entity2,
                'relationship_type': result.get('relationship_type', 'related_to'),
                'weight': result.get('weight', 0.5),
                'description': result.get('description', ''),
                'bidirectional': result.get('bidirectional', False),
                'confidence': result.get('confidence', 0.5),
                'exists': result.get('relationship_exists', True)
            }

        except Exception as e:
            print(f"Error analyzing relationship: {e}")
            return {
                'entity1': entity1,
                'entity2': entity2,
                'relationship_type': 'unknown',
                'weight': 0.3,
                'description': f"Could not analyze relationship",
                'error': str(e),
                'bidirectional': False,
                'exists': False
            }

    def batch_analyze_relationships(self, entities: List[str],
                                   context: str = "") -> List[Dict[str, Any]]:
        """
        Analyze relationships between all pairs of entities.

        Args:
            entities: List of entities
            context: Additional context

        Returns:
            List of relationship analysis results
        """
        relationships = []

        # Analyze all pairs
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i + 1:]:
                rel = self.analyze_relationship(entity1, entity2, context)
                if rel.get('exists', False) and rel.get('weight', 0) > 0.1:
                    relationships.append(rel)

        return relationships

    def discover_related_entities(self, entity: str,
                                 context: str = "",
                                 max_entities: int = 5) -> List[str]:
        """
        Discover entities related to the given entity.

        Args:
            entity: Source entity
            context: Additional context
            max_entities: Maximum number of related entities to return

        Returns:
            List of related entity names
        """
        if not self.client:
            return []

        prompt = f"""Given this entity, list up to {max_entities} other entities that are directly related to it:

Entity: {entity}
Context: {context if context else "General context"}

Return only a JSON array of entity names, like: ["Entity1", "Entity2", "Entity3"]
Focus on concrete, specific entities (people, organizations, places, products, concepts).
No additional text, just the JSON array."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text

            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if json_match:
                related_entities = json.loads(json_match.group())
            else:
                related_entities = json.loads(result_text)

            return related_entities[:max_entities]

        except Exception as e:
            print(f"Error discovering related entities: {e}")
            return []

    def expand_entity_network(self, seed_entities: List[str],
                            context: str = "",
                            expansion_order: int = 1,
                            max_per_entity: int = 3) -> List[str]:
        """
        Expand the entity network by discovering related entities.

        Args:
            seed_entities: Initial list of entities
            context: Additional context
            expansion_order: How many levels to expand (1 = direct neighbors only)
            max_per_entity: Maximum related entities per entity

        Returns:
            Expanded list of all discovered entities
        """
        all_entities = set(seed_entities)
        current_level = set(seed_entities)

        for order in range(expansion_order):
            next_level = set()

            for entity in current_level:
                related = self.discover_related_entities(
                    entity,
                    context,
                    max_per_entity
                )
                next_level.update(related)

            # Remove entities we've already seen
            next_level -= all_entities
            all_entities.update(next_level)
            current_level = next_level

            if not current_level:
                break

        return list(all_entities)
