# Deep Search Knowledge Graph

Una aplicación avanzada de búsqueda profunda que utiliza análisis de redes y grafos de conocimiento para descubrir y analizar relaciones entre entidades.

## Características Principales

- **Análisis de Grafos de Conocimiento**: Construcción automática de grafos de conocimiento a partir de entidades
- **Órdenes de Vecindad**: Análisis de conexiones a diferentes distancias (1er orden, 2do orden, etc.)
- **Análisis de Caminos**: Identificación de rutas y conexiones entre entidades
- **Ponderación de Relaciones**: Evaluación automática de la fuerza de relaciones (escala 0-1)
- **Visualización Interactiva**: Grafos interactivos con Plotly
- **Análisis Estadístico**: Métricas de centralidad, clustering, detección de comunidades y más

## Arquitectura

```
deep_search_app/
├── core/                          # Módulos principales
│   ├── knowledge_graph.py         # Grafo de conocimiento con NetworkX
│   ├── search_engine.py           # Motor de búsqueda y análisis
│   ├── relationship_analyzer.py   # Análisis de relaciones
│   └── path_analyzer.py           # Análisis de caminos y vecindad
├── visualization/                 # Visualización
│   └── graph_visualizer.py        # Visualizador interactivo con Plotly
├── analysis/                      # Análisis estadístico
│   └── statistics.py              # Métricas y estadísticas de red
├── examples/                      # Ejemplos de uso
│   ├── example_usage.py           # Ejemplos en Python
│   └── example_entities.txt       # Ejemplo de archivo de entidades
├── main.py                        # Aplicación CLI principal
└── requirements.txt               # Dependencias
```

## Instalación

### 1. Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### 2. Instalar Dependencias

```bash
cd deep_search_app
pip install -r requirements.txt
```

### 3. Configurar API Key (Opcional pero Recomendado)

Para funcionalidad completa, necesitas una API key de Anthropic Claude:

```bash
cp .env.example .env
# Edita .env y agrega tu ANTHROPIC_API_KEY
```

Obtén tu API key en: https://console.anthropic.com/

## Uso

### Modo CLI Básico

```bash
# Analizar entidades específicas
python main.py -e "Python" "JavaScript" "TypeScript" -c "Lenguajes de programación"

# Analizar desde un archivo
python main.py --file entities.txt --context "Tu contexto aquí"

# Expandir la red descubriendo entidades relacionadas
python main.py -e "Apple" "Microsoft" --expand --order 2

# Especificar directorio de salida
python main.py -e "Entity1" "Entity2" -o mi_analisis
```

### Opciones Avanzadas

```bash
python main.py \
  -e "Entidad1" "Entidad2" "Entidad3" \
  -c "Contexto de análisis" \
  --expand \                    # Expandir red
  --order 2 \                   # Expandir 2 niveles
  --max-per-entity 5 \          # Max 5 entidades relacionadas por entidad
  --threshold 0.3 \             # Umbral mínimo de peso de relación
  -o output_dir                 # Directorio de salida
```

### Parámetros

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `-e, --entities` | Entidades a analizar (separadas por espacio) | - |
| `-f, --file` | Archivo con entidades (una por línea) | - |
| `-c, --context` | Contexto para el análisis | "" |
| `--expand` | Expandir red descubriendo entidades relacionadas | False |
| `--order` | Orden de expansión (niveles) | 1 |
| `--max-per-entity` | Máximo de entidades relacionadas por entidad | 3 |
| `--threshold` | Umbral mínimo de peso de relación (0-1) | 0.2 |
| `-o, --output` | Directorio de salida | output |
| `--api-key` | API key de Anthropic | $ANTHROPIC_API_KEY |

## Output Esperado

### 1. Conclusiones

El análisis genera conclusiones automáticas sobre:
- Tamaño y estructura de la red
- Conectividad entre entidades
- Fuerza promedio de las relaciones
- Entidades más influyentes
- Distancias entre entidades consultadas
- Estructura de comunidades

