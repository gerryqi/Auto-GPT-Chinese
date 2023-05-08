from colorama import Fore

from autogpt.config.ai_config import AIConfig
from autogpt.config.config import Config
from autogpt.llm import ApiManager
from autogpt.logs import logger
from autogpt.prompts.generator import PromptGenerator
from autogpt.setup import prompt_user
from autogpt.utils import clean_input

CFG = Config()

DEFAULT_TRIGGERING_PROMPT = (
    "确定要使用的下一个命令，并使用上面指定的格式进行响应："
)


def build_default_prompt_generator() -> PromptGenerator:
    """
    This function generates a prompt string that includes various constraints,
        commands, resources, and performance evaluations.

    Returns:
        str: The generated prompt string.
    """

    # Initialize the PromptGenerator object
    prompt_generator = PromptGenerator()

    # Add constraints to the PromptGenerator object
    prompt_generator.add_constraint(
        "短期内存限制为4000字左右。你的短期记忆很短，"
        "所以立即将重要信息保存到文件中。"
    )
    prompt_generator.add_constraint(
        "如果你不确定自己以前是怎么做的，或者想回忆过去"
        "事件，思考类似的事件会帮助你记忆。"
    )
    prompt_generator.add_constraint("无用户帮助")
    prompt_generator.add_constraint(
        '仅使用双引号中列出的命令，例如"command name"'
    )

    # Add resources to the PromptGenerator object
    prompt_generator.add_resource(
        "用于搜索和信息收集的互联网接入。"
    )
    prompt_generator.add_resource("长期内存管理。")
    prompt_generator.add_resource(
        "GPT-3.5支持的代理用于简单任务的委派。"
    )
    prompt_generator.add_resource("文件输出。")

    # Add performance evaluations to the PromptGenerator object
    prompt_generator.add_performance_evaluation(
        "不断地回顾和分析你的行动，以确保你发挥出了最大的能力。"
    )
    prompt_generator.add_performance_evaluation(
        "不断地进行建设性的自我批评。"
    )
    prompt_generator.add_performance_evaluation(
        "反思过去的决策和策略，以完善您的方法。"
    )
    prompt_generator.add_performance_evaluation(
        "每一个命令都有代价，所以要聪明高效。目标是用最少的步骤完成任务。"
    )
    prompt_generator.add_performance_evaluation("将所有代码写入一个文件。")
    return prompt_generator


def construct_main_ai_config() -> AIConfig:
    """Construct the prompt for the AI to respond to

    Returns:
        str: The prompt string
    """
    config = AIConfig.load(CFG.ai_settings_file)
    if CFG.skip_reprompt and config.ai_name:
        logger.typewriter_log("名字 :", Fore.GREEN, config.ai_name)
        logger.typewriter_log("角色 :", Fore.GREEN, config.ai_role)
        logger.typewriter_log("目标:", Fore.GREEN, f"{config.ai_goals}")
        logger.typewriter_log(
            "API预算:",
            Fore.GREEN,
            "不限制的" if config.api_budget <= 0 else f"${config.api_budget}",
        )
    elif config.ai_name:
        logger.typewriter_log(
            "欢迎回来!\n",
            Fore.GREEN,
            f"{config.ai_name},你想让我回归现实吗?",
            speak_text=True,
        )
        should_continue = clean_input(
            f"""继续上次设置?
名字:  {config.ai_name}
角色:  {config.ai_role}
目标: {config.ai_goals}
API预算: {"不限制" if config.api_budget <= 0 else f"${config.api_budget}"}
继续 ({CFG.authorise_key}/{CFG.exit_key}): """
        )
        if should_continue.lower() == CFG.exit_key:
            config = AIConfig()

    if not config.ai_name:
        config = prompt_user()
        config.save(CFG.ai_settings_file)

    # set the total api budget
    api_manager = ApiManager()
    api_manager.set_total_budget(config.api_budget)

    # Agent Created, print message
    logger.typewriter_log(
        config.ai_name,
        Fore.LIGHTBLUE_EX,
        "已创建，具有以下详细信息:",
        speak_text=True,
    )

    # Print the ai config details
    # Name
    logger.typewriter_log("名字:", Fore.GREEN, config.ai_name, speak_text=False)
    # Role
    logger.typewriter_log("角色:", Fore.GREEN, config.ai_role, speak_text=False)
    # Goals
    logger.typewriter_log("目标:", Fore.GREEN, "", speak_text=False)
    for goal in config.ai_goals:
        logger.typewriter_log("-", Fore.GREEN, goal, speak_text=False)

    return config
