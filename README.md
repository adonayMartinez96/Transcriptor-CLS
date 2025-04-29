Guía de Instalación para Script con Whisper (OpenAI)

📋 Requisitos mínimos
Python 3.9 o superior (imprescindible)

FFmpeg (obligatorio para procesar audio)

4GB+ RAM (recomendado 8GB para modelos medianos/grandes)

🚀 Instalación en 3 pasos
1. Instalar dependencias del sistema
Windows (PowerShell):
powershell
winget install Python.Python.3.10
choco install ffmpeg
Linux (Ubuntu/Debian):
bash
sudo apt update && sudo apt install python3 python3-pip ffmpeg
macOS (Homebrew):
bash
brew install python ffmpeg
2. Instalar Python (si no está instalado)
Descargar desde python.org
✅ Marcar opción "Add Python to PATH"

3. Instalar dependencias de Python
bash
pip install openai-whisper torch ffmpeg-python
📄 Archivo requirements.txt optimizado
openai-whisper==20231117
torch==2.2.1
ffmpeg-python==0.2.0
Nota sobre Torch: Si tienes GPU NVIDIA, instala esta versión después:

bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
▶️ Ejecución del script
bash
python tu_script_con_whisper.py
🔍 Solución rápida de problemas
Error común	Solución
No module named 'whisper'	pip uninstall whisper && pip install openai-whisper
FFmpeg not found	Verificar instalación con ffmpeg -version
Out of memory	Usar modelo más pequeño: whisper.load_model('tiny')
