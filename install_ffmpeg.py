import os
import subprocess
import urllib.request
import zipfile
import tempfile
from tkinter import messagebox
import tkinter as tk

def install_ffmpeg_windows():
    """Instalación para Windows con descarga automática"""
    root = tk.Tk()
    root.withdraw()
    
    try:
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "ffmpeg.zip")
        
        messagebox.showinfo("Instalación", "Descargando FFmpeg...")
        
        # Descargar
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        # Extraer
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Buscar el binario ffmpeg.exe
        ffmpeg_path = None
        for root, _, files in os.walk(temp_dir):
            if 'ffmpeg.exe' in files:
                ffmpeg_path = os.path.join(root, 'ffmpeg.exe')
                break
        
        if ffmpeg_path:
            # Copiar a la carpeta del script
            target_dir = os.path.join(os.path.dirname(__file__), 'ffmpeg')
            os.makedirs(target_dir, exist_ok=True)
            
            import shutil
            shutil.copy(ffmpeg_path, target_dir)
            
            # Añadir al PATH
            os.environ['PATH'] += os.pathsep + os.path.abspath(target_dir)
            
            messagebox.showinfo("Éxito", "FFmpeg instalado correctamente en la carpeta ffmpeg/")
            return True
        else:
            messagebox.showerror("Error", "No se encontró ffmpeg.exe en el paquete descargado")
            return False
            
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo instalar FFmpeg:\n{str(e)}")
        return False
    finally:
        root.destroy()