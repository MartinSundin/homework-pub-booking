# Ex9 — Reflection

## Q1 — Planner handoff decision

### Your answer

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

### Your answer

I found that in exercise 5 the final output was sometimes marked as successful even when the output values were incongurent with the inputs. E.g. when the checker found a CSS color containing `c`, it misstook it for a temperature value. Adding structure to the inputs and outputs made the model fail much less frequently, giving a significant improvement. I suspect that this is because the structured input is the same every time while in natural language the same information can be stated in many different ways or variations. 

### Citations

- `Session sess_529122a48208` (exercise 5)
- `Session sess_fcedb959a6bb` (exercise 6)
- `Session 071f9e05581c` (exercise 7)
- `Session sess_d4b8c9c978de` (exercise 8)


## Q3 — Removing one framework primitive

### Your answer

If I were to rewrite the framework I would probably start out by forking a well known and widely available framework like `langchain` or `strands` and implement the missing functionality in a separate script.

I found the logging in plain text to be very good. It would perhaps been instructive to also log the output using a freely available web framework like `weights & biases`. The logged json was clear and easy to read. Some error messages were not self evident of how to interpret, but it was often not difficult to dig deeper to find the actual error.

A next step would be to have the model query its own logs. It would then be possible to ask it questions like "why did the Haymarket reject our booking request?" Also most tasks were missing their ticket_id for unknown reason. This was not a problem in this context but might cause problem if the agent were to process 100s or 1000s of tickets a day.

### Citations

- `Session sess_c4c2cb1b352b` (exercise 5)
- `Session sess_fcedb959a6bb` (exercise 6)
- `Session 43ed4e05d39d` (exercise 7)
- `Session sess_c24b1db259f8` (exercise 8)
