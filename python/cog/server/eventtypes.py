from typing import Any, Dict

from attrs import define, field, validators

from ..schema import RemotePredictor
from .telemetry import TraceContext


# From worker parent process
#
@define
class PredictionInput:
    payload: Dict[str, Any]
    # add trace context to pass traceparent and tracestate to child processes
    trace_context: TraceContext

@define
class PredictorWorkflowRequest:
    pass

@define
class PredictorWorkflowResponse:
    workflow: Dict[str, Any]


@define
class RemotePredictorRequest:
    predictor: RemotePredictor
    add: bool = True


@define
class Shutdown:
    pass


# From predictor child process
#
@define
class Log:
    message: str
    source: str = field(validator=validators.in_(["stdout", "stderr"]))


@define
class PredictionOutput:
    payload: Any


@define
class PredictionOutputType:
    multi: bool = False


@define
class Done:
    canceled: bool = False
    error: bool = False
    error_detail: str = ""
