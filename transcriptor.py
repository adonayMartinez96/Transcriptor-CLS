import whisper
import os
import datetime
import sys
import math
import time
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def mostrar_progreso(porcentaje):
    """Muestra una barra de progreso simple en la consola"""
    bar_length = 50
    block = int(round(bar_length * porcentaje))
    progress = "▋" * block + "-" * (bar_length - block)
    sys.stdout.write(f"\rProgreso: [{progress}] {math.floor(porcentaje*100)}%")
    sys.stdout.flush()
    if porcentaje >= 1.0:
        print()

def limpiar_transcripcion(texto):
    """Limpia el texto eliminando repeticiones y silencios"""
    lineas = texto.split('\n')
    lineas_limpias = []
    
    for linea in lineas:
        if linea.strip().isdigit():
            continue
            
        palabras = linea.split()
        palabras_limpias = []
        for j, palabra in enumerate(palabras):
            if j == 0 or palabra.lower() != palabras[j-1].lower():
                palabras_limpias.append(palabra)
        linea_limpia = ' '.join(palabras_limpias)
        
        if len(linea_limpia.strip()) > 1:
            lineas_limpias.append(linea_limpia)
    
    return '\n'.join(lineas_limpias)

def formatear_timestamps(segundos):
    """Convierte segundos a formato MM:SS"""
    minutos = int(segundos // 60)
    segundos = int(segundos % 60)
    return f"{minutos}:{segundos:02d}"

def crear_documento_word(texto, nombre_archivo):
    """Crea un documento Word con formato profesional"""
    doc = Document()
    titulo = doc.add_heading('Transcripción de Audio/Video', level=1)
    titulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    estilo = doc.styles['Normal']
    estilo.font.name = 'Calibri'
    estilo.font.size = Pt(11)
    
    for bloque in texto.split('\n\n'):
        if not bloque.strip():
            continue
            
        lineas = bloque.split('\n')
        if len(lineas) >= 2:
            doc.add_paragraph(lineas[0], style='Heading 2')
            parrafo = doc.add_paragraph(' '.join(lineas[1:]))
            parrafo.paragraph_format.space_after = Pt(12)
    
    doc.save(nombre_archivo)

def verificar_ffmpeg():
    """Verifica si FFmpeg está disponible"""
    try:
        import ffmpeg
        return True
    except ImportError:
        return False

def transcribir_video(ruta_video, modelo="base", guardar_archivo=True):
    """
    Versión mejorada que maneja rutas problemáticas y caracteres especiales
    """
    inicio = datetime.datetime.now()
    
    try:
        # Paso 1: Verificación robusta del archivo
        ruta_abs = os.path.abspath(ruta_video.strip('"'))
        print(f"\nVerificando archivo en ruta: {ruta_abs}")  # Debug
        
        if not os.path.exists(ruta_abs):
            raise FileNotFoundError(f"El archivo no existe en: {ruta_abs}")
        
        # Paso 2: Crear copia temporal en ubicación segura
        import tempfile
        import shutil
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "temp_whisper_audio.wav")
        
        # Convertir a formato compatible
        print("Preparando archivo temporal...")
        os.system(f'ffmpeg -i "{ruta_abs}" -acodec pcm_s16le -ar 16000 "{temp_file}"')
        
        if not os.path.exists(temp_file):
            raise RuntimeError("No se pudo crear el archivo temporal. Verifique FFmpeg")
        
        # Paso 3: Cargar modelo y transcribir
        print(f"\nCargando modelo Whisper ({modelo})...")
        model = whisper.load_model(modelo)
        
        print("Iniciando transcripción...")
        resultado = model.transcribe(
            temp_file,
            verbose=False,
            task="transcribe",
            fp16=False
        )
        
        # Procesar segmentos
        texto_con_timestamps = ""
        for segment in resultado['segments']:
            if segment['text'].strip():
                timestamp = formatear_timestamps(segment['start'])
                texto_limpio = limpiar_transcripcion(segment['text'])
                texto_con_timestamps += f"{timestamp}\n{texto_limpio}\n\n"
        
        # Barra de progreso
        for i in range(101):
            mostrar_progreso(i/100)
            time.sleep(0.02)
        print()
        
        # Guardar resultados
        if guardar_archivo:
            nombre_base = os.path.splitext(ruta_abs)[0]
            archivo_txt = f"{nombre_base}_transcripcion.txt"
            archivo_docx = f"{nombre_base}_transcripcion.docx"
            
            with open(archivo_txt, "w", encoding="utf-8") as f:
                f.write(texto_con_timestamps)
            
            crear_documento_word(texto_con_timestamps, archivo_docx)
            
            print(f"\n✓ Transcripción guardada en:")
            print(f"- {archivo_txt}")
            print(f"- {archivo_docx}")
        
        # Limpieza
        os.remove(temp_file)
        
        return {
            'texto': texto_con_timestamps,
            'tiempo': str(datetime.datetime.now() - inicio)
        }
    
    except Exception as e:
        print(f"\n✗ Error durante la transcripción: {str(e)}")
        
        # Limpieza en caso de error
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)
        
        return None

def mostrar_menu():
    """Muestra el menú de opciones"""
    print("\n" + "="*50)
    print("TRANSCRIPTOR DE VIDEOS USANDO WHISPER".center(50))
    print("="*50)
    print("\nOpciones de modelo:")
    print("1. tiny (rápido)")
    print("2. base (recomendado)")
    print("3. small")
    print("4. medium")
    print("5. large (preciso)")
    print("\nS. Salir")

def main():
    while True:
        mostrar_menu()
        opcion = input("\nSeleccione el modelo (1-5) o S para salir: ").upper()
        
        if opcion == "S":
            print("\n¡Hasta luego!")
            break
        
        modelos = {"1": "tiny", "2": "base", "3": "small", "4": "medium", "5": "large"}
        
        if opcion in modelos:
            modelo = modelos[opcion]
            ruta_video = input("\nIngrese la ruta del video/audio: ").strip('"')
            
            try:
                ruta_video = os.path.abspath(ruta_video)
                if not os.path.exists(ruta_video):
                    print(f"\nError: Archivo no encontrado en:\n{ruta_video}")
                    continue
                
                print(f"\nIniciando transcripción con modelo {modelo}...")
                resultado = transcribir_video(ruta_video, modelo)
                
                if resultado:
                    print("\n" + "-"*50)
                    print("TRANSCRIPCIÓN COMPLETADA".center(50))
                    print("-"*50)
                    print(f"\nTiempo: {resultado['tiempo']}")
                    print("\nExtracto:\n")
                    print(resultado['texto'][:500] + "...")
            except Exception as e:
                print(f"\nError: {str(e)}")
        else:
            print("\nOpción no válida")

if __name__ == "__main__":
    main()