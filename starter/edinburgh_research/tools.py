"""Ex5 tools. Four tools the agent uses to research an Edinburgh booking.

Each tool:
  1. Reads its fixture from sample_data/ (DO NOT modify the fixtures).
  2. Logs its arguments and output into _TOOL_CALL_LOG (see integrity.py).
  3. Returns a ToolResult with success=True/False, output=dict, summary=str.

The grader checks for:
  * Correct parallel_safe flags (reads True, generate_flyer False).
  * Every tool's results appear in _TOOL_CALL_LOG.
  * Tools fail gracefully on missing fixtures or bad inputs (ToolError,
    not RuntimeError).
"""

from __future__ import annotations

import json
from pathlib import Path

from sovereign_agent.session.directory import Session
from sovereign_agent.tools.registry import ToolError, ToolRegistry, ToolResult, _RegisteredTool

from starter.edinburgh_research.integrity import _TOOL_CALL_LOG, record_tool_call

_SAMPLE_DATA = Path(__file__).parent / "sample_data"


# ---------------------------------------------------------------------------
# TODO 1 — venue_search
# ---------------------------------------------------------------------------
def venue_search(near: str, party_size: int, budget_max_gbp: int = 1000) -> ToolResult:
    """Search for Edinburgh venues near <near> that can seat the party.

    Reads sample_data/venues.json. Filters by:
      * open_now == True
      * area contains <near> (case-insensitive substring match)
      * seats_available_evening >= party_size
      * hire_fee_gbp + min_spend_gbp <= budget_max_gbp

    Returns a ToolResult with:
      output: {"near": ..., "party_size": ..., "results": [<venue dicts>], "count": int}
      summary: "venue_search(<near>, party=<N>): <count> result(s)"

    MUST call record_tool_call(...) before returning so the integrity
    check can see what data was produced.
    """
    # TODO 1a: load venues.json. Raise ToolError(SA_TOOL_DEPENDENCY_MISSING)
    #          if the file is absent.
    search_count = sum(1 for r in _TOOL_CALL_LOG if r.tool_name == "venue_search")
    if search_count >= 5:  # 3:
        return ToolResult(
            success=False,
            output={"error": "too_many_searches", "count": search_count},
            summary="STOP calling venue_search; use the results you already have.",
        )

    data_path = _SAMPLE_DATA / "venues.json"
    if not data_path.exists():
        raise ToolError("SA_TOOL_DEPENDENCY_MISSING")

    with open(data_path) as f:
        data = json.load(f)

    available_venues = [
        venue
        for venue in data
        if venue["open_now"]
        and near.lower() in venue["area"].lower()
        and venue["seats_available_evening"] >= party_size
        and venue["hire_fee_gbp"] + venue["min_spend_gbp"] <= budget_max_gbp
    ]

    if available_venues:
        output = {
            "near": near,
            "party_size": party_size,
            "results": available_venues,
            "count": len(available_venues),
        }
    else:
        output = {"near": near, "party_size": party_size, "results": [], "count": 0}

    summary = f"venue_search({near}, party={party_size}): {len(available_venues)} result(s)"
    record_tool_call("venue_search", {"near": near, "party_size": party_size}, output)
    return ToolResult(success=output["results"] != [], output=output, summary=summary)


# ---------------------------------------------------------------------------
# TODO 2 — get_weather
# ---------------------------------------------------------------------------
def get_weather(city: str, date: str) -> ToolResult:
    """Look up the scripted weather for <city> on <date> (YYYY-MM-DD).

    Reads sample_data/weather.json. Returns:
      output: {"city": str, "date": str, "condition": str, "temperature_c": int, ...}
      summary: "get_weather(<city>, <date>): <condition>, <temp>C"

    If the city or date is not in the fixture, return success=False with
    a clear ToolError (SA_TOOL_INVALID_INPUT). Do NOT raise.

    MUST call record_tool_call(...) before returning.
    """

    data_path = _SAMPLE_DATA / "weather.json"
    with open(data_path) as f:
        data = json.load(f)
    weather = data[city][date]
    summary = f"get_weather({city}, {date}): {weather['condition']}, {weather['temperature_c']}°C"
    record_tool_call("get_weather", {"city": city, "date": date}, weather)
    return ToolResult(success=True, output=weather, summary=summary)


