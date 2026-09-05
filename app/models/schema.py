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
    from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Numeric
    from sqlalchemy.orm import relationship
    from ..database import Base
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    Base = object

# ==========================================
# SQLAlchemy Models (Neon PostgreSQL Database)
# ==========================================

if HAS_SQLALCHEMY:
    class Customer(Base):
        __tablename__ = "customers"

        customer_id = Column(String(50), primary_key=True, index=True)
        name = Column(String(100))
        risk_level = Column(String(20), default="LOW")
        account_age_days = Column(Integer, default=365)
        occupation = Column(String(100), nullable=True)
        declared_income = Column(Numeric(15, 2), nullable=True, default=500000.0)
        date_of_birth = Column(String(20), nullable=True)
        kyc_status = Column(String(30), default="VERIFIED")
        onboarding_date = Column(DateTime, default=datetime.utcnow)
        address = Column(String(200), nullable=True)
        country = Column(String(50), default="IND")
        created_at = Column(DateTime, default=datetime.utcnow)

        accounts = relationship("Account", back_populates="customer")
        beneficiaries = relationship("Beneficiary", back_populates="customer")
        devices = relationship("Device", back_populates="customer")
        transactions = relationship("Transaction", back_populates="customer")
        alerts = relationship("Alert", back_populates="customer")

    class Account(Base):
        __tablename__ = "accounts"

        account_id = Column(String(50), primary_key=True, index=True)
        customer_id = Column(String(50), ForeignKey("customers.customer_id"))
        account_type = Column(String(30))
        status = Column(String(20), default="ACTIVE")
        opening_date = Column(DateTime, default=datetime.utcnow)
        balance = Column(Numeric(15, 2), default=0.0)
        currency = Column(String(10), default="INR")
        branch_country = Column(String(50), default="IND")
        created_at = Column(DateTime, default=datetime.utcnow)

        customer = relationship("Customer", back_populates="accounts")
        transactions = relationship("Transaction", back_populates="account")

    class Beneficiary(Base):
        __tablename__ = "beneficiaries"

        beneficiary_id = Column(String(50), primary_key=True, index=True)
        customer_id = Column(String(50), ForeignKey("customers.customer_id"))
        name = Column(String(100))
        account_number = Column(String(50))
        created_at = Column(DateTime, default=datetime.utcnow)

        customer = relationship("Customer", back_populates="beneficiaries")
        transactions = relationship("Transaction", back_populates="beneficiary")

    class Device(Base):
        __tablename__ = "devices"

        device_id = Column(String(50), primary_key=True)
        customer_id = Column(String(50), ForeignKey("customers.customer_id"), primary_key=True)
        device_type = Column(String(50))
        first_seen = Column(DateTime, default=datetime.utcnow)
        last_seen = Column(DateTime, default=datetime.utcnow)

        customer = relationship("Customer", back_populates="devices")

    class Transaction(Base):
        __tablename__ = "transactions"

        transaction_id = Column(String(50), primary_key=True, index=True)
        customer_id = Column(String(50), ForeignKey("customers.customer_id"))
        account_id = Column(String(50), ForeignKey("accounts.account_id"))
        receiver_account_id = Column(String(50), nullable=True)
        beneficiary_id = Column(String(50), ForeignKey("beneficiaries.beneficiary_id"), nullable=True)
        amount = Column(Numeric(15, 2))
        currency = Column(String(10), default="INR")
        transaction_type = Column(String(30)) # WIRE, TRANSFER, CASH_DEPOSIT, ACH, PAYMENT
        channel = Column(String(30), default="MOBILE_APP")
        status = Column(String(20), default="COMPLETED")
        description = Column(String(255), nullable=True)
        device_id = Column(String(50), nullable=True)
        ip_address = Column(String(45), nullable=True)
        transaction_timestamp = Column(DateTime, default=datetime.utcnow)

        customer = relationship("Customer", back_populates="transactions")
        account = relationship("Account", back_populates="transactions")
        beneficiary = relationship("Beneficiary", back_populates="transactions")
        alerts = relationship("Alert", back_populates="transaction")

    class Alert(Base):
        __tablename__ = "alerts"

        alert_id = Column(String(50), primary_key=True, index=True)
        customer_id = Column(String(50), ForeignKey("customers.customer_id"))
        transaction_id = Column(String(50), ForeignKey("transactions.transaction_id"))
        alert_type = Column(String(100))
        triggered_rules = Column(JSON, nullable=True)
        initial_risk = Column(Numeric(5, 2), default=50.0)
        risk_score = Column(Numeric(5, 2))
        description = Column(String(255), nullable=True)
        status = Column(String(30), default="OPEN") # OPEN, UNDER_INVESTIGATION, RESOLVED, ESCALATED, CLOSED
        created_at = Column(DateTime, default=datetime.utcnow)

        customer = relationship("Customer", back_populates="alerts")
        transaction = relationship("Transaction", back_populates="alerts")

    # Legacy / Additional Models
    class RawAlert(Base):
        __tablename__ = "raw_alerts"

        id = Column(String, primary_key=True, index=True)
        account_id = Column(String, ForeignKey("accounts.account_id"))
        rule_name = Column(String)
        trigger_evidence = Column(JSON)
        timestamp = Column(DateTime, default=datetime.utcnow)

    class InvestigationCase(Base):
        __tablename__ = "investigation_cases"
        
        id = Column(String, primary_key=True, index=True) # CASE_ALT_...
        alert_id = Column(String, unique=True)
        entity_id = Column(String)
        objective = Column(String, nullable=True)
        typology = Column(String, nullable=True)
        status = Column(String, default="OPEN") # OPEN, CLOSED
        priority_score = Column(Float)
        priority_band = Column(String) # CRITICAL, HIGH, MEDIUM, LOW
        
        # LangGraph Output
        final_risk_score = Column(Float, nullable=True)
        decision = Column(String, nullable=True) # ALLOW, REVIEW, BLOCK
        state_snapshot_json = Column(JSON, nullable=True) # Full LangGraph State memory
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class RegulatoryGuidance(Base):
        __tablename__ = "regulatory_guidance"

        id = Column(String(50), primary_key=True)
        topic = Column(String(100), index=True) # STRUCTURING, FAN_IN, FAN_OUT, RAPID_PASS_THROUGH, CIRCULAR_FLOW, MULE_ACCOUNT
        title = Column(String(200))
        source_org = Column(String(100)) # FATF, FinCEN, FIU-IND, RBI
        section_ref = Column(String(100))
        content_summary = Column(String(1000))
        retrieval_date = Column(DateTime, default=datetime.utcnow)

else:
    class Customer: pass
    class Account: pass
    class Beneficiary: pass
    class Device: pass
    class Transaction: pass
    class Alert: pass
    class RawAlert: pass
    class InvestigationCase: pass
    class RegulatoryGuidance: pass

# ==========================================
# Pydantic Models (API / LangGraph)
# ==========================================

class ClassifiedAlert(BaseModel):
    # Field aliases to accept Phase-1 JSON directly
    alert_id: Optional[str] = None
    classified_alert_id: Optional[str] = None
    
    entity_id: Optional[str] = None
    account_id: Optional[str] = None
    customer_id: Optional[str] = None
    
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
        return self.entity_id or self.customer_id or self.account_id or "ACC_UNKNOWN"

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
