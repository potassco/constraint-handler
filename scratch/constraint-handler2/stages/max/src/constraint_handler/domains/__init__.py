"""Domain representations and topological domain computation.

domain_from_values constructs exact explicit domains unless values would collide;
join_domains combines domains soundly but may overapproximate their union.
Domain equality and hashing compare representations rather than denotations.
"""

from .computer import compute_domains
from .values import (
    DEFAULT_BOOLEAN_THRESHOLD,
    DEFAULT_THRESHOLD,
    EMPTY_DOMAIN,
    TRUE_FALSE_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    DomainStore,
    DomainValue,
    SetValue,
    domain_from_values,
    join_domains,
)

__all__ = [
    "DEFAULT_BOOLEAN_THRESHOLD",
    "DEFAULT_THRESHOLD",
    "EMPTY_DOMAIN",
    "TRUE_FALSE_DOMAIN",
    "UNKNOWN_DOMAIN",
    "Domain",
    "DomainStore",
    "DomainValue",
    "SetValue",
    "compute_domains",
    "domain_from_values",
    "join_domains",
]
