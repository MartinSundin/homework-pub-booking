# Ex6 — Rasa structured half

## Your answer

Exercise 6 uses the Rasa API to convert the booking request into a more structured format. Running the exercise involves 3 steps:
1. The **Rasa Scenario** (client) impemented in `validator.py` which takes the unstructured question/request and converts it to a structured format.
2. The **Rasa Server** implemented in `structured_half.py` which posts the structured request to the actions and interprets the response.
3. The **Rasa Actions** implemented in `actions.py` which handles the booking request and returns a structured response.

Running all three gives the output
```bash
summary: booking confirmed by rasa (ref=BK-7D401E9E)
```
The run produces two files. `SESSION.md` with instructions and `session.json` with a json containing the session id and time but otherwise is mostly empty. Otherwise, all folders in `~/.local/share/sovereign-agent/examples/ex6-rasa-half/sess_fcedb959a6bb` are empty. No logs outlining the steps run are produced.

Overall I would say that exercise 6 shows how Rasa can be used to bring structure to requests. However, it does not show how to implement the Rasa API or how Rasa can be called from other frameworks like lang-chain. The session ran smoothly without any problems. Unfortunately the logs are empty, it would have been very interesting to examine the original request, structure request, structured response and final unstructure response. The exercise gives some introduction to the functionality of Rasa.


## Citations

- `starter/rasa_half/validator.py`
- `starter/rasa_half/structured_half.py`
- `starter/rasa_half/actions.py`
- `Session sess_fcedb959a6bb`
