from fastapi import FastAPI, HTTPException, Request, Form
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

class Farmer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    password: str = None
    name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    country: str
    zip: str

class GroceryItem(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str
    price: str
    quantity: str
    city: str
    state: str
    country: str
    farmer_id: int = Field(default=None, foreign_key="farmer.id")

class Contact(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str

class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    order_status: str
    total: float = None
    address: str
    zip: str

class OrderItem(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    order_id: int = Field(default=None, foreign_key="order.id")
    grocery_item_id: int = Field(default=None, foreign_key="groceryitem.id")
    quantity: str

ADMIN = {
    "username": "admin",
    "password": "admin"
}
# class Cart(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True)
#     user_id: int = Field(default=None, foreign_key="user.id")

# class CartItem(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True)
#     cart_id: int = Field(default=None, foreign_key="cart.id")
#     grocery_item_id: int = Field(default=None, foreign_key="groceryitem.id")
#     quantity: str

CART = {}

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
    try:
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()
            if user and user.password == password:
                return RedirectResponse(url="/home", status_code=302)
    except:
        pass
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
        
        return RedirectResponse(url="/recipe-sharing", status_code=302)
    
@app.get("/farmer-registration")
async def farmer_registration(request: Request):
    return templates.TemplateResponse(request=request, name="farmer-registration.html")

@app.post("/farmer-registration")
async def farmer_registration(request: Request):
    form = await request.form()
    name = form.get("name")
    password = form.get("password")
    email = form.get("email")
    phone = form.get("phone")
    address = form.get("address")
    city = form.get("city")
    state = form.get("state")
    country = form.get("country")
    zip = form.get("zip")
    with Session(engine) as session:
        farmer_exists = session.exec(select(Farmer).where(Farmer.email == email)).first()
        if farmer_exists:
            return templates.TemplateResponse(request=request, name="farmer-registration.html", context={"response": "Farmer already exists"})
        
        number_exists = session.exec(select(Farmer).where(Farmer.phone == phone)).first()
        if number_exists:
            return templates.TemplateResponse(request=request, name="farmer-registration.html", context={"response": "Phone number already exists"})

        farmer = Farmer(name=name, password=password, email=email, phone=phone, address=address, city=city, state=state, country=country, zip=zip)
        session.add(farmer)
        session.commit()
        session.refresh(farmer)

    return RedirectResponse(url="/farmer-login", status_code=302)

@app.get("/farmer-login")
async def farmer_login(request: Request):
    return templates.TemplateResponse(request=request, name="farmer-login.html")

@app.post("/farmer-login")
async def farmer_login(request: Request):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    try:
        with Session(engine) as session:
            farmer = session.exec(select(Farmer).where(Farmer.email == email)).first()
            if farmer and farmer.password == password:
                return RedirectResponse(url=f"/farmer-dashboard/{farmer.id}", status_code=302)
    except:
        pass
    return templates.TemplateResponse(request=request, name="farmer-login.html", context={"response": "Invalid email or password"})

@app.get("/farmer-dashboard/{farmer_id}")
async def farmer_dashboard(request: Request, farmer_id: int):
    with Session(engine) as session:
        farmer = session.exec(select(Farmer).where(Farmer.id == farmer_id)).first()
        grocery_items = session.exec(select(GroceryItem).where(GroceryItem.farmer_id == farmer_id)).all()
        if farmer:
            return templates.TemplateResponse(request=request, name="farmer-dashboard.html", context={"farmer": farmer, "grocery_items": grocery_items})
        return RedirectResponse(url="/farmer-login", status_code=302)
    
@app.post("/add-grocery-item/{farmer_id}")
async def add_grocery_item(request: Request):
    form = await request.form()
    name = form.get("item")
    description = form.get("description")
    price = form.get("price")
    quantity = form.get("quantity")
    farmer_id = int(request.path_params["farmer_id"])
    with Session(engine) as session:
        city = session.exec(select(Farmer).where(Farmer.id == farmer_id)).first().city
        state = session.exec(select(Farmer).where(Farmer.id == farmer_id)).first().state
        country = session.exec(select(Farmer).where(Farmer.id == farmer_id)).first().country
        grocery_item = GroceryItem(name=name, city=city, state=state, country=country, description=description, price=price, quantity=quantity, farmer_id=farmer_id)
        session.add(grocery_item)
        session.commit()
        session.refresh(grocery_item)
    return RedirectResponse(url=f"/farmer-dashboard/{farmer_id}", status_code=302)

@app.get("/local-ordering")
async def local_ordering():
    index_path = os.path.join(frontend_path, "local-ordering.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Local Ordering file not found")

@app.get("/search-grocery")
async def search_grocery(request: Request, query: str, city: str, state: str, country: str):
    with Session(engine) as session:
        if query == None:
            items = session.exec(select(GroceryItem).where(
                GroceryItem.city.ilike(f"%{city}%"),
                GroceryItem.state.ilike(f"%{state}%"),
                GroceryItem.country.ilike(f"%{country}%")
            )).all()
            return templates.TemplateResponse(request=request, name="search-grocery.html", context={"items": items})
        else:
            items = session.exec(select(GroceryItem).where(
                GroceryItem.name.ilike(f"%{query}%"),
                GroceryItem.city.ilike(f"%{city}%"),
                GroceryItem.state.ilike(f"%{state}%"),
                GroceryItem.country.ilike(f"%{country}%")
            )).all()
        return templates.TemplateResponse(request=request, name="search-grocery.html", context={"items": items})
    
@app.post("/add-to-cart")
async def add_to_cart(request: Request):
    with Session(engine) as session:
        form = await request.form()
        item_id = int(form.get("item_id"))
        quantity = form.get("quantity")
        item = session.exec(select(GroceryItem).where(GroceryItem.id == item_id)).first()
        if item:
            CART[item_id] = {"name": item.name, "price": item.price, "quantity": quantity}
            print(CART)
            return RedirectResponse(url="/view-cart", status_code=302)
        return RedirectResponse(url="/local-ordering", status_code=302)
    
@app.get("/view-cart")
async def view_cart(request: Request):
    total = 0
    for item_id, item in CART.items():
        # print(item)
        CART[item_id]["total"] = round(float(item["price"]) * int(item["quantity"]), 2)
        total += CART[item_id]["total"]
    return templates.TemplateResponse(request=request, name="view-cart.html", context={"cart": CART, "total": total})

@app.post("/confirm-order")
async def confirm_order(request: Request):
    with Session(engine) as session:
        form = await request.form()
        username = form.get("username")
        address = form.get("address")
        zip = form.get("zip")
        user = session.exec(select(User).where(User.username == username)).first()
        total = sum([int(item["total"]) for item in CART.values()])
        order = Order(user_id=user.id, total=total, address=address, zip=zip, order_status="Pending")
        session.add(order)
        session.commit()
        session.refresh(order)
        for item_id, item in CART.items():
            grocery_item = session.exec(select(GroceryItem).where(GroceryItem.id == item_id)).first()
            grocery_item.quantity = str(int(grocery_item.quantity) - int(item["quantity"]))
            if int(grocery_item.quantity) <= 0:
                session.delete(grocery_item)
            else:
                session.add(grocery_item)
            order_item = OrderItem(order_id=order.id, grocery_item_id=item_id, quantity=item["quantity"])
            session.add(order_item)
            session.commit()
            session.refresh(order_item)
        
        CART.clear()
        return templates.TemplateResponse(request=request, name="order-confirmation.html", context={"order_id": order.id})
    
@app.get("/order-tracking")
async def order_tracking(request: Request):
    return templates.TemplateResponse(request=request, name="order-tracking.html")

@app.post("/order-tracking")
async def order_status(request: Request):
    form = await request.form()
    order_id = form.get("order_id")
    with Session(engine) as session:
        order = session.exec(select(Order).where(Order.id == order_id)).first()
        items = session.exec(select(OrderItem, GroceryItem).where(OrderItem.order_id == order_id).where(OrderItem.grocery_item_id == GroceryItem.id)).all()
        item_details = [{"name": item.GroceryItem.name, "quantity": item.OrderItem.quantity} for item in items]
        if order:
            return templates.TemplateResponse(request=request, name="order-status.html", context={"order": order, "item_details": item_details})
        return RedirectResponse(url="/order-tracking", status_code=302)

@app.get("/admin-login")
async def admin_login(request: Request):
    return templates.TemplateResponse(request=request, name="admin-login.html", context={"response": ""})

@app.post("/admin-login")
async def admin_login(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    if username == ADMIN["username"] and password == ADMIN["password"]:
        return RedirectResponse(url="/admin-dashboard", status_code=302)
    return templates.TemplateResponse(request=request, name="admin-login.html", context={"response": "Invalid username or password"})

@app.get("/admin")
async def admin(request: Request):
    return RedirectResponse(url="/admin-login", status_code=302)

@app.get("/admin-dashboard")
async def admin_dashboard(request: Request):
    with Session(engine) as session:
        orders = session.exec(select(Order)).all()
        return templates.TemplateResponse("admin-dashboard.html", {
            "request": request,
            "orders": orders
        })

# Update order status
@app.post("/update-order-status/{order_id}")
async def update_order_status(order_id: int, order_status: str = Form(...)):
    with Session(engine) as session:
        order = session.get(Order, order_id)
        if order:
            order.order_status = order_status
            session.add(order)
            session.commit()
    return RedirectResponse(url="/admin-dashboard", status_code=303)


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