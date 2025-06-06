from typing import Dict, Any, Tuple, Optional

from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Context
from pydantic import BaseModel, Field

from app.logger import get_logger
from app.tools import post_msg

logger = get_logger("agent_tools")


# 定义 adjust_plan 的参数 schema
class AdjustPlanArgs(BaseModel):
    fitness_goals: Optional[str] = Field(
        "", description="健身目标，可选值: ['lose_weight', 'build_muscle']"
    )
    workout_type: Optional[str] = Field(
        "", description="运动类型，可选值: ['standing_exercises', 'sitting_exercises']"
    )
    workout_duration: Optional[str] = Field(
        "", description="运动时长，可选值: ['5-10', '10-15', '15-20', '20-30']"
    )
    target_position: Optional[str] = Field(
        "", description="运动类型，可选值: ['shoulder', 'back']"
    )
    avoid_position: Optional[str] = Field(
        "", description="运动类型，可选值: ['knee', 'waist']"
    )
    chronic_conditions: Optional[str] = Field(
        "", description="慢性病，可选值: ['asthma', 'hypertension']"
    )
    physical_limitation: Optional[str] = Field(
        "", description="有伤部位，可选值: ['achilles_tendon', 'knee']"
    )
    equipment: Optional[str] = Field(
        "", description="运动器械，可选值: ['dumbbell', 'resistance band']"
    )
    coach: Optional[str] = Field(
        "", description="教练性别，可选值: ['male', 'female', 'both']"
    )


# 定义 update_basic_information 的参数 schema
class UpdateBasicInformationArgs(BaseModel):
    nickname: Optional[str] = Field("", description="用户昵称")
    age: Optional[str] = Field("", description="年龄(岁)")
    height: Optional[str] = Field("", description="身高(cm)")
    weight: Optional[str] = Field("", description="体重(kg)")


async def safe_put_with_retry(
    payload: Dict[str, Any], request_name: str, ctx: Context
) -> Dict[str, Any]:
    try:
        user_email = await ctx.get("user_id")
        result = post_msg(user_email=user_email, msg=payload)
        if result:
            return {"success": True}
        else:
            raise Exception("调用工具失败")
    except Exception as e:
        logger.error(f"修改用户的 {request_name} 失败, Exception: {e}")


async def update_ctx_data(
    ctx: Context, key: str, value: Any, payload: Dict[str, Any], state_key: str
) -> Tuple[Dict[str, Any], Context]:
    state = await ctx.get("state") or {}
    state.setdefault(state_key, {})
    if value:
        state[state_key][key] = value
        payload[key] = value
    await ctx.set("state", state)
    return payload, ctx


async def adjust_plan(
    ctx: Context,
    args: AdjustPlanArgs,
):
    """
    修改用户的健身计划，包括：
        Workout Type：运动类型
        Workout Duration：运动时长
        Training postures：运动姿势
        Target position：目标锻炼部位
        Avoid position：避免锻炼部位
        Equipment：运动器械
        Coach：教练性别
    可以一次修改多项

    Args:
        ctx (Context): 上下文对象，用于存储和访问状态
        args (AdjustPlanArgs): 包含所有可修改参数的数据模型
            - workout_type (str): 用户想要修改的运动类型，可选值: ["standing_exercises", "sitting_exercises"]，默认为: ""
            - target_position (str): 用户想要修改的目标锻炼部位，可选值: ["shoulder", "back", "wrist", "hip", "knee", "ankle"]，默认为: ""
            - avoid_position (str): 用户想要修改的避免锻炼部位，可选值: ["achilles_tendon", "knee"]，默认为: ""
            - workout_duration (str): 用户想要修改的运动时长，提供值为时间区间，单位为`分钟`，可选值: ["5-10", "10-15", "15-20", "20-30"]，默认为: ""
            - preferred_position (str): 用户想要修改的锻炼部位，可选值: ["shoulder", "back", "wrist", "hip", "knee", "ankle"]，默认为: ""
            - equipment (str): 用户想要修改的运动器械，可选值: ["dumbbell", "elastic_bands", "no_instruments"]，默认为: ""
            - coach (str): 用户想要修改的教练性别，可选值: ["male", "female", "both"]，默认为: ""

    Returns:
        str: 操作结果描述，包含成功更新的字段或错误信息

    Raises:
        ValueError: 当提供的参数值不在允许的范围内时
    """
    try:
        args = dict(args)
        logger.info(f"修改用户计划, Args: {args}, Type: {type(args)}")
        logger.info(f"Ctx: {ctx.data}")

        # 从args中提取参数
        workout_type = args.get("workout_type", "")
        target_position = args.get("target_position", "")
        avoid_position = args.get("avoid_position", "")
        workout_duration = args.get("workout_duration", "")
        preferred_position = args.get("preferred_position", "")
        equipment = args.get("equipment", "")
        coach = args.get("coach", "")

        plan_list = [
            {"key": "workout_type", "value": workout_type},
            {"key": "workout_duration", "value": workout_duration},
            {"key": "preferred_position", "value": preferred_position},
            {"key": "equipment", "value": equipment},
            {"key": "coach", "value": coach},
            {"key": "target_position", "value": target_position},
            {"key": "avoid_position", "value": avoid_position},
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
            payload, ctx = await update_ctx_data(
                ctx=ctx,
                key=key,
                value=value,
                payload=payload,
                state_key="workout_plan_params",
            )

        result = await safe_put_with_retry(
            payload=payload, request_name="Plan", ctx=ctx
        )

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
    ctx: Context,
    args: UpdateBasicInformationArgs,
):
    """
    修改用户的基础信息，只包括：
        nickname：用户昵称
        age：年龄
        height：身高
        weight：体重

    Args：
        ctx(Context)：上下文对象
        args(UpdateBasicInformationArgs)：包含所有可修改参数的数据模型
            - nickname(Optional[str])：用户昵称
            - age(Optional[str])：年龄(岁)
            - height(Optional[str])：身高(cm)
            - weight(Optional[str])：体重(kg)

    Returns：
        str: 操作结果描述，包含成功更新的字段或错误信息

    Raises:
        ValueError: 当提供的参数值不在允许的范围内时
    """
    args = dict(args)
    logger.info(f"修改用户信息, Args: {args}, Type: {type(args)}")
    basic_information_list = [
        {"key": "nickname", "value": args.get("nickname", "")},
        {"key": "age", "value": args.get("age", "")},
        {"key": "height", "value": args.get("height", "")},
        {"key": "weight", "value": args.get("weight", "")},
    ]
    logger.info(f"Basic information: {basic_information_list}")
    payload = {}
    for basic_information in basic_information_list:
        key = basic_information.get("key")
        value = basic_information.get("value")
        payload, ctx = await update_ctx_data(
            ctx=ctx,
            key=key,
            value=value,
            payload=payload,
            state_key="basic_info_params",
        )
    logger.info(f"Payload: {payload}")
    result = await safe_put_with_retry(
        payload=payload, request_name="Basic Information", ctx=ctx
    )

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
