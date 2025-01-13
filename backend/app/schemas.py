from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str
    code: str

class CommentResponse(BaseModel):
    Rendimiento: str
    Fallos_Solucion: str
    Fallos_Prueba: str
    Comentarios_Generales: str