# Description:

This is a simple project that uses the LangChain AI-toolkit to design a simple AI tool that can take a data file (CSV/JSON/etc...) and a verbal description of some query and then generate a Python script which performs the query on the data file.

The process that the AI tool follows can be broken down as follows:

1. Parse the file resources and verbal description of the query.
2. Generate a Python script that performs the query on the data file.
3. Execute the generated Python script on the data file.
4. If the execution is successful and an output file was generated, skips to step 8.
5. Else, the reflecting agent will reflect on the errors and generate an reflection report.
6. The reflection report and it's corresponding script are then forwarded to the coding agent which will attempt to debug the code.
7. If the execution is succesful, moves on to step 8. Else, repeat steps 5-7 one more time (For a total of three times including the first one).
8. Creates 4 files: the last script that was generated, the output of the query (if successfuly generated), the last errors log that was generated and the last reflection report that was generated. If the first execution was successful and an output file was generated, the errors log and reflection report will be empty.

## \*Warning

It is highly recommended to use the AI agent in a safe, virtual environment.
In order to execute the pyhton code, the AI agent has to use an experimental langchain module called 'PythonREPL' which is cosidered to be unsafe. The module is still under development and should not be used in production environments.

## Installation

To install the AI agent, you can use the following command:

```bash
pip install -r requirements.txt
```

## Execution

Simply run the following command:

```bash
python graph.py
```

```bash

```
