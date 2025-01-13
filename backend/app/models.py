
import json
import logging
import re
from ollama import generate
from ollama import GenerateResponse

# Configurar el logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_json(text: str) -> str:
    """
    Extrae el bloque de texto entre "JSON_BEGIN" y "JSON_END".

    :param text: Texto completo de la respuesta.
    :return: Cadena de texto que contiene el JSON.
    """
    json_pattern = re.compile(r'JSON_BEGIN\s*(\{.*?\})\s*JSON_END', re.DOTALL)
    match = json_pattern.search(text)
    if match:
        return match.group(1)
    return ''

def generate_comments(prompt: str, code: str) -> dict:
    prompt_text = (
        f'En base a la siguiente orden: "{prompt}", genera una retroalimentación instructiva y educacional del siguiente código: "{code}"'
        'de carácter universitario del siguiente código en lenguaje de Python. La retroalimentación debe estar '
        'estructurada exclusivamente en un JSON con las siguientes claves exactas: "Rendimiento", "Fallos de Solución", "Fallos de Prueba" y '
        '"Comentarios Generales". Cada clave debe tener como valor un párrafo separado correspondiente al tipo de retroalimentación. '
        'NO incluyas ningún texto, explicación o comentario adicional fuera del JSON. A continuación, incluye únicamente el JSON solicitado, '
        'encerrado entre las etiquetas "JSON_BEGIN" y "JSON_END".'
    )
    
    try:
        response: GenerateResponse = generate(
            model='llama3.2',
            prompt=prompt_text
        )
        response_text = response.get('response', '')
        logger.debug(f"Respuesta completa de Ollama: {response_text}")
        
        # Intentar extraer el JSON utilizando expresiones regulares con delimitadores
        json_str = extract_json(response_text)
        if not json_str:
            logger.error("No se encontró un bloque JSON delimitado en la respuesta de Ollama.")
            return {"error": "La respuesta de Ollama no contiene un JSON válido delimitado correctamente."}
        
        # Intentar parsear el JSON extraído
        comments = json.loads(json_str)
        
        # Validar que las claves necesarias estén presentes
        required_keys = ["Rendimiento", "Fallos de Solución", "Fallos de Prueba", "Comentarios Generales"]
        for key in required_keys:
            if key not in comments:
                return {"error": f'Falta la clave "{key}" en la respuesta.'}
        
        # Renombrar las claves para adaptarse al esquema de Pydantic
        return {
            "Rendimiento": comments["Rendimiento"],
            "Fallos_Solucion": comments["Fallos de Solución"],
            "Fallos_Prueba": comments["Fallos de Prueba"],
            "Comentarios_Generales": comments["Comentarios Generales"],
        }
        
    except json.JSONDecodeError:
        logger.error("La respuesta de Ollama no es un JSON válido.")
        logger.debug(f"Respuesta que falló al parsear: {response_text}")
        return {"error": "La respuesta de Ollama no es un JSON válido."}
    except Exception as e:
        logger.error(f'Ocurrió un error al generar comentarios: {e}')
        return {"error": f'Ocurrió un error al generar comentarios: {e}'}
