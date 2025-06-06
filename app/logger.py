import os
import sys
from pathlib import Path
from typing import Optional

import loguru

logger = loguru.logger


def get_logger(log_name: Optional[str] = None):
    """
    初始化日志配置。
    :param log_name: 日志文件名（不带路径和扩展名），默认使用调用文件名
    """
    # 日志目录：项目根目录下 logs/
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # 自动获取调用者脚本名
    if log_name is None:
        import inspect
        caller_frame = inspect.stack()[1]
        caller_path = Path(caller_frame.filename)
        log_name = caller_path.stem  # 不带后缀的脚本名

    log_file_path = log_dir / f"{log_name}.log"

    # 移除默认配置
    logger.remove()

    # 控制台输出
    logger.add(sys.stderr, level="INFO",
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}:{line}</cyan> - <level>{message}</level>")

    # 文件输出
    logger.add(
        log_file_path,
        rotation="10 MB",  # 超过大小自动轮转
        retention="7 days",  # 保留 7 天日志
        encoding="utf-8",
        enqueue=True,  # 多进程安全
        level="INFO"
    )

    return logger
