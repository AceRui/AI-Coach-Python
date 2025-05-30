from typing import Dict, Any, Tuple, Optional

import requests
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Context
from pydantic import BaseModel, Field

from app.logger import get_logger

logger = get_logger("agent_tools")


# 定义 adjust_plan 的参数 schema
class AdjustPlanArgs(BaseModel):
    fitness_goals: Optional[str] = Field("", description="健身目标，可选值: ['lose_weight', 'build_muscle']")
    workout_type: Optional[str] = Field("", description="运动类型，可选值: ['standing_exercises', 'sitting_exercises']")
    workout_duration: Optional[int] = Field(0, description="运动时长（秒）")
    preferred_position: Optional[str] = Field("", description="锻炼部位，例如: 'shoulder', 'back'")
    chronic_conditions: Optional[str] = Field("", description="慢性病，可选值: ['asthma', 'hypertension']")
    physical_limitation: Optional[str] = Field("", description="有伤部位，可选值: ['achilles_tendon', 'knee']")
    equipment: Optional[str] = Field("", description="运动器械，可选值: ['dumbbell', 'resistance band']")
    coach: Optional[str] = Field("", description="教练性别，可选值: ['male', 'female']")


# 定义 update_basic_information 的参数 schema
class UpdateBasicInformationArgs(BaseModel):
    nickname: Optional[str] = Field("", description="用户昵称")
    age: Optional[int] = Field(0, description="年龄(岁)")
    height: Optional[float] = Field(0, description="身高(cm)")
    weight: Optional[float] = Field(0, description="体重(kg)")


def safe_put_with_retry(url: str, payload: Dict[str, Any], request_name: str, retry_num: int = 3) -> Dict[str, Any]:
    attempts = 0
    while attempts < retry_num:
        try:
            r = requests.put(url=url, json=payload)
            r.raise_for_status()
            return {"status": r.json()}
        except Exception as e:
            attempts += 1
            logger.warning(f"修改用户的 {request_name} 失败, 开始第{attempts}次重试, Exception: {e}")

    logger.error(f"{retry_num}次修改用户的 {request_name} 均失败")
    return {"status": False}


async def update_ctx_data(ctx: Context, key: str, value: Any, payload: Dict[str, Any], state_key: str) \
        -> Tuple[Dict[str, Any], Context]:
    state = await ctx.get("state") or {}
    state.setdefault(state_key, {})
    if value:
        state[state_key][key] = value
        payload[key] = value
    await ctx.set("state", state)
    return payload, ctx


# async def adjust_plan(
#         ctx: Context, fitness_goals: Optional[str] = "", workout_type: Optional[str] = "",
#         workout_duration: Optional[int] = 0, preferred_position: Optional[str] = "",
#         chronic_conditions: Optional[str] = "", physical_limitation: Optional[str] = "",
#         equipment: Optional[str] = "", coach: Optional[str] = ""
# ):
#     """
#     修改用户的Plan，只包括：
#         Fitness Goals：健身目标
#         Workout Type：运动类型
#         Workout Duration：运动时长
#         Preferred Position：锻炼部位
#         Chronic Conditions：慢性病
#         Physical Limitation：有伤部位
#         Equipment：运动器械
#         Coach：教练性别
#     可以一次修改多项
#
#     Args:
#         ctx (Context): 上下文对象，用于存储和访问状态
#         fitness_goals (Optional[str]): 用户想要修改的健身目标，可选值: ["lose_weight", "build_muscle"]
#         workout_type (Optional[str]): 用户想要修改的运动类型，可选值: ["standing_exercises", "sitting_exercises"]
#         workout_duration (Optional[int]): 用户想要修改的运动时长（秒）
#         preferred_position (Optional[str]): 用户想要修改的锻炼部位，例如: "shoulder", "back"
#         chronic_conditions (Optional[str]): 用户想要修改的慢性病，可选值: ["asthma", "hypertension"]
#         physical_limitation (Optional[str]): 用户想要修改的有伤部位，可选值: ["achilles_tendon", "knee"]
#         equipment (Optional[str]): 用户想要修改的运动器械，可选值: ["dumbbell", "resistance band"]
#         coach (Optional[str]): 用户想要修改的教练性别，可选值: ["male", "female"]
#
#     Returns:
#         str: 操作结果描述，包含成功更新的字段或错误信息
#
#     Raises:
#         ValueError: 当提供的参数值不在允许的范围内时
#
#     """
#     url = "https://eoo14fnitgkpcxu.m.pipedream.net"
#     plan_list = [
#         {"key": "fitness_goals", "value": fitness_goals},
#         {"key": "workout_type", "value": workout_type},
#         {"key": "workout_duration", "value": workout_duration},
#         {"key": "preferred_position", "value": preferred_position},
#         {"key": "equipment", "value": equipment},
#         {"key": "coach", "value": coach},
#         {"key": "chronic_conditions", "value": chronic_conditions},
#         {"key": "physical_limitation", "value": physical_limitation}
#     ]
#     logger.debug(f"调用 adjust plan tool，\n{plan_list}")
#     payload = {}
#     for plan in plan_list:
#         key = plan.get("key")
#         value = plan.get("value")
#         ctx, payload = await update_ctx_data(ctx=ctx, key=key, value=value, payload=payload)
#
#     result = safe_put_with_retry(url=url, payload=payload, request_name="Plan")
#     return f"Plan已更新, Result: {result}"

