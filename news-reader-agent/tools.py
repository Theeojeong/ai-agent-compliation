from crewai.tools import tool

@tool
def counter_tool(sentence: str):
    """문장이 주어지면 문장의 글자 수를 세어서 출력하는 함수입니다. """
    return len(sentence)