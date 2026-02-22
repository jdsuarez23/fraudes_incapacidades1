from __future__ import annotations

import json
import random
import re
from crewai.tools import tool

@tool("Validar Colegiatura del Médico en RETHUS")
def validar_rethus_tool(nombre_medico: str) -> str:
    """
    Busca al médico proporcionado en la base de datos oficial del RETHUS (Registro Único Nacional en Salud Colombiano)
    para verificar que cuenta con tarjeta profesional activa.
    
    Ejemplo de uso de input: "Dr. Carlos Perez" o "Carlos Perez"
    """
    if "no encontrado" in nombre_medico.lower() or not nombre_medico.strip():
        return "ERROR: No se ha podido extraer un nombre de médico legible del documento. Falla la validación institucional."
    
    # En un entorno de producción, aquí se realizaría web scraping con Selenium/Playwright 
    # o llamadas a una API oficial de MinSalud conectada al ReTHUS.
    # Dado que es una validación arquitectónica, simulamos determinísticamente la revisión.
    
    nombres_verídicos_conocidos = [
        "carlos", "maria", "juan", "andres", "luis", "diana", "jorge", "laura", "natalia"
    ]
    
    nombre_lower = nombre_medico.lower()
    es_valido = any(nombre in nombre_lower for nombre in nombres_verídicos_conocidos)
    
    if es_valido:
        # Simulamos respuesta exitosa de API
        return json.dumps({
            "estado": "ACTIVO",
            "profesion": "MEDICINA",
            "entidad_reportadora": "COLEGIO MEDICO COLOMBIANO",
            "mensaje": f"El profesional {nombre_medico} SI existe en RETHUS y está autorizado para emitir incapacidades."
        })
    else:
        # Simulamos médico no registrado (Bandera roja enorme)
        return json.dumps({
            "estado": "NO ENCONTRADO",
            "mensaje": f"ALERTA CRÍTICA: El profesional {nombre_medico} NO aparece en el Registro de MinSalud RETHUS. Alta sospecha de fraude o identidad falsa."
        })

@tool("Validar Código de Enfermedad CIE-10")
def validar_cie10_tool(codigo_cie10: str, dias_otorgados: int) -> str:
    """
    Busca el diagnóstico (ej. "J069") en el manual del CIE-10 y verifica si la cantidad de 
    días de incapacidad otorgados es congruente con los lineamientos del Ministerio de Salud.
    """
    codigo = str(codigo_cie10).strip().upper()
    
    # Simulador base de top diagnósticos
    base_cie10 = {
        "J069": {"enfermedad": "Infección aguda de las vías respiratorias", "max_dias_promedio": 3},
        "A09": {"enfermedad": "Diarrea y gastroenteritis infecciosa", "max_dias_promedio": 3},
        "M545": {"enfermedad": "Lumbago no especificado", "max_dias_promedio": 5},
        "F329": {"enfermedad": "Episodio depresivo no especificado", "max_dias_promedio": 30},
        "N390": {"enfermedad": "Infección de vías urinarias", "max_dias_promedio": 4}
    }
    
    # Búsqueda por similitud del código
    diagnostico = next((v for k, v in base_cie10.items() if codigo.startswith(k)), None)
    
    if diagnostico:
        try:
            dias = int(dias_otorgados)
            if dias <= diagnostico["max_dias_promedio"]:
                return f"CONGRUENCIA MÉDICA VALIDADA: El código {codigo} ({diagnostico['enfermedad']}) justifica plenamente {dias} días de reposo."
            else:
                return f"ALERTA CLÍNICA: La incapacidad otorga {dias} días para {codigo} ({diagnostico['enfermedad']}). El tiempo promedio máximo avalado suele ser {diagnostico['max_dias_promedio']} días. Podría ser exageración por fraude en días."
        except:
             return f"Enfermedad detectada: {diagnostico['enfermedad']}, pero no se pudo leer la cantidad de días."
    else:
        return f"El código {codigo} NO FUE IDENTIFICADO en los principales catálogos del CIE-10 O está mal escrito."
