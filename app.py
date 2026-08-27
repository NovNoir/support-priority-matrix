"""Support Priority Matrix — Priority = Scope x Criticality.

Run locally:  pip install -r requirements.txt && python app.py
"""
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

SCOPES = [
    {"id": "network", "label": "Whole network / several schools",
     "why": "Many schools are affected at once, so the impact multiplies and there is no local fallback."},
    {"id": "school", "label": "A whole school",
     "why": "Every user at one site is affected; the school's day-to-day operation is disrupted."},
    {"id": "team", "label": "A team or department",
     "why": "A functional group is blocked, but the rest of the school keeps running."},
    {"id": "user", "label": "A single user",
     "why": "One person is affected. Scope alone does not make this urgent — the system's criticality decides."},
]

TIERS = [
    {"id": "t1", "label": "Tier 1 · Critical",
     "examples": "SIS, email & login, network/Wi-Fi, payroll, attendance & wellbeing records",
     "why": "Teaching, safety or pay stops when this system is down. There is no acceptable workaround."},
    {"id": "t2", "label": "Tier 2 · Important",
     "examples": "LMS, finance & procurement, Laserfiche Forms/Workflow, timetabling, library",
     "why": "Work slows and backlogs build, but a short-term workaround keeps people going."},
    {"id": "t3", "label": "Tier 3 · Supporting",
     "examples": "Room bookings, digital signage, internal dashboards, niche departmental tools",
     "why": "Inconvenient, but people can wait or use another route without real cost."},
]

# rows = scopes (in order above), cols = tiers
GRID = [
    ["P1", "P1", "P2"],
    ["P1", "P2", "P3"],
    ["P1", "P3", "P4"],
    ["P2", "P4", "P4"],
]

PRIORITIES = {
    "P1": {"name": "Critical", "respond": "15 min", "update": "Every hour",
           "work": "Drop everything, all hands, escalate to vendor immediately."},
    "P2": {"name": "High", "respond": "1 hour", "update": "Twice a day",
           "work": "Same-day focus; pause project work if needed."},
    "P3": {"name": "Medium", "respond": "4 hours", "update": "At resolution",
           "work": "Next in queue; fit around planned work."},
    "P4": {"name": "Low", "respond": "1 business day", "update": "At resolution",
           "work": "Batch with similar requests; may be scheduled."},
}

# Cell-specific reasoning: why this combination lands where it does.
REASONS = {
    ("network", "t1"): "The most severe case: a critical system is down everywhere. Rolls, attendance, pay or logins stop across the whole organisation.",
    ("network", "t2"): "An important system is down everywhere. Workarounds exist per site but the backlog compounds across every school, so it is treated as critical.",
    ("network", "t3"): "Wide but shallow. Lots of people notice, nobody is blocked. Breadth alone lifts it to P2, not P1.",
    ("school", "t1"):  "One site cannot operate. A whole school losing SIS, login or network is a P1 regardless of the other 17 being fine.",
    ("school", "t2"):  "A school is slowed but not stopped. Worth same-day attention because the workaround gets painful at school scale.",
    ("school", "t3"):  "Classic 'big group, low stakes'. A whole school sees the problem, but a supporting tool being down costs little. Head count does not make it urgent.",
    ("team", "t1"):    "A department blocked on a critical system — e.g. the office cannot access attendance or pay. Small scope, but the function that stopped is essential.",
    ("team", "t2"):    "A department is inconvenienced on an important system with a workaround. Genuine work, but it can wait a few hours.",
    ("team", "t3"):    "A team missing a convenience tool. Low priority; schedule it.",
    ("user", "t1"):    "One person, but on a system where their task cannot wait — the payroll officer on pay day, the receptionist doing attendance. Outranks a whole school on a Tier 3 tool.",
    ("user", "t2"):    "One person slowed on an important system. A workaround almost always exists; low priority unless a modifier applies.",
    ("user", "t3"):    "One person, supporting tool. The lowest-stakes combination on the board.",
}

MODIFIERS = [
    {"id": "workaround", "label": "A workaround exists", "delta": +1,
     "why": "The person can keep working another way, so it is less urgent than it looks."},
    {"id": "deadline", "label": "Hard deadline (census, reporting, enrolment cut-off)", "delta": -1,
     "why": "A fixed external deadline turns a slow problem into a blocking one."},
    {"id": "security", "label": "Data loss, corruption or security exposure", "delta": "P1",
     "why": "Anything that risks losing or exposing data jumps the queue regardless of scope."},
    {"id": "repeat", "label": "Repeat incident (third time this month)", "delta": -1,
     "why": "Recurring failures indicate a problem record is needed, not another ticket."},
]

ORDER = ["P1", "P2", "P3", "P4"]


def score(scope_id, tier_id, modifier_ids):
    r = next(i for i, s in enumerate(SCOPES) if s["id"] == scope_id)
    c = next(i for i, t in enumerate(TIERS) if t["id"] == tier_id)
    base = GRID[r][c]
    steps = [{"label": "Matrix result", "priority": base,
              "why": REASONS[(scope_id, tier_id)]}]
    idx = ORDER.index(base)
    forced_p1 = False
    for m in MODIFIERS:
        if m["id"] not in modifier_ids:
            continue
        if m["delta"] == "P1":
            forced_p1 = True
            steps.append({"label": m["label"], "priority": "P1", "why": m["why"]})
        else:
            # cap movement at one step in each direction so modifiers can't stack
            idx = max(0, min(3, idx + m["delta"]))
            steps.append({"label": m["label"], "priority": ORDER[idx], "why": m["why"]})
    final = "P1" if forced_p1 else ORDER[idx]
    return {"base": base, "final": final, "steps": steps,
            "scope": next(s for s in SCOPES if s["id"] == scope_id),
            "tier": next(t for t in TIERS if t["id"] == tier_id),
            "targets": PRIORITIES[final]}


@app.route("/")
def index():
    return render_template("index.html", scopes=SCOPES, tiers=TIERS, grid=GRID,
                           priorities=PRIORITIES, modifiers=MODIFIERS)


@app.route("/api/score")
def api_score():
    scope = request.args.get("scope")
    tier = request.args.get("tier")
    mods = [m for m in request.args.get("mods", "").split(",") if m]
    if scope not in {s["id"] for s in SCOPES} or tier not in {t["id"] for t in TIERS}:
        return jsonify({"error": "unknown scope or tier"}), 400
    return jsonify(score(scope, tier, mods))


if __name__ == "__main__":
    app.run(debug=True)
