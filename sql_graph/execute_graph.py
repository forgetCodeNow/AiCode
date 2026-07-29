import asyncio

from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

from sql_graph.llm_model import llm
from sql_graph.text2sql_graph import make_graph


async def execute_graph():
    """执行工作流"""
    async with make_graph() as graph:
        while True:
            user_input = input('用户：')
            if user_input.lower() in ['q', 'exit', 'quit']:
                print('对话结束，拜拜！')
                break
            else:
                async for event in graph.astream({"messages": [{"role": "user", "content": user_input}]},
                                                 stream_mode="values"):
                    event["messages"][-1].pretty_print()

if __name__ == '__main__':
    # db = SQLDatabase.from_uri('sqlite:///../chinook.db')
    # toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    #
    # tools = toolkit.get_tools()
    # for tool in tools:
    #     print(tool.name+'===='+tool.description)
    #
    # list_tables_tool = next(tool for tool in tools if tool.name == 'sql_db_list_tables')
    #
    # resp = list_tables_tool.invoke('')
    # print(resp)

    asyncio.run(execute_graph())