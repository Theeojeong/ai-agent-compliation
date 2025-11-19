import os
from graphviz import Digraph

# Common attributes for Korean support
FONT_NAME = 'Malgun Gothic'
ATTRS = {
    'fontname': FONT_NAME
}

def create_chatgpt_diagram():
    dot = Digraph(comment='ChatGPT Clone Agent Workflow', format='png')
    dot.attr(rankdir='TD', **ATTRS)
    dot.attr('node', **ATTRS)
    dot.attr('edge', **ATTRS)

    dot.node('User', '사용자 (User)', shape='ellipse', style='filled', fillcolor='lightblue')
    dot.node('UI', 'Streamlit UI', shape='box', style='filled', fillcolor='lightgrey')
    dot.node('Runner', 'Agent Runner', shape='box')
    dot.node('Agent', 'ChatGPT Clone Agent', shape='component', style='filled', fillcolor='lightyellow')

    with dot.subgraph(name='cluster_tools') as c:
        c.attr(label='사용 가능한 도구 (Tools)', style='dashed', **ATTRS)
        c.node('Web', '🌐 웹 검색 (Web Search)', shape='box')
        c.node('File', '📂 파일 검색 (File Search)', shape='box')
        c.node('Img', '🎨 이미지 생성 (Image Gen)', shape='box')
        c.node('Code', '💻 코드 인터프리터 (Code Interpreter)', shape='box')
        c.node('MCP', '🔌 MCP 도구 (MCP Tools)', shape='box')

    dot.edge('User', 'UI', label='질문/파일 업로드')
    dot.edge('UI', 'Runner', label='메시지 전달')
    dot.edge('Runner', 'Agent', label='실행')
    dot.edge('Agent', 'Web')
    dot.edge('Agent', 'File')
    dot.edge('Agent', 'Img')
    dot.edge('Agent', 'Code')
    dot.edge('Agent', 'MCP')
    dot.edge('Web', 'Agent', label='결과')
    dot.edge('File', 'Agent')
    dot.edge('Img', 'Agent')
    dot.edge('Code', 'Agent')
    dot.edge('MCP', 'Agent')
    dot.edge('Agent', 'UI', label='최종 응답')
    dot.edge('UI', 'User', label='화면 표시')

    output_path = os.path.join(os.path.dirname(__file__), 'chatgpt_workflow')
    dot.render(output_path, cleanup=True)
    print(f"Generated {output_path}.png")

def create_coding_agent_diagram():
    dot = Digraph(comment='Coding Agent Workflow', format='png')
    dot.attr(rankdir='TD', **ATTRS)
    dot.attr('node', **ATTRS)
    dot.attr('edge', **ATTRS)

    dot.node('User', '사용자 (User)', shape='ellipse', style='filled', fillcolor='lightblue')
    dot.node('Agent', 'Coding Agent', shape='component', style='filled', fillcolor='lightyellow')
    
    with dot.subgraph(name='cluster_tools') as c:
        c.attr(label='도구 (Tools)', style='dashed', **ATTRS)
        c.node('Shell', '🛠️ Shell Tool', shape='box')
        c.node('Web', '🔍 Web Search', shape='box')
        c.node('Patch', '📝 Apply Patch', shape='box')
        c.node('MCP', '📚 Context7 MCP', shape='box')

    dot.node('Project', '대상 프로젝트 (Target Project)', shape='folder', style='filled', fillcolor='lightgrey')

    dot.edge('User', 'Agent', label='작업 요청')
    dot.edge('Agent', 'MCP', label='문서 검색')
    dot.edge('MCP', 'Agent')
    dot.edge('Agent', 'Shell', label='파일 읽기/명령 실행')
    dot.edge('Shell', 'Agent')
    dot.edge('Agent', 'Patch', label='코드 수정')
    dot.edge('Patch', 'Project', label='파일 변경')
    dot.edge('Project', 'Patch')
    dot.edge('Patch', 'Agent', label='결과 확인')
    dot.edge('Agent', 'User', label='완료 보고')

    # Save to coding-agent directory
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../coding-agent'))
    output_path = os.path.join(output_dir, 'coding_agent_workflow')
    dot.render(output_path, cleanup=True)
    print(f"Generated {output_path}.png")

