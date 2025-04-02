REACT_INSTRUCTIONS = {
    "instructions": """If parameters are required, they are defined by placeholder pattern in curly braces. 
                        Parameter placeholders need to be replaced by the actual action input.
                        - Thoughts can reason about the current situation.
                        - Actions will provide you with further external observations as result of this action.
                        - When you found an Action, stop and return the Thought and Action.
                        - When you found an Answer, stop and return this Answer.
                        - Call the tools corresponding to action once you defined the parameters needed"""
}

TRIAGE_INSTRUCTIONS = {
    "triage_rules": {
        "ignore": "Marketing newsletters, spam emails, mass company announcements",
        "notify": "Team member out sick, build system notifications, project status updates",
        "respond": "Direct questions from team members, meeting requests, critical bug reports",
    },
    "agent_instructions": "Use these tools when appropriate to help manage John's tasks efficiently.",
}
