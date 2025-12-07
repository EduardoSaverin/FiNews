from pydantic import BaseModel

class Article(BaseModel):
    id: int
    title: str
    link: str
    summary: str
    source_name: str
    published_at: str
    content: str