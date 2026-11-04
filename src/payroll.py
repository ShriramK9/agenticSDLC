import uuid
import logging
from decimal import Decimal
from src.schemas import PayrollBatchRequest, EmployeePayoutRecord

logger = logging.getLogger("payroll")

class InMemoryTransactionalPayrollStore:
    def __init__(self):
        self.records = {}
        self.audit_logs = []
        self.locked_rows = set()

    def acquire_row_lock(self, employee_id: str) -> bool:
        logger.info(f"[STAGE: CONCURRENCY_MANAGEMENT] Attempting to acquire row lock for employee: {employee_id}")
        if employee_id in self.locked_rows:
            logger.error(f"[STAGE: CONCURRENCY_MANAGEMENT] Lock Conflict: Employee state {employee_id} is already locked!")
            return False
        self.locked_rows.add(employee_id)
        logger.info(f"[STAGE: CONCURRENCY_MANAGEMENT] Lock successfully acquired for employee: {employee_id}")
        return True

    def release_row_lock(self, employee_id: str):
        self.locked_rows.discard(employee_id)
        logger.info(f"[STAGE: CONCURRENCY_MANAGEMENT] Released lock for employee: {employee_id}")

    def save_payout_record(self, record: EmployeePayoutRecord) -> bool:
        self.records[record.payout_id] = record
        return True

    def update_payout_status(self, payout_id: uuid.UUID, status: str) -> bool:
        if payout_id in self.records:
            old = self.records[payout_id]
            self.records[payout_id] = EmployeePayoutRecord(
                payout_id=old.payout_id, batch_id=old.batch_id, employee_id=old.employee_id,
                gross_pay=old.gross_pay, net_pay=old.net_pay,
                idempotency_key=old.idempotency_key, status=status
            )
            return True
        return False

    def log_audit_trail(self, actor: str, action: str, details: str) -> None:
        msg = f"[AUDIT] Actor: {actor} | Action: {action} | Details: {details}"
        self.audit_logs.append(msg)
        logger.info(msg)

class PayrollOrchestrationService:
    def __init__(self, repo: InMemoryTransactionalPayrollStore):
        self.repo = repo

    def process_employee_payment(self, batch: PayrollBatchRequest, employee_id: str, gross: Decimal) -> uuid.UUID:
        if not self.repo.acquire_row_lock(employee_id):
            raise RuntimeError(f"Lock Conflict: Employee state {employee_id} is currently locked by another worker thread.")
        
        idempotency_key = f"{batch.batch_id}_{employee_id}"
        payout_id = uuid.uuid4()
        net = gross * Decimal("0.70")
        
        record = EmployeePayoutRecord(
            payout_id=payout_id, batch_id=batch.batch_id, employee_id=employee_id,
            gross_pay=gross, net_pay=net, idempotency_key=idempotency_key, status="PENDING"
        )
        
        self.repo.save_payout_record(record)
        self.repo.log_audit_trail("SYSTEM_WORKER", "PAYROLL_COMPUTE", f"Calculated net pay for {employee_id}")
        return payout_id

    def commit_to_ledger(self, payout_id: uuid.UUID) -> bool:
        self.repo.log_audit_trail("SYSTEM_WORKER", "LEDGER_COMMIT", f"Committed payout {payout_id} to banking network infrastructure.")
        return self.repo.update_payout_status(payout_id, "COMPLETED")
