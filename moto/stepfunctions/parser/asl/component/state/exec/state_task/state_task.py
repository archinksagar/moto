from __future__ import annotations

import abc
from typing import List, Optional

from moto.stepfunctions.parser.api import HistoryEventType, TaskTimedOutEventDetails
from moto.stepfunctions.parser.asl.component.common.error_name.failure_event import (
    FailureEvent,
)
from moto.stepfunctions.parser.asl.component.common.error_name.states_error_name import (
    StatesErrorName,
)
from moto.stepfunctions.parser.asl.component.common.error_name.states_error_name_type import (
    StatesErrorNameType,
)
from moto.stepfunctions.parser.asl.component.common.parameters import Parameters
from moto.stepfunctions.parser.asl.component.state.exec.execute_state import (
    ExecutionState,
)
from moto.stepfunctions.parser.asl.component.state.exec.state_task.service.resource import (
    Resource,
)
from moto.stepfunctions.parser.asl.component.state.state_props import StateProps
from moto.stepfunctions.parser.asl.eval.environment import Environment
from moto.stepfunctions.parser.asl.eval.event.event_detail import EventDetails


class StateTask(ExecutionState, abc.ABC):
    resource: Resource
    parameters: Optional[Parameters]

    def __init__(self):
        super(StateTask, self).__init__(
            state_entered_event_type=HistoryEventType.TaskStateEntered,
            state_exited_event_type=HistoryEventType.TaskStateExited,
        )
        # Parameters (Optional)
        # Used to state_pass information to the API actions of connected resources. The parameters can use a mix of static
        # JSON and JsonPath.
        self.parameters = None

    def from_state_props(self, state_props: StateProps) -> None:
        super(StateTask, self).from_state_props(state_props)
        self.parameters = state_props.get(Parameters)
        self.resource = state_props.get(Resource)

    def _get_supported_parameters(self) -> Optional[Set[str]]:  # noqa
        return None

    def _eval_parameters(self, env: Environment) -> dict:
        # Eval raw parameters.
        parameters = dict()
        if self.parameters:
            self.parameters.eval(env=env)
            parameters = env.stack.pop()

        # Handle supported parameters.
        supported_parameters = self._get_supported_parameters()
        if supported_parameters:
            unsupported_parameters: List[str] = [
                parameter
                for parameter in parameters.keys()
                if parameter not in supported_parameters
            ]
            for unsupported_parameter in unsupported_parameters:
                parameters.pop(unsupported_parameter, None)

        return parameters

    def _get_timed_out_failure_event(self) -> FailureEvent:
        return FailureEvent(
            error_name=StatesErrorName(typ=StatesErrorNameType.StatesTimeout),
            event_type=HistoryEventType.TaskTimedOut,
            event_details=EventDetails(
                taskTimedOutEventDetails=TaskTimedOutEventDetails(
                    error=StatesErrorNameType.StatesTimeout.to_name(),
                )
            ),
        )

    def _from_error(self, env: Environment, ex: Exception) -> FailureEvent:
        if isinstance(ex, TimeoutError):
            return self._get_timed_out_failure_event()
        return super()._from_error(env=env, ex=ex)

    def _eval_body(self, env: Environment) -> None:
        super(StateTask, self)._eval_body(env=env)
        env.context_object_manager.context_object["Task"] = None
