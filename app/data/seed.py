import os
import random
from datetime import datetime, timedelta
from app.database import engine, Base, SessionLocal
from app.models.schema import Customer, Account, Beneficiary, Device, Transaction, Alert, RegulatoryGuidance

def seed():
    print("Recreating database tables for Fin-Spectra real data layer...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Clear existing data safely without schema lock conflicts
        db.query(Alert).delete()
        db.query(Transaction).delete()
        db.query(Device).delete()
        db.query(Beneficiary).delete()
        db.query(Account).delete()
        db.query(Customer).delete()
        db.query(RegulatoryGuidance).delete()
        db.commit()

        print("Seeding database with 100 realistic alerts & financial-crime dataset...")

        customers = []
        accounts = []
        beneficiaries = []
        devices = []
        transactions = []
        alerts = []
        guidances = []

        now = datetime.utcnow()
        base_time = now - timedelta(days=30)

        # -------------------------------------------------------------
        # 1. REGULATORY GUIDANCE KNOWLEDGE BASE (Phase 14)
        # -------------------------------------------------------------
        reg_items = [
            {
                "id": "REG-FATF-REC13",
                "topic": "CORRESPONDENT_BANKING",
                "title": "FATF Recommendation 13: Correspondent Banking & Shell Intermediaries",
                "source_org": "FATF",
                "section_ref": "Recommendation 13.2",
                "content_summary": "Financial institutions must gather sufficient information about a respondent institution to understand fully the nature of the respondent's business and prevent shell bank transactions."
            },
            {
                "id": "REG-FINCEN-STRUCT",
                "topic": "STRUCTURING",
                "title": "FinCEN Guidance on CTR Avoidance & Structuring",
                "source_org": "FinCEN",
                "section_ref": "31 CFR § 1010.314",
                "content_summary": "Structuring occurs when a person conducts multiple currency transactions below $10,000 for the purpose of evading currency transaction reporting (CTR) requirements."
            },
            {
                "id": "REG-FIU-PASSTHROUGH",
                "topic": "RAPID_PASS_THROUGH",
                "title": "FIU Advisory on Rapid In-Out Layering & Mule Accounts",
                "source_org": "FIU-IND",
                "section_ref": "AML-ADV-2023-04",
                "content_summary": "Accounts experiencing sudden incoming wire funds followed immediately (within minutes to hours) by outbound transfers of nearly equal magnitude exhibit rapid pass-through layering behavior."
            },
            {
                "id": "REG-FATF-FANOUT",
                "topic": "FAN_OUT",
                "title": "FATF Guidance on Trade-Based Money Laundering & Network Dispersion",
                "source_org": "FATF",
                "section_ref": "TBML-RPT-2020",
                "content_summary": "Rapid distribution of consolidated funds to multiple unrelated beneficiary accounts (Fan-Out) is a primary indicator of illicit proceeds integration and mule payout structures."
            },
            {
                "id": "REG-RBI-KYC-MISMATCH",
                "topic": "MULE_ACCOUNT",
                "title": "RBI Master Direction on Customer Due Diligence & Profile Mismatch",
                "source_org": "RBI",
                "section_ref": "MD-KYC-2016 Section 37",
                "content_summary": "Financial institutions are required to continuously monitor customer transactions to ensure they align with the customer's declared profile, income, and risk category."
            },
            {
                "id": "REG-FIU-CIRCULAR",
                "topic": "CIRCULAR_FLOW",
                "title": "FIU Guidelines on Round-Tripping & Circular Transaction Networks",
                "source_org": "FIU-IND",
                "section_ref": "CIRC-2022-09",
                "content_summary": "Circular movement of funds across multiple entity accounts returning to the originating account or beneficial owner constitutes round-tripping money laundering."
            }
        ]

        for reg in reg_items:
            guidances.append(RegulatoryGuidance(
                id=reg["id"],
                topic=reg["topic"],
                title=reg["title"],
                source_org=reg["source_org"],
                section_ref=reg["section_ref"],
                content_summary=reg["content_summary"],
                retrieval_date=now
            ))

        # -------------------------------------------------------------
        # 2. GENERATE 100 REALISTIC CUSTOMER COHORTS & ALERTS
        # -------------------------------------------------------------
        alert_types = [
            "STRUCTURING", "RAPID_PASS_THROUGH", "FAN_IN", "FAN_OUT",
            "CIRCULAR_FLOW", "LARGE_AMOUNT", "HIGH_VELOCITY", "ROUND_AMOUNT"
        ]
        occupations = ["Software Engineer", "Trader", "Consultant", "Unemployed", "Student", "Director", "Manager", "Sole Proprietor"]
        risk_levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

        for i in range(1, 101):
            c_id = f"CUST-{1000 + i}"
            a_id = f"ACCT-{2000 + i}"
            t_id = f"TXN-{3000 + i}"
            alt_id = f"ALT-{4000 + i}"

            # Determine risk tier distribution for 100 alerts
            if i <= 35:
                # Critical Risk (80-99)
                risk_score = round(random.uniform(80.0, 99.0), 1)
                risk_tier = "CRITICAL"
            elif i <= 65:
                # High Risk (60-79)
                risk_score = round(random.uniform(60.0, 79.9), 1)
                risk_tier = "HIGH"
            elif i <= 85:
                # Medium Risk (40-59)
                risk_score = round(random.uniform(40.0, 59.9), 1)
                risk_tier = "MEDIUM"
            else:
                # Low Risk (10-39)
                risk_score = round(random.uniform(10.0, 39.9), 1)
                risk_tier = "LOW"

            a_type = alert_types[(i - 1) % len(alert_types)]
            occ = occupations[(i - 1) % len(occupations)]

            # Customer
            c = Customer(
                customer_id=c_id,
                name=f"Entity {i}",
                risk_level=risk_tier,
                account_age_days=random.randint(15, 1200),
                occupation=occ,
                declared_income=float(random.choice([250000, 500000, 1200000, 2500000])),
                date_of_birth=f"{1980 + (i % 20)}-0{1 + (i % 8)}-{10 + (i % 15)}",
                kyc_status="VERIFIED" if i % 10 != 0 else "PENDING_REVERIFICATION",
                onboarding_date=base_time - timedelta(days=random.randint(100, 1000)),
                country="IND"
            )
            customers.append(c)

            # Account
            a = Account(
                account_id=a_id,
                customer_id=c_id,
                account_type=random.choice(["Checking", "Business", "Savings"]),
                status="ACTIVE",
                balance=float(random.randint(50000, 5000000)),
                currency="INR"
            )
            accounts.append(a)

            # Beneficiary
            b_id = f"BEN-{5000 + i}"
            b = Beneficiary(
                beneficiary_id=b_id,
                customer_id=c_id,
                name=f"Beneficiary Corp {i}",
                account_number=f"ACC-BEN-{9000 + i}"
            )
            beneficiaries.append(b)

            # Device
            d = Device(
                device_id=f"DEV-{6000 + i}",
                customer_id=c_id,
                device_type=random.choice(["iOS Mobile App", "Chrome Web Portal", "Android App"]),
                first_seen=base_time + timedelta(days=i),
                last_seen=now - timedelta(hours=i)
            )
            devices.append(d)

            # Historical ledger entries (3-5 routine transactions per account)
            for j in range(1, 5):
                hist_amt = round(random.uniform(500.0, 15000.0), 2)
                transactions.append(Transaction(
                    transaction_id=f"TXN-HIST-{i}-{j}",
                    customer_id=c_id,
                    account_id=a_id,
                    amount=hist_amt,
                    currency="INR",
                    transaction_type="TRANSFER" if j % 2 == 0 else "PAYMENT",
                    status="COMPLETED",
                    transaction_timestamp=base_time + timedelta(days=j*2)
                ))

            # Trigger Transaction
            trig_amt = round(random.uniform(950000.0, 9800000.0) if risk_tier in ["CRITICAL", "HIGH"] else random.uniform(5000.0, 450000.0), 2)
            trig_tx = Transaction(
                transaction_id=t_id,
                customer_id=c_id,
                account_id=a_id,
                beneficiary_id=b_id,
                receiver_account_id=f"ACCT-{2000 + ((i % 100) + 1)}",
                amount=trig_amt,
                currency="INR",
                transaction_type="WIRE" if a_type in ["RAPID_PASS_THROUGH", "FAN_OUT", "CIRCULAR_FLOW"] else ("CASH_DEPOSIT" if a_type == "STRUCTURING" else "TRANSFER"),
                channel="WIRE_TRANSFER" if a_type == "RAPID_PASS_THROUGH" else "MOBILE_APP",
                status="COMPLETED",
                description=f"Transaction triggering {a_type} rule",
                transaction_timestamp=now - timedelta(hours=i)
            )
            transactions.append(trig_tx)

            # Alert
            alt = Alert(
                alert_id=alt_id,
                customer_id=c_id,
                transaction_id=t_id,
                alert_type=a_type,
                initial_risk=risk_score,
                risk_score=risk_score,
                status="OPEN" if i <= 80 else ("UNDER_INVESTIGATION" if i <= 90 else "CLOSED"),
                description=f"{a_type} risk signature detected with priority score {risk_score}",
                created_at=now - timedelta(hours=i)
            )
            alerts.append(alt)

        db.add_all(guidances)
        db.add_all(customers)
        db.add_all(accounts)
        db.add_all(beneficiaries)
        db.add_all(devices)
        db.add_all(transactions)
        db.add_all(alerts)

        db.commit()
        print("Fin-Spectra database successfully seeded with 100 alerts across Critical, High, Medium, and Low risk tiers.")
    except Exception as e:
        print("Error during seeding:", e)
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()
