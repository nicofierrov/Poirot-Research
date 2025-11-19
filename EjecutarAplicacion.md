# Cómo Ejecutar la Aplicación

## Paso 1: Navegar al directorio
cd deep_search_app
## Paso 2: Instalar dependencias
pip install -r requirements.txt

O si tienes problemas:

pip3 install -r requirements.txt

## Paso 3: (Opcional pero Recomendado) Configurar API Key
Para funcionalidad completa, configura tu API key de Anthropic:

# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env y agregar tu API key
# ANTHROPIC_API_KEY=tu_api_key_aquí
Si no tienes API key, la aplicación funcionará en modo limitado (sin análisis de relaciones automático).

Paso 4: Ejecutar
Ejemplo básico:

python main.py -e "Python" "JavaScript" "TypeScript" -c "Lenguajes de programación"
Ejemplo con más opciones:

python main.py -e "Apple" "Microsoft" "Google" -c "Tech companies" --expand --order 2
Desde un archivo de entidades:

# Crear un archivo con tus entidades
echo "Python
JavaScript
TypeScript
React
Django" > mis_entidades.txt

# Ejecutar
python main.py --file mis_entidades.txt -c "Web development"
Paso 5: Ver los Resultados
Los resultados se generan en el directorio output/:

# Ver el grafo interactivo (abre en tu navegador)
firefox output/graph_interactive.html  # O tu navegador preferido
# O simplemente abre el archivo output/graph_interactive.html

# Ver los resultados JSON
cat output/results.json
Opciones Completas
python main.py \
  -e "Entidad1" "Entidad2" "Entidad3" \  # Entidades a analizar
  -c "Contexto del análisis" \            # Contexto
  --expand \                              # Expandir red
  --order 2 \                             # Niveles de expansión
  --max-per-entity 5 \                    # Max entidades relacionadas
  --threshold 0.2 \                       # Umbral mínimo de relación
  -o mi_output                            # Directorio de salida
Ver Ayuda
python main.py --help
Probar que Funciona
Ejecuta los tests básicos:

python test_basic.py
Ejecutar Ejemplos
python examples/example_usage.py
¿Quieres que te ayude a ejecutarlo con entidades específicas?

