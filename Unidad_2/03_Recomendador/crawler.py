#!/usr/bin/env python3
"""Extrae fichas de animeflv.or.at y completa con TioAnime, ordenadas por afinidad.
Uso: python crawler.py --limit 750 --output anime_dataset_750.csv
Si el catálogo no alcanza el límite, guarda los disponibles e informa el faltante.
"""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
import json
import re
import time
import unicodedata
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = 'https://animeflv.or.at'
NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}


def clean(value):
    return re.sub(r'\s+', ' ', value).strip()


def key(value):
    return re.sub(r'[^\w]+', '', unicodedata.normalize('NFKC', value).casefold())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=750)
    parser.add_argument('--output', default='anime_dataset_750.csv')
    args = parser.parse_args()
    if args.limit < 1:
        parser.error('--limit debe ser positivo')
    session = requests.Session()
    session.headers['User-Agent'] = 'AnimeDatasetResearch/1.0'

    def get(url):
        for attempt in range(3):
            try:
                response = session.get(url, timeout=30)
                response.raise_for_status()
                time.sleep(0.25)
                return response.text
            except requests.RequestException:
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))

    sitemap = ET.fromstring(get(BASE + '/category-sitemap.xml'))
    urls = list(dict.fromkeys(
        node.text for node in sitemap.findall('s:url/s:loc', NS)
        if re.fullmatch(re.escape(BASE) + r'/anime/[^/]+/', node.text or '')
    ))
    rows, seen, errors = [], set(), []
    cache = Path('.anime_cache')
    cache.mkdir(exist_ok=True)
    for i, url in enumerate(urls, 1):
        try:
            path = cache / (url.rstrip('/').split('/')[-1] + '.html')
            if path.exists():
                html = path.read_text(encoding='utf-8')
            else:
                html = get(url)
                path.write_text(html, encoding='utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.select_one('h1.anime-title')
            synopsis = soup.select_one('.anime-synopsis')
            genres = list(dict.fromkeys(clean(x.get_text(' ', strip=True)) for x in soup.select('.anime-genres .genre-tag')))
            if synopsis:
                for heading in synopsis.select('h1,h2,h3'):
                    heading.decompose()
            description = clean(synopsis.get_text(' ', strip=True)) if synopsis else ''
            if not title or not description or not genres:
                errors.append({'url': url, 'error': 'Ficha incompleta', 'titulo': bool(title), 'resena': bool(description), 'generos': bool(genres)})
                continue
            title = clean(title.get_text(' ', strip=True))
            if key(title) not in seen:
                seen.add(key(title))
                rows.append({'titulo': title, 'resena': description, 'generos': ', '.join(genres), '_genres': set(genres)})
            if i % 20 == 0:
                print(f'Consultadas {i}/{len(urls)}; completas {len(rows)}', flush=True)
        except Exception as exc:
            errors.append({'url': url, 'error': str(exc)})

    primary_count = len(rows)
    visited = set()
    page = 1
    tio = 'https://tioanime.com'
    def fetch_tio(url):
        path = cache / ('tio_' + url.rstrip('/').split('/')[-1] + '.html')
        for attempt in range(3):
            try:
                if path.exists():
                    html = path.read_text(encoding='utf-8')
                else:
                    # Una sesión independiente por petición concurrente.
                    response = requests.get(url, timeout=25, headers={'User-Agent': 'AnimeDatasetResearch/1.0'})
                    response.raise_for_status()
                    html = response.text
                    path.write_text(html, encoding='utf-8')
                    time.sleep(0.4)
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.select_one('article.anime-single h1.title')
                synopsis = soup.select_one('article.anime-single .sinopsis')
                genres = list(dict.fromkeys(clean(x.get_text(' ', strip=True)) for x in soup.select('article.anime-single .genres a')))
                # Unificar etiquetas equivalentes entre ambas fuentes.
                genres = [{'Aventuras': 'Aventura'}.get(x, x) for x in genres]
                if not title or not synopsis or not genres:
                    return None
                title = clean(title.get_text(' ', strip=True))
                description = clean(synopsis.get_text(' ', strip=True))
                if not title or not description:
                    return None
                return {'titulo': title, 'resena': description, 'generos': ', '.join(genres), '_genres': set(genres)}
            except requests.RequestException:
                if attempt == 2:
                    return None
                time.sleep(2 * (attempt + 1))

    with ThreadPoolExecutor(max_workers=3) as pool:
        while len(rows) < args.limit:
            html = get(f'{tio}/directorio?p={page}')
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            for anchor in soup.select('a[href^="/anime/"]'):
                url = urljoin(tio, anchor['href'])
                if url in visited:
                    continue
                visited.add(url)
                # Evita volver a consultar títulos ya presentes.
                if key(clean(anchor.get_text(' ', strip=True))) not in seen:
                    links.append(url)
            for row in pool.map(fetch_tio, links):
                if row and key(row['titulo']) not in seen:
                    seen.add(key(row['titulo']))
                    rows.append(row)
                    if len(rows) == args.limit:
                        break
            print(f'TioAnime página {page}: {len(rows)}/{args.limit} animes únicos', flush=True)
            if not soup.select('a[href^="/anime/"]'):
                break
            pages = [int(x) for a in soup.select('a[href]') for x in re.findall(r'[?&]p=(\d+)', a['href'])]
            if page >= max(pages, default=page):
                break
            page += 1

    # Elige el siguiente título por géneros compartidos con el anterior.
    ordered = []
    while rows and len(ordered) < args.limit:
        if ordered:
            previous = ordered[-1]['_genres']
            index = max(range(len(rows)), key=lambda i: (len(previous & rows[i]['_genres']) / len(previous | rows[i]['_genres']), len(previous & rows[i]['_genres'])))
        else:
            index = 0
        ordered.append(rows.pop(index))
    output = Path(args.output)
    with output.open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['titulo', 'resena', 'generos'], delimiter='\t', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(ordered)
    report = {'fuentes': [BASE, tio], 'registros_animeflv': min(primary_count, len(ordered)), 'registros_tioanime': max(0, len(ordered) - primary_count), 'objetivo': args.limit, 'fichas_en_sitemap': len(urls), 'registros_guardados': len(ordered), 'faltantes': max(0, args.limit-len(ordered)), 'errores': errors}
    output.with_suffix('.informe.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
