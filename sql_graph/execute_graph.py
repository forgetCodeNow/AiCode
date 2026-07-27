from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

from sql_graph.llm_model import llm

if __name__ == '__main__':
    db = SQLDatabase.from_uri('sqlite:///../chinook.db')
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    tools = toolkit.get_tools()
    for tool in tools:
        print(tool.name+'===='+tool.description)

    list_tables_tool = next(tool for tool in tools if tool.name == 'sql_db_list_tables')

    resp = list_tables_tool.invoke('')
    print(resp)