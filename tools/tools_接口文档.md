# 工具接口文档

> 项目：ctrip_assistant
> 说明：本文档整理了 tools/ 包中所有工具函数及其接口规范，供开发和集成参考。

---

## 目录

1. [位置转换工具](#1-位置转换工具)
2. [酒店工具](#2-酒店工具)
3. [航班工具](#3-航班工具)
4. [汽车租赁工具](#4-汽车租赁工具)
5. [旅行推荐工具](#5-旅行推荐工具)
6. [向量检索工具](#6-向量检索工具)
7. [工具错误处理器](#7-工具错误处理器)
8. [数据库初始化工具](#8-数据库初始化工具)
9. [附录：公共数据库与依赖](#9-附录公共数据库与依赖)

---

## 1. 位置转换工具

**文件**：`location_trans.py`

### `transform_location(chinese_city)`

将中文城市名转换为英文城市名。如果输入不是中文，则原样返回。

| 项目 | 说明 |
|---|---|
| **功能** | 中文城市名 → 英文城市名映射 |
| **参数** | `chinese_city (str)`：中文城市名 |
| **返回** | `str`：英文城市名；未找到时返回 `"城市名称未找到"` |
| **调用方** | 被 search_hotels、search_car_rentals、search_trip_recommendations 内部调用 |

**支持的城市映射**：

| 中文 | 英文 |
|---|---|
| 北京 | Beijing |
| 上海 | Shanghai |
| 广州 | Guangzhou |
| 深圳 | Shenzhen |
| 成都 | Chengdu |
| 杭州 | Hangzhou |
| 巴塞尔 | Basel |
| 苏黎世 | Zurich |

---
## 2. 酒店工具

**文件**：`hotels_tools.py`

**数据表**：`hotels`

**装饰器**：`@tool`（LangChain 工具装饰器）

### 2.1 `search_hotels(location, name)`

根据位置和名称搜索酒店。

| 项目 | 说明 |
|---|---|
| **功能** | 搜索酒店信息 |
| **参数** | `location (Optional[str])`：酒店位置（支持中文，自动转换） |
| | `name (Optional[str])`：酒店名称 |
| **返回** | `list[dict]`：匹配的酒店信息列表 |

> 注：价格层级、入住/退房日期参数已注释，当前未启用。

### 2.2 `book_hotel(hotel_id)`

通过 ID 预订酒店，将 `booked` 字段置为 `1`。

| 项目 | 说明 |
|---|---|
| **功能** | 预订酒店 |
| **参数** | `hotel_id (int)`：酒店 ID |
| **返回** | `str`：成功/失败消息 |

### 2.3 `update_hotel(hotel_id, checkin_date, checkout_date)`

更新酒店预订的入住和退房日期。

| 项目 | 说明 |
|---|---|
| **功能** | 更新酒店预订日期 |
| **参数** | `hotel_id (int)`：酒店 ID |
| | `checkin_date (Optional[datetime, date])`：新入住日期 |
| | `checkout_date (Optional[datetime, date])`：新退房日期 |
| **返回** | `str`：成功/失败消息 |

### 2.4 `cancel_hotel(hotel_id)`

取消酒店预订，将 `booked` 字段置为 `0`。

| 项目 | 说明 |
|---|---|
| **功能** | 取消酒店预订 |
| **参数** | `hotel_id (int)`：酒店 ID |
| **返回** | `str`：成功/失败消息 |

---

## 3. 航班工具

**文件**：`flights_tools.py`

**涉及数据表**：`tickets`、`ticket_flights`、`flights`、`boarding_passes`

**装饰器**：`@tool`（LangChain 工具装饰器）

### 3.1 `fetch_user_flight_information(config)`

通过乘客 ID 获取该乘客的所有机票信息及关联的航班信息和座位分配情况。

| 项目 | 说明 |
|---|---|
| **功能** | 查询当前用户的全部机票与航班信息 |
| **参数** | `config (RunnableConfig)`：需包含 `configurable.passenger_id` |
| **返回** | `List[Dict]`：机票 + 航班 + 座位信息列表 |
| **异常** | `ValueError`：未配置乘客 ID 时抛出 |

**返回字段**：`ticket_no`、`book_ref`、`flight_id`、`flight_no`、`departure_airport`、`arrival_airport`、`scheduled_departure`、`scheduled_arrival`、`seat_no`、`fare_conditions`

### 3.2 `search_flights(departure_airport, arrival_airport, start_time, end_time, limit)`

根据指定参数搜索航班。

| 项目 | 说明 |
|---|---|
| **功能** | 搜索航班信息 |
| **参数** | `departure_airport (Optional[str])`：出发机场 |
| | `arrival_airport (Optional[str])`：到达机场 |
| | `start_time (Optional[date, datetime])`：出发时间范围起始 |
| | `end_time (Optional[date, datetime])`：出发时间范围结束 |
| | `limit (int)`：返回结果上限，默认 20 |
| **返回** | `List[Dict]`：匹配的航班信息列表 |

### 3.3 `update_ticket_to_new_flight(ticket_no, new_flight_id, config)`

将用户的机票改签到新的有效航班。

**校验流程**：

1. 检查乘客 ID 是否存在
2. 查询新航班详情
3. 验证起飞时间距当前时间不少于 3 小时
4. 确认原机票存在
5. 验证乘客身份（必须是该机票的拥有者）
6. 更新 ticket_flights 表中的 flight_id

| 项目 | 说明 |
|---|---|
| **功能** | 改签机票 |
| **参数** | `ticket_no (str)`：机票编号 |
| | `new_flight_id (int)`：新航班 ID |
| | `config (RunnableConfig)`：需包含 `configurable.passenger_id` |
| **返回** | `str`：操作结果消息 |
| **时区** | `Etc/GMT-3` |

### 3.4 `cancel_ticket(ticket_no, config)`

取消用户的机票并将其从数据库中删除。

**校验流程**：检查乘客ID → 查询机票存在性 → 验证乘客身份 → 删除 ticket_flights 中记录

| 项目 | 说明 |
|---|---|
| **功能** | 取消机票 |
| **参数** | `ticket_no (str)`：机票编号 |
| | `config (RunnableConfig)`：需包含 `configurable.passenger_id` |
| **返回** | `str`：操作结果消息 |

---
## 4. 汽车租赁工具

**文件**：`car_tools.py`

**数据表**：`car_rentals`

**装饰器**：`@tool`（LangChain 工具装饰器）

### 4.1 `search_car_rentals(location, name)`

根据位置和名称搜索汽车租赁信息。

| 项目 | 说明 |
|---|---|
| **功能** | 搜索租车信息 |
| **参数** | `location (Optional[str])`：位置（支持中文，自动转换） |
| | `name (Optional[str])`：租车公司名称 |
| **返回** | `list[dict]`：匹配的租车信息列表 |

### 4.2 `book_car_rental(rental_id)`

通过 ID 预订租车服务。

| 项目 | 说明 |
|---|---|
| **功能** | 预订租车 |
| **参数** | `rental_id (int)`：租车服务 ID |
| **返回** | `str`：成功/失败消息 |

### 4.3 `update_car_rental(rental_id, start_date, end_date)`

更新租车服务的开始和结束日期。

| 项目 | 说明 |
|---|---|
| **功能** | 更新租车日期 |
| **参数** | `rental_id (int)`：租车服务 ID |
| | `start_date (Optional[datetime, date])`：新开始日期 |
| | `end_date (Optional[datetime, date])`：新结束日期 |
| **返回** | `str`：成功/失败消息 |

### 4.4 `cancel_car_rental(rental_id)`

取消租车预订。

| 项目 | 说明 |
|---|---|
| **功能** | 取消租车预订 |
| **参数** | `rental_id (int)`：租车服务 ID |
| **返回** | `str`：成功/失败消息 |

---

## 5. 旅行推荐工具

**文件**：`trip_tools.py`

**数据表**：`trip_recommendations`

**装饰器**：`@tool`（LangChain 工具装饰器）

### 5.1 `search_trip_recommendations(location, name, keywords)`

根据位置、名称和关键词搜索旅行推荐。

| 项目 | 说明 |
|---|---|
| **功能** | 搜索旅行推荐 |
| **参数** | `location (Optional[str])`：位置（支持中文，自动转换） |
| | `name (Optional[str])`：推荐名称 |
| | `keywords (Optional[str])`：关键词，逗号分隔，多个之间用 OR 匹配 |
| **返回** | `List[dict]`：匹配的旅行推荐列表 |

### 5.2 `book_excursion(recommendation_id)`

预订一个旅行推荐项目。

| 项目 | 说明 |
|---|---|
| **功能** | 预订旅行推荐 |
| **参数** | `recommendation_id (int)`：推荐 ID |
| **返回** | `str`：成功/失败消息 |

### 5.3 `update_excursion(recommendation_id, details)`

更新旅行推荐的详细信息。

| 项目 | 说明 |
|---|---|
| **功能** | 更新旅行推荐详情 |
| **参数** | `recommendation_id (int)`：推荐 ID |
| | `details (str)`：新的详细信息文本 |
| **返回** | `str`：成功/失败消息 |

### 5.4 `cancel_excursion(recommendation_id)`

取消旅行推荐。

| 项目 | 说明 |
|---|---|
| **功能** | 取消旅行推荐 |
| **参数** | `recommendation_id (int)`：推荐 ID |
| **返回** | `str`：成功/失败消息 |

---

## 6. 向量检索工具

**文件**：`retriever_vector.py`

**数据源**：`../order_faq.md`（Markdown 格式，按 `##` 标题分割）

### 6.1 `lookup_policy(query)`

通过语义相似度检索公司政策/FAQ 内容。在航班变更、取消等写操作之前建议调用。

| 项目 | 说明 |
|---|---|
| **功能** | 语义检索 FAQ / 公司政策 |
| **参数** | `query (str)`：查询文本 |
| **返回** | `str`：最相关的 2 个 FAQ 片段拼接结果 |
| **向量模型** | ZhipuAIEmbeddings(embedding-3)，密钥从环境变量 GLM_API_KEY 读取 |
| **相似度计算** | 向量点积（np.dot） |

**检索流程**：

1. 读取 ../order_faq.md，按 ## 标题分割为多个文档
2. 使用智谱 embedding-3 模型生成文档向量
3. 查询时对用户输入生成向量，计算向量点积相似度
4. 返回相似度最高的前 2 个文档内容

### 6.2 `VectorStoreRetriever` 类

自定义向量存储检索器。

| 方法 | 说明 |
|---|---|
| `from_docs(docs)` | 类方法，从文档列表生成向量并构建检索器 |
| `query(query, k=5)` | 查询最相似的 k 个文档，返回文档内容及相似度分数 |

---
## 7. 工具错误处理器

**文件**：`tools_handler.py`

### 7.1 `handle_tool_error(state)`

工具执行出错时的回调函数，捕获错误并生成 ToolMessage 反馈。

| 项目 | 说明 |
|---|---|
| **功能** | 工具异常处理 |
| **参数** | `state (dict)`：状态字典，包含 error 和 messages |
| **返回** | `dict`：包含错误消息的 ToolMessage 列表 |

### 7.2 `create_tool_node_with_fallback(tools)`

创建带有回退机制的工具节点，工具抛出异常时自动调用 handle_tool_error。

| 项目 | 说明 |
|---|---|
| **功能** | 构建带容错的工具节点 |
| **参数** | `tools (list)`：LangChain 工具列表 |
| **返回** | `ToolNode`：配置了回退的工具节点 |

### 7.3 `_print_event(event, _printed, max_length)`

调试辅助函数，打印事件信息，支持消息截断。

| 项目 | 说明 |
|---|---|
| **功能** | 调试打印事件信息 |
| **参数** | `event (dict)`：事件字典 |
| | `_printed (set)`：已打印消息 ID 集合 |
| | `max_length (int)`：消息最大长度，默认 1500 |

---

## 8. 数据库初始化工具

**文件**：`init_db.py`

### `update_dates()`

将数据库中的日期字段向前推移，与当前时间对齐。适用于测试环境。

| 项目 | 说明 |
|---|---|
| **功能** | 重置并更新数据库中所有日期字段至当前时间 |
| **返回** | `str`：更新后的数据库文件路径 ../travel_new.sqlite |

**流程**：

1. 用备份文件 travel2.sqlite 覆盖 travel_new.sqlite
2. 读取所有表数据
3. 计算示例时间和当前时间的差值
4. 更新 bookings.book_date 和 flights 中四个时间列
5. 将数据写回数据库

---

## 9. 附录：公共数据库与依赖

### 数据库

所有 SQL 工具共享同一个 SQLite 数据库文件：

```
db = "../travel_new.sqlite"
```

涉及的数据表：

| 表名 | 使用模块 |
|---|---|
| hotels | hotels_tools.py |
| car_rentals | car_tools.py |
| flights | flights_tools.py |
| tickets | flights_tools.py |
| ticket_flights | flights_tools.py |
| boarding_passes | flights_tools.py |
| bookings | init_db.py |
| trip_recommendations | trip_tools.py |

### 运行时依赖

| 依赖 | 用途 |
|---|---|
| langchain_core | @tool 装饰器、RunnableConfig、ToolMessage |
| langgraph | ToolNode |
| numpy | 向量相似度计算 |
| pandas | 数据库日期更新操作 |
| pytz | 时区处理（航班改签时间校验） |
| 智谱 embedding-3 | FAQ 向量检索 |
| Python 内置 sqlite3 | 数据库操作 |

---

*文档生成时间：2026-07-08*
