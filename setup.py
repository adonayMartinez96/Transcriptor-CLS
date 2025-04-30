import os
import subprocess
import sys
import platform
from tkinter import messagebox
import tkinter as tk

def check_and_install_requirements():
    try:
        # Verificar si requirements.txt existe
        if not os.path.exists('requirements.txt'):
            create_requirements_file()
        
        # Instalar dependencias generales de Python
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        # Instalar torch y torchaudio solo con soporte CPU
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch==2.1.0+cpu", "torchaudio==2.1.0+cpu",
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ])
        
        # Verificar e instalar FFmpeg según el sistema operativo
        install_ffmpeg()
        
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron instalar los requisitos:\n{str(e)}")
        return False

def create_requirements_file():
    requirements = """
python-dotenv==1.0.0
whisper==1.1.10
openai-whisper==20231117
tk==0.1.0
python-docx==0.8.11
fpdf2==2.7.5
requests==2.31.0
tqdm==4.66.1
numpy==1.26.0
ffmpeg-python==0.2.0
"""
    with open('requirements.txt', 'w') as f:
        f.write(requirements.strip())

def install_ffmpeg():
    system = platform.system()
    
    try:
        # Verificar si FFmpeg ya está instalado
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return
    except:
        pass
    
    if system == "Windows":
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        messagebox.showinfo("Instalación", "Se descargará FFmpeg. Esto puede tomar unos minutos.")
        
        try:
            import urllib.request
            import zipfile
            
            urllib.request.urlretrieve(ffmpeg_url, 'ffmpeg.zip')
            with zipfile.ZipFile('ffmpeg.zip', 'r') as zip_ref:
                zip_ref.extractall('ffmpeg')
            
            os.environ['PATH'] += os.pathsep + os.path.abspath('ffmpeg/bin')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo instalar FFmpeg automáticamente.\n"
                                          f"Por favor descárgalo manualmente de:\n"
                                          f"https://ffmpeg.org/download.html\n\n"
                                          f"Error: {str(e)}")
    elif system == "Linux":
        try:
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'], check=True)
        except:
            messagebox.showwarning("Advertencia", "No se pudo instalar FFmpeg automáticamente.\n"
                                                  "Ejecuta en terminal:\n"
                                                  "sudo apt update && sudo apt install ffmpeg")
    elif system == "Darwin":
        try:
            subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
        except:
            messagebox.showwarning("Advertencia", "No se pudo instalar FFmpeg automáticamente.\n"
                                                  "Ejecuta en terminal:\n"
                                                  "brew install ffmpeg")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    if check_and_install_requirements():
        messagebox.showinfo("Éxito", "Todas las dependencias se instalaron correctamente.\n"
                                     "Ahora puedes ejecutar la aplicación principal.")
    else:
        messagebox.showerror("Error", "Hubo problemas instalando las dependencias.\n"
                                      "Consulta los mensajes anteriores para más detalles.")
    
    root.destroy()
