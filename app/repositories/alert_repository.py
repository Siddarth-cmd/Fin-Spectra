from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError
from app.models.schema import Alert, Customer, Transaction, Account, Beneficiary, Device

class AlertRepository:
    """
    Repository for managing Phase-1 alerts and fetching enriched contextual entity data from Neon DB.
    """
    def __init__(self, db: Session):
        self.db = db

    def fetch_and_claim_open_alert(self) -> Optional[Dict[str, Any]]:
        """
        Atomically fetches one OPEN alert from Neon DB, marks its status as UNDER_INVESTIGATION,
        and loads all related customer, transaction, account, beneficiary, and device data.

        Returns:
            Dict containing enriched alert and entity data, or None if no OPEN alerts exist.
        """
        try:
            # Query for one OPEN alert with pessimistic locking (skip locked rows for concurrency safety)
            alert = (
                self.db.query(Alert)
                .filter(Alert.status == "OPEN")
                .order_by(Alert.created_at.asc())
                .with_for_update(skip_locked=True)
                .first()
            )

            if not alert:
                return None

            # Atomically update status to UNDER_INVESTIGATION
            alert.status = "UNDER_INVESTIGATION"
            self.db.commit()
            self.db.refresh(alert)

            # Load related entities for full contextual enrichment
            customer = self.db.query(Customer).filter(Customer.customer_id == alert.customer_id).first()
            transaction = self.db.query(Transaction).filter(Transaction.transaction_id == alert.transaction_id).first()
            
            accounts = self.db.query(Account).filter(Account.customer_id == alert.customer_id).all()
            beneficiaries = self.db.query(Beneficiary).filter(Beneficiary.customer_id == alert.customer_id).all()
            devices = self.db.query(Device).filter(Device.customer_id == alert.customer_id).all()

            # Identify specific transaction account and beneficiary if present
            tx_account = None
            if transaction and transaction.account_id:
                tx_account = self.db.query(Account).filter(Account.account_id == transaction.account_id).first()

            tx_beneficiary = None
            if transaction and transaction.beneficiary_id:
                tx_beneficiary = self.db.query(Beneficiary).filter(Beneficiary.beneficiary_id == transaction.beneficiary_id).first()

            enriched_data = {
                "alert": {
                    "alert_id": alert.alert_id,
                    "customer_id": alert.customer_id,
                    "transaction_id": alert.transaction_id,
                    "alert_type": alert.alert_type,
                    "risk_score": float(alert.risk_score) if alert.risk_score is not None else 0.0,
                    "status": alert.status,
                    "created_at": alert.created_at.isoformat() if alert.created_at else None,
                },
                "customer": {
                    "customer_id": customer.customer_id,
                    "name": customer.name,
                    "risk_level": customer.risk_level,
                    "account_age_days": customer.account_age_days,
                    "occupation": customer.occupation,
                    "created_at": customer.created_at.isoformat() if customer.created_at else None,
                } if customer else None,
                "transaction": {
                    "transaction_id": transaction.transaction_id,
                    "customer_id": transaction.customer_id,
                    "account_id": transaction.account_id,
                    "beneficiary_id": transaction.beneficiary_id,
                    "amount": float(transaction.amount) if transaction.amount is not None else 0.0,
                    "transaction_type": transaction.transaction_type,
                    "transaction_timestamp": transaction.transaction_timestamp.isoformat() if transaction.transaction_timestamp else None,
                    "status": transaction.status,
                } if transaction else None,
                "transaction_account": {
                    "account_id": tx_account.account_id,
                    "customer_id": tx_account.customer_id,
                    "account_type": tx_account.account_type,
                    "status": tx_account.status,
                    "created_at": tx_account.created_at.isoformat() if tx_account.created_at else None,
                } if tx_account else None,
                "transaction_beneficiary": {
                    "beneficiary_id": tx_beneficiary.beneficiary_id,
                    "customer_id": tx_beneficiary.customer_id,
                    "name": tx_beneficiary.name,
                    "account_number": tx_beneficiary.account_number,
                    "created_at": tx_beneficiary.created_at.isoformat() if tx_beneficiary.created_at else None,
                } if tx_beneficiary else None,
                "accounts": [
                    {
                        "account_id": acc.account_id,
                        "customer_id": acc.customer_id,
                        "account_type": acc.account_type,
                        "status": acc.status,
                        "created_at": acc.created_at.isoformat() if acc.created_at else None,
                    }
                    for acc in accounts
                ],
                "beneficiaries": [
                    {
                        "beneficiary_id": b.beneficiary_id,
                        "customer_id": b.customer_id,
                        "name": b.name,
                        "account_number": b.account_number,
                        "created_at": b.created_at.isoformat() if b.created_at else None,
                    }
                    for b in beneficiaries
                ],
                "devices": [
                    {
                        "device_id": d.device_id,
                        "customer_id": d.customer_id,
                        "device_type": d.device_type,
                        "first_seen": d.first_seen.isoformat() if d.first_seen else None,
                        "last_seen": d.last_seen.isoformat() if d.last_seen else None,
                    }
                    for d in devices
                ]
            }

            return enriched_data

        except DBAPIError as err:
            self.db.rollback()
            raise err
        except Exception as err:
            self.db.rollback()
            raise err