### 2. Grafo Interactivo

Se genera un grafo visual con:
- **Nodos**: Entidades (tamaño proporcional a importancia)
- **Aristas**: Relaciones (grosor y color según peso)
- **Ponderación**: 0 = sin relación, 1 = relación muy fuerte
- **Interactividad**: Zoom, pan, hover para detalles

### 3. Análisis Estadístico

#### Métricas de Red
- **Centralidad**: Degree, Betweenness, Closeness, Eigenvector, PageRank
- **Clustering**: Coeficiente de clustering, detección de comunidades
- **Conectividad**: Componentes conectados, diámetro, longitud promedio de caminos
- **Estructura**: Asortatividad, reciprocidad, distribución de grados

#### Análisis de Vecindad
Para cada entidad analizada:
- **Orden 1**: Contactos directos
- **Orden 2**: Contactos de contactos
- **Orden 3**: Tercer nivel de conexión
- Detalles de pesos y tipos de relación

#### Análisis de Caminos
- Caminos más cortos entre entidades
- Caminos alternativos
- Peso promedio de cada camino
- Fuerza de conexión (strength score)

### 4. Archivos Generados

```
output/
├── results.json                  # Resultados completos en JSON
├── knowledge_graph.json          # Grafo exportado
├── graph_interactive.html        # Visualización interactiva principal
├── weight_distribution.html      # Distribución de pesos
└── degree_distribution.html      # Distribución de grados
```

## Uso Programático

### Ejemplo Básico

```python
from core.knowledge_graph import KnowledgeGraph
from core.relationship_analyzer import RelationshipAnalyzer
from core.search_engine import SearchEngine

# Crear grafo
kg = KnowledgeGraph()
search_engine = SearchEngine(api_key="tu_api_key")
analyzer = RelationshipAnalyzer(kg, search_engine)

# Analizar entidades
entities = ["Python", "JavaScript", "TypeScript"]
context = "Lenguajes de programación"

analyzer.build_graph_from_entities(entities, context, threshold=0.3)

# Ver relaciones
print(f"Grafo con {len(kg)} entidades")
for entity in entities:
    connections = analyzer.find_strongest_connections(entity, n=3)
    print(f"\n{entity}:")
    for target, weight, rel_type in connections:
        print(f"  → {target}: {weight:.2f} ({rel_type})")
```

### Ejemplo con Análisis de Caminos

```python
from core.path_analyzer import PathAnalyzer

path_analyzer = PathAnalyzer(kg)

# Analizar vecindad
neighborhoods = path_analyzer.analyze_neighborhood_orders("Python", max_order=3)
for order, data in neighborhoods.items():
    print(f"Orden {order}: {data['count']} entidades")

# Encontrar caminos
paths = path_analyzer.find_all_connecting_paths("Python", "TypeScript")
print(f"\nCaminos encontrados: {len(paths)}")
if paths:
    strongest = paths[0]
    print(f"Camino más fuerte: {' → '.join(strongest['path'])}")
    print(f"Peso promedio: {strongest['average_weight']:.2f}")
```

### Ejemplo con Visualización

```python
from visualization.graph_visualizer import GraphVisualizer

visualizer = GraphVisualizer(kg)

# Crear grafo interactivo
fig = visualizer.create_interactive_graph(
    title="Mi Grafo de Conocimiento",
    highlight_entities=["Python", "JavaScript"]
)

# Guardar
visualizer.save_html(fig, "mi_grafo.html")
```

### Ejemplo con Estadísticas

```python
from analysis.statistics import GraphStatistics

stats = GraphStatistics(kg)

# Resumen completo
summary = stats.get_network_summary()
print(f"Nodos: {summary['basic_stats']['num_nodes']}")
print(f"Densidad: {summary['basic_stats']['density']:.3f}")

# Top entidades
top_entities = stats.get_top_central_nodes('pagerank', n=5)
for entity, score in top_entities:
    print(f"{entity}: {score:.4f}")

# Detectar comunidades
communities = stats.detect_communities()
print(f"\nComunidades detectadas: {len(communities)}")
```

