import os
from agent_graph.tools import *
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import ToolExecutor, ToolInvocation


# ----------------------------------------------------------
# Tools
# ----------------------------------------------------------

tools = [python_repl, validate_json]
tool_executer = ToolExecutor(tools)


# ----------------------------------------------------------
# Graph State
# ----------------------------------------------------------

class MyState(TypedDict):
    query_name: str = ""
    data_file: str = ""
    columns: str = ""
    description: str = ""
    pq: str = ""
    pq_output: str = ""
    exe_output: str = ""
    num_of_exe: int = None
    errors: str = ""
    reflection: str = ""
    recent_errors: str = ""


# ----------------------------------------------------------
# Prompt
# ----------------------------------------------------------

initial_prompt = ChatPromptTemplate.from_messages([
    ('system',
        "You are an expert python coder which likes using the pandas library."
        "You write code that is well commented and easy to understand."
        "The comments will explain your chain of thought."
        "The user will give you:"
        "   1. The name of a data file."
        "   2. The names of the data file's columns, separated by commas."
        "   3. A description of a query to the data file."
        "   4. A name of a target file."
        "You will generate a python program that:"
        "   1. Queries the CSV file according to the description."
        "   2. Saves the result to the target file as a JSON array."
        "***Notes:"
        "   1. Do not responds with anything else except for the code and comments."
        "   2. Make sure NOT to wrap code snippet in triple backticks."
        "   3. Don't Write anything that is not part of the code or the comments."
     ),
    ('human',
        "Data file name: {data_file}."
        "Columns: {columns}."
        "Query description: {description}."
        "Target file: {query_name}.txt"
     ),
    ('placeholder',
        "{conversation}"
     )
])


# ----------------------------------------------------------
# LLM
# ----------------------------------------------------------

load_dotenv()

model = AzureChatOpenAI(
    azure_endpoint='https://openaifor3267.openai.azure.com/',
    azure_deployment='gpt4',
    openai_api_version='2024-02-01',
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    temperature=0.5,
)


# ----------------------------------------------------------
# Chain
# ----------------------------------------------------------

chain = initial_prompt | model | StrOutputParser()


# ----------------------------------------------------------
# Agents
# ----------------------------------------------------------

def init(state):
    with open('query_input.txt', 'r') as file:
        lines = file.readlines()

    state['query_name'] = lines[0].split(":")[1].strip()
    state['data_file'] = lines[1].split(":")[1].strip()
    state['columns'] = lines[2].split(":")[1].strip()

    description_file = state['query_name'] + "_query.txt"
    with open(description_file, 'r') as file:
        state['description'] = file.read().strip()

    print("Executing Agent: Initialize")
    return state


def generate_pq(state):
    prompt_info = {
        'data_file': state['data_file'],
        'columns': state['columns'],
        'description': state['description'],
        'query_name': state['query_name'],
    }

    state['pq'] = chain.invoke(input=prompt_info).strip()
    print("Executing Agent: GenQueryProgram")
    return state


def execute_pq(state):

    python_tool = ToolInvocation(tool='python_repl', tool_input=state['pq'])
    python_tool_res = tool_executer.invoke(python_tool)
    state['exe_output'] = python_tool_res.strip()
    state['num_of_exe'] += 1
    print(f"Executing Agent: ExecuteProgram (#{state['num_of_exe']})")
    return state


def check_4_err(state):
    state['recent_errors'] = state['errors']
    state['errors'] = ""
    if (state['exe_output'] != ""):
        state['errors'] = state['exe_output']
    elif not (os.path.exists(f"{state['query_name']}.txt")):
        state['errors'] = "The program executed without errors but the output file was not created."
    else:
        with open(f"{state['query_name']}.txt", 'r') as file:
            state['pq_output'] = file.read().strip()
        json_tool = ToolInvocation(
            tool='validate_json', tool_input=state['pq_output'])
        if not (tool_executer.invoke(json_tool)):
            state['errors'] = "The program executed without errors but the output file does not contain a valid JSON array."

    print("Executing Agent: Chk4rErr")
    return state


def reflect_on_err(state):
    conversation = [
        ('ai', f"{state['pq']}"),
        ('system',
         "Understand the original prompt made by the human."
         "Reflect on the code provided by the AI."
         "The human will list all the errors that occured."
         "Understand the errors and which part of the code caused them."
         "Verbally explain the errors."
         "Suggest how they can be fixed."
         ),
        ('human', f"The errors: {state['errors']}"),
    ]

    prompt_info = {
        'data_file': state['data_file'],
        'columns': state['columns'],
        'description': state['description'],
        'query_name': state['query_name'],
        'conversation': conversation
    }

    state['reflection'] = chain.invoke(input=prompt_info).strip()
    print("Executing Agent: ReflectOnErr")
    return state


def regenerate_pq(state):
    conversation = [
        ('ai', f"{state['pq']}"),
        ('system',
         "The code generated by the AI is faulty."
         "You will be given a list of errors that occured when the code was executed."
         "You will be given a verbal reflection of the errors and what caused them."
         "Use insights from the reflection to regenerate the code."
         ),
        ('human', f"The errors were:{state['errors']}"),
        ('human', f"My reflection on the issues: {state['reflection']}"),
    ]

    prompt_info = {
        'data_file': state['data_file'],
        'columns': state['columns'],
        'description': state['description'],
        'query_name': state['query_name'],
        'conversation': conversation
    }

    state['pq'] = chain.invoke(input=prompt_info).strip()
    print("Executing Agent: ReGenQueryPgm")
    return state


def prep_2_terminate(state):
    if (state['recent_errors'] == None):
        state['recent_errors'] = "No errors were found."
    if (state['reflection'] == None):
        state['reflection'] = "No reflection was generated."
    with open(f'{state["query_name"]}_errors.txt', 'w') as file:
        file.write(state['recent_errors'])
    with open(f'{state["query_name"]}_reflect.txt', 'w') as file:
        file.write(state['reflection'])
    with open(f'{state["query_name"]}.py', 'w') as file:
        file.write(state['pq'])

    print("Executing Agent: PrepareToTerminate")
    return state