async def adjust_plan(
        ctx: Context, workout_type: str, training_position: str, workout_duration: str, preferred_position: str,
        equipment: str, coach: str
):
    """
    修改用户的健身计划，包括：
        Workout Type：运动类型
        Workout Duration：运动时长
        Training postures：运动姿势
        Preferred Position：锻炼部位
        Equipment：运动器械
        Coach：教练性别
    可以一次修改多项

    Args:
        ctx (Context): 上下文对象，用于存储和访问状态
        workout_type (str): 用户想要修改的运动类型，可选值: ["standing_exercises", "sitting_exercises"]，默认为: ""
        training_position (str): 用户想要修改的运动姿势，可选值：["standing", "sitting", "both"]，默认为: ""
        workout_duration (str): 用户想要修改的运动时长，提供值为时间区间，单位为`分钟`，可选值: ["5-10", "10-15", "15-20", "20-30"]，默认为: ""
        preferred_position (str): 用户想要修改的锻炼部位，可选值: ["shoulder", "back", "wrist", "hip", "knee", "ankle"]，默认为: ""
        equipment (str): 用户想要修改的运动器械，可选值: ["dumbbell", "elastic_bands", "no_instruments"]，默认为: ""
        coach (str): 用户想要修改的教练性别，可选值: ["male", "female", "both"]，默认为: ""

    Returns:
        str: 操作结果描述，包含成功更新的字段或错误信息

    Raises:
        ValueError: 当提供的参数值不在允许的范围内时

    """
    try:
        print(f"调用adjust_plan函数，参数：workout_duration={workout_duration}, workout_type={workout_type}")
        url = "https://eoo14fnitgkpcxu.m.pipedream.net"

        # 确保所有参数都初始化为至少是空字符串
        workout_type = workout_type or ""
        training_position = training_position or ""
        workout_duration = workout_duration or ""
        preferred_position = preferred_position or ""
        equipment = equipment or ""
        coach = coach or ""

        plan_list = [
            {"key": "workout_type", "value": workout_type},
            {"key": "workout_duration", "value": workout_duration},
            {"key": "preferred_position", "value": preferred_position},
            {"key": "equipment", "value": equipment},
            {"key": "coach", "value": coach},
            {"key": "training_position", "value": training_position}
        ]
        logger.info(f"调用 adjust plan tool，参数：{plan_list}")

        # 创建有效的参数负载
        payload = {}
        modified_params = []

        for plan in plan_list:
            key = plan.get("key")
            value = plan.get("value")

            # 只有当值非空时才认为是要修改的参数
            if value:
                modified_params.append(key)

            # 无论如何都添加到payload和state中
            ctx, payload = await update_ctx_data(ctx=ctx, key=key, value=value, payload=payload)

        result = safe_put_with_retry(url=url, payload=payload, request_name="Plan")

        # 判断哪些参数被修改了
        if modified_params:
            return f"成功修改了以下参数: {', '.join(modified_params)}。Result: {result}"
        else:
            return "没有参数被修改，因为没有提供有效的参数值。"

    except Exception as e:
        error_msg = f"修改计划时发生错误: {str(e)}"
        logger.error(error_msg)
        return error_msg


async def update_basic_information(
        ctx: Context, nickname: Optional[str] = "", age: Optional[int] = 0,
        height: Optional[float] = 0, weight: Optional[float] = 0
):
    """
    修改用户的基础信息，只包括：
        nickname：用户昵称
        age：年龄
        height：身高
        weight：体重

    Args：
        ctx(Context)：上下文对象
        nickname(Optional[str])：用户昵称
        age(Optional[int])：年龄(岁)
        height(Optional[float])：身高(cm)
        weight(Optional[float])：体重(kg)

    Returns：
        str: 操作结果描述，包含成功更新的字段或错误信息

    Raises:
        ValueError: 当提供的参数值不在允许的范围内时

    """
    logger.info("修改用户信息")
    url = "https://eoo14fnitgkpcxu.m.pipedream.net"
    basic_information_list = [
        {"key": "nickname", "value": nickname},
        {"key": "age", "value": age},
        {"key": "height", "value": height},
        {"key": "weight", "value": weight}
    ]
    logger.info(f"Basic information: {basic_information_list}")
    payload = {}
    for basic_information in basic_information_list:
        key = basic_information.get("key")
        value = basic_information.get("value")
        payload, ctx = await update_ctx_data(ctx=ctx, key=key, value=value, payload=payload,
                                             state_key="basic_info_params")
        logger.info(f"Payload: {payload}")

    result = safe_put_with_retry(url=url, payload=payload, request_name="Basic Information")
    return f"Basic Information已更新, Result: {result}"


adjust_plan_tool = FunctionTool.from_defaults(
    fn=adjust_plan,
    name="adjust_workout_plan_tool",
    description="修改用户的健身计划",
)

update_basic_information_tool = FunctionTool.from_defaults(
    fn=update_basic_information,
    name="update_basic_information_tool",
    description="修改用户的基础信息，包括昵称、年龄、身高、体重。",
)
