import fitz
import os
import json
import re

MAPA_GRADOS = {
    '1er grado': '1er grado',
    '2 do grado': '2do grado',
    '2do grado': '2do grado',
    '3ero Secuencias': '3er grado',
    '4to': '4to grado',
    '5to Secuencias': '5to grado',
    '6 to grado': '6to grado',
    '7MO GRADO E4 DE6': '7mo grado',
    'adecuación curricular ppi': 'Adecuación Curricular',
}

PALABRAS_LENGUA = [
    'lengua', 'lenguaje', 'pdl', 'lectura', 'escritura', 'cuento',
    'secuencia', 'literatura', 'texto', 'leer', 'escribir', 'selva',
    'alicia', 'sapo', 'novela', 'relato', 'poesia', 'alfabetiz',
    'practicas', 'prácticas', 'ortografia', 'ortografía', 'pl',
    'reescribir', 'botin', 'gato', 'botas', 'rueditas', 'morgue',
    'crímenes', 'policial', 'molestar', 'ruido', 'viento', 'esiteca',
    'ciruela', 'afectividad', 'maestro', 'plan maestro'
]

PALABRAS_MATE = [
    'mate', 'matemática', 'matematica', 'número', 'numero',
    'suma', 'resta', 'multiplicacion', 'fraccion', 'geometria',
    'progresiones', 'numeracion', 'fepba', 'tesba', 'evaluacion',
    'diagnostico', 'bimestre'
]

PALABRAS_NATU = [
    'natu', 'naturales', 'ciencias naturales', 'cuerpo', 'sistema',
    'funcion', 'planta', 'animal', 'ecosistema', 'fasiculo',
    'cuaderno', 'biologia', 'fisica', 'quimica', 'salud'
]

PALABRAS_SOCIALES = [
    'sociales', 'social', 'historia', 'geografia', 'sociedad',
    'escuela', 'ayer', 'hoy', 'barrio', 'ciudad', 'pais',
    'revolucion', 'independencia', 'san martin', 'patria',
    'superpatriota', 'globalizacion', 'globalización', 'trabajadores',
    'sancor', 'petroleo', 'petróleo', 'mujeres', 'derechos',
    'publicidad', 'bicentenario', 'uniones', 'esclavos'
]

def detectar_materia(nombre):
    nombre_lower = nombre.lower()
    
    puntaje = {
        'Prácticas del Lenguaje': 0,
        'Matemática': 0,
        'Ciencias Naturales': 0,
        'Ciencias Sociales': 0,
    }
    
    for p in PALABRAS_LENGUA:
        if p in nombre_lower:
            puntaje['Prácticas del Lenguaje'] += 1
    for p in PALABRAS_MATE:
        if p in nombre_lower:
            puntaje['Matemática'] += 1
    for p in PALABRAS_NATU:
        if p in nombre_lower:
            puntaje['Ciencias Naturales'] += 1
    for p in PALABRAS_SOCIALES:
        if p in nombre_lower:
            puntaje['Ciencias Sociales'] += 1
    
    mejor = max(puntaje, key=puntaje.get)
    if puntaje[mejor] == 0:
        return 'Sin clasificar'
    return mejor

def leer_pdf(ruta):
    try:
        doc = fitz.open(ruta)
        texto = ""
        for pagina in doc:
            texto += pagina.get_text()
        return texto.strip()
    except:
        return ""

def procesar_archivo(ruta, nombre):
    ext = os.path.splitext(nombre)[1].lower()
    texto = ""
    
    if ext == '.pdf':
        texto = leer_pdf(ruta)
    else:
        return None
    
    if not texto or len(texto) < 50:
        return None
    
    return {
        'titulo': os.path.splitext(nombre)[0],
        'contenido': texto[:8000],
    }

carpeta_base = r"C:\Users\Usuario\Desktop\mis proyectos\materiales"
resultado = {}

def procesar_carpeta(ruta_carpeta, grado):
    if grado not in resultado:
        resultado[grado] = {
            'Prácticas del Lenguaje': [],
            'Matemática': [],
            'Ciencias Naturales': [],
            'Ciencias Sociales': [],
            'Sin clasificar': []
        }
    
    for item in os.listdir(ruta_carpeta):
        ruta_item = os.path.join(ruta_carpeta, item)
        
        if os.path.isdir(ruta_item):
            item_lower = item.lower().strip()
            materia_directa = None
            
            if any(p in item_lower for p in ['pdl', 'pl', 'lengua', 'lenguaje', 'practicas']):
                materia_directa = 'Prácticas del Lenguaje'
            elif any(p in item_lower for p in ['mate', 'matematica', 'matemática']):
                materia_directa = 'Matemática'
            elif any(p in item_lower for p in ['natu', 'naturales']):
                materia_directa = 'Ciencias Naturales'
            elif any(p in item_lower for p in ['sociales', 'social']):
                materia_directa = 'Ciencias Sociales'
            
            for subitem in os.listdir(ruta_item):
                ruta_sub = os.path.join(ruta_item, subitem)
                if os.path.isfile(ruta_sub) and subitem.lower().endswith('.pdf'):
                    doc = procesar_archivo(ruta_sub, subitem)
                    if doc:
                        materia = materia_directa if materia_directa else detectar_materia(subitem)
                        resultado[grado][materia].append(doc)
                        print(f"✅ {grado} | {materia} | {doc['titulo'][:50]}")
        
        elif os.path.isfile(ruta_item) and item.lower().endswith('.pdf'):
            doc = procesar_archivo(ruta_item, item)
            if doc:
                materia = detectar_materia(item)
                resultado[grado][materia].append(doc)
                print(f"✅ {grado} | {materia} | {doc['titulo'][:50]}")

for carpeta_grado in os.listdir(carpeta_base):
    ruta_grado = os.path.join(carpeta_base, carpeta_grado)
    if not os.path.isdir(ruta_grado):
        continue
    grado = MAPA_GRADOS.get(carpeta_grado, carpeta_grado)
    procesar_carpeta(ruta_grado, grado)

# Limpiar materias vacías
for grado in resultado:
    resultado[grado] = {k: v for k, v in resultado[grado].items() if v}

with open("secuencias_clean.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print("\n✅ ¡Listo! Resumen:")
for grado, materias in resultado.items():
    for materia, docs in materias.items():
        print(f"  {grado} | {materia}: {len(docs)} archivos")