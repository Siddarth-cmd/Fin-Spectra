import json
from app.database import SessionLocal
from app.repositories import AlertRepository
from app.models.schema import Alert

def test_fetch_and_claim_neon_alert():
    print("=" * 70)
    print(" 🧪 NEON DB ALERT REPOSITORY TEST (STEPS 1-3)")
    print("=" * 70)

    db = SessionLocal()
    try:
        repo = AlertRepository(db)

        print("\n[1] FETCHING & CLAIMING ONE 'OPEN' ALERT FROM NEON...")
        enriched_alert = repo.fetch_and_claim_open_alert()

        if not enriched_alert:
            print("❌ No OPEN alerts available in database.")
            return

        alert_info = enriched_alert["alert"]
        alert_id = alert_info["alert_id"]
        
        print("\n[2] SUCCESSFULLY CLAIMED ALERT:")
        print(f" -> Alert ID: {alert_info['alert_id']}")
        print(f" -> Customer ID: {alert_info['customer_id']}")
        print(f" -> Transaction ID: {alert_info['transaction_id']}")
        print(f" -> Alert Type: {alert_info['alert_type']}")
        print(f" -> Risk Score: {alert_info['risk_score']}")
        print(f" -> Status: {alert_info['status']}")

        assert alert_info["status"] == "UNDER_INVESTIGATION", f"Expected status UNDER_INVESTIGATION, got {alert_info['status']}"

        # Verify DB persistence of claimed status
        db_alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        print(f" -> Verified Status in Neon DB: {db_alert.status}")
        assert db_alert.status == "UNDER_INVESTIGATION", "DB status was not persisted correctly!"

        print("\n[3] LOADED ENRICHED ENTITY CONTEXT:")
        print(f" -> Customer Name: {enriched_alert['customer']['name'] if enriched_alert.get('customer') else 'N/A'}")
        print(f" -> Customer Risk Level: {enriched_alert['customer']['risk_level'] if enriched_alert.get('customer') else 'N/A'}")
        print(f" -> Transaction Amount: ${enriched_alert['transaction']['amount'] if enriched_alert.get('transaction') else 0.0}")
        print(f" -> Accounts Count: {len(enriched_alert.get('accounts', []))}")
        print(f" -> Beneficiaries Count: {len(enriched_alert.get('beneficiaries', []))}")
        print(f" -> Devices Count: {len(enriched_alert.get('devices', []))}")

        print("\n[4] FULL ENRICHED ALERT JSON STRUCTURE:")
        print(json.dumps(enriched_alert, indent=2))

        print("\n✅ TEST PASSED SUCCESSFULLY: Neon → fetch ONE OPEN alert → claim → return enriched data")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    test_fetch_and_claim_neon_alert()