# ---------------------------------------------------------------------------
# TODO 3 — calculate_cost
# ---------------------------------------------------------------------------
def calculate_cost(
    venue_id: str,
    party_size: int,
    duration_hours: int,
    catering_tier: str = "bar_snacks",
) -> ToolResult:
    """Compute the total cost for a booking.

    Formula:
      base_per_head = base_rates_gbp_per_head[catering_tier]
      venue_mult    = venue_modifiers[venue_id]
      subtotal      = base_per_head * venue_mult * party_size * max(1, duration_hours)
      service       = subtotal * service_charge_percent / 100
      total         = subtotal + service + <venue's hire_fee_gbp + min_spend_gbp>
      deposit_rule  = per deposit_policy thresholds

    Returns:
      output: {
        "venue_id": str,
        "party_size": int,
        "duration_hours": int,
        "catering_tier": str,
        "subtotal_gbp": int,
        "service_gbp": int,
        "total_gbp": int,
        "deposit_required_gbp": int,
      }
      summary: "calculate_cost(<venue>, <party>): total £<N>, deposit £<M>"

    MUST call record_tool_call(...) before returning.
    """

    data_path = _SAMPLE_DATA / "catering.json"
    with open(data_path) as f:
        catering = json.load(f)
    subtotal = (
        catering["base_rates_gbp_per_head"][catering_tier] * party_size * max(1, duration_hours)
    )
    service = subtotal * catering["service_charge_percent"] / 100

    data_path = _SAMPLE_DATA / "venues.json"
    with open(data_path) as f:
        venues = json.load(f)

    valid_venues = [venue for venue in venues if venue["id"] == venue_id]
    if len(valid_venues) == 0:
        return ToolResult(
            success=False, output=valid_venues, summary=f"No venue with venue_id {venue_id} found"
        )
    else:
        hire_fee = valid_venues[0]["hire_fee_gbp"]
        min_spend = valid_venues[0]["min_spend_gbp"]

    # parse the deposit policies
    deposit_required_rule = None
    for spend_rule, deposit_rule in catering["deposit_policy"].items():
        if spend_rule.startswith("under_") and int(spend_rule.split("_")[-1]) < subtotal:
            deposit_required_rule = deposit_rule
        elif spend_rule.startswith("over_") and int(spend_rule.split("_")[-1]) > subtotal:
            deposit_required_rule = deposit_rule
        elif (
            "_to_" in spend_rule
            and int(spend_rule.split("_")[1]) <= subtotal
            and subtotal <= int(spend_rule.split("_")[-1])
        ):
            deposit_required_rule = deposit_rule
        else:
            raise ValueError(f"unable to parse spend_rule: {spend_rule}")

    # parse the found deposit rule
    if deposit_required_rule == "no_deposit_required":
        deposit_required = 0.0
    elif "_percent" in deposit_required_rule:
        deposit_required = int(deposit_required_rule.split("_")[1]) * subtotal / 100
    else:
        raise ValueError(f"Unable to parse deposit_required_rule: {deposit_required_rule}")

    output = {
        "venue_id": venue_id,
        "party_size": party_size,
        "duration_hours": duration_hours,
        "catering_tier": catering_tier,
        "subtotal_gbp": subtotal,
        "service_gbp": service,
        "total_gbp": subtotal + service + hire_fee + min_spend,
        "deposit_required_gbp": int(deposit_required),
    }

    summary = f"calculate_cost({venue_id}, {party_size}): total £{output['total_gbp']}, deposit £{output['deposit_required_gbp']}"
    record_tool_call(
        "calculate_cost",
        {
            "venue_id": venue_id,
            "party_size": party_size,
            "duration_hours": duration_hours,
            "catering_tier": catering_tier,
        },
        output,
    )
    return ToolResult(success=True, output=output, summary=summary)


