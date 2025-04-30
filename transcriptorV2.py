
import whisper # type: ignore
import os
import datetime
import sys
import math
import time
import logging
from logging.handlers import RotatingFileHandler
import subprocess  # Añade esto con los otros imports

# Configuración inicial del logging
def setup_logging():
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_file = 'whisper_transcriber.log'
    
    # Handler para archivo (rotativo, máximo 5MB)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024, 
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configurar el logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

def mostrar_progreso(porcentaje):
    """Muestra una barra de progreso simple en la consola"""
    bar_length = 50
    block = int(round(bar_length * porcentaje))
    progress = "▋" * block + "-" * (bar_length - block)
    sys.stdout.write(f"\rProgreso: [{progress}] {math.floor(porcentaje*100)}%")
    sys.stdout.flush()
    if porcentaje >= 1.0:
        print()

def transcribir_video(ruta_video, modelo="base", guardar_archivo=True):
    """
    Versión final con manejo robusto de FFmpeg y paths
    """
    inicio = datetime.datetime.now()
    temp_file = None
    
    try:
        # 1. Verificación avanzada de ruta
        ruta_abs = os.path.abspath(ruta_video.strip('"'))
        logger.info(f"\nVerificando archivo: {ruta_abs}")
        
        if not os.path.exists(ruta_abs):
            logger.error("ARCHIVO NO ENCONTRADO")
            print(f"\nError: El archivo no existe en:\n{ruta_abs}")
            return None

        # 2. Configuración de FFmpeg
        ffmpeg_path = "ffmpeg"  # Intenta encontrarlo en PATH
        if os.name == 'nt':  # Windows
            # Rutas comunes donde podría estar FFmpeg
            possible_paths = [
                r"C:\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                os.path.join(os.environ.get('PROGRAMFILES', ''), "ffmpeg", "bin", "ffmpeg.exe")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    ffmpeg_path = path
                    break
        
        # 3. Crear archivo temporal seguro
        temp_dir = os.path.join(os.environ.get('TEMP', ''), "WhisperTemp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_file = os.path.join(temp_dir, f"temp_{os.getpid()}.wav")
        
        # 4. Conversión con FFmpeg (método robusto)
        ffmpeg_cmd = [
            ffmpeg_path,
            '-hide_banner',
            '-loglevel', 'error',
            '-y',
            '-i', ruta_abs,
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            temp_file
        ]
        
        logger.info(f"Ejecutando: {' '.join(ffmpeg_cmd)}")
        try:
            result = subprocess.run(
                ffmpeg_cmd,
                check=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except FileNotFoundError:
            logger.error("FFMPEG NO ENCONTRADO EN EL SISTEMA")
            print("\nERROR: FFmpeg no está instalado o no está en el PATH")
            print("Instale FFmpeg desde: https://ffmpeg.org/")
            print("O ejecute: choco install ffmpeg (en PowerShell como Admin)")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"ERROR FFMPEG:\n{e.stderr}")
            raise RuntimeError("Error al procesar el archivo de audio")
        
        logger.info("Iniciando transcripción...")
        print("Procesando el video/audio...")
        resultado = model.transcribe(temp_file, fp16=False)
        # Paso 5: Proceso de transcripción
        logger.info(f"CARGANDO MODELO {modelo.upper()}...")
        print(f"\nCargando modelo Whisper ({modelo})...")
        model = whisper.load_model(modelo)
        
        logger.info("INICIANDO TRANSCRIPCIÓN...")
        print("Procesando el video/audio...")
        resultado = model.transcribe(temp_file, fp16=False, verbose=False)
        logger.debug("Transcripción completada")

        # Procesamiento de segmentos
        texto_con_timestamps = ""
        for segment in resultado['segments']:
            ts = formatear_timestamps(segment['start'])
            texto = limpiar_transcripcion(segment['text'])
            texto_con_timestamps += f"{ts}\n{texto}\n\n"

        # Barra de progreso
        [mostrar_progreso(i/100) or time.sleep(0.02) for i in range(101)]
        print()

        # Guardado de resultados
        if guardar_archivo:
            base_name = os.path.splitext(ruta_abs)[0]
            txt_file = f"{base_name}_transcripcion.txt"
            
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(texto_con_timestamps)
            logger.info(f"TRANSCRIPCIÓN GUARDADA EN: {txt_file}")
            print(f"\n✓ Transcripción guardada en: {txt_file}")

        # Estadísticas finales
        tiempo_total = datetime.datetime.now() - inicio
        logger.info(f"TIEMPO TOTAL: {tiempo_total}")
        
        return {
            'texto': texto_con_timestamps,
            'tiempo': str(tiempo_total)
        }

    except Exception as e:
        logger.exception("ERROR CRÍTICO", exc_info=True)
        print(f"\n✗ Error: {str(e)}")
        return None
        
    finally:
        # Limpieza garantizada
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

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

def main():
    logger.info("Iniciando aplicación de transcripción")
    while True:
        mostrar_menu()
        opcion = input("\nSeleccione el modelo (1-5) o S para salir: ").upper()
        
        if opcion == "S":
            logger.info("Aplicación finalizada por el usuario")
            print("\n¡Hasta luego!")
            break
        
        modelos = {
            "1": "tiny",
            "2": "base",
            "3": "small",
            "4": "medium",
            "5": "large"
        }
        
        if opcion in modelos:
            modelo = modelos[opcion]
            logger.info(f"Modelo seleccionado: {modelo}")
            ruta_video = input("\nIngrese la ruta del video/audio a transcribir: ")
            logger.debug(f"Ruta ingresada por usuario: {ruta_video}")
            
            try:
                ruta_abs = os.path.abspath(ruta_video.strip('"'))
                if not os.path.exists(ruta_abs):
                    logger.error(f"Archivo no encontrado: {ruta_abs}")
                    print("\nError: El archivo no existe. Verifique la ruta.")
                    continue
                
                logger.info(f"Iniciando transcripción para: {ruta_abs}")
                print(f"\nIniciando transcripción con modelo {modelo}...")
                
                resultado = transcribir_video(ruta_abs, modelo)
                
                if resultado:
                    logger.info("Transcripción completada exitosamente")
                    print("\n" + "-"*50)
                    print("TRANSCRIPCIÓN COMPLETADA".center(50))
                    print("-"*50)
                    print(f"\nTiempo de procesamiento: {resultado['tiempo']}")
                    print("\nExtracto de la transcripción:\n")
                    print(resultado['texto'][:500] + "...")
                    print("\n" + "-"*50)
            except Exception as e:
                logger.error(f"Error en el flujo principal: {str(e)}")
                print(f"\nError: {str(e)}")
        else:
            logger.warning(f"Opción no válida seleccionada: {opcion}")
            print("\nOpción no válida. Intente nuevamente.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Error no manejado: {str(e)}", exc_info=True)
        print(f"\nError crítico: {str(e)}")