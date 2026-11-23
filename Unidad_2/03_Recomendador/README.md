# Dataset de anime

`anime_dataset_750.csv` contiene 750 registros y una fila de encabezados, en UTF-8, separados por tabulaciones. Columnas: `titulo`, `resena`, `generos`. No contiene una columna URL.

Fuentes: animeflv.or.at y TioAnime. Se extrae la sinopsis publicada en cada ficha. Se omiten fichas incompletas y se eliminan títulos duplicados al normalizar mayúsculas, espacios y puntuación. Las filas se ordenan por afinidad entre géneros de títulos consecutivos; no implica que el sitio los haya recomendado explícitamente.

Para regenerar:

```bash
pip install -r requirements.txt
python crawler.py --limit 750 --output anime_dataset_750.csv
```

El crawler consulta el mapa público de categorías de AnimeFLV y completa el resultado con el directorio de TioAnime. Usa hasta tres peticiones simultáneas en la segunda fuente, pausas y reintentos. Conserva las páginas consultadas en `.anime_cache/` para evitar descargas repetidas. El informe JSON registra el número obtenido y los errores; si las fuentes no alcanzan el objetivo, informa el faltante.
