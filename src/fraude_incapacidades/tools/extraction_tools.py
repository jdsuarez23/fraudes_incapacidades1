from __future__ import annotations

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import docx
import exifread
import os
from PyPDF2 import PdfReader
from crewai.tools import tool

@tool("Extraer texto y metadatos del documento")
def extract_document_info_tool(file_path: str) -> str:
    """
    Extrae el texto completo de un documento (PDF, DOCX, JPG, PNG) y busca activamente metadatos (EXIF)
    para detectar rastros de edición digital en metadatos, software utilizado para crearlo (ej. Adobe),
    y fechas de creación vs modificación.
    
    Retorna un reporte estructurado con el texto plano y los metadatos relevantes encontrados.
    """
    if not os.path.exists(file_path):
        return f"Error: No se encontró el archivo en la ruta {file_path}"
        
    text_content = ""
    metadata_report = []
    file_ext = file_path.lower().split('.')[-1]
    
    try:
        # Extracción PDF
        if file_ext == "pdf":
            # Extraer Texto
            doc = fitz.open(file_path)
            for page in doc:
                text_content += page.get_text()
                
            # Extraer Metadatos
            try:
                reader = PdfReader(file_path)
                meta = reader.metadata
                if meta:
                    metadata_report.append(f"Metadatos PDF:")
                    metadata_report.append(f"- Autor: {meta.get('/Author', 'N/A')}")
                    metadata_report.append(f"- Creador/Software: {meta.get('/Creator', 'N/A')}")
                    metadata_report.append(f"- Productor/Herramienta: {meta.get('/Producer', 'N/A')}")
                    metadata_report.append(f"- Fecha Creación: {meta.get('/CreationDate', 'N/A')}")
                    metadata_report.append(f"- Fecha Modificación: {meta.get('/ModDate', 'N/A')}")
            except Exception as meta_err:
                metadata_report.append(f"No se pudieron extraer metadatos del PDF: {meta_err}")
                
        # Extracción DOCX
        elif file_ext in ["docx", "doc"]:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text_content += para.text + "\n"
            
            # Extracción propiedades Core de Word
            core_props = doc.core_properties
            metadata_report.append(f"Metadatos Word:")
            metadata_report.append(f"- Autor: {core_props.author}")
            metadata_report.append(f"- Último modificador: {core_props.last_modified_by}")
            metadata_report.append(f"- Fecha Creación: {core_props.created}")
            metadata_report.append(f"- Fecha Modificación: {core_props.modified}")
            
        # Extracción Imagen (OCR y EXIF)
        elif file_ext in ["jpg", "jpeg", "png"]:
            img = Image.open(file_path)
            text_content = pytesseract.image_to_string(img, lang="spa")
            
            # Extraer Exif
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                metadata_report.append("Metadatos EXIF Imagen:")
                if tags:
                    soft_tag = tags.get('Image Software', 'N/A')
                    date_tag = tags.get('Image DateTime', 'N/A')
                    metadata_report.append(f"- Software/Edición: {soft_tag}")
                    metadata_report.append(f"- Fecha Captura/Edición: {date_tag}")
                else:
                    metadata_report.append("- No se detectaron datos EXIF (podría provenir de WhatsApp recortado o screenshot).")
                    
        else:
            return "Formato de archivo no soportado."
            
        full_report = f"[TEXTO EXTRAÍDO DEL DOCUMENTO]\n{text_content}\n\n[ANÁLISIS DE METADATOS Y RASTROS DIGITALES]\n" + "\n".join(metadata_report)
        return full_report
        
    except Exception as e:
        return f"Error procesando el archivo para extracción profunda: {e}"
