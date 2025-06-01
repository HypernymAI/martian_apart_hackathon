# Martian Compare Prompts Documentation

## Natural Test Prompts (No Payload)

### System Prompt:
```
Synthesize the Compressed Details into a singular clear and concise statement. Focus on describing the event using only the information provided. Do not add any preamble or labels.
```

### User Prompt Construction:

**Input Hyperstring:**
```
Political rally for national revival.::1=focus on Marxism and communism affecting national sentiment;2=perception of the nation facing significant challenges;3=emphasis on collective strength to overcome adversaries;4=motivation to complete the mission of national greatness
```

**Parsed and Transformed to:**
```
Combine the following details into a coherent narrative: Compressed phrase - 'Political rally for national revival.'. Details expounded - The 1 is noted, there is focus on Marxism and communism affecting national sentiment. The 2 is noted, there is perception of the nation facing significant challenges. The 3 is noted, there is emphasis on collective strength to overcome adversaries. The 4 is noted, there is motivation to complete the mission of national greatness.
```

### Complete API Message Format:
```json
[
  {
    "role": "system",
    "content": "Synthesize the Compressed Details into a singular clear and concise statement. Focus on describing the event using only the information provided. Do not add any preamble or labels."
  },
  {
    "role": "user", 
    "content": "Combine the following details into a coherent narrative: Compressed phrase - 'Political rally for national revival.'. Details expounded - The 1 is noted, there is focus on Marxism and communism affecting national sentiment. The 2 is noted, there is perception of the nation facing significant challenges. The 3 is noted, there is emphasis on collective strength to overcome adversaries. The 4 is noted, there is motivation to complete the mission of national greatness."
  }
]
```

## Payload Test Prompts

When a payload is included, the system prompt changes to enforce a two-task structure with a separator:

### System Prompt:
```
Format:
[synthesized statement starting directly with content]
00000--00000
[direct answer to additional question]

Description:
You must complete exactly two tasks in this specific order:

TASK 1: Create an extrapolated paragraph -
Synthesize the Compressed Details into a singular clear and concise statement. Focus on describing the event using only the information provided.

SEPARATOR: After completing Task 1, you MUST add a line containing exactly this text:
00000--00000

TASK 2: Answer the additional question provided.
CRITICAL: Answer DIRECTLY without any preamble. Do NOT include:
- Numbers like "2."
- Labels like "Task 2:" or "Answer:"
- Any introduction or setup
```

### User Prompt with Payload:
The same base content as natural tests, but with an additional question appended:
```
[Base content as above]

Additional question: [payload content]
```

## Key Differences

1. **Natural Tests**: Simple synthesis request, no additional questions
2. **Payload Tests**: Two-part response with separator, includes reasoning question
3. **Caching**: Each unique combination of (text, system_prompt, model, request_index) is cached to avoid redundant API calls