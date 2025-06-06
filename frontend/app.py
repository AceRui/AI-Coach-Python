import streamlit as st
import requests
import json
import time
from typing import Generator
import uuid

# 页面配置
st.set_page_config(
    page_title="AI Coach - 智能健身教练",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    color: #1f77b4;
    margin-bottom: 2rem;
}

.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #1f77b4;
}

.user-message {
    background-color: #e3f2fd;
    border-left-color: #2196f3;
}

.assistant-message {
    background-color: #f3e5f5;
    border-left-color: #9c27b0;
}

.agent-info {
    font-size: 0.8rem;
    color: #666;
    font-style: italic;
    margin-bottom: 0.5rem;
}

.sidebar-info {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}

.status-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 0.5rem;
}

.status-online {
    background-color: #4caf50;
}

.status-offline {
    background-color: #f44336;
}

.chat-input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: white;
    padding: 1rem;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
    z-index: 1000;
}

.chat-container {
    margin-bottom: 120px; /* 为底部输入框留出空间 */
    padding-bottom: 2rem;
}

.language-selector {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
}

.language-option {
    cursor: pointer;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    margin-right: 0.5rem;
    transition: all 0.3s ease;
}

.language-option.active {
    background-color: #1f77b4;
    color: white;
}

.language-option:hover:not(.active) {
    background-color: #e3f2fd;
}

/* 隐藏Streamlit默认元素 */
#MainMenu {visibility: hidden;}
.stDeployButton {display:none;}
footer {visibility: hidden;}

