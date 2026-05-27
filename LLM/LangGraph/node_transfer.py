from __future__ import annotations

from typing import Any
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

class TransferState(TypedDict):
    recipient: str
    amount: int
    memo: str
    approved: bool
    final_status: str

def review_transfer(state: TransferState) -> dict[str, Any]:
    pending_transfer = {
        "recipient": state["recipient"],
        "amount": state["amount"],
        "memo": state["memo"],
    }
    user_review = interrupt({ # “暂停/挂起”，等待外部输入
        "title": "转账审核",
        "pending_transfer": pending_transfer,
        "instruction": "请返回 bool(是否批准) 或 dict(可改 recipient/amount/memo，并带 approved 字段)。",
    })
    approved = False
    updated_transfer = dict(pending_transfer)

    if isinstance(user_review, bool):
        approved = user_review
    elif isinstance(user_review, dict):
        approved = bool(user_review.get("approved", True))
        for k in ("recipient", "amount", "memo"):
            if k in user_review:
                updated_transfer[k] = user_review[k]
    return {
        "approved": approved,
        "recipient": updated_transfer["recipient"],
        "amount": updated_transfer["amount"],
        "memo": updated_transfer["memo"],
    }

def execute_transfer(state: TransferState) -> dict[str, str]:
    if not state["approved"]:
        return {"final_status": "已取消：用户未批准转账"}

    recipient = state["recipient"]
    amount = state["amount"]
    memo = state["memo"]
    return {"final_status": f"已转账：收款人={recipient}，金额={amount}，备注={memo}"}

def build_graph():
    builder = StateGraph(TransferState)

    builder.add_node(review_transfer)
    builder.add_node(execute_transfer)

    builder.add_edge(START, "review_transfer")
    builder.add_edge("review_transfer", "execute_transfer")
    builder.add_edge("execute_transfer", END)

    graph = builder.compile(checkpointer=InMemorySaver())

    initial_state: TransferState = {
        "recipient": "Alice",
        "amount": 100,
        "memo": "午饭AA",
        "approved": False,
        "final_status": "",
    }
    config = {"configurable": {"thread_id": "interrupt-demo-1"}}
    first = graph.invoke(initial_state, config=config)
    interrupt_payload = first["__interrupt__"][0].value

    print("\n[System] 图已暂停，等待用户审核。可给用户展示的数据如下：")
    print(interrupt_payload)

    user_resume_value = {"approved": Ture, "amount": 80, "memo": "改为80元（实际应付）"}
    final = graph.invoke(Command(resume=user_resume_value), config=config)
    print("\n[System] 已恢复执行，最终结果：")
    print(final["final_status"])

if __name__ == "__main__":
    build_graph()





