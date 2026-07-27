from contextlib import asynccontextmanager

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph

from langchain_mcp_adapters.client import MultiServerMCPClient

from sql_graph.my_state import SQLState

mcp_server_config = {
    'url': 'http://localhost:8008/sse',
    'transport': 'sse',
}

@asynccontextmanager
async def make_graph():
    """定义、并且编译工作流"""
    mcp_client = MultiServerMCPClient({'my_mcp': mcp_server_config})
    tools = mcp_client.get_tools()
    # 获取所有表名的工具
    list_tables_tool = next(tool for tool in tools if tool.name == 'list_tables_tool')
    # 执行SQL语句的工具
    db_query_tool = next(tool for tool in tools if tool.name == 'db_query_tool')

    def list_tables(state: SQLState):
        """获取数据库所有表名(自定义工具指令和工具调用)"""
        # 自定义工具调用指令
        tool_call = {
            'name': 'list_tables_tool',
            'args': {},
            'id': 'abc123',
            'type': 'tool_call'
        }
        tool_call_message = AIMessage(content='', tool_calls=[tool_call])
        # 工具调用
        tool_message = list_tables_tool.invoke(tool_call)

        response = AIMessage(f'所有可用的表: {tool_message.content}')
        return {'messages': [tool_call_message, tool_message, response]}

    workflow = StateGraph(SQLState)