.welcome-card {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 1rem;
    margin-bottom: 2rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.feature-card {
    background-color: rgba(255, 255, 255, 0.1);
    padding: 1rem;
    border-radius: 0.5rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"
if 'api_status' not in st.session_state:
    st.session_state.api_status = "unknown"


# 检查API状态的函数
def check_api_status(api_url: str) -> bool:
    try:
        response = requests.get(f"{api_url}/docs", timeout=5)
        return response.status_code == 200
    except:
        return False


# 侧边栏配置
with st.sidebar:
    st.markdown("### ⚙️ 系统配置")

    # API服务器配置
    api_url = st.text_input(
        "API服务器地址",
        value=st.session_state.api_url,
        help="AI Coach API服务器的地址"
    )

    # 检查API状态
    if st.button("🔍 检查连接状态"):
        with st.spinner("检查中..."):
            is_online = check_api_status(api_url)
            st.session_state.api_status = "online" if is_online else "offline"
            st.session_state.api_url = api_url

    # 显示API状态
    status_class = "status-online" if st.session_state.api_status == "online" else "status-offline"
    status_text = "在线" if st.session_state.api_status == "online" else "离线"
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <span class="status-indicator {status_class}"></span>
        <strong>API状态:</strong> {status_text}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 用户配置
    st.markdown("### 👤 用户设置")

    user_id = st.text_input(
        "用户ID",
        value=st.session_state.user_id,
        help="用于识别用户身份，保持对话连续性"
    )
    st.session_state.user_id = user_id

    # 语言选择
    language = st.selectbox(
        "选择语言",
        options=[
            "zh",  # Chinese (Simplified)
            "zh-TW",  # Chinese (Traditional)
            "en",  # English
            "fr",  # French
            "de",  # German
            "es",  # Spanish
            "pt",  # Portuguese
            "it",  # Italian
            "ru",  # Russian
            "ja",  # Japanese
            "ko",  # Korean
            "ar",  # Arabic
            "hi",  # Hindi
            "th",  # Thai
            "vi",  # Vietnamese
            "tr",  # Turkish
            "nl",  # Dutch
            "pl",  # Polish
            "uk",  # Ukrainian
            "id",  # Indonesian
            "el",  # Greek
            "hu",  # Hungarian
            "cs",  # Czech
            "ro",  # Romanian
            "he",  # Hebrew
            "sv",  # Swedish
            "fi",  # Finnish
            "da",  # Danish
            "no"  # Norwegian
        ],
        format_func=lambda x: "🇨🇳 中文" if x == "zh" else "🇺🇸 English",
        help="选择对话语言"
    )

# 主页面标题
st.markdown('<h1 class="main-header">🏃‍♂️ AI Coach - 智能健身教练</h1>', unsafe_allow_html=True)

# 创建聊天容器
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# 显示对话历史
for i, message in enumerate(st.session_state.messages):
    with st.container():
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 你:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            agent_name = message.get("agent", "AI Coach")
            agent_emoji = {
                "路由智能体": "🎯",
                "健身教练智能体": "💪",
                "健康/康复建议智能体": "💪",
                "订阅支持智能体": "💳",
                "订阅与付费智能体": "💳",
                "技术支持智能体": "🔧",
                "故障排查智能体": "🔧",
                "个人定制智能体": "⚙️",
                "使用指南智能体": "⚙️"
            }.get(agent_name, "🤖")

            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="agent-info">{agent_emoji} {agent_name}</div>
                <strong>AI Coach:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 聊天输入区域 - 移到页面底部
st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    # 输入区域
    user_input = st.text_area(
        "请输入你的问题:",
        placeholder="例如: 我想要一个适合老年人的锻炼计划，每天15分钟左右...",
        height=100,
        help="详细描述你的需求，我会为你提供专业的建议和帮助"
    )

    # 快捷问题按钮
    st.markdown("**💡 快捷问题:**")
    col1, col2, col3, col4 = st.columns(4)

    quick_questions = [
        "制定健身计划",
        "修改个人信息",
        "订阅相关问题",
        "技术支持"
    ]

    for i, (col, question) in enumerate(zip([col1, col2, col3, col4], quick_questions)):
        with col:
            if st.form_submit_button(f"📝 {question}", use_container_width=True):
                user_input = f"我需要关于{question}的帮助"

    # 主发送按钮
    submit_button = st.form_submit_button(
        "🚀 发送消息",
        type="primary",
        use_container_width=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# 处理用户输入
if submit_button and user_input.strip():
    # 检查API状态
    if st.session_state.api_status != "online":
        st.warning("⚠️ API服务器似乎未连接，请检查服务器状态后重试")
        st.stop()

    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 显示用户消息
    with st.container():
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 你:</strong><br>
            {user_input}
        </div>
        """, unsafe_allow_html=True)

    # 显示加载状态
    with st.spinner("🤖 AI Coach团队正在为你分析问题..."):
        try:
            # 准备请求数据
            request_data = {
                "user_id": st.session_state.user_id,
                "query": user_input,
                "user_language": language
            }

            # 发送非流式请求
            response = requests.post(
                f"{st.session_state.api_url}/api/chat",
                json=request_data,
                timeout=120
            )

            if response.status_code == 200:
                # 创建容器显示响应
                response_container = st.empty()
                response_data = response.json()
                full_response = response_data.get("response", "")
                current_agent = response_data.get("agent", "AI Coach")

                # 获取智能体emoji
                agent_emoji = {
                    "路由智能体": "🎯",
                    "健身教练智能体": "💪",
                    "健康/康复建议智能体": "💪",
                    "订阅支持智能体": "💳",
                    "订阅与付费智能体": "💳",
                    "技术支持智能体": "🔧",
                    "故障排查智能体": "🔧",
                    "个人定制智能体": "⚙️",
                    "使用指南智能体": "⚙️"
                }.get(current_agent, "🤖")

                # 显示响应
                response_container.markdown(f"""
                <div class="chat-message assistant-message">
                    <div class="agent-info">{agent_emoji} {current_agent}</div>
                    <strong>AI Coach:</strong><br>
                    {full_response}
                </div>
                """, unsafe_allow_html=True)

                # 添加完整响应到历史
                if full_response:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response,
                        "agent": current_agent
                    })

                    # 显示成功提示
                    st.success("✅ 回复完成！")

            else:
                st.error(f"❌ 请求失败: {response.status_code}")
                if response.text:
                    st.error(f"错误详情: {response.text}")

        except requests.exceptions.Timeout:
            st.error("⏰ 请求超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            st.error("🔌 连接错误，请检查API服务器是否正在运行")
            st.info("💡 确保API服务器地址正确且服务正在运行")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ 网络请求错误: {str(e)}")
        except Exception as e:
            st.error(f"❌ 发生未知错误: {str(e)}")
            st.info("🔧 请联系技术支持获取帮助")

# 页面底部信息
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 2rem 0;">
    <div style="margin-bottom: 1rem;">
        <strong>🏃‍♂️ AI Coach - 基于LlamaIndex的多智能体健身教练系统</strong>
    </div>
    <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
        <span>💡 智能路由</span>
        <span>💪 专业指导</span>
        <span>🔧 全面支持</span>
        <span>⚙️ 个性定制</span>
    </div>
    <div style="margin-top: 1rem;">
        <small>如遇问题，请联系: contactus@laien.io</small>
    </div>
</div>
""", unsafe_allow_html=True)
