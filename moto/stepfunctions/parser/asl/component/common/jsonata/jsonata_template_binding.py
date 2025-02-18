from __future__ import annotations

from moto.stepfunctions.parser.asl.component.common.jsonata.jsonata_template_value import (
    JSONataTemplateValue,
)
from moto.stepfunctions.parser.asl.component.eval_component import EvalComponent
from moto.stepfunctions.parser.asl.eval.environment import Environment


class JSONataTemplateBinding(EvalComponent):
    identifier: str
    value: JSONataTemplateValue

    def __init__(self, identifier: str, value: JSONataTemplateValue):
        self.identifier = identifier
        self.value = value

    def _eval_body(self, env: Environment) -> None:
        binding_container: dict = env.stack.pop()
        self.value.eval(env=env)
        value = env.stack.pop()
        binding_container[self.identifier] = value
        env.stack.append(binding_container)
