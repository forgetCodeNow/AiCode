import uuid
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from tools.init_db import update_dates

from graph_chat.assistant import create_assistant_node, part_1_tools
from graph_chat.state import State
from langgraph.prebuilt import tools_condition

from tools.tools_handler import create_tool_node_with_fallback, _print_event

# 定义了一个流程图的构建对象
builder = StateGraph(State)

# 自定义函数代表节点，Runnable，或者一个自定义的类都可以是节点
builder.add_node('assistant', create_assistant_node())


# 添加一个名为‘tools’的节点，该节点创建了一个带有回退机制的工具节点
builder.add_node('tools', create_tool_node_with_fallback(part_1_tools))

# 定义边：这些边决定了控制流如何移动
# 从起点START到‘assistant’节点添加一条边
builder.add_edge(START, 'assistant')
# 从assistant节点根据条件判断添加到其他节点的边
# 使用tools_condition来决定哪些条件满足时应跳转到哪些节点
builder.add_conditional_edges(
    'assistant',
    tools_condition,    # 条件路由函数，返回值是tools对应节点tools名字，可以自定义
)
# 从tools节点回到assistant节点添加一条边
builder.add_edge('tools', 'assistant')

# 检查点让状态图可以持久化其状态
# 这是整个状态图的完整内存
memory = MemorySaver()

# 变异状态图，配置检查点为memory
graph = builder.compile(checkpointer=memory)


session_id = uuid.uuid4()
update_dates()  # 每次测试的时候：保证数据库时全新的，保证时间也是最近的时间

config = {
    "configurable": {
        # passenger_id用于我们的航班工具，以获取用户的航班信息
        "passenger_id": '12345678',
        # 检查点有session_id访问
        "thread_id": session_id,
    }
}


_printed = set()

# 执行工作流
while True:
    question = input('用户：')
    if question.lower() in ['q', 'exit', 'quit']:
        print('exit')
        break
    else:
        events = graph.stream({'messages': ('user', question)}, config, stream_mode='values')
        for event in events:
            _print_event(event, _printed)
