from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# قاعدة بيانات SQLite جاهزة للعمل مباشرة على السيرفر السحابي
SQLALCHEMY_DATABASE_URL = "sqlite:///./portfolio.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(100))

Base.metadata.create_all(bind=engine)

def init_db():
    db = SessionLocal()
    if not db.query(UserModel).filter(UserModel.username == "fatima").first():
        default_user = UserModel(username="fatima", password="1234")
        db.add(default_user)
        db.commit()
    db.close()

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginData(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# عرض الصفحة الرئيسية مباشرة عند فتح الرابط
@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.post("/api/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(
        UserModel.username == data.username,
        UserModel.password == data.password
    ).first()
    
    if user:
        return {"status": "success", "message": f"Welcome back, {user.username}!"}
    
    raise HTTPException(status_code=401, detail="Invalid username or password!")