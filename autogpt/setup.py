"""Set up the AI and its goals"""
import re

from colorama import Fore, Style

from autogpt import utils
from autogpt.config import Config
from autogpt.config.ai_config import AIConfig
from autogpt.llm import create_chat_completion
from autogpt.logs import logger

CFG = Config()


def prompt_user() -> AIConfig:
    """Prompt the user for input

    Returns:
        AIConfig: The AIConfig object tailored to the user's input
    """
    ai_name = ""
    ai_config = None

    # Construct the prompt
    logger.typewriter_log(
        "欢迎来到Auto-GPT! ",
        Fore.GREEN,
        "有关详细信息，请使用“--help”运行。",
        speak_text=True,
    )

    # Get user desire
    logger.typewriter_log(
        "创建一个AI助手:",
        Fore.GREEN,
        "输入 '--manual' 以进入手动模式。",
        speak_text=True,
    )

    user_desire = utils.clean_input(
        f"{Fore.LIGHTBLUE_EX}你想让Auto-GPT做什么{Style.RESET_ALL}: "
    )

    if user_desire == "":
        user_desire = "写一篇关于该项目的维基百科风格的文章：https://github.com/significant-gravitas/Auto-GPT"  # Default prompt

    # If user desire contains "--manual"
    if "--manual" in user_desire:
        logger.typewriter_log(
            "已选择手动模式",
            Fore.GREEN,
            speak_text=True,
        )
        return generate_aiconfig_manual()

    else:
        try:
            return generate_aiconfig_automatic(user_desire)
        except Exception as e:
            logger.typewriter_log(
                "无法根据用户需求自动生成AI配置.",
                Fore.RED,
                "回退到手动模式.",
                speak_text=True,
            )

            return generate_aiconfig_manual()


def generate_aiconfig_manual() -> AIConfig:
    """
    Interactively create an AI configuration by prompting the user to provide the name, role, and goals of the AI.

    This function guides the user through a series of prompts to collect the necessary information to create
    an AIConfig object. The user will be asked to provide a name and role for the AI, as well as up to five
    goals. If the user does not provide a value for any of the fields, default values will be used.

    Returns:
        AIConfig: An AIConfig object containing the user-defined or default AI name, role, and goals.
    """

    # Manual Setup Intro
    logger.typewriter_log(
        "创建一个AI助手:",
        Fore.GREEN,
        "在下面输入您的人工智能的名称及其角色。输入任何内容都不会加载默认值",
        speak_text=True,
    )

    # Get AI Name from User
    logger.typewriter_log(
        "AI的名字: ", Fore.GREEN, "例如, '财务助手'"
    )
    ai_name = utils.clean_input("AI名字: ")
    if ai_name == "":
        ai_name = "企业家GPT"

    logger.typewriter_log(
        f"{ai_name} 在这里!", Fore.LIGHTBLUE_EX, "我正在为你服务", speak_text=True
    )

    # Get AI Role from User
    logger.typewriter_log(
        "描述一下你的AI的角色: ",
        Fore.GREEN,
        "例如，'一种旨在自主开发和运营企业的人工智能，其唯一目标是增加你的净资产。'",
    )
    ai_role = utils.clean_input(f"{ai_name} is: ")
    if ai_role == "":
        ai_role = "一种旨在自主开发和经营企业的人工智能，其唯一目标是增加您的净资产。"

    # Enter up to 5 goals for the AI
    logger.typewriter_log(
        "为您的人工智能输入最多5个目标: ",
        Fore.GREEN,
        "例如: \n自动增加收入净值, 注册推特账户，自动管理、开发多个业务线",
    )
    logger.info("不输入任何内容以加载默认值，完成时不输入任何信息。")
    ai_goals = []
    for i in range(5):
        ai_goal = utils.clean_input(f"{Fore.LIGHTBLUE_EX}Goal{Style.RESET_ALL} {i+1}: ")
        if ai_goal == "":
            break
        ai_goals.append(ai_goal)
    if not ai_goals:
        ai_goals = [
            "增加净值",
            "注册推特账户",
            "自动管理、开发多个业务线",
        ]

    # Get API Budget from User
    logger.typewriter_log(
        "增加Twitter帐户输入API调用预算: ",
        Fore.GREEN,
        "例如: $1.50",
    )
    logger.info("不输入任何内容，让AI在没有货币限制的情况下运行")
    api_budget_input = utils.clean_input(
        f"{Fore.LIGHTBLUE_EX}预算{Style.RESET_ALL}: $"
    )
    if api_budget_input == "":
        api_budget = 0.0
    else:
        try:
            api_budget = float(api_budget_input.replace("$", ""))
        except ValueError:
            logger.typewriter_log(
                "无效的预算输入。将预算设置为无限制.", Fore.RED
            )
            api_budget = 0.0

    return AIConfig(ai_name, ai_role, ai_goals, api_budget)


def generate_aiconfig_automatic(user_prompt) -> AIConfig:
    """Generates an AIConfig object from the given string.

    Returns:
    AIConfig: The AIConfig object tailored to the user's input
    """

    system_prompt = """
您的任务是为自治代理设计多达5个高效目标和一个适当的基于角色的名称（_GPT），以确保目标与成功完成分配的任务保持最佳一致。
用户将提供任务，您将只提供以下指定格式的输出，没有解释或对话。
示例输入：
帮助我营销我的业务
输出示例：
名称：CMOGPT
描述：一个专业的数字营销人工智能，通过为SaaS、内容产品、代理等解决营销问题提供世界级的专业知识，帮助Solopreneurs发展业务。
目标：
-作为您的虚拟首席营销官，参与有效的解决问题、确定优先级、规划和支持执行，以满足您的营销需求。
-提供具体、可行和简洁的建议，帮助您在不使用陈词滥调或过于冗长的解释的情况下做出明智的决定。
-确定并优先考虑快速获胜和具有成本效益的活动，以最少的时间和预算投资最大限度地实现结果。
-当面临不明确的信息或不确定性时，积极主动地为您提供指导和建议，以确保您的营销策略保持在正轨上。
"""

    # Call LLM with the string as user input
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": f"任务: '{user_prompt}'\n仅使用系统提示中指定的确切格式的输出进行响应，没有任何解释或对话.\n",
        },
    ]
    output = create_chat_completion(messages, CFG.fast_llm_model)

    # Debug LLM Output
    logger.debug(f"AI配置生成器原始输出: {output}")

    # Parse the output
    ai_name = re.search(r"Name(?:\s*):(?:\s*)(.*)", output, re.IGNORECASE).group(1)
    ai_role = (
        re.search(
            r"Description(?:\s*):(?:\s*)(.*?)(?:(?:\n)|Goals)",
            output,
            re.IGNORECASE | re.DOTALL,
        )
        .group(1)
        .strip()
    )
    ai_goals = re.findall(r"(?<=\n)-\s*(.*)", output)
    api_budget = 0.0  # TODO: parse api budget using a regular expression

    return AIConfig(ai_name, ai_role, ai_goals, api_budget)