## Conceptos Clave

### Órdenes de Vecindad

- **Orden 1**: Entidades directamente conectadas (1 salto)
- **Orden 2**: Entidades a 2 saltos de distancia (contactos de contactos)
- **Orden N**: Entidades a N saltos de distancia

### Análisis de Caminos

- **Camino Más Corto**: Ruta con menor número de saltos
- **Caminos Alternativos**: Todas las rutas posibles entre dos entidades
- **Peso del Camino**: Promedio de los pesos de las relaciones en el camino
- **Fuerza del Camino**: Métrica que combina peso y longitud

### Ponderación de Relaciones (0-1)

- **0.0-0.2**: Relación débil o tangencial
- **0.3-0.5**: Relación moderada
- **0.6-0.8**: Relación fuerte
- **0.9-1.0**: Relación muy fuerte/directa

### Métricas de Centralidad

- **Degree**: Número de conexiones directas
- **Betweenness**: Frecuencia en caminos entre otros nodos
- **Closeness**: Cercanía promedio a todos los demás nodos
- **PageRank**: Importancia basada en enlaces (algoritmo de Google)
- **Eigenvector**: Importancia basada en conexiones importantes

## Ejemplos de Casos de Uso

### 1. Análisis de Tecnologías

```bash
python main.py -e "React" "Vue" "Angular" "Svelte" \
  -c "Frontend frameworks" --expand --order 1
```

### 2. Investigación de Empresas

```bash
python main.py -e "Apple" "Microsoft" "Google" "Amazon" \
  -c "Tech companies" --expand --order 2 --max-per-entity 5
```

### 3. Conceptos Académicos

```bash
python main.py -e "Machine Learning" "Deep Learning" "Neural Networks" \
  -c "AI concepts" --threshold 0.4
```

### 4. Análisis de Personas/Organizaciones

```bash
python main.py -e "Entidad1" "Entidad2" "Entidad3" \
  -c "Contexto específico" --expand
```

## Limitaciones y Consideraciones

1. **API Key Requerida**: Para funcionalidad completa, se necesita una API key de Anthropic Claude
2. **Rate Limits**: Ten en cuenta los límites de la API al analizar muchas entidades
3. **Costos**: El uso de la API tiene costos asociados
4. **Calidad de Datos**: La calidad del análisis depende de la información disponible sobre las entidades

## Solución de Problemas

### Error: "No API key provided"

Asegúrate de configurar tu API key:
```bash
export ANTHROPIC_API_KEY="tu_api_key"
# O configura .env
```

### Gráfico vacío o sin relaciones

- Reduce el `--threshold` (ej: 0.1)
- Verifica que las entidades estén bien escritas
- Agrega más contexto con `-c`

### Análisis muy lento

- Reduce `--order` (niveles de expansión)
- Reduce `--max-per-entity`
- No uses `--expand` para análisis rápido

## Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del repositorio
2. Crea una branch para tu feature
3. Haz commit de tus cambios
4. Haz push a la branch
5. Abre un Pull Request

## Licencia

MIT License - ver archivo LICENSE para detalles

## Contacto y Soporte

Para preguntas, problemas o sugerencias, abre un issue en el repositorio.

## Roadmap Futuro

- [ ] Integración con más fuentes de datos
- [ ] Exportación a otros formatos (GraphML, GEXF)
- [ ] Interfaz web interactiva
- [ ] Análisis temporal de evolución de relaciones
- [ ] Soporte para grafos más grandes (> 10k nodos)
- [ ] Análisis de sentimiento en relaciones
- [ ] Comparación de múltiples grafos

## Agradecimientos

Construido con:
- [NetworkX](https://networkx.org/) - Análisis de grafos
- [Plotly](https://plotly.com/) - Visualizaciones interactivas
- [Anthropic Claude](https://anthropic.com/) - Análisis de relaciones con IA
