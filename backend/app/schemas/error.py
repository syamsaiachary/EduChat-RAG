from pydantic import BaseModel

class AppErrorSchema(BaseModel):
    error: bool = True
    code: str
    message: str
    status_code: int
