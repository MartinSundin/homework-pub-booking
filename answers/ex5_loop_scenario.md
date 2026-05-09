# Ex5 — Edinburgh research loop scenario

## Your answer

This exercise was quite easy to pass the offline deterministic scenario, even if many bugs still remained. The real scenario was more difficult since the model repeatedly ignored the tool instructions and tried to call the tool `venue_search` with some random parameters multiple times. After failing this step the model did not proceed any further and did not output a flyer. I tried changing the model, but without any changes (also many models in Nebius returned a `model not found` error messages). It was first after adding additional system prompts for the planning and executor that the model performed the correct tool calls. The checks then passed. However, inspecting the logs showed that the toolcalls were not correct. After some additional debugging I was able to make the full agentic loop run correctly.

After the planning stage, the model created two tickets:
- subgoal `sg_1`, ticket `tk_8796c945`
- subgoal `sg_2`, ticket `tk_02173737`
I was unable to determine whick ticket was `venue_search` and which was `get_weather` since both calls had `ticket_id: null`. The model then proceeded to
1. call `calculate_cost` (not always called)
2. call `generate_flyer`
3. call `complete_task`
4. call `generate_flyer` (one more time)
5. call `complete_task` (one more time)

For the flyer I settled with a simple html list with styled CSS I acquired from Google. But another option would be to let Google Nano Banana generate the flyer for me. I should mention that the CSS contained the color `#a69d8c` which was interpreted by the grader as a temperature in the flyer. I therefore had to modify it to `#a69d8d` to avoid the error.

## Citations

- `starter/edinburgh_research/tools.py`
- `started/edinburgh_research/run.py`
- `Session sess_c4c2cb1b352b`
- `Session sess_529122a48208`


---

The planner produced two subgoals: sg_1 (research venues near Haymarket
for a party of 6, assigned to loop) and sg_2 (produce a flyer with the
chosen venue, weather, and cost, also loop). Both ran in the same
executor session.

Turn 1 called venue_search, get_weather, and calculate_cost in parallel
— all three are parallel_safe because they only read fixtures. Turn 2
wrote the flyer via generate_flyer (parallel_safe=False because it
writes a file). Turn 3 called complete_task.

The dataflow integrity check caught one issue during development: the
template for "no deposit required" originally read "total under £300
threshold", which put £300 in the flyer prose. That value was never
returned by any tool — it's a rule threshold, not data. I simplified
the phrasing to "No deposit required for this booking." Without the
integrity check this would have slipped past review because £300 looks
like a reasonable number in the right context.

## Citations

- sessions/sess_*/logs/trace.jsonl — tool call sequence
- sessions/sess_*/workspace/flyer.md — the produced flyer
