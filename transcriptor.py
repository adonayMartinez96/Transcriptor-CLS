import whisper
import os
import datetime
import sys
import math
import time

def mostrar_progreso(porcentaje):
    """Muestra una barra de progreso simple en la consola"""
    bar_length = 50
    block = int(round(bar_length * porcentaje))
    progress = "▋" * block + "-" * (bar_length - block)
    sys.stdout.write(f"\rProgreso: [{progress}] {math.floor(porcentaje*100)}%")
    sys.stdout.flush()
    if porcentaje >= 1.0:
        print()  # Nueva línea al completar

def transcribir_video(ruta_video, modelo="base", guardar_archivo=True):
    """
    Transcribe un video/audio usando Whisper con marcas de tiempo
    
    Args:
        ruta_video (str): Ruta al archivo de video/audio
        modelo (str): Modelo a usar (tiny, base, small, medium, large)
        guardar_archivo (bool): Si True, guarda la transcripción en un archivo
    
    Returns:
        dict: {'texto': texto_transcrito, 'tiempo': tiempo_procesamiento}
    """
    inicio = datetime.datetime.now()
    
    try:
        # Cargar el modelo
        print(f"\nCargando modelo Whisper ({modelo})...")
        model = whisper.load_model(modelo)
        
        # Transcribir el audio
        print("Procesando el video/audio...")
        resultado = model.transcribe(
            ruta_video,
            verbose=False,
            task="transcribe",
            fp16=False
        )
        
        # Procesar los segmentos para obtener el formato con timestamps
        texto_con_timestamps = ""
        for segment in resultado['segments']:
            inicio_seg = segment['start']
            texto = segment['text']
            
            # Formatear los tiempos (MM:SS)
            minutos = int(inicio_seg // 60)
            segundos = int(inicio_seg % 60)
            
            # Añadir al texto final
            texto_con_timestamps += f"\n{minutos}:{segundos:02d}\n{texto.strip()}\n"
        
        # Simulación de progreso (opcional)
        for i in range(101):
            mostrar_progreso(i/100)
            time.sleep(0.05)
        print()
        
        # Guardar la transcripción
        if guardar_archivo:
            nombre_base = os.path.splitext(ruta_video)[0]
            archivo_txt = f"{nombre_base}_transcripcion.txt"
            
            with open(archivo_txt, "w", encoding="utf-8") as f:
                f.write(texto_con_timestamps)
            
            print(f"\n✓ Transcripción guardada en: {archivo_txt}")
        
        tiempo_procesamiento = datetime.datetime.now() - inicio
        
        return {
            'texto': texto_con_timestamps,
            'tiempo': str(tiempo_procesamiento)
        }
    
    except Exception as e:
        print(f"\n✗ Error al procesar el video: {e}")
        return None


def mostrar_menu():
    """Muestra el menú de opciones"""
    print("\n" + "="*50)
    print("TRANSCRIPTOR DE VIDEOS USANDO WHISPER".center(50))
    print("="*50)
    print("\nOpciones de modelo (mayor tamaño = mayor precisión):")
    print("1. tiny (más rápido, menos preciso)")
    print("2. base (equilibrado)")
    print("3. small")
    print("4. medium")
    print("5. large (más lento, más preciso)")
    print("\nS. Salir")

def main():
    while True:
        mostrar_menu()
        opcion = input("\nSeleccione el modelo (1-5) o S para salir: ").upper()
        
        if opcion == "S":
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
            ruta_video = input("\nIngrese la ruta del video/audio a transcribir: ")
            
            if not os.path.exists(ruta_video):
                print("\nError: El archivo no existe. Verifique la ruta.")
                continue
            
            print(f"\nIniciando transcripción con modelo {modelo}...")
            resultado = transcribir_video(ruta_video, modelo)
            
            if resultado:
                print("\n" + "-"*50)
                print("TRANSCRIPCIÓN COMPLETADA".center(50))
                print("-"*50)
                print(f"\nTiempo de procesamiento: {resultado['tiempo']}")
                print("\nExtracto de la transcripción:\n")
                print(resultado['texto'][:500] + "...")  # Muestra solo los primeros 500 caracteres
                print("\n" + "-"*50)
        else:
            print("\nOpción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()