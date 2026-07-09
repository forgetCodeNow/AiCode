import uuid

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from tools.flights_tools import fetch_user_flight_information
from tools.init_db import update_dates

from graph_chat.assistant import create_assistant_node, safe_tools, sensitive_tools, sensitive_tool_names
from graph_chat.state import State
from langgraph.prebuilt import tools_condition

from tools.tools_handler import create_tool_node_with_fallback, _print_event

# 定义了一个流程图的构建对象
builder = StateGraph(State)

# 自定义函数代表节点，Runnable，或者一个自定义的类都可以是节点
builder.add_node('assistant', create_assistant_node())


def get_user_info(state: State):
    """
    获取用户的航班信息并更新状态字典
    :param state:当前状态字典
    :return:dict:包含用户信息的新字典
    """
    return {'user_info': fetch_user_flight_information.invoke({})}


# 新增：fetch_user_info节点首先运行，这意味着我们的助手可以再不采取任何行动的情况下获取到用户的航班信息
builder.add_node('fetch_user_info', get_user_info)
builder.add_edge(START, 'fetch_user_info')

# 分两个工具节点，safe_tools sensitive_tools
builder.add_node('safe_tools', create_tool_node_with_fallback(safe_tools))
builder.add_node('sensitive_tools', create_tool_node_with_fallback(sensitive_tools))

# 定义边：这些边决定了控制流如何移动
# 从起点START到‘assistant’节点添加一条边
builder.add_edge('fetch_user_info', 'assistant')
# 从assistant节点根据条件判断添加到其他节点的边
# 使用tools_condition来决定哪些条件满足时应跳转到哪些节点
def route_condition_tools(state: State):
    """
    根据当前状态，来决定下一个要执行的节点
    :param state:当前状态
    :return:下一个要执行的节点的名字
    """
    next_node = tools_condition(state)
    if next_node == END:
        return END

    ai_message = state['messages'][-1]
    tool_call = ai_message.tool_calls[0]
    if tool_call['name'] in sensitive_tool_names:
        # 条件成立肯定是敏感工具，需要加入中断用户确认
        return 'sensitive_tools'
    else:
        return 'safe_tools'

builder.add_conditional_edges(
    'assistant',
    route_condition_tools,  # 自定义条件路由函数，判断调用的工具是否是敏感工具，来决定路由到那个工具节点
    path_map=['safe_tools', 'sensitive_tools', END]
)

builder.add_edge('safe_tools', 'assistant')
builder.add_edge('sensitive_tools', 'assistant')

# 检查点让状态图可以持久化其状态
# 这是整个状态图的完整内存
memory = MemorySaver()

# 变异状态图，配置检查点为memory，配置中断点
graph = builder.compile(checkpointer=memory, interrupt_before=['sensitive_tools'])

session_id = uuid.uuid4()
update_dates()  # 每次测试的时候：保证数据库时全新的，保证时间也是最近的时间

config = {
    "configurable": {
        # passenger_id用于我们的航班工具，以获取用户的航班信息
        "passenger_id": '8149 604011',
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
        # 打印消息
        for event in events:
            _print_event(event, _printed)

        current_state = graph.get_state(config)
        if current_state.next:
            user_input = input(
                "是否批准上述操作，输入y继续，否则请说明请求的更改。\n"
            )

            if user_input.strip().lower() == 'y':
                # 继续执行
                events = graph.stream(None, config, stream_mode='values')
                # 打印消息
                for event in events:
                    _print_event(event, _printed)
            else:
                # 通过提供关于请求的更改/改变主意的指示来满足工具调用
                result = graph.stream(
                    {
                        "messages": [
                            ToolMessage(
                                tool_call_id=event["messages"][-1].tool_calls[0]["id"],
                                content=f"Tool的调用被用户拒绝。原因：'{user_input}'。",
                            )
                        ]
                    },
                    config,
                )
                # 打印事件详情
                for event in result:
                    _print_event(event, _printed)
