from pydantic import BaseModel

# Pydantic models
class TaskCreateUpdateModel(BaseModel):
    title: str
    description: str

class TaskResponseModel(TaskCreateUpdateModel):
    id: int