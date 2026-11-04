import pytest
import uuid
import logging
from datetime import datetime
from decimal import Decimal
from src.schemas import ContextMetadata, HumanAuthorizationToken, PipelineStatus, PayrollBatchRequest
from src.engine import ContextAwareSDLCPlatform
from src.payroll import InMemoryTransactionalPayrollStore, PayrollOrchestrationService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def test_scenario_a_url_shortener_context():
    context = ContextMetadata(context_id=uuid.uuid4(), name="URL Shortener Campaign Link Engine")
    context.vectors = {
        "Primary Business Context": "SMS Notification Payload",
        "Operational Scale": {"high_burst": False}
    }
    platform = ContextAwareSDLCPlatform(context)
    assert platform.status == PipelineStatus.AWAITING_HUMAN_REQUIREMENT_APPROVAL

    token = HumanAuthorizationToken("MARKETING_LEAD", "2026-11-04", ["Primary Business Context", "Operational Scale"], False)
    platform.submit_requirement_approval(token)
    platform.run_architecture_and_generation_phase()
    
    assert platform.token_len_mutated == 4
    assert platform.status == PipelineStatus.READY_FOR_PRODUCTION

def test_scenario_b_long_running_payroll_jobs():
    context = ContextMetadata(context_id=uuid.uuid4(), name="Long Running Payroll Jobs System Context")
    context.vectors = {
        "Primary Business Context": "Internal Payroll Core Ledger",
        "Operational Scale": {"high_burst": True}
    }
    platform = ContextAwareSDLCPlatform(context)
    assert platform.scope.requires_midpoint_human_review is True

    with pytest.raises(PermissionError):
        platform.run_architecture_and_generation_phase()

    req_token = HumanAuthorizationToken("FIN_OPS_DIRECTOR_01", "2026-11-04", ["Primary Business Context", "Operational Scale"], False)
    platform.submit_requirement_approval(req_token)
    platform.run_architecture_and_generation_phase()
    assert platform.status == PipelineStatus.AWAITING_CRITICAL_LOGIC_APPROVAL

    repo = InMemoryTransactionalPayrollStore()
    service = PayrollOrchestrationService(repo)
    batch = PayrollBatchRequest(uuid.uuid4(), "CORP_XYZ", "2026-11-30", ["EMP_A"])
    
    payout_id = service.process_employee_payment(batch, "EMP_A", Decimal("7500.00"))
    with pytest.raises(RuntimeError, match="Lock Conflict"):
        service.process_employee_payment(batch, "EMP_A", Decimal("7500.00"))

    service.repo.release_row_lock("EMP_A")
    service.commit_to_ledger(payout_id)

    code_token = HumanAuthorizationToken("LEAD_ARCHITECT", "2026-11-04", ["CRITICAL_CODE_REVIEW"], False)
    platform.submit_critical_logic_approval(code_token)
    assert platform.status == PipelineStatus.READY_FOR_PRODUCTION

def test_scenario_c_java_version_upgrade():
    context = ContextMetadata(context_id=uuid.uuid4(), name="Enterprise Core Microservice Framework Java Upgrade")
    context.vectors = {
        "Primary Business Context": "Technical Modernization Stack Update",
        "target_jdk": "27"
    }
    platform = ContextAwareSDLCPlatform(context)
    assert platform.scope.requires_midpoint_human_review is True

    req_token = HumanAuthorizationToken("ENTERPRISE_ARCHITECT", "2026-11-04", ["Primary Business Context", "target_jdk"], False)
    platform.submit_requirement_approval(req_token)
    platform.run_architecture_and_generation_phase()
    assert platform.status == PipelineStatus.AWAITING_CRITICAL_LOGIC_APPROVAL

    code_token = HumanAuthorizationToken("SECURITY_OFFICER", "2026-11-04", ["CRITICAL_CODE_REVIEW"], False)
    platform.submit_critical_logic_approval(code_token)
    assert platform.status == PipelineStatus.READY_FOR_PRODUCTION
