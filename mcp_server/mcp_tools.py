from langchain_community.utilities import SQLDatabase
from mcp.server import FastMCP

mcp_server = FastMCP(name='my_mcp', instructions='我的mcp服务器', port=8008)
db = SQLDatabase.from_uri('sqlite:///../chinook.db')

@mcp_server.tool(name='list_tables_tool', description='输入一个空字符串，返回数据库中所有以逗号分割的表名列表')
def list_tables_tool(query: str) -> str:
    """输入一个空字符串，返回数据库中所有以逗号分割的表名列表"""
    return ", ".join(db.get_usable_table_names())


@mcp_server.tool(name='db_query_tool', description='执行SQL查询并返回结果，如果查询不正确，将错误信息返回，如果返回错误，请重写查询语句，检查后重试')
def db_query_tool(query: str):
    """执行SQL查询并返回结果，如果查询不正确，将错误信息返回，如果返回错误，请重写查询语句，检查后重试"""
    result = db.run_no_throw(query)
    if not result:
        return "错误：查询失败，请修改查询语句后重试"
    return result