# ---------------------------------------------------------------------------
# TODO 4 — generate_flyer
# ---------------------------------------------------------------------------
def generate_flyer(session: Session, event_details: dict) -> ToolResult:
    """Produce an HTML flyer and write it to workspace/flyer.html.

    event_details is expected to contain at least:
      venue_name, venue_address, date, time, party_size, condition,
      temperature_c, total_gbp, deposit_required_gbp

    Write a self-contained HTML flyer (inline CSS, no external assets). Tag every key fact with data-testid="<n>" so the integrity check can parse it.

    Write a formatted HTML flyer with an H1 title, the event
    facts, a weather summary, and the cost breakdown.

    Returns:
      output: {"path": "workspace/flyer.html", "bytes_written": int}
      summary: "generate_flyer: wrote <path> (<N> chars)"

    MUST call record_tool_call(...) before returning — the integrity
    check compares the flyer's contents against earlier tool outputs.

    IMPORTANT: this tool MUST be registered with parallel_safe=False
    because it writes a file.
    """
    # I follow README.md (and not ASSIGNMENT.md) and generate a html page for the flyer
    flyer = """
        <doctype html>
        <head>
        <style>
    <style> /* CSS styles from Gemini */
    body {
        /* A warm, oaten background color */
        background-color: #f2eee5;
        /* Creating a subtle "woven" texture using CSS gradients */
        background-image:
        linear-gradient(90deg, rgba(255,255,255,.5) 50%, transparent 50%),
        linear-gradient(rgba(255,255,255,.5) 50%, transparent 50%);
        background-size: 4px 4px;
        color: #332f2;
        font-family: "Times New Roman", Times, serif;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        margin: 0;
        padding: 20px;
    }

    /* The Flyer Box */
    .container {
        background: #fffcf5;
        max-width: 450px;
        width: 100%;
        padding: 40px;
        border: 1px solid #d1c7b7;
        box-shadow: 12px 12px 0px #2d4231; /* A "Scottish Green" hard shadow */
        position: relative;
    }

    /* Corner accents for a vintage feel */
    .container::before {
        content: "";
        position: absolute;
        top: 10px; left: 10px; right: 10px; bottom: 10px;
        border: 1px solid #e8e1d5;
        pointer-events: none;
    }

    h1 {
        font-size: 2.2rem;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #1b1b1b;
        margin: 0 0 20px 0;
        border-bottom: 3px double #2d4231;
        padding-bottom: 10px;
    }

    ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    li {
        margin-bottom: 15px;
        line-height: 1.4;
        font-size: 1.1rem;
        /* Using Monospace for details gives a "ticket" or "receipt" look */
        font-family: "Courier New", Courier, monospace;
    }

    /* Styling the labels (Location, Time, etc.) */
    li strong, li b {
        display: block;
        font-family: "Times New Roman", Times, serif;
        font-variant: small-caps;
        color: #8b3a3a; /* Deep Highland Madder (Red) */
        font-size: 0.9rem;
        letter-spacing: 1px;
    }

    /* Aesthetic flourish at the bottom */
    .flourish {
        text-align: center;
        margin-top: 30px;
        font-size: 1.5rem;
        color: #a69d8d;
    }
    </style>
    <title>Pub Event in Edinburgh</title>
    <meta charset="utf-8">

    </head>
    <body>
    <h1>Pub Event in Edinburgh</h1>\n
        """

    flyer += f"""<ul>\n
        <li data-testid=1>Venue: {event_details["venue_name"]}</li>
        <li data-testid=2>Address: {event_details["venue_address"]}</li>
        <li data-testid=3>Date: {event_details["date"]}</li>
        <li data-testid=4>Time: {event_details["time"]}</li>
        <li data-testid=5>Party Size: {event_details["party_size"]}</li>
        <li data-testid=6>Weather: {event_details["condition"]}, {event_details["temperature_c"]}°C</li>
        <li data-testid=7>Total Cost: £{event_details["total_gbp"]}</li>
        <li data-testid=8>Deposit Required: £{event_details["deposit_required_gbp"]}</li>
    </ul>\n"""
    flyer += "</body>\n</html>\n"

    flyer_path = session.workspace_dir / "flyer.html"
    with open(flyer_path, "w") as f:
        f.write(flyer)

    summary = f"generate_flyer: wrote workspace/flyer.html ({len(flyer)} chars)"
    output = {"path": flyer_path, "bytes_written": len(flyer)}
    record_tool_call("generate_flyer", event_details, output)
    # import pdb; pdb.set_trace()
    return output, summary


