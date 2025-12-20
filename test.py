"""
Step 1: LangGraph 기본 - State와 Node 이해하기
목표: 카운터가 3이 될 때까지 반복하는 그래프
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict

# 1. State 정의 - 그래프 전체에서 공유되는 데이터
class CounterState(TypedDict):
    count: int
    messages: list[str]


# 2. Node 함수들 - 각 단계에서 실행되는 작업
def add_one(state):
    """ 카운트 1 증가 """
    new_count = state["count"] + 1
    new_messages = f"Count increased to {state['count']} → {new_count}"

    print(new_messages)

    return {
        "count": new_count,
        "messages": state["messages"] + [new_messages],
    }

def finish(state):
    """ 완료 메시지 출력 """
    final_message = f"Finished! Final count is {state['count']}"
    print(final_message)

    return {
        "messages": state["messages"] + [final_message],
    }

# 3. 조건부 노드 함수 - 다음에 어디로 갈지 결정 (표지판 역할)
def should_count(state):
    """ 카운트가 3 미만이면 계속, 아니면 종료 """
    if state["count"] < 3:
        return "add_one"
    else:
        return "finish"


# 4. 그래프 만들기
workflow = StateGraph(CounterState)

# 노드 추가
workflow.add_node("counter", add_one)
workflow.add_node("finish", finish)

# 시작점 설정 - counter 노드에서 시작
workflow.set_entry_point("counter")

# 조건부 엣지 - 핵심! 여기서 분기가 일어남 (카운트에 따라 다르게 이동)
workflow.add_conditional_edges(
    "counter",
    should_count,
    {
        "add_one": "counter",  # 계속 카운트 증가
        "finish": "finish",    # 완료로 이동
    },
)

# 마지막 엣지
workflow.add_edge("finish", END)

# 5. 컴파일
app = workflow.compile()

# 6. 실행
print("Starting LangGraph Counter Example...")
result = app.invoke({"count": 0, "messages": []})

print("Final State:", result)
input("\n실행 완료! 엔터를 누르면 종료됩니다...")