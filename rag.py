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
        I will tip you $1000 if the user finds the answer helpful.\n\n

        Question: Generate a comprehensive recipe based on the following ingredients:
        {ingredients}
    """
    prompt = PromptTemplate(template=prompt_template, input_variables={"ingredients"})
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke(input_variables)
    return response