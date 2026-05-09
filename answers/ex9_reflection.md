# Ex9 — Reflection


## Q1 — Planner handoff decision

_Find a point in your Ex7 logs where the planner decided to hand off to the structured half. Quote the planner's reasoning or the specific subgoal's assigned_half field. What signal caused the decision?_

### Your answer

In exercise 7, the planner handed over to the structured half when a venue failed to be found and when a venue was found. More specifically `handoff to structured half: loop half identified a candidate venue; passing to structured half for confirmation under policy rules` (zero venues were found) and `handoff to structured half: retry after reverse handoff \u2014 scaled down to fit policy` (1 venue found). These handoffs both came after the tool call was performed.

I found that the planner handoff worked well in all exercises following exercise 5. In exercise 5 I needed to give very direct prompts for the model to perform the correct tool calls, and often for it to perform the tool calls at all. In the following exercises the Rasa structured calls and handoff bridge made the model perform the correct tool call without any additional prompts. This was very helpful but came at the cost of additional tooling and complexity.

I inspected the responses from all runs, with the exception of most runs for exercise 7 where the logs were missing or deleted for most of my runs. It was necessary to inspect the logs since many runs completed with the first impression that they were successful. One alternative here could have been to introduce a "debug mode" where the loop exits with an error whenever it hits an unsuccessful step, although I understand that this behaviour can be difficult to specify when the model is designed to retry failed steps.

The planner decides the following tool calls, but it cannot plan for all possible combinations of errors. Ideally the planner could outline the plan in steps, so if one step is only partially successful, the planner needs to an another round of planning when the original plan fails. This comes at a cost, of course.

### Citations

- `started/edinburgh_research/run.py`
- `Session sess_c4c2cb1b352b` (exercise 5)
- `Session sess_529122a48208` (exercise 5)
- `Session sess_fcedb959a6bb` (exercise 6)
- `Session ba3418f77a3c` (exercise 7)
- `Session 43ed4e05d39d` (exercise 7)
- `Session 071f9e05581c` (exercise 7)
- `Session: sess_561c3a242f5f` (exercise 8)
- `Session sess_d4b8c9c978de` (exercise 8)
- `Session: sess_e90261be636f` (exercise 8)
- `Session sess_c24b1db259f8` (exercise 8)


## Q2 — Dataflow integrity catch

_Describe one instance where your Ex5 dataflow integrity check caught something manual inspection missed, OR (if you never saw it trigger) describe a plausible scenario where it WOULD catch a failure that a human reviewer wouldn't. Your scenario must be specific enough that someone else could construct the test case._

### Your answer

My impression was the reverse for exercise 5. In almost all cases the integrity check completed with a `successful` status, while studying the logs gave another picture. A possible scenario is when the model hallucinates a tool call response that "looks" correct but is found to be incorrect on closer inspection. Such an error might be missed by a human, but caught in dataflow integrity checks.

I found that in exercise 5 the final output was sometimes marked as successful even when the output values were incongurent with the inputs. E.g. when the checker found a CSS color containing `c`, it misstook it for a temperature value. Adding structure to the inputs and outputs made the model fail much less frequently, giving a significant improvement. I suspect that this is because the structured input is the same every time while in natural language the same information can be stated in many different ways or variations. 

### Citations

- `Session sess_529122a48208` (exercise 5)
- `Session sess_fcedb959a6bb` (exercise 6)
- `Session 071f9e05581c` (exercise 7)
- `Session sess_d4b8c9c978de` (exercise 8)


## Q3 — Removing one framework primitive

_If you were shipping this agent to a real pub-booking business next week, what's the first production failure you'd expect, and which sovereign-agent primitive (ticket state machine, manifest discipline, IPC atomic rename, SessionQueue retry, etc.) would surface it? One specific primitive, one specific failure mode._

### Your answer

If I were to ship this app into production next week, I would expect that SessionQueue retry would fail first. This is because the model would most probably try to retry a failed query or alter the parameters in such a way that the query was successful, but the new booking was too unlike the original query to be accepted by the user. In other words, the model would retry until a successfull booking was made, even if it was not the original booking request. Because the model can have difficulty to differentiate between an actualy failure (the booking request is not possible) and a failure of the tools (an incorrect query). The real world is more messy than this controlled exercise, that is why I expect the SessionQueue retry to fail first.


If I were to rewrite the framework I would probably start out by forking a well known and widely available framework like `langchain` or `strands` and implement the missing functionality in a separate script.

I found the logging in plain text to be very good. It would perhaps been instructive to also log the output using a freely available web framework like `weights & biases`. The logged json was clear and easy to read. Some error messages were not self evident of how to interpret, but it was often not difficult to dig deeper to find the actual error.

A next step would be to have the model query its own logs. It would then be possible to ask it questions like "why did the Haymarket reject our booking request?" Also most tasks were missing their ticket_id for unknown reason. This was not a problem in this context but might cause problem if the agent were to process 100s or 1000s of tickets a day.

### Citations

- `Session sess_c4c2cb1b352b` (exercise 5)
- `Session sess_fcedb959a6bb` (exercise 6)
- `Session 43ed4e05d39d` (exercise 7)
- `Session sess_c24b1db259f8` (exercise 8)