# ---------------------------------------------------------------------------
# Registry builder — DO NOT MODIFY the name, signature, or registration calls.
# The grader imports and calls this to pick up your tools.
# ---------------------------------------------------------------------------
def build_tool_registry(session: Session) -> ToolRegistry:
    """Build a session-scoped tool registry with all four Ex5 tools plus
    the sovereign-agent builtins (read_file, write_file, list_files,
    handoff_to_structured, complete_task).

    DO NOT change the tool names — the tests and grader call them by name.
    """
    from sovereign_agent.tools.builtin import make_builtin_registry

    reg = make_builtin_registry(session)

    # venue_search
    reg.register(
        _RegisteredTool(
            name="venue_search",
            description="Search Edinburgh venues by area, party size, and max budget.",
            fn=venue_search,
            parameters_schema={
                "type": "object",
                "properties": {
                    "near": {"type": "string"},
                    "party_size": {"type": "integer"},
                    "budget_max_gbp": {"type": "integer", "default": 1000},
                },
                "required": ["near", "party_size"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,  # read-only
            examples=[
                {
                    "input": {"near": "Haymarket", "party_size": 6, "budget_max_gbp": 800},
                    "output": {"count": 1, "results": [{"id": "haymarket_tap"}]},
                }
            ],
        )
    )

    # get_weather
    reg.register(
        _RegisteredTool(
            name="get_weather",
            description="Get scripted weather for a city on a YYYY-MM-DD date.",
            fn=get_weather,
            parameters_schema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "date": {"type": "string"},
                },
                "required": ["city", "date"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,  # read-only
            examples=[
                {
                    "input": {"city": "Edinburgh", "date": "2026-04-25"},
                    "output": {"condition": "cloudy", "temperature_c": 12},
                }
            ],
        )
    )

    # calculate_cost
    reg.register(
        _RegisteredTool(
            name="calculate_cost",
            description="Compute total cost and deposit for a booking.",
            fn=calculate_cost,
            parameters_schema={
                "type": "object",
                "properties": {
                    "venue_id": {"type": "string"},
                    "party_size": {"type": "integer"},
                    "duration_hours": {"type": "integer"},
                    "catering_tier": {
                        "type": "string",
                        "enum": ["drinks_only", "bar_snacks", "sit_down_meal", "three_course_meal"],
                        "default": "bar_snacks",
                    },
                },
                "required": ["venue_id", "party_size", "duration_hours"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,  # pure compute, no shared state
            examples=[
                {
                    "input": {
                        "venue_id": "haymarket_tap",
                        "party_size": 6,
                        "duration_hours": 3,
                    },
                    "output": {"total_gbp": 540, "deposit_required_gbp": 0},
                }
            ],
        )
    )

    # generate_flyer — parallel_safe=False because it writes a file
    def _flyer_adapter(event_details: dict) -> ToolResult:
        return generate_flyer(session, event_details)

    reg.register(
        _RegisteredTool(
            name="generate_flyer",
            description="Write an HTML flyer for the event to workspace/flyer.html.",
            fn=_flyer_adapter,
            parameters_schema={
                "type": "object",
                "properties": {"event_details": {"type": "object"}},
                "required": ["event_details"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=False,  # writes a file — MUST be False
            examples=[
                {
                    "input": {
                        "event_details": {
                            "venue_name": "Haymarket Tap",
                            "date": "2026-04-25",
                            "party_size": 6,
                        }
                    },
                    "output": {"path": "workspace/flyer.html"},
                }
            ],
        )
    )

    return reg


__all__ = [
    "build_tool_registry",
    "venue_search",
    "get_weather",
    "calculate_cost",
    "generate_flyer",
]
