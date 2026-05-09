# Ex7 — Handoff bridge

## Your answer

Exercise 7 uses the `HandoffBridge` to produce a roundtrip between the structure Rasa part and the unstructured input part. The fake-backend part of the exercise runs without any problems.

The process runs the steps:
1. `bride.round_start` (starting the loop)
2. `planner.called` (planning the task)
3. `planner.produced_subgoals` (produce 1 subgoal)
4. `executor.tool_called` (run the `venue_search` tool, runs unsuccessfully)
5. `executor.tool_called` (calls `handoff_to_structured` with a candidate venue even if step 4 was unsuccessful)
6. `session.state_changed` (from `loop` to `structured`)
7. `session.state_changed` (from `structured` to `loop`, request is rejected sine the party is too large)

This exercise was hard to inspect since the temporary files were deleted after each run. I was able to read partial files when pausing the script half-way to inspect the logs.

Next I tried to run
```bash
make ex7-real
```
but this `make` command did not exist. I added the implementation but was stopped by an error, `[SA_EXT_UNEXPECTED_RESPONSE] FakeLLMClient ran out of scripted responses`. I added two more `ScriptedResponse` and then instead encountered the error `[SA_VAL_INVALID_PLANNER_OUTPUT] planner returned empty content`.

Inspection of the logs showed that the error occurs at `session.state_changed` because of `rejection_reason": "rasa unreachable: <urlopen error [Errno 111] Connection refused>"`. This error occured since I did not realise that the rasa services needs to run while performing this exercise.

After making sure the services were running I found that the script ran successfully end-to-end. The process first tried to book for 12 people near Haymarket, but was rejected since the party ws too large. It then retried for 6 people near Old Town (one of the scripted responses) and was successful. After successfully completing the booking it exited the loop.

## Citations

- `starter.handoff_bridge.run.py`
- `starter.rasa_half.structured_half.py`
- `Session ba3418f77a3c`
- `Session 43ed4e05d39d`
- `Session 071f9e05581c`
