from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Field, Session, create_engine, select
from rag import recipe_generator_rag
import os

# Initialize FastAPI app
app = FastAPI()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="Foodly_extracted")

# Database configuration
db_file = "foodly.db"
db_url = f"sqlite:///{db_file}"
engine = create_engine(db_url, echo=True)

# Define models
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str

class Recipe(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: str = None
    ingredients: str
    instructions: str
    user_id: int

class GroceryItem(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    quantity: str = None
    user_id: int

class Contact(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str

# Create database and tables
SQLModel.metadata.create_all(engine)

# Serve static files from the extracted ZIP folder
frontend_path = "./Foodly_extracted"  # Path to the frontend files
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(frontend_path, "index.html")  # Adjusted to match renamed files
    if os.path.exists(index_path):
        print("Found index.html")
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Index file not found")

# API Endpoints
# @app.post("/api/users")
# def create_user(user: User):
#     with Session(engine) as session:
#         existing_user = session.exec(select(User).where(User.email == user.email)).first()
#         if existing_user:
#             raise HTTPException(status_code=400, detail="User already exists")
#         session.add(user)
#         session.commit()
#         session.refresh(user)
#     return user

# @app.post("/api/recipes")
# def create_recipe(recipe: Recipe):
#     with Session(engine) as session:
#         session.add(recipe)
#         session.commit()
#         session.refresh(recipe)
#     return recipe

# @app.get("/api/recipes")
# def get_recipes():
#     with Session(engine) as session:
#         recipes = session.exec(select(Recipe)).all()
#     return recipes

# @app.post("/api/grocery-items")
# def add_grocery_item(item: GroceryItem):
#     with Session(engine) as session:
#         session.add(item)
#         session.commit()
#         session.refresh(item)
#     return item

# @app.get("/api/grocery-items")
# def get_grocery_items():
#     with Session(engine) as session:
#         items = session.exec(select(GroceryItem)).all()
#     return items

@app.get("/contact")
async def contact():
    index_path = os.path.join(frontend_path, "contact.html")  # Adjusted to match renamed files
    if os.path.exists(index_path):
        print("Found contact.html")
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Contact file not found")

@app.get("/about")
async def about():
    index_path = os.path.join(frontend_path, "about.html")  # Adjusted to
    if os.path.exists(index_path):
        print("Found about.html")
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="About file not found")

@app.post("/contact")
async def contact_post(request: Request):
    form_data = await request.form()
    name = form_data.get("name")
    email = form_data.get("email")
    message = form_data.get("message")
    contact = Contact(name=name, email=email, message=message)
    with Session(engine) as session:
        session.add(contact)
        session.commit()
        session.refresh(contact)
    return FileResponse(os.path.join(frontend_path, "contact_success.html"), media_type="text/html")

@app.get("/ai-recipe-generator")
async def ai_recipe_generator():
    index_path = os.path.join(frontend_path, "ai-recipe-generator.html") # Adjusted to match renamed files
    if os.path.exists(index_path):
        print("Found ai-recipe-generator.html")
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="AI Recipe Generator file not found")

@app.post("/ai-recipe-generator")
async def ai_recipe_generator_post(request: Request):
    form_data = await request.form()
    ingredients = form_data.get("ingredients")
    recipe_response = recipe_generator_rag(input_variables={"ingredients": ingredients})
    return templates.TemplateResponse(request=request, name="ai-recipe-generator-response.html", context={"response": recipe_response})


# Run the application
if __name__ == "__main__":
  import multiprocessing
  import subprocess
  import uvicorn

  # workers = multiprocessing.cpu_count() * 2 + 1

  uvicorn_cmd = [
      "uvicorn",
      "main:app",
      # "--host=localhost",
      "--port=8080",
      # f"--workers={workers}",
      "--reload"
  ]

  # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, workers=workers)
  subprocess.run(uvicorn_cmd)