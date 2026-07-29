from contextlib import asynccontextmanager

from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import ToolNode, tools_condition

from sql_graph.llm_model import llm
from sql_graph.my_state import SQLState
from sql_graph.tools_node import generate_query_system_prompt, query_check_system, call_get_schema, get_schema_node

mcp_server_config = {
    'url': 'http://localhost:8008/sse',
    'transport': 'sse',
}


@asynccontextmanager
async def make_graph():
    """定义、并且编译工作流"""
    mcp_client = MultiServerMCPClient({'my_mcp': mcp_server_config})
    tools = await mcp_client.get_tools()
    # 获取所有表名的工具
    list_tables_tool = next(tool for tool in tools if tool.name == 'list_tables_tool')
    # 执行SQL语句的工具
    db_query_tool = next(tool for tool in tools if tool.name == 'db_query_tool')

    async def list_tables(state: SQLState):
        """第一个节点：获取数据库所有表名(自定义工具指令和工具调用)"""
        # 自定义工具调用指令
        tool_call = {
            'name': 'list_tables_tool',
            'args': {'query': ''},
            'id': 'abc123',
            'type': 'tool_call'
        }
        tool_call_message = AIMessage(content='', tool_calls=[tool_call])
        # 工具调用
        tool_message = await list_tables_tool.ainvoke(tool_call)

        response = AIMessage(f'所有可用的表: {tool_message.content}')
        return {'messages': [tool_call_message, tool_message, response]}

    def generate_query(state: SQLState):
        """第四个节点：生成SQL语句"""
        system_message = {
            'role': 'system',
            'content': generate_query_system_prompt
        }

        llm_with_tools = llm.bind_tools([db_query_tool])

        response = llm_with_tools.invoke([system_message] + state['messages'])
        return {'messages': [response]}

    def check_query(state: SQLState):
        """第五个节点：检查SQL语句"""
        system_message = {
            'role': 'system',
            'content': query_check_system
        }
        tool_call = state['messages'][-1].tool_calls[0]
        # 得到生成后的SQL语句
        user_message = {'role': 'user', 'content': tool_call['args']['query']}
        llm_with_tools = llm.bind_tools([db_query_tool])

        response = llm_with_tools.invoke([system_message,user_message])
        response.id = state['messages'][-1].id

        return {'messages': [response]}

    # 第六个节点：执行SQL语句节点
    run_query_node = ToolNode([db_query_tool], name='run_query')

    def should_continue(state: SQLState) -> Literal[END, "check_query"]:
        """条件路由，动态边"""
        messages = state['messages']
        last_message = messages[-1]
        if not last_message.tool_calls:
            return END
        else:
            return 'check_query'


    workflow = StateGraph(SQLState)
    workflow.add_node(list_tables)
    workflow.add_node(call_get_schema)
    workflow.add_node(get_schema_node)
    workflow.add_node(generate_query)
    workflow.add_node(check_query)
    workflow.add_node(run_query_node)

    workflow.add_edge(START, 'list_tables')
    workflow.add_edge('list_tables', 'call_get_schema')
    workflow.add_edge('call_get_schema', 'get_schema')
    workflow.add_edge('get_schema', 'generate_query')
    workflow.add_conditional_edges(
        'generate_query',
        should_continue,
    )
    workflow.add_edge('check_query', 'run_query')
    workflow.add_edge('run_query', 'generate_query')

    graph = workflow.compile()

    yield graph


