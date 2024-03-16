from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from fastapi_neon import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

class Todo(SQLModel, table =True):
    id: Optional[int] = Field(None, primary_key=True)
    content:str = Field(index=True)

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine) 
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield
    
app = FastAPI(lifespan=lifespan, title="Hello World API with DB by Afnan",
    version="0.0.1",
    servers=[
        {
            "url": "https://wasp-hot-unlikely.ngrok-free.app/",
            "description": "Development Server"
        }
    ])

def get_session():
    with Session(engine) as session:
        yield session
        
@app.get('/')
def read_root(session: Session = Depends(get_session)):
    todos = session.exec(select(Todo)).all()
    return todos

@app.post('/todos/')
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
    return {"message": "Todo deleted successfully"}


origins = [
    "*",
    "https://todo-fastapi-lglaft0ln-muhammad-afnan-siddiquis-projects.vercel.app",
    "https://todo-fastapi-git-master-muhammad-afnan-siddiquis-projects.vercel.app",
    "https://todo-fastapi-ten.vercel.app",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://wasp-hot-unlikely.ngrok-free.app/" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
