import os
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.schema import Customer, Account, Transaction, Alert

def seed():
    print("Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding database with 100 records...")
        
        customers = []
        accounts = []
        transactions = []
        alerts = []
        
        alert_types = ["RAPID_PASS_THROUGH", "STRUCTURING", "LARGE_AMOUNT", "FAN_IN", "FAN_OUT", "ROUND_AMOUNT", "HIGH_VELOCITY"]
        risk_levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        occupations = ["Software Engineer", "Trader", "Consultant", "Unemployed", "Student", "Director", "Manager"]
        
        base_time = datetime.utcnow() - timedelta(days=30)
        
        for i in range(1, 101):
            # Customer
            c_id = f"CUST-{1000 + i}"
            c = Customer(
                customer_id=c_id, 
                name=f"User {i}", 
                risk_level=random.choice(risk_levels), 
                account_age_days=random.randint(10, 1000), 
                occupation=random.choice(occupations)
            )
            customers.append(c)
            
            # Account
            a_id = f"ACCT-{2000 + i}"
            a = Account(
                account_id=a_id, 
                customer_id=c_id, 
                account_type=random.choice(["Checking", "Savings", "Business"]), 
                status="ACTIVE"
            )
            accounts.append(a)
            
            # Transaction
            t_id = f"TXN-{3000 + i}"
            amount = round(random.uniform(100.0, 50000.0), 2)
            t = Transaction(
                transaction_id=t_id, 
                customer_id=c_id, 
                account_id=a_id, 
                amount=amount, 
                transaction_type=random.choice(["Wire", "Transfer", "ACH", "Cash"]), 
                status="COMPLETED",
                transaction_timestamp=base_time + timedelta(hours=i*2)
            )
            transactions.append(t)
            
            # Alert
            alt_id = f"ALT-{4000 + i}"
            risk_score = random.uniform(10.0, 99.0)
            alt = Alert(
                alert_id=alt_id, 
                customer_id=c_id, 
                transaction_id=t_id, 
                alert_type=random.choice(alert_types), 
                risk_score=round(risk_score, 1), 
                status="OPEN",
                created_at=base_time + timedelta(hours=i*2 + 1)
            )
            alerts.append(alt)
            
        db.add_all(customers)
        db.add_all(accounts)
        db.add_all(transactions)
        db.add_all(alerts)

        db.commit()
        print("Database seeded successfully with 100 records.")
    except Exception as e:
        print("Error during seeding:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