def create_customer_support_diagram():
    dot = Digraph(comment='Customer Support Agent Workflow', format='png')
    dot.attr(rankdir='TD', **ATTRS)
    dot.attr('node', **ATTRS)
    dot.attr('edge', **ATTRS)

    dot.node('User', '사용자 (User)', shape='ellipse', style='filled', fillcolor='lightblue')
    dot.node('Triage', '🤖 Triage Agent (분류)', shape='component', style='filled', fillcolor='orange')

    with dot.subgraph(name='cluster_specialists') as c:
        c.attr(label='전문 에이전트 (Specialists)', style='dashed', **ATTRS)
        c.node('Tech', '🔧 Technical Agent', shape='component', style='filled', fillcolor='lightyellow')
        c.node('Bill', '💳 Billing Agent', shape='component', style='filled', fillcolor='lightyellow')
        c.node('Order', '📦 Order Agent', shape='component', style='filled', fillcolor='lightyellow')
        c.node('Acct', '👤 Account Agent', shape='component', style='filled', fillcolor='lightyellow')

    with dot.subgraph(name='cluster_guardrails') as c:
        c.attr(label='안전 장치 (Guardrails)', style='dotted', **ATTRS)
        c.node('InputGuard', '입력 가드레일', shape='octagon', style='filled', fillcolor='pink')
        c.node('OutputGuard', '출력 가드레일', shape='octagon', style='filled', fillcolor='pink')

    dot.edge('User', 'InputGuard', label='문의')
    dot.edge('InputGuard', 'Triage', label='검증됨')
    
    dot.edge('Triage', 'Tech', label='기술 문제')
    dot.edge('Triage', 'Bill', label='결제/환불')
    dot.edge('Triage', 'Order', label='배송/반품')
    dot.edge('Triage', 'Acct', label='계정 설정')

    dot.edge('Tech', 'OutputGuard', label='응답')
    dot.edge('Bill', 'OutputGuard', label='응답')
    dot.edge('Order', 'OutputGuard', label='응답')
    dot.edge('Acct', 'OutputGuard', label='응답')

    dot.edge('OutputGuard', 'User', label='최종 답변')

    # Save to customer-support-agent directory
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../customer-support-agent'))
    output_path = os.path.join(output_dir, 'customer_support_workflow')
    dot.render(output_path, cleanup=True)
    print(f"Generated {output_path}.png")

def create_my_first_agent_diagram():
    dot = Digraph(comment='My First Agent Workflow', format='png')
    dot.attr(rankdir='LR', **ATTRS)
    dot.attr('node', **ATTRS)
    dot.attr('edge', **ATTRS)

    dot.node('User', '사용자 (User)', shape='ellipse', style='filled', fillcolor='lightblue')
    dot.node('App', 'Python App', shape='box', style='filled', fillcolor='lightgrey')
    dot.node('LLM', 'OpenAI Model', shape='cloud', style='filled', fillcolor='white')
    dot.node('Tool', 'Weather Function', shape='box', style='filled', fillcolor='lightgreen')

    dot.edge('User', 'App', label='입력')
    dot.edge('App', 'LLM', label='메시지 전송')
    dot.edge('LLM', 'App', label='도구 호출 요청')
    dot.edge('App', 'Tool', label='함수 실행')
    dot.edge('Tool', 'App', label='결과 반환')
    dot.edge('App', 'LLM', label='결과 전송')
    dot.edge('LLM', 'App', label='자연어 응답')
    dot.edge('App', 'User', label='출력')

    # Save to my-first-agent directory
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../my-first-agent'))
    output_path = os.path.join(output_dir, 'my_first_agent_workflow')
    dot.render(output_path, cleanup=True)
    print(f"Generated {output_path}.png")

if __name__ == '__main__':
    create_chatgpt_diagram()
    create_coding_agent_diagram()
    create_customer_support_diagram()
    create_my_first_agent_diagram()
