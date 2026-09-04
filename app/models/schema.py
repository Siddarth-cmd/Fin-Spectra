from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from pydantic import BaseModel, ConfigDict
except ImportError:
    # Minimal Pydantic-like fallback for standalone execution
    class ConfigDict:
        def __init__(self, **kwargs): pass
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        model_config = {}

try:
    from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
    from sqlalchemy.orm import relationship
    from ..database import Base
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    Base = object

# ==========================================
# SQLAlchemy Models (Database)
# ==========================================

if HAS_SQLALCHEMY:
    class Account(Base):
        __tablename__ = "accounts"

        id = Column(String, primary_key=True, index=True)
        customer_name = Column(String)
        account_type = Column(String)
        kyc_occupation = Column(String, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        is_dormant = Column(Boolean, default=False)
        
        transactions_out = relationship("Transaction", foreign_keys="[Transaction.source_account_id]", back_populates="source_account")
        transactions_in = relationship("Transaction", foreign_keys="[Transaction.destination_account_id]", back_populates="destination_account")

    class Transaction(Base):
        __tablename__ = "transactions"

        id = Column(String, primary_key=True, index=True)
        source_account_id = Column(String, ForeignKey("accounts.id"))
        destination_account_id = Column(String, ForeignKey("accounts.id"))
        amount = Column(Float)
        currency = Column(String, default="USD")
        timestamp = Column(DateTime, default=datetime.utcnow)
        payment_channel = Column(String) # Wire, ACH, Cash
        
        # Hidden Ground Truth for Evaluation
        is_fraud_ground_truth = Column(Boolean, default=False)
        fraud_typology_ground_truth = Column(String, nullable=True)

        source_account = relationship("Account", foreign_keys=[source_account_id], back_populates="transactions_out")
        destination_account = relationship("Account", foreign_keys=[destination_account_id], back_populates="transactions_in")

    class RawAlert(Base):
        __tablename__ = "raw_alerts"

        id = Column(String, primary_key=True, index=True)
        account_id = Column(String, ForeignKey("accounts.id"))
        rule_name = Column(String)
        trigger_evidence = Column(JSON)
        timestamp = Column(DateTime, default=datetime.utcnow)

    class InvestigationCase(Base):
        __tablename__ = "investigation_cases"
        
        id = Column(String, primary_key=True, index=True) # CASE_ALT_...
        alert_id = Column(String, unique=True)
        entity_id = Column(String, ForeignKey("accounts.id"))
        status = Column(String, default="OPEN") # OPEN, CLOSED
        priority_score = Column(Float)
        priority_band = Column(String) # CRITICAL, HIGH, MEDIUM, LOW
        
        # LangGraph Output
        final_risk_score = Column(Float, nullable=True)
        decision = Column(String, nullable=True) # ALLOW, REVIEW, BLOCK
        state_snapshot_json = Column(JSON, nullable=True) # Full LangGraph State memory
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
else:
    class Account: pass
    class Transaction: pass
    class RawAlert: pass
    class InvestigationCase: pass

# ==========================================
# Pydantic Models (API / LangGraph)
# ==========================================

class ClassifiedAlert(BaseModel):
    # Field aliases to accept Phase-1 JSON directly
    alert_id: Optional[str] = None
    classified_alert_id: Optional[str] = None
    
    entity_id: Optional[str] = None
    account_id: Optional[str] = None
    
    alert_type: str
    
    severity: Optional[str] = None
    risk_level: Optional[str] = "HIGH"
    
    raw_score: Optional[float] = 0.0
    risk_score: Optional[float] = None
    
    priority_rank: Optional[int] = 1
    
    trigger_reason: Optional[str] = None
    detected_reason: Optional[str] = None
    
    features_json: Optional[Dict[str, Any]] = None
    evidence: Optional[Dict[str, Any]] = None

    def get_alert_id(self) -> str:
        return self.alert_id or self.classified_alert_id or "ALT_UNKNOWN"

    def get_entity_id(self) -> str:
        return self.entity_id or self.account_id or "ACC_UNKNOWN"

    def get_severity(self) -> str:
        return self.severity or self.risk_level or "HIGH"

    def get_score(self) -> float:
        if self.raw_score is not None and self.raw_score != 0.0:
            return float(self.raw_score)
        if self.risk_score is not None:
            return float(self.risk_score)
        return 50.0

    def get_trigger_reason(self) -> str:
        return self.trigger_reason or self.detected_reason or ""

    def get_features(self) -> Dict[str, Any]:
        return self.features_json or self.evidence or {}

    model_config = ConfigDict(from_attributes=True)
