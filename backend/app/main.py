from fastapi import FastAPI, HTTPException
from app.schemas import PromptRequest, CommentResponse
from app.models import generate_comments

app = FastAPI(
    title="API de Generación de Comentarios con Ollama",
    description="Una API para generar retroalimentación educativa sobre código Python utilizando Ollama.",
    version="1.1.0"
)

@app.post("/generate_comments", response_model=CommentResponse)
async def generate_comments_endpoint(request: PromptRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="El campo 'prompt' no puede estar vacío.")
    
    response = generate_comments(request.prompt, request.code)
    
    if "error" in response:
        if response["error"].startswith("Falta la clave"):
            raise HTTPException(status_code=500, detail=response["error"])
        else:
            raise HTTPException(status_code=500, detail=response["error"])
    
    return CommentResponse(
        Rendimiento=response["Rendimiento"],
        Fallos_Solucion=response["Fallos_Solucion"],
        Fallos_Prueba=response["Fallos_Prueba"],
        Comentarios_Generales=response["Comentarios_Generales"]
    )
