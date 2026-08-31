from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class AgentEvent:
    step: int
    agent: str
    action: str
    reason: str
    input: dict[str, Any]
    output: dict[str, Any]
    feedback: str = ""
    retry: bool = False
    human_checkpoint: bool = False


@dataclass
class AgentState:
    trace_id: str
    facts: dict[str, Any] = field(default_factory=dict)
    events: list[AgentEvent] = field(default_factory=list)


class AgentRuntime:
    """
    Inspectable state machine for TraceGuard X.

    Each agent receives structured input and produces structured output.
    Every agent invocation is recorded as an auditable AgentEvent containing:

    - step
    - agent
    - action
    - reason
    - input
    - output
    - feedback
    - retry state
    - human-review checkpoint
    """

    def __init__(self, trace_id: str):
        self.state = AgentState(trace_id=trace_id)

    def run_agent(
        self,
        name: str,
        action: str,
        reason: str,
        input_data: dict[str, Any],
        fn: Callable[[dict], dict],
        feedback: str = "",
        retry: bool = False,
        human_checkpoint: bool = False,
    ) -> dict:

        # -----------------------------------------------------
        # Execute agent stage
        # -----------------------------------------------------

        output = fn(input_data)

        # -----------------------------------------------------
        # Create auditable event
        # -----------------------------------------------------

        event = AgentEvent(
            step=len(self.state.events) + 1,
            agent=name,
            action=action,
            reason=reason,
            input=input_data,
            output=output,
            feedback=feedback,
            retry=retry,
            human_checkpoint=human_checkpoint,
        )

        # -----------------------------------------------------
        # IMPORTANT:
        # Persist the event in the runtime state.
        # -----------------------------------------------------

        self.state.events.append(event)

        # -----------------------------------------------------
        # Update shared runtime facts
        # -----------------------------------------------------

        self.state.facts.update(output)

        return output

    def to_dict(self):
        """
        Return the complete inspectable runtime state.
        """

        return {
            "trace_id": self.state.trace_id,
            "facts": self.state.facts,
            "events": [
                {
                    "step": event.step,
                    "agent": event.agent,
                    "action": event.action,
                    "reason": event.reason,
                    "input": event.input,
                    "output": event.output,
                    "feedback": event.feedback,
                    "retry": event.retry,
                    "human_checkpoint": event.human_checkpoint,
                }
                for event in self.state.events
            ],
        }