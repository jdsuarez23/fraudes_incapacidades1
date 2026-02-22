# 🛡️ Sistema Híbrido de Detección de Fraude en Incapacidades (SGSSS)

Este proyecto es una herramienta impulsada por Inteligencia Artificial (CrewAI) y FastAPI en el backend, con un frontend moderno en Next.js. El sistema automatiza el análisis forense y médico de incapacidades colombianas para detectar posibles fraudes mediante la validación de códigos CIE-10, revisión cruzada de días de reposo, validación simulada en RETHUS y análisis profundo de metadatos (EXIF/CoreProps).

---

## 📋 Prerrequisitos

Asegúrate de tener instalado lo siguiente en tu sistema operativo:
- **Python 3.10+**
- **Node.js 18+** y `npm`
- **Git** (Opcional, para clonaje)

---

## ⚙️ 1. Configuración e Instalación del Backend (Python / FastAPI)

El backend orquesta el análisis utilizando **CrewAI** y procesa la extracción de documentos (PDF, DOCX, JPG, PNG).

### Paso 1: Crear entorno virtual
Abre una terminal en la raíz del proyecto (`fraude_incapacidades`) y ejecuta:
```bash
python -m venv .venv
```

### Paso 2: Activar el entorno virtual
En Windows (PowerShell/CMD):
```bash
.\.venv\Scripts\activate
```
En macOS/Linux:
```bash
source .venv/bin/activate
```

### Paso 3: Instalar Dependencias
Con el entorno virtual activado (debes ver `(.venv)` en la línea de comandos), instala todas las librerías necesarias:
```bash
pip install fastapi uvicorn python-multipart crewai pydentic PyYAML PyPDF2 python-docx exifread pytesseract Pillow beautifulsoup4 requests
```
*(Nota: Pytesseract requiere tener instalado el motor binario de Tesseract OCR en tu sistema para el escaneo de imágenes).*

### Paso 4: Variables de Entorno
Crea un archivo llamado `.env` en la raíz del proyecto (junto a `pyproject.toml`) y agrega tu API Key de OpenAI:
```env
OPENAI_API_KEY=tu_clave_api_aqui_sk-....
```

### Paso 5: Iniciar el servidor local
Para levantar la API de análisis, ejecuta:
```bash
uvicorn src.fraude_incapacidades.api:app --reload --port 8000
```
El servidor backend quedará escuchando peticiones en `http://127.0.0.1:8000`.

---

## 🖥️ 2. Configuración e Instalación del Frontend (Next.js)

El frontend sirve la interfaz "Cyber-Security" con un módulo de Drag & Drop para arrastrar documentos.

### Paso 1: Navegar a la carpeta del frontend
Abre una **nueva terminal** (mantén el backend corriendo en la otra), y navega al directorio del frontend:
```bash
cd frontend
```

### Paso 2: Instalar dependencias de Node
Ejecuta el siguiente comando para descargar los paquetes UI (lucide-react, react-dropzone, tailwindcss):
```bash
npm install
```

### Paso 3: Iniciar el servidor de desarrollo UI
```bash
npm run dev
```
La aplicación web estará disponible en [http://localhost:3000](http://localhost:3000).

---

## 🚀 Uso del Aplicativo

1. Abre tu navegador y dirígete a `http://localhost:3000`.
2. Verás el **Forensic Dashboard**.
3. Arrastra una incapacidad en formato **PDF**, **Word (.docx/.doc)**, o **Imagen (.png/.jpg)** a la zona delineada.
4. El Frontend enviará el archivo de forma segura y efímera a la API de FastAPI.
5. El framework de CrewAI iniciará el análisis en 3 pasos:
   - *Perito Forense*: Extrae textos puros y Metadatos ocultos.
   - *Auditor Médico*: Valida heurísticamente al médico contra simulador de RETHUS y días asignados mediante scraping del código CIE-10.
   - *Investigador OSINT*: Dictamina el porcentaje final de veracidad asumiendo la inocencia, salvo hallazgos de alteración digital o banderas médicas graves.
6. Espera a que termine la rueda de carga y observa el Score (%) y el Dictamen (VÁLIDA, SOSPECHOSA o FRAUDULENTA).
