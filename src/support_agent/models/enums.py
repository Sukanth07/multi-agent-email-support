"""Closed enumerations for intents and workflow routing."""

from enum import Enum


class Intent(str, Enum):
    """Customer intent categories, aligned with the knowledge base."""

    AUTHENTICATION = "authentication"
    SSO = "sso"
    BILLING = "billing"
    USER_MANAGEMENT = "user_management"
    API = "api"
    INTEGRATIONS = "integrations"
    SECURITY = "security"
    TROUBLESHOOTING = "troubleshooting"
    PRODUCT_FEATURES = "product_features"
    ENTERPRISE_SUPPORT = "enterprise_support"
    OTHER = "other"


class NextAction(str, Enum):
    """Routing decisions the orchestrator emits at branching points."""

    RETRY_RETRIEVAL = "retry_retrieval"
    PLAN = "plan"
    REWRITE = "rewrite"
    FINISH = "finish"
