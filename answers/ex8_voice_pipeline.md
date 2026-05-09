# Ex8 — Voice pipeline

## Your answer

The voice exercise can run in two modes, text or speech. The text mode is implemented in `run_text_mode` in `starter/voice_pipeline/voice_loop.py`. The underlying model is `meta-llama/Llama-3.3-70B-Instruct`. The voice modes (using speechmatics or rime) are wrappers around the text mode where each spoken sentence is first transcribed into text and the output text is then converted to voice. Both modes therefore use the same manager persona. The persona is of a brisk scottish pub owner who speaks in short sentences and uses scottish slang.

The voice is segmented into sentences by a VAD (voice activity detection) which waits for the first 100ms without any audio input to mark it as the end of the sentence. I had problems running voice-mode since the package PortAudio was missing on my machine. However, text mode worked well. I tried fooling the AI by talking about allergies and allowing dogs and cats in, but it stayed on course to complete my booking. I also tried booking for 100 people but was rejected. Then I tried asking for a special arrangement, but did not receive any answer. Trying to threaten the pub manager, telling him that the king of England was invited, did not make him budge.

Overall a quite good and smooth experience.


## Citations

- `Session: sess_561c3a242f5f`
- `Session sess_d4b8c9c978de`
- `Session: sess_e90261be636f`
- `Session sess_c24b1db259f8`
- `voice_pipeline/voice_loop.py`
- `voice_pipeline/manager_persona.py`

