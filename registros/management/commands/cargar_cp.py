# registros/management/commands/cargar_cp.py
from django.core.management.base import BaseCommand
from registros.models import CodigoPostal
from html.parser import HTMLParser

class CPParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.en_fila = False
        self.celda_actual = 0
        self.fila_actual = []
        self.datos = []

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.en_fila = True
            self.fila_actual = []
            self.celda_actual = 0
        elif tag == 'td':
            self.fila_actual.append('')

    def handle_data(self, data):
        if self.en_fila and self.fila_actual:
            self.fila_actual[-1] += data.strip()

    def handle_endtag(self, tag):
        if tag == 'tr' and len(self.fila_actual) >= 6:
            cp = self.fila_actual[0].strip()
            estado = self.fila_actual[1].strip()
            municipio = self.fila_actual[2].strip()
            asentamiento = self.fila_actual[5].strip()
            if cp.isdigit() and len(cp) == 5:
                self.datos.append({
                    'cp': cp,
                    'estado': estado,
                    'municipio': municipio,
                    'colonia': asentamiento
                })
            self.en_fila = False
import chardet

class Command(BaseCommand):
    help = 'Carga códigos postales de Tlaxcala'

    def handle(self, *args, **kwargs):
        import os
        archivo = os.path.join(os.path.dirname(__file__), 'tlaxcala_cp.html')
        
        with open(archivo, 'rb') as f:
            raw = f.read()
            encoding_detectado = chardet.detect(raw)['encoding']
            contenido = raw.decode(encoding_detectado, errors='replace')

        parser = CPParser()
        parser.feed(contenido)

        # Agrupar colonias por CP
        mapa = {}
        for row in parser.datos:
            cp = row['cp']
            if cp not in mapa:
                mapa[cp] = {
                    'estado': row['estado'],
                    'municipio': row['municipio'],
                    'colonias': []
                }
            if row['colonia'] and row['colonia'] not in mapa[cp]['colonias']:
                mapa[cp]['colonias'].append(row['colonia'])

        creados = 0
        for cp, data in mapa.items():
            obj, created = CodigoPostal.objects.update_or_create(
                cp=cp,
                defaults={
                    'estado': data['estado'],
                    'municipio': data['municipio'],
                    'colonias': data['colonias']
                }
            )
            if created:
                creados += 1

        self.stdout.write(self.style.SUCCESS(
            f'✅ Listo. {creados} CPs nuevos, {len(mapa)} total procesados.'
        ))