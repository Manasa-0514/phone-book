from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import Contact
from database import SessionLocal, engine, init_db

app = FastAPI()

# Initialize the database
init_db()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for contact
class ContactCreate(BaseModel):
    name: str
    phone: str

class ContactResponse(BaseModel):
    id: int
    name: str
    phone: str

    class Config:
        orm_mode = True

# Routes
@app.get("/api/contacts", response_model=list[ContactResponse])
def read_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return contacts

@app.post("/api/contacts", response_model=ContactResponse)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    db_contact = Contact(name=contact.name, phone=contact.phone)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.delete("/api/contacts/{contact_id}", status_code=204)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(db_contact)
    db.commit()
