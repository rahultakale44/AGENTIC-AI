from typing import TypedDict, Any
from langgraph.graph import StateGraph, END


class EventState(TypedDict, total=False):
    task: str
    budget_limit: int
    students: int
    iteration: int
    plan: dict[str, Any]
    budget_total: int
    budget_ok: bool
    budget_feedback: str
    review_feedback: str
    approved: bool
    final_report: str
    log: list[str]


def add_log(state: EventState, message: str) -> list[str]:
    return state.get("log", []) + [message]


# AGENT 1: Event Planner
def event_planner(state: EventState) -> dict:
    round_no = state.get("iteration", 0)

    if round_no == 0:
        # Deliberately ambitious first proposal to give the agents
        # something meaningful to negotiate.
        plan = {
            "speaker": 4500,
            "refreshments": 4000,
            "materials": 1500,
            "printing_certificates": 700,
            "venue": 0,
            "schedule": [
                "09:30 - Opening",
                "10:00 - Technical session",
                "12:00 - Hands-on activity",
                "14:00 - Project discussion",
                "16:00 - Closing"
            ],
            "backup_plan": "Not specified"
        }
        note = "Round 1: proposed a premium speaker and full refreshments."
    else:
        # Revised after the budget and feasibility agents' feedback.
        plan = {
            "speaker": 3000,
            "refreshments": 3200,
            "materials": 1000,
            "printing_certificates": 500,
            "venue": 0,
            "av_backup": 500,
            "contingency": 800,
            "schedule": [
                "09:30 - Registration and opening",
                "10:00 - Technical session",
                "11:15 - Tea break",
                "11:30 - Hands-on activity",
                "13:00 - Lunch",
                "14:00 - Team project discussion",
                "15:30 - Q&A and feedback",
                "16:00 - Closing"
            ],
            "backup_plan": "Keep a spare HDMI cable and presentation copy on a USB drive."
        }
        note = (
            "Round 2: reduced speaker and refreshment costs, added AV backup, "
            "contingency and a break in the schedule."
        )

    return {
        "iteration": round_no + 1,
        "plan": plan,
        "log": add_log(state, f"[Event Planner] {note}")
    }


# AGENT 2: Budget Controller
def budget_controller(state: EventState) -> dict:
    plan = state["plan"]
    cost_keys = [
        "speaker", "refreshments", "materials", "printing_certificates",
        "venue", "av_backup", "contingency"
    ]
    total = sum(plan.get(key, 0) for key in cost_keys)
    limit = state["budget_limit"]
    ok = total <= limit

    if ok:
        feedback = f"Budget approved: Rs. {total:,} is within Rs. {limit:,}."
    else:
        feedback = (
            f"Budget rejected: Rs. {total:,} exceeds the Rs. {limit:,} limit "
            f"by Rs. {total - limit:,}. Reduce costs before approval."
        )

    return {
        "budget_total": total,
        "budget_ok": ok,
        "budget_feedback": feedback,
        "log": add_log(state, f"[Budget Controller] {feedback}")
    }


# AGENT 3: Feasibility Reviewer
def feasibility_reviewer(state: EventState) -> dict:
    plan = state["plan"]
    issues = []

    schedule_text = " ".join(plan.get("schedule", [])).lower()
    if "break" not in schedule_text and "tea" not in schedule_text:
        issues.append("Add a short break to the schedule.")
    if not plan.get("backup_plan") or plan.get("backup_plan") == "Not specified":
        issues.append("Add a basic AV/presentation backup plan.")

    if issues:
        review = "Needs revision: " + " ".join(issues)
    else:
        review = "Feasibility approved: break and AV backup are included."

    approved = state["budget_ok"] and not issues
    return {
        "review_feedback": review,
        "approved": approved,
        "log": add_log(state, f"[Feasibility Reviewer] {review}")
    }


def supervisor_route(state: EventState) -> str:
    if state.get("approved"):
        return "finalize"
    if state.get("iteration", 0) >= 2:
        return "finalize"
    return "revise"


def finalize(state: EventState) -> dict:
    plan = state["plan"]
    total = state["budget_total"]
    report = [
        "FINAL WORKSHOP PLAN",
        f"Participants: {state['students']}",
        f"Budget limit: Rs. {state['budget_limit']:,}",
        f"Estimated cost: Rs. {total:,}",
        f"Remaining budget: Rs. {state['budget_limit'] - total:,}",
        "",
        "COST BREAKDOWN"
    ]

    for key, value in plan.items():
        if isinstance(value, int):
            report.append(f"- {key.replace('_', ' ').title()}: Rs. {value:,}")

    report += ["", "SCHEDULE"] + [f"- {item}" for item in plan["schedule"]]
    report += [
        "",
        f"AV backup: {plan.get('backup_plan', 'Not specified')}",
        f"Supervisor decision: {'APPROVED' if state.get('approved') else 'NOT APPROVED'}"
    ]

    return {
        "final_report": "\n".join(report),
        "log": add_log(state, "[Supervisor] Final report generated.")
    }


def build_graph():
    graph = StateGraph(EventState)
    graph.add_node("event_planner", event_planner)
    graph.add_node("budget_controller", budget_controller)
    graph.add_node("feasibility_reviewer", feasibility_reviewer)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("event_planner")
    graph.add_edge("event_planner", "budget_controller")
    graph.add_edge("budget_controller", "feasibility_reviewer")
    graph.add_conditional_edges(
        "feasibility_reviewer",
        supervisor_route,
        {"revise": "event_planner", "finalize": "finalize"}
    )
    graph.add_edge("finalize", END)
    return graph.compile()


if __name__ == "__main__":
    initial_state: EventState = {
        "task": "Plan a one-day technical workshop for 40 students.",
        "budget_limit": 10000,
        "students": 40,
        "iteration": 0,
        "log": []
    }

    app = build_graph()
    result = app.invoke(initial_state)

    print("AGENT COLLABORATION LOG")
    print("=" * 60)
    for entry in result["log"]:
        print(entry)

    print("\n" + result["final_report"])
