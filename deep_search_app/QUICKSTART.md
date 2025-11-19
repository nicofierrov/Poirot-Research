# Guía de Inicio Rápido

## Instalación en 3 Pasos

### 1. Instalar dependencias

```bash
cd deep_search_app
pip install -r requirements.txt
```

### 2. Configurar API Key (Opcional)

```bash
cp .env.example .env
# Edita .env y agrega: ANTHROPIC_API_KEY=tu_api_key
```

### 3. Ejecutar tu primer análisis

```bash
python main.py -e "Python" "JavaScript" "TypeScript" -c "Lenguajes de programación"
```

## Ejemplo Completo

```bash
# Análisis completo con expansión de red
python main.py \
  -e "Apple" "Microsoft" "Google" \
  -c "Tech companies" \
  --expand \
  --order 2 \
  --max-per-entity 5 \
  -o mi_analisis
```

Esto generará:
- `mi_analisis/graph_interactive.html` - Grafo interactivo
- `mi_analisis/results.json` - Resultados completos
- `mi_analisis/knowledge_graph.json` - Grafo exportado

## Verificar Instalación

```bash
python test_basic.py
```

## Comandos Útiles

### Analizar desde archivo

```bash
# Crear archivo con entidades
echo "Python
JavaScript
TypeScript
React
Django" > entities.txt

# Analizar
python main.py --file entities.txt -c "Web technologies"
```

### Modo sin API (Limitado)

```bash
# Funciona sin API key pero con análisis limitado
python main.py -e "Entity1" "Entity2" -c "Context"
```

### Ejecutar ejemplos

```bash
python examples/example_usage.py
```

## Estructura del Output

```
output/
├── graph_interactive.html        # Abre en navegador
├── results.json                  # Datos completos
├── knowledge_graph.json          # Grafo exportado
├── weight_distribution.html      # Análisis de pesos
└── degree_distribution.html      # Análisis de grados
```

## Prompt de Ejemplo para Uso Directo

Si quieres usar el prompt directamente como mencionaste:

```python
from main import DeepSearchApp

app = DeepSearchApp(api_key="tu_api_key")

# Tus entidades
entities = [
    "Entidad 1",
    "Entidad 2",
    "Entidad 3",
    # ... hasta Entidad n
]

# Realizar búsqueda profunda
results = app.deep_search(
    entities=entities,
    context="Tu contexto aquí",
    expand=True,
    expansion_order=2,
    threshold=0.2,
    output_dir="mi_output"
)

# Acceder a resultados
print("\nConclusiones:")
for conclusion in results['conclusions']:
    print(f"- {conclusion}")

print("\nEstadísticas:")
stats = results['statistics']
print(f"Entidades: {stats['basic_stats']['num_nodes']}")
print(f"Relaciones: {stats['basic_stats']['num_edges']}")
```

## Solución Rápida de Problemas

### No encuentra módulos

```bash
pip install -r requirements.txt
```

### Error de API Key

```bash
export ANTHROPIC_API_KEY="tu_api_key"
```

### Gráfico vacío

```bash
# Reduce el threshold
python main.py -e "Entity1" "Entity2" --threshold 0.1
```

## Próximos Pasos

1. Lee el [README.md](README.md) completo para documentación detallada
2. Explora [examples/example_usage.py](examples/example_usage.py)
3. Experimenta con diferentes parámetros

## Ayuda

```bash
python main.py --help
```
