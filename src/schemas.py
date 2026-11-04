from enum import Enum
from typing import List, Optional, Set, Dict, Any
from dataclasses import dataclass, field
import uuid

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class PipelineStatus(Enum):
    AWAITING_HUMAN_REQUIREMENT_APPROVAL = "AWAITING_HUMAN_REQUIREMENT_APPROVAL"
    AWAITING_CRITICAL_LOGIC_APPROVAL = "AWAITING_CRITICAL_LOGIC_APPROVAL"
    ARCHITECTURE_DESIGN = "ARCHITECTURE_DESIGN"
    COMPILING_CORE = "COMPILING_CORE"
    TESTING = "TESTING"
    READY_FOR_PRODUCTION = "READY_FOR_PRODUCTION"
    HALTED = "HALTED"

@dataclass
class ContextMetadata:
    context_id: uuid.UUID
    name: str
    vectors: Dict[str, Any] = field(default_factory=dict)
    agent_assumed_flags: Set[str] = field(default_factory=set)

@dataclass(frozen=True)
class ScopeAssessment:
    assessment_id: uuid.UUID
    financial_exposure: RiskLevel
    customer_blast_radius: RiskLevel
    logic_criticality: RiskLevel
    requires_midpoint_human_review: bool

@dataclass(frozen=True)
class HumanAuthorizationToken:
    approver_id: str
    timestamp: str
    approved_vectors: List[str]
    override_applied: bool

@dataclass(frozen=True)
class PayrollBatchRequest:
    batch_id: uuid.UUID
    corporate_id: str
    pay_period_end: str
    employee_ids: List[str]

@dataclass(frozen=True)
class EmployeePayoutRecord:
    payout_id: uuid.UUID
    batch_id: uuid.UUID
    employee_id: str
    gross_pay: Any
    net_pay: Any
    idempotency_key: str
    status: str
