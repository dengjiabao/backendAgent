class AgentError(Exception):
    """Agent 领域错误基类。"""


class ConnectorUnavailable(AgentError):
    pass


class PermissionDenied(AgentError):
    pass


class BusinessOperationFailed(AgentError):
    pass


class UnsupportedCapability(AgentError):
    pass
