import uuid
import logging
from src.schemas import ContextMetadata, ScopeAssessment, RiskLevel, HumanAuthorizationToken

logger = logging.getLogger("governance")

class GovernanceEngine:
    @staticmethod
    def evaluate_scope(context: ContextMetadata) -> ScopeAssessment:
        logger.info(f"[STAGE: SCOPE_DETERMINATION] Evaluating scope context for: {context.name}")
        is_financial = "payroll" in context.name.lower() or "ledger" in context.name.lower()
        is_upgrade = "upgrade" in context.name.lower() or "java" in context.name.lower()
        has_large_scale = context.vectors.get("Operational Scale", {}).get("high_burst", False) or is_upgrade
        
        financial_risk = RiskLevel.CRITICAL if is_financial else RiskLevel.LOW
        blast_radius = RiskLevel.HIGH if has_large_scale else RiskLevel.LOW
        logic_criticality = RiskLevel.CRITICAL if (is_financial or is_upgrade) else RiskLevel.LOW
        
        requires_midpoint = (
            financial_risk == RiskLevel.CRITICAL or 
            blast_radius == RiskLevel.HIGH or 
            logic_criticality == RiskLevel.CRITICAL
        )
        
        logger.info(f"[STAGE: SCOPE_DETERMINATION] Calculated Profile - Financial Exposure: {financial_risk.value}, Blast Radius: {blast_radius.value}, Logic Criticality: {logic_criticality.value}. Midpoint Intercept Triggered: {requires_midpoint}")
        
        return ScopeAssessment(
            assessment_id=uuid.uuid4(),
            financial_exposure=financial_risk,
            customer_blast_radius=blast_radius,
            logic_criticality=logic_criticality,
            requires_midpoint_human_review=requires_midpoint
        )

    @staticmethod
    def verify_token(token: HumanAuthorizationToken, expected_vectors: list) -> bool:
        logger.info(f"[STAGE: TOKEN_VERIFICATION] Checking token signatures from user: {token.approver_id}")
        if token.override_applied:
            logger.warning("[STAGE: TOKEN_VERIFICATION] Warning! Admin master override token applied.")
            return True
        verified = all(v in token.approved_vectors for v in expected_vectors)
        if not verified:
            logger.error("[STAGE: PIPELINE_BREACH_HALT] Security Event! Invalid token signature vector match.")
        else:
            logger.info("[STAGE: TOKEN_VERIFICATION] Token verified successfully.")
        return verified
