REACT_INSTRUCTIONS = {
    "instructions": """1.Begin with an observation that outlines the primary task or question you want the agent to address.
2. Analyze the observation to generate exactly one thought that leads to an actionable step using one of the available tools.
3. Log the generated thought and corresponding action pair for transparency and future reference.
4. Execute the exactly one action using the choosen tool and specify the parameters needed.
5. Collect the new observation or insights generated from the tool's output.
6. Is further analysis or action needed, think how other possible tools may help to improve the output?
- If yes, create new thought and action pairs.
- If no, provide a concise conclusion.
Use tools that relly on memory first"""
}

TRIAGE_INSTRUCTIONS = {
    "triage_rules": {
        "ignore": "Marketing newsletters, spam emails, mass company announcements",
        "notify": "Team member out sick, build system notifications, project status updates",
        "respond": "Direct questions from team members, meeting requests, critical bug reports",
    },
    "agent_instructions": "Use these tools when appropriate to help manage John's tasks efficiently.",
}
