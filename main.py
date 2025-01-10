from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Field, Session, create_engine, select
from rag import recipe_generator_rag, grocery_list_rag, meal_planning_rag
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
    image_url: str = None
    description: str = None
    ingredients: str
    instructions: str
    prep_time: str = None
    cook_time: str = None
    servings: str = None
    dietary_notes: str = None
    user_id: int = Field(default=None, foreign_key="user.id")

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

@app.get("/")
async def home(request: Request):
    return RedirectResponse(url="/login", status_code=302)

@app.get("/home", response_class=HTMLResponse)
async def read_index(request: Request):
    index_path = os.path.join(frontend_path, "index.html")  # Adjusted to match renamed files
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Index file not found")

@app.get("/login")
async def login(request: Request):
    index_path = os.path.join(frontend_path, "login.html")  # Adjusted to match renamed files
    if os.path.exists(index_path):
        return templates.TemplateResponse(request=request, name="login.html", context={"response": ""})
    raise HTTPException(status_code=404, detail="Login file not found")

@app.post("/login")
async def login_user(request: Request):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if user and user.password == password:
            return RedirectResponse(url="/home", status_code=302)
    return templates.TemplateResponse(request=request, name="login.html", context={"response": "Invalid username or password"})

@app.get("/signup")
async def register(request: Request):
    index_path = os.path.join(frontend_path, "signup.html")
    if os.path.exists(index_path):
        return templates.TemplateResponse(request=request, name="signup.html", context={"response": ""})
    raise HTTPException(status_code=404, detail="Signup file not found")

@app.post("/signup")
async def register_user(request: Request):
    form_data = await request.form()
    username = form_data.get("username")
    email = form_data.get("email")
    password = form_data.get("password")
    with Session(engine) as session:
        # Check if username already exists
        user_exists = session.exec(select(User).where(User.username == username)).first()
        if user_exists:
            return templates.TemplateResponse(request=request, name="signup.html", context={"response": "Username already exists"})
        
        # Check if email already exists
        email_exists = session.exec(select(User).where(User.email == email)).first()
        if email_exists:
            return templates.TemplateResponse(request=request, name="signup.html", context={"response": "Email already exists"})
        
        # Create new user
        user = User(username=username, email=email, password=password)
        session.add(user)
        session.commit()
        session.refresh(user)

    return RedirectResponse(url="/login", status_code=302)

@app.get("/contact")
async def contact():
    index_path = os.path.join(frontend_path, "contact.html")  # Adjusted to match renamed files
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Contact file not found")

@app.get("/about")
async def about():
    index_path = os.path.join(frontend_path, "about.html")  # Adjusted to
    if os.path.exists(index_path):
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
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="AI Recipe Generator file not found")

@app.post("/ai-recipe-generator")
async def ai_recipe_generator_post(request: Request):
    form_data = await request.form()
    ingredients = form_data.get("ingredients")
    recipe_response = recipe_generator_rag(input_variables={"ingredients": ingredients})
    print(recipe_response)
    return templates.TemplateResponse(request=request, name="ai-recipe-generator-response.html", context={"response": recipe_response})

@app.get("/smart-grocery-list")
async def smart_grocery_list():
    index_path = os.path.join(frontend_path, "smart-grocery-list.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Smart Grocery List file not found")

@app.post("/smart-grocery-list")
async def smart_grocery_list_post(request: Request):
    form_data = await request.form()
    grocery_list = form_data.get("grocery")
    servings = form_data.get("servings")
    note = form_data.get("note")
    input_variables = {"grocery_list": grocery_list, "servings": servings, "note": note}
    response = grocery_list_rag(input_variables)
    print(response)
    return templates.TemplateResponse(request=request, name="smart-grocery-list-response.html", context={"response": response})

@app.get("/meal-planning")
async def meal_planning():
    index_path = os.path.join(frontend_path, "meal-planning.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Meal Planning file not found")

@app.post("/meal-planning")
async def meal_planning_post(request: Request):
    form_data = await request.form()
    allergies = form_data.get("allergies")
    dietary_restrictions = form_data.get("dietary-restrictions")
    health_conditions = form_data.get("health-conditions")
    time_constraints = form_data.get("time-constraints")
    cooking_skills = form_data.get("cooking-skills")
    budget = form_data.get("budget")
    taste_preferences = form_data.get("taste-preferences")
    meal_plan = meal_planning_rag(input_variables={"allergies": allergies, "dietary_restrictions": dietary_restrictions, "health_conditions": health_conditions, "time_constraints": time_constraints, "cooking_skills": cooking_skills, "budget": budget, "taste_preferences": taste_preferences})
    return templates.TemplateResponse(request=request, name="meal-planning-response.html", context={"response": meal_plan})

@app.get("/recipe-sharing")
async def recipe_sharing(request: Request):
    index_path = os.path.join(frontend_path, "recipe-sharing.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Recipe Sharing file not found")

@app.post("/recipe-sharing")
async def recipe_sharing_post(request: Request):
    form_data = await request.form()
    recipe_title = form_data.get("recipe_title")
    image_url = form_data.get("imageurl")
    description = form_data.get("description")
    ingredients = form_data.get("ingredients")
    instructions = form_data.get("instructions")
    prep_time = form_data.get("preptime")
    cook_time = form_data.get("cooktime")
    servings = form_data.get("servings")
    dietary_notes = form_data.get("dietarynotes")
    username = form_data.get("username")

    with Session(engine) as session:
        
        user = session.exec(select(User).where(User.username == username)).first()
        if user:
            print(recipe_title)
            recipe = Recipe(
                title=recipe_title,
                image_url=image_url,
                description=description,
                ingredients=ingredients,
                instructions=instructions,
                prep_time=prep_time,
                cook_time=cook_time,
                servings=servings,
                dietary_notes=dietary_notes,
                user_id=user.id
            )
            session.add(recipe)
            session.commit()
            session.refresh(recipe)

            return RedirectResponse(url=f"/recipes-sharing-blog/{recipe.id}", status_code=302)
        else:
            return templates.TemplateResponse(request=request, name="recipe-sharing.html", context={"response": "User not found"})

@app.get("/recipes-sharing-blog/{recipe_id}")
async def recipe_sharing_blog(request: Request, recipe_id: int):
    with Session(engine) as session:
        recipe = session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()
        user = session.exec(select(User).where(User.id == recipe.user_id)).first()
        if recipe:
            return templates.TemplateResponse(request=request, name="recipe-sharing-blog.html", context={
                "recipe_title": recipe.title.replace("\n", "<br>"),
                "image_url": recipe.image_url,
                "description": recipe.description.replace("\n", "<br>"),
                "ingredients": recipe.ingredients.replace("\n", "<br>"),
                "instructions": recipe.instructions.replace("\n", "<br>"),
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "servings": recipe.servings,
                "dietary_notes": recipe.dietary_notes.replace("\n", "<br>"),
                "author": user.username
            })

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