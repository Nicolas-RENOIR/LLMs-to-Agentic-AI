from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/publications/", response_model=schemas.Publication)
def create_publication(publication: schemas.PublicationCreate, db: Session = Depends(get_db)):
    db_pub = models.Publication(**publication.dict())
    db.add(db_pub)
    db.commit()
    db.refresh(db_pub)
    return db_pub

@app.get("/publications/", response_model=list[schemas.Publication])
def read_publications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Publication).offset(skip).limit(limit).all()

@app.get("/publications/{pub_id}", response_model=schemas.Publication)
def read_publication(pub_id: int, db: Session = Depends(get_db)):
    pub = db.query(models.Publication).filter(models.Publication.id == pub_id).first()
    if pub is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    return pub

@app.put("/publications/{pub_id}", response_model=schemas.Publication)
def update_publication(pub_id: int, updated: schemas.PublicationCreate, db: Session = Depends(get_db)):
    pub = db.query(models.Publication).filter(models.Publication.id == pub_id).first()
    if pub is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    for key, value in updated.dict().items():
        setattr(pub, key, value)
    db.commit()
    db.refresh(pub)
    return pub

@app.delete("/publications/{pub_id}")
def delete_publication(pub_id: int, db: Session = Depends(get_db)):
    pub = db.query(models.Publication).filter(models.Publication.id == pub_id).first()
    if pub is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    db.delete(pub)
    db.commit()
    return {"detail": "Deleted"}