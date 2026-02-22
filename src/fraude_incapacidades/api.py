from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os
import shutil
import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Importar el crew configurado
from fraude_incapacidades.crew import crew

app = FastAPI(title="Motor Antifraude SGSSS", description="API Forense para evaluación de incapacidades")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API Forense activa"}

@app.post("/api/v1/analyze")
async def analyze_document(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Formato no soportado, ingrese PDF o Imagen")

    # Cumplimiento Habeas Data: Crear directorio temporal protegido
    temp_dir = tempfile.mkdtemp()
    secure_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Guardar archivo de forma segura temporalmente
        with open(secure_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Ejecutar análisis exhaustivo con CrewAI
        # Pasamos el path temporal al input del primer task
        result = crew.kickoff(inputs={'file_path': secure_path})
        
        # CrewAI retorna un string que se espera sea JSON (formateado según expected_output)
        raw_result = str(result.raw if hasattr(result, 'raw') else result)
        
        # Intentar parsear a JSON si CrewAI devolvió JSON plano o markdown
        try:
            # Limpiar posible markdown (backticks)
            cleaned_result = raw_result.strip()
            if cleaned_result.startswith("```json"):
                cleaned_result = cleaned_result[7:]
            if cleaned_result.startswith("```"):
                cleaned_result = cleaned_result[3:]
            if cleaned_result.endswith("```"):
                cleaned_result = cleaned_result[:-3]
                
            report_data = json.loads(cleaned_result.strip())
        except json.JSONDecodeError:
            print(f"Error parseando JSON. Resultado raw: {raw_result}")
            # Fallback en caso de que el LLM no respete el formato estricto
            report_data = {
                "puntaje_veracidad": 50,
                "hallazgos_medicos": "Incapacidad procesada, pero el reporte no pudo ser parseado estructuralmente.",
                "analisis_forense": raw_result,
                "veredicto": "SOSPECHOSA"
            }
            
        return {"status": "success", "report": report_data}
        
    except Exception as e:
        print(f"Error en análisis de CrewAI: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Cumplimiento de la Ley 1581: borrar inmediatamente después de analizar
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
