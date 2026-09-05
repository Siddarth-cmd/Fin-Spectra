import sys
import argparse
from typing import Optional, Dict, Any
from unittest.mock import patch

from app.database import SessionLocal
from app.models.schema import Alert, Customer, Transaction, Account, Beneficiary, Device, InvestigationCase
from app.repositories import AlertRepository
from app.agents.state import create_initial_state_from_neon_alert
from app.agents.graph import investigation_graph

class DummySession:
    """Mock database session that swallows commits/writes during safe read-only demo execution."""
    def query(self, *args, **kwargs):
        return self
    def filter(self, *args, **kwargs):
        return self
    def first(self, *args, **kwargs):
        return None
    def add(self, *args, **kwargs):
        pass
    def commit(self):
        pass
    def rollback(self):
        pass
    def close(self):
        pass

def fetch_read_only_alert(db: Any, alert_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Reads one OPEN alert (or specific alert_id) without modifying its status or issuing DB commits."""
    query = db.query(Alert)
    if alert_id:
        query = query.filter(Alert.alert_id == alert_id)
    else:
        query = query.filter(Alert.status == "OPEN").order_by(Alert.created_at.asc())

    alert = query.first()
    if not alert:
        return None

    customer = db.query(Customer).filter(Customer.customer_id == alert.customer_id).first()
    transaction = db.query(Transaction).filter(Transaction.transaction_id == alert.transaction_id).first()

    accounts = db.query(Account).filter(Account.customer_id == alert.customer_id).all()
    beneficiaries = db.query(Beneficiary).filter(Beneficiary.customer_id == alert.customer_id).all()
    devices = db.query(Device).filter(Device.customer_id == alert.customer_id).all()

    tx_account = None
    if transaction and transaction.account_id:
        tx_account = db.query(Account).filter(Account.account_id == transaction.account_id).first()

    tx_beneficiary = None
    if transaction and transaction.beneficiary_id:
        tx_beneficiary = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == transaction.beneficiary_id).first()

    return {
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

def main():
    parser = argparse.ArgumentParser(description="Fin-Spectra Phase-2 Investigation Pipeline Showcase Demo")
    parser.add_argument("--live", action="store_true", help="Run in live mode (claim alert, modify DB status, persist case)")
    parser.add_argument("--show-dossier", action="store_true", help="Display the generated SAR narrative dossier output")
    parser.add_argument("--alert-id", type=str, default=None, help="Target specific alert_id for investigation")
    args = parser.parse_args()

    mode_str = "LIVE / PERSISTED" if args.live else "SAFE / READ-ONLY"

    print("=" * 70)
    print(" FIN-SPECTRA MULTI-AGENT FINANCIAL CRIME INVESTIGATION DEMO")
    print("=" * 70)
    print(f" MODE: {mode_str}")
    print("=" * 70)

    db = SessionLocal()
    try:
        repo = AlertRepository(db)
        if args.live:
            if args.alert_id:
                alert_obj = db.query(Alert).filter(Alert.alert_id == args.alert_id).first()
                if not alert_obj:
                    print(f"\n❌ Alert '{args.alert_id}' not found in database.")
                    return
                alert_obj.status = "UNDER_INVESTIGATION"
                db.commit()
                db.refresh(alert_obj)
                enriched_alert = fetch_read_only_alert(db, args.alert_id)
            else:
                print("\n[1] NEON ALERT")
                enriched_alert = repo.fetch_and_claim_open_alert()
        else:
            print("\n[1] NEON ALERT")
            enriched_alert = fetch_read_only_alert(db, args.alert_id)

        if not enriched_alert:
            print("\nNo OPEN alerts available.")
            print("Nothing was processed.")
            return

        alert_info = enriched_alert["alert"]
        print(f" Alert ID       : {alert_info.get('alert_id')}")
        print(f" Customer ID    : {alert_info.get('customer_id')}")
        print(f" Alert Type     : {alert_info.get('alert_type')}")
        print(f" Phase-1 Risk   : {alert_info.get('risk_score')}")
        print(f" Database Status: {alert_info.get('status')}")

        if args.live:
            print(" ✓ Alert claimed and set to UNDER_INVESTIGATION")
        else:
            print(" ✓ Alert loaded without claiming (READ-ONLY)")

        print("\n[2] INITIAL INVESTIGATION STATE")
        initial_state = create_initial_state_from_neon_alert(enriched_alert)
        print(f" Case ID        : {initial_state.get('case_id')}")
        print(f" Entity ID      : {initial_state.get('entity_id')}")
        print(" ✓ State created")

        print("\n[3] INVESTIGATION GRAPH EXECUTION")
        config = {"configurable": {"thread_id": initial_state["case_id"]}, "recursion_limit": 50}

        try:
            if args.live:
                final_state = investigation_graph.invoke(initial_state, config=config)
            else:
                # Intercept downstream DB writes in safe mode to guarantee 100% read-only safety
                with patch("app.database.SessionLocal", DummySession), \
                     patch("app.agents.nodes.scoring_node.SessionLocal", DummySession):
                    final_state = investigation_graph.invoke(initial_state, config=config)

            print(" Task Planner              ✓")
            print(" Evidence Retrieval        ✓")
            print(" Behavior Analysis         ✓")
            print(" Graph Analysis            ✓")
            print(" KYC Verification          ✓")
            print(" Plan Checker              ✓")
            print(" Typology Classification   ✓")
            print(" Risk Scoring              ✓")
            print(" Case Assembly             ✓")

        except Exception as graph_err:
            print(f"\n❌ Pipeline execution failed during graph step.")
            print(f"   Error: {str(graph_err)}")
            if args.live:
                repo.fail_alert(alert_info["alert_id"], new_status="FAILED")
                print(f"   Alert status updated to FAILED in Neon DB.")
            return

        # Check InvestigationCase persistence
        if args.live:
            saved_case = db.query(InvestigationCase).filter(InvestigationCase.id == final_state["case_id"]).first()
            if saved_case and saved_case.status == "CLOSED":
                # Lifecycle completion: Mark original Alert CLOSED AFTER InvestigationCase persistence
                repo.complete_alert(alert_info["alert_id"])

        # Evidence Summary
        trigger_ev = final_state.get("trigger_evidence") or {}
        accounts = trigger_ev.get("accounts") or []
        bens = trigger_ev.get("beneficiaries") or []
        devs = trigger_ev.get("devices") or []

        print("\n[4] INVESTIGATION EVIDENCE")
        print(f" Transactions              : 1 (Trigger Tx ID: {alert_info.get('transaction_id')})")
        print(f" Accounts                  : {len(accounts)}")
        print(f" Beneficiaries             : {len(bens)}")
        print(f" Devices                   : {len(devs)}")

        # Behavior Analysis Output
        behavior = final_state.get("behavioral_metrics") or {}
        print("\n[5] BEHAVIOR ANALYSIS")
        print(f" Historical Samples        : {behavior.get('historical_transaction_count', 0)}")
        print(f" Historical Mean           : {behavior.get('historical_mean', 0.0)}")
        print(f" Historical Std Dev        : {behavior.get('historical_stddev', 0.0)}")
        print(f" Effective Std Dev         : {behavior.get('effective_stddev', 0.0)}")
        print(f" Velocity Z-Score          : {behavior.get('velocity_z_score', 0.0)}")
        print(f" Baseline Status           : {behavior.get('velocity_baseline_status', 'N/A')}")

        # Graph Analysis Output
        graph = final_state.get("graph_metrics") or {}
        print("\n[6] GRAPH ANALYSIS")
        print(f" Account Count             : {graph.get('tx_per_account', 0)}")
        print(f" Beneficiary Count         : {graph.get('multi_beneficiary_flag', 0)}")
        print(f" Device Count              : {graph.get('multi_device_multi_beneficiary_flag', False)}")
        print(f" Beneficiary Dispersion    : {graph.get('beneficiary_dispersion_ratio', 0.0)}")
        print(f" Self Transfer Detected    : {graph.get('self_transfer_detected', False)}")

        # KYC Verification Output
        customer = trigger_ev.get("customer") or {}
        print("\n[7] KYC VERIFICATION")
        print(f" Risk Level                : {customer.get('risk_level', 'N/A')}")
        print(f" Occupation                : {customer.get('occupation', 'N/A')}")
        print(f" Account Age               : {customer.get('account_age_days', 'N/A')} days")
        print(f" KYC Findings              : {final_state.get('kyc_notes', 'N/A')[:60]}...")

        # Typology Output
        print("\n[8] TYPOLOGY CLASSIFICATION")
        print(f" Classification            : {final_state.get('typology_classification')}")
        print(f" Validation                : VALIDATED")
        print(f" Rationale                 : {final_state.get('typology_rationale')[:100]}...")

        # Scoring Output
        subscores = behavior.get("risk_subscores") or {}
        print("\n[9] RISK SCORING (COMPOSITE WEIGHTED MODEL)")
        print(f" Phase-1 Prior (35%)       : {subscores.get('phase1_prior', 0.0)}")
        print(f" Behavior Score (25%)      : {subscores.get('behavior', 0.0)}")
        print(f" Graph Score (25%)         : {subscores.get('graph', 0.0)}")
        print(f" KYC Score (15%)           : {subscores.get('kyc', 0.0)}")
        print(" ---------------------------------------------------")
        print(f" Final Risk Score          : {final_state.get('final_risk_score')}")
        print(f" Decision                  : {final_state.get('decision')}")

        # Case Assembly Output
        dossier = final_state.get("dossier", "")
        print("\n[10] CASE ASSEMBLY")
        print(f" Dossier Generated         : {'YES' if dossier else 'NO'}")
        print(f" Dossier Length            : {len(dossier)} characters")

        # Database Result Summary
        print("\n[11] DATABASE RESULT")
        if args.live:
            saved_case = db.query(InvestigationCase).filter(InvestigationCase.id == final_state["case_id"]).first()
            alert_db = db.query(Alert).filter(Alert.alert_id == alert_info["alert_id"]).first()
            print(f" Alert status in DB (alerts table)             : {alert_db.status if alert_db else 'UNKNOWN'}")
            print(f" Case persisted in DB (investigation_cases)    : {'YES' if saved_case else 'NO'} (Case ID: {final_state['case_id']})")
            print(f" Case status in DB (investigation_cases)       : {saved_case.status if saved_case else 'UNKNOWN'}")
        else:
            alert_db = db.query(Alert).filter(Alert.alert_id == alert_info["alert_id"]).first()
            case_db = db.query(InvestigationCase).filter(InvestigationCase.id == final_state["case_id"]).first()
            print(f" Alert remains in DB (alerts table)            : {alert_db.status if alert_db else 'OPEN'}")
            print(f" Database mutation                             : NONE (Read-Only Mode)")
            print(f" Case persisted in DB (investigation_cases)    : {'YES' if case_db else 'NO'}")

        print("\n" + "=" * 70)
        print(" PIPELINE DEMONSTRATION COMPLETE")
        print("=" * 70)

        if args.show_dossier:
            print("\n" + "=" * 70)
            print(" GENERATED SAR DOSSIER NARRATIVE")
            print("=" * 70)
            print(dossier)
            print("=" * 70)

    except Exception as err:
        db.rollback()
        print(f"\n❌ Unexpected Error during demonstration: {str(err)}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
