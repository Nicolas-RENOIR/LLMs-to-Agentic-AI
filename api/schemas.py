from pydantic import BaseModel

class PublicationBase(BaseModel):
    id_campaign: str
    id_publication: str
    image_prompt: str
    caption: str
    image: str

class PublicationCreate(PublicationBase):
    pass

class Publication(PublicationBase):
    id: int

    class Config:
        orm_mode = True