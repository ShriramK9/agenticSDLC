import uuid
import logging
from typing import Optional
from src.schemas import ContextMetadata, ScopeAssessment, PipelineStatus, HumanAuthorizationToken
from src.governance import GovernanceEngine

logger = logging.getLogger("engine")

class ContextAwareSDLCPlatform:
    def __init__(self, context: ContextMetadata):
        self.context = context
        logger.info(f"[STAGE: PHASE_0_INITIALIZATION] Initializing Context Loop Engine v2 for scenario: '{context.name}'")
        self.scope = GovernanceEngine.evaluate_scope(self.context)
        self.status = PipelineStatus.AWAITING_HUMAN_REQUIREMENT_APPROVAL
        self.requirement_token = None
        self.logic_token = None
        self.token_len_mutated = 6

    def submit_requirement_approval(self, token: HumanAuthorizationToken):
        expected_vectors = list(self.context.vectors.keys())
        if GovernanceEngine.verify_token(token, expected_vectors):
            self.requirement_token = token
            self.status = PipelineStatus.ARCHITECTURE_DESIGN
            logger.info("[STAGE: REQ_INTERROGATION_BARRIER] Step 0.5 Roadblock unblocked by verified manual token signature.")
        else:
            self.status = PipelineStatus.HALTED
            logger.error("[STAGE: PIPELINE_BREACH_HALT] Execution frozen permanently due to requirements validation failure.")
            raise ValueError("Requirement Verification Token missing required corporate vectors.")

    def run_architecture_and_generation_phase(self):
        if self.status != PipelineStatus.ARCHITECTURE_DESIGN:
            logger.error("[STAGE: REQ_INTERROGATION_BARRIER] Human Roadblock Active. Halting code paths pending Phase 0 manual sign-off.")
            raise PermissionError("Pipeline is locked. Awaiting Phase 0 manual confirmation signature.")
        
        logger.info("[STAGE: COMPILING_CORE] Commencing architecture mutations and payload asset synthesis loops...")
        
        # Context-Driven Mutation Analysis
        if self.context.vectors.get("Primary Business Context") == "SMS Notification Payload":
            self.token_len_mutated = 4
            logger.info("[CONTEXT_MUTATION_OUTPUT] URL Shortener Rules Evaluated. Detected SMS context payload -> Mutating token lengths down to: 4 chars.")
        elif "upgrade" in self.context.name.lower() or "java" in self.context.name.lower():
            target_jdk = self.context.vectors.get("target_jdk", "11")
            logger.info(f"[CONTEXT_MUTATION_OUTPUT] Stack Modernization Vector Captured. Upgrading environment framework manifests to JDK Version: {target_jdk}")

        if self.scope.requires_midpoint_human_review:
            self.status = PipelineStatus.AWAITING_CRITICAL_LOGIC_APPROVAL
            logger.info("[STAGE: BUSINESS_LOGIC_BARRIER] Step 2.5 Midpoint Code Review Gate Active. Pipeline execution paused.")
        else:
            self.status = PipelineStatus.READY_FOR_PRODUCTION
            logger.info("[STAGE: COMPILING_CORE] Baseline compilation finalized. Infrastructure declared safe for deployment.")

    def submit_critical_logic_approval(self, token: HumanAuthorizationToken):
        if self.status != PipelineStatus.AWAITING_CRITICAL_LOGIC_APPROVAL:
            raise PermissionError("Engine is not currently paused on a critical logic gate checkpoint.")
        
        if token.override_applied or "CRITICAL_CODE_REVIEW" in token.approved_vectors:
            self.logic_token = token
            self.status = PipelineStatus.READY_FOR_PRODUCTION
            logger.info("[STAGE: BUSINESS_LOGIC_BARRIER] Step 2.5 Midpoint Code Review Gate unblocked via verified architect review.")
        else:
            self.status = PipelineStatus.HALTED
            logger.error("[STAGE: PIPELINE_BREACH_HALT] Security Event! Invalid token verification recorded.")
            raise ValueError("Critical Logic review vector signature rejected.")
