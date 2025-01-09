import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.75)

def recipe_generator_rag(input_variables):
    prompt_template = """
        Answer the following question in a detailed manner providing each and every step. Include all the necessary details. You must include the ingredients and its quantity, the cooking time, the cooking method, and any other relevant information. You may also include extra ingredients if you think it will enhance the recipe.
        Think step by step before providing an answer, and make sure to provide all the details.
        Always return the response in HTML body format.
        Do not include ''', * and <html>, <body>, <li> tags in the response. Always mention the ingredients along with their quantities. Use <br> to differentiate the points.\n
        \n\n

        Question: Generate a comprehensive recipe based on the following ingredients:
        {ingredients}
    """
    prompt = PromptTemplate(template=prompt_template, input_variables={"ingredients"})
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke(input_variables)
    return response

def grocery_list_rag(input_variables):
    # prompt_template = """
    #     Include all the necessary details. You may also include extra ingredients if you think it will enhance the recipe. 
    #     Think step by step before providing an answer, and make sure to provide all the details.
    #     You must identify the ingredients and their quantities from the recipes' names or ingredients provided.
    #     Always mention the grocery items in a list format along with their quantities.\n\n

    #     Question: Generate a comprehensive grocery list along with their quantities based on the recipes' names: 

    #     {grocery_list}

    #     Servings: {servings}
    # """
    prompt_template = """
        Provide a grocery list for the following recipe name:
        Recipe: {grocery_list}
        Servings: {servings}
        Note: {note}
    """
    prompt = PromptTemplate(template=prompt_template, input_variables={"grocery_list", "servings", "note"})
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke(input_variables)
    return response

def meal_planning_rag(input_variables):
    prompt_template = """
        Provide a meal planning based on the following factors:
        
        Allergies/Intolerances: {allergies}
        
        Dietary Restrictions: {dietary_restrictions}
        
        Health Conditions: {health_conditions}
        
        Time Constraints: {time_constraints}
        
        Cooking skills: {cooking_skills}
        
        Grocery Budget: {budget}
        
        Taste preferences: {taste_preferences}
    """
    prompt = PromptTemplate(template=prompt_template, input_variables={"allergies", "dietary_restrictions", "health_conditions", "time_constraints", "cooking_skills", "budget", "taste_preferences"})
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke(input_variables)
    return response