# 🚀 Cómo Ejecutar la Aplicación Poirot Research

Sigue estos pasos para instalar y ejecutar la aplicación.

---

## 1️⃣ Navega al Directorio

```bash
cd deep_search_app
```

---

## 2️⃣ Instala las Dependencias

```bash
pip install -r requirements.txt
```
<sub>Si tienes problemas, prueba con:</sub>
```bash
pip3 install -r requirements.txt
```

---

## 3️⃣ (Opcional & Recomendado) Configura tu API Key de Anthropic

Para acceso completo, agrega tu API key:

1. Copia el archivo de ejemplo:
   ```bash
   cp .env.example .env
   ```
2. Edita `.env` y agrega tu API key:
   ```
   ANTHROPIC_API_KEY=tu_api_key_aquí
   ```

<details>
  <summary>¿No tienes API Key?</summary>
  <img src="https://img.icons8.com/color/48/000000/key.png" height="24"/>
  La app funcionará en modo limitado (sin análisis automático de relaciones).
</details>

---

## 4️⃣ Ejecuta la Aplicación

### Ejemplo básico

```bash
python main.py -e "Python" "JavaScript" "TypeScript" -c "Lenguajes de programación"
```

### Ejemplo avanzado

```bash
python main.py -e "Apple" "Microsoft" "Google" -c "Tech companies" --expand --order 2
```

### Desde un archivo de entidades

1. Crea el archivo:

   ```bash
   echo "Python
   JavaScript
   TypeScript
   React
   Django" > mis_entidades.txt
   ```

2. Ejecuta:

   ```bash
   python main.py --file mis_entidades.txt -c "Web development"
   ```

---

## 5️⃣ Ver los Resultados

Los resultados se guardan en el directorio `output/`.

- **Ver grafo interactivo**  
  <sub>Abre en tu navegador favorito:</sub>
  ```bash
  firefox output/graph_interactive.html
  # O simplemente abre el archivo manualmente
  ```

- **Ver resultados JSON**
  ```bash
  cat output/results.json
  ```

---

## 📋 Opciones Completas

```bash
python main.py \
  -e "Entidad1" "Entidad2" "Entidad3" \  # Entidades a analizar
  -c "Contexto del análisis" \            # Contexto
  --expand \                              # Expandir red
  --order 2 \                             # Niveles de expansión
  --max-per-entity 5 \                    # Máx. entidades relacionadas
  --threshold 0.2 \                       # Umbral mínimo de relación
  -o mi_output                            # Directorio de salida
```

---

## ℹ️ Ver Ayuda

```bash
python main.py --help
```

---

## 🧪 Probar que Funciona

Ejecuta los tests básicos:

```bash
python test_basic.py
```

---

## 🧑‍💻 Ejecutar Ejemplos

```bash
python examples/example_usage.py
```

---

---

**Aplicación creada y documentada por Nicolás Fierro.**  
El desarrollo, documentación y enfoque de esta herramienta para análisis de entidades, investigación de mercado, y visualización de relaciones ha sido realizado íntegramente por mí, buscando facilitar proyectos propios y de terceros.
