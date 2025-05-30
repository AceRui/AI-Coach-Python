# 智能体的Redis记忆功能

本项目使用Redis实现了智能体的短期记忆功能，使智能体能够记住与用户的对话历史，提供更加连贯、个性化的体验。

## 功能特点

1. 基于Redis的持久化存储，即使应用重启也能保持对话记忆
2. 自定义TTL（生存时间），可配置记忆保留时长
3. 用户隔离，每个用户拥有独立的记忆空间
4. 与LlamaIndex无缝集成，扩展了原有的ChatMemoryBuffer功能
5. 自动存储用户问题和智能体回复

## 使用方法

### 配置Redis

在`.env`文件中配置Redis连接信息：

```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_MEMORY_TTL=3600  # 记忆保留1小时
```

### 代码中使用

```python
from app.agent.agent_memory import RedisMemoryBuffer

# 为特定用户创建记忆缓冲区
memory = RedisMemoryBuffer(user_id="user123")

# 将记忆添加到智能体上下文
ctx = Context(agent)
await ctx.set("memory", memory)

# 记忆会自动在对话过程中更新
```

## 实现原理

1. `RedisMemory` 类：提供基础的Redis操作，包括存储、获取和清除消息
2. `RedisMemoryBuffer` 类：继承LlamaIndex的`ChatMemoryBuffer`，在内存缓冲的同时同步到Redis
3. 消息格式：`{"role": "user|assistant", "content": "消息内容", "timestamp": 时间戳}`

## 注意事项

1. 需要确保Redis服务正常运行
2. 建议定期监控Redis内存使用情况
3. 可以通过调整`REDIS_MEMORY_TTL`控制记忆保留时长
4. 默认保留最近10条消息，可通过`limit`参数调整 