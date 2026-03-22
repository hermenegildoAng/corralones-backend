import os
import django
import pandas as pd

# 1. Configuración de Django - Usando 'core' como nombre del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from registros.models import CodigoPostal

def importar():
    file_path = 'CodigosPostales.xls'
    print(f"🚀 Iniciando importación desde {file_path}...")
    
    try:
        # Abrimos el archivo manualmente con el encoding correcto
        with open(file_path, 'r', encoding='latin-1') as f:
            html_content = f.read()
        
        # Pasamos el CONTENIDO del texto, no la ruta del archivo
        tablas = pd.read_html(html_content) 
        df = tablas[1] 
        print(f"📊 Registros encontrados en el archivo: {len(df)}")
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return

    # ... (el resto del código del bucle for y bulk_create se queda igual)

    batch = []
    total_creados = 0
    
    for _, row in df.iterrows():
        try:
            # Limpiar CP y asegurar que tenga 5 dígitos (rellena con ceros a la izquierda)
            cp_raw = str(row[0]).strip().split('.')[0]
            cp = cp_raw.zfill(5)

            if not cp.isdigit() or len(cp) != 5:
                continue

            # Mapeo exacto según el HTML de SEPOMEX que pegaste:
            # row[0]: CP | row[1]: Estado | row[2]: Municipio | row[5]: Asentamiento
            batch.append(CodigoPostal(
                cp=cp,
                colonia=str(row[5]).strip(),
                municipio=str(row[2]).strip(),
                estado=str(row[1]).strip()
            ))

            # Guardar en bloques de 1000 para no saturar la memoria
            if len(batch) >= 1000:
                CodigoPostal.objects.bulk_create(batch, ignore_conflicts=True)
                total_creados += len(batch)
                print(f"✅ {total_creados} registros procesados...")
                batch = []

        except Exception as e:
            continue

    # Insertar el último grupo
    if batch:
        CodigoPostal.objects.bulk_create(batch, ignore_conflicts=True)
        total_creados += len(batch)

    print(f"✨ Importación terminada con éxito.")
    print(f"📈 Total final en la base de datos: {CodigoPostal.objects.count()}")

if __name__ == "__main__":
    importar()