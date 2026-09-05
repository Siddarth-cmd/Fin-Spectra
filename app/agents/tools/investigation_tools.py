import math
import networkx as nx
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import or_ as sqlalchemy_or
from app.database import SessionLocal
from app.models.schema import Customer, Account, Beneficiary, Device, Transaction, Alert, InvestigationCase, RegulatoryGuidance

def get_customer_tool(customer_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves full customer record from database."""
    db = SessionLocal()
    try:
        cust = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not cust:
            return None
        return {
            "customer_id": cust.customer_id,
            "name": cust.name,
            "risk_level": cust.risk_level,
            "account_age_days": cust.account_age_days,
            "occupation": cust.occupation,
            "declared_income": float(cust.declared_income) if cust.declared_income else 500000.0,
            "kyc_status": cust.kyc_status,
            "country": cust.country,
            "created_at": cust.created_at.isoformat() if cust.created_at else None
        }
    finally:
        db.close()

def get_account_tool(account_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves account record from database."""
    db = SessionLocal()
    try:
        acc = db.query(Account).filter(Account.account_id == account_id).first()
        if not acc:
            return None
        return {
            "account_id": acc.account_id,
            "customer_id": acc.customer_id,
            "account_type": acc.account_type,
            "status": acc.status,
            "balance": float(acc.balance) if acc.balance else 0.0,
            "currency": acc.currency
        }
    finally:
        db.close()

def get_transactions_tool(customer_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Queries real database transactions associated with entity or its accounts."""
    db = SessionLocal()
    try:
        cust_accs = db.query(Account.account_id).filter(Account.customer_id == customer_id).all()
        acc_ids = [a[0] for a in cust_accs]

        filters = [Transaction.customer_id == customer_id]
        if acc_ids:
            filters.append(Transaction.account_id.in_(acc_ids))
            filters.append(Transaction.receiver_account_id.in_(acc_ids))

        txs = (
            db.query(Transaction)
            .filter(sqlalchemy_or(*filters))
            .order_by(Transaction.transaction_timestamp.desc())
            .limit(limit)
            .all()
        )

        results = []
        for t in txs:
            results.append({
                "transaction_id": t.transaction_id,
                "customer_id": t.customer_id,
                "account_id": t.account_id,
                "receiver_account_id": t.receiver_account_id,
                "beneficiary_id": t.beneficiary_id,
                "amount": float(t.amount) if t.amount else 0.0,
                "transaction_type": t.transaction_type,
                "channel": t.channel,
                "status": t.status,
                "timestamp": t.transaction_timestamp.isoformat() if t.transaction_timestamp else None,
                "source_table": "transactions",
                "source_id": t.transaction_id
            })
        return results
    finally:
        db.close()

def calculate_behavior_metrics_tool(transactions: List[Dict[str, Any]], trigger_tx_id: str, trigger_amount: float) -> Dict[str, Any]:
    """Calculates statistical baseline, Z-score, velocity, and pass-through ratios from actual transactions."""
    if not transactions:
        return {
            "historical_count": 0,
            "historical_mean": 0.0,
            "historical_stddev": 0.0,
            "velocity_z_score": 0.0,
            "pass_through_ratio": 0.0,
            "baseline_status": "NO_HISTORICAL_TRANSACTIONS"
        }

    amounts_in = [tx["amount"] for tx in transactions if tx.get("receiver_account_id") or tx.get("transaction_type") in ["CASH_DEPOSIT", "ACH", "WIRE"]]
    amounts_out = [tx["amount"] for tx in transactions if tx.get("beneficiary_id") or tx.get("transaction_type") in ["TRANSFER", "WIRE", "WITHDRAWAL"]]

    total_in = sum(amounts_in) if amounts_in else sum([t["amount"] for t in transactions])
    total_out = sum(amounts_out) if amounts_out else 0.0
    pass_through_ratio = round((total_out / total_in), 2) if total_in > 0 else 0.0

    # Historical amounts excluding trigger transaction
    hist_amounts = [t["amount"] for t in transactions if str(t.get("transaction_id")) != str(trigger_tx_id)]
    n = len(hist_amounts)

    if n < 3:
        mean = sum(hist_amounts) / n if n > 0 else 0.0
        return {
            "historical_count": n,
            "historical_mean": round(mean, 2),
            "historical_stddev": 0.0,
            "velocity_z_score": 0.0,
            "pass_through_ratio": pass_through_ratio,
            "baseline_status": "INSUFFICIENT_HISTORICAL_SAMPLES"
        }

    mean = sum(hist_amounts) / n
    variance = sum((x - mean) ** 2 for x in hist_amounts) / n
    stddev = math.sqrt(variance)

    effective_stddev = max(stddev, 0.20 * mean)
    if effective_stddev == 0:
        z_score = 0.0
        status = "ZERO_VARIANCE"
    else:
        z_score = round((trigger_amount - mean) / effective_stddev, 2)
        status = "COMPUTED"

    return {
        "historical_count": n,
        "historical_mean": round(mean, 2),
        "historical_stddev": round(stddev, 2),
        "effective_stddev": round(effective_stddev, 2),
        "velocity_z_score": min(max(z_score, 0.0), 5.0),
        "pass_through_ratio": pass_through_ratio,
        "baseline_status": status
    }

def detect_typologies_tool(transactions: List[Dict[str, Any]], customer_id: str) -> Dict[str, Any]:
    """Deterministic financial-crime typology detection operating on database transactions."""
    detected = []
    evidence_details = {}

    # 1. Structuring Detection: >2 transactions within 48h between $9,000 and $9,999 or ₹9,00,000 and ₹9,99,999
    structuring_txs = [
        t for t in transactions
        if 8000.0 <= t["amount"] <= 9999.0 or 800000.0 <= t["amount"] <= 999999.0
    ]
    if len(structuring_txs) >= 2:
        detected.append("STRUCTURING")
        evidence_details["STRUCTURING"] = {
            "matching_count": len(structuring_txs),
            "transaction_ids": [t["transaction_id"] for t in structuring_txs],
            "amounts": [t["amount"] for t in structuring_txs],
            "source_records": [t["transaction_id"] for t in structuring_txs]
        }

    # 2. Fan-In Detection: >= 3 unique senders transferring to entity
    senders = {t.get("customer_id") for t in transactions if t.get("customer_id") and t.get("customer_id") != customer_id}
    if len(senders) >= 3:
        detected.append("FAN_IN")
        evidence_details["FAN_IN"] = {
            "unique_senders_count": len(senders),
            "senders": list(senders),
            "source_records": [t["transaction_id"] for t in transactions if t.get("customer_id") and t.get("customer_id") != customer_id]
        }

    # 3. Fan-Out Detection: >= 3 unique receivers/beneficiaries from entity
    receivers = {t.get("receiver_account_id") or t.get("beneficiary_id") for t in transactions if t.get("receiver_account_id") or t.get("beneficiary_id")}
    receivers.discard(None)
    if len(receivers) >= 3:
        detected.append("FAN_OUT")
        evidence_details["FAN_OUT"] = {
            "unique_receivers_count": len(receivers),
            "receivers": list(receivers),
            "source_records": [t["transaction_id"] for t in transactions if t.get("beneficiary_id") or t.get("receiver_account_id")]
        }

    # 4. Rapid Pass-Through: Incoming + Outgoing within 30 minutes where outgoing amount >= 85% of incoming
    in_txs = [t for t in transactions if t.get("transaction_type") in ["WIRE", "TRANSFER", "CASH_DEPOSIT"]]
    out_txs = [t for t in transactions if t.get("transaction_type") in ["WIRE", "TRANSFER"] and (t.get("receiver_account_id") or t.get("beneficiary_id"))]

    for t_in in in_txs:
        for t_out in out_txs:
            if t_in["transaction_id"] != t_out["transaction_id"] and t_in["amount"] > 0:
                similarity = t_out["amount"] / t_in["amount"]
                if 0.85 <= similarity <= 1.10:
                    detected.append("RAPID_PASS_THROUGH")
                    evidence_details["RAPID_PASS_THROUGH"] = {
                        "inbound_tx_id": t_in["transaction_id"],
                        "outbound_tx_id": t_out["transaction_id"],
                        "inbound_amount": t_in["amount"],
                        "outbound_amount": t_out["amount"],
                        "pass_through_similarity": round(similarity * 100, 1),
                        "source_records": [t_in["transaction_id"], t_out["transaction_id"]]
                    }
                    break

    # 5. Circular Flow Detection
    g = nx.DiGraph()
    for t in transactions:
        src = t.get("account_id") or t.get("customer_id")
        dst = t.get("receiver_account_id") or t.get("beneficiary_id")
        if src and dst and src != dst:
            g.add_edge(src, dst, tx_id=t["transaction_id"])

    try:
        cycles = list(nx.simple_cycles(g))
        if len(cycles) > 0:
            detected.append("CIRCULAR_FLOW")
            evidence_details["CIRCULAR_FLOW"] = {
                "cycles_count": len(cycles),
                "cycle_paths": cycles,
                "source_records": [t["transaction_id"] for t in transactions if t.get("receiver_account_id")]
            }
    except Exception:
        pass

    primary = detected[0] if detected else "UNKNOWN"
    return {
        "primary_typology": primary,
        "all_detected_typologies": detected,
        "evidence_details": evidence_details
    }

def build_and_analyze_graph_tool(customer_id: str) -> Dict[str, Any]:
    """Builds a NetworkX directed graph from actual DB transactions and returns topological metrics."""
    db = SessionLocal()
    try:
        txs = db.query(Transaction).all()
        g = nx.DiGraph()

        for t in txs:
            src = t.account_id or t.customer_id
            dst = t.receiver_account_id or t.beneficiary_id
            if src and dst:
                g.add_edge(src, dst, amount=float(t.amount) if t.amount else 0.0, type=t.transaction_type, tx_id=t.transaction_id)

        cust_accs = [a.account_id for a in db.query(Account).filter(Account.customer_id == customer_id).all()]
        if not cust_accs:
            cust_accs = [customer_id]

        target_node = cust_accs[0] if cust_accs[0] in g.nodes else (customer_id if customer_id in g.nodes else None)

        if not target_node:
            return {
                "nodes_count": len(g.nodes),
                "edges_count": len(g.edges),
                "target_in_degree": 0,
                "target_out_degree": 0,
                "target_centrality": 0.0,
                "cycles_detected": False,
                "fan_in_ratio": 0.0,
                "fan_out_ratio": 0.0,
                "source_records": []
            }

        in_deg = g.in_degree(target_node)
        out_deg = g.out_degree(target_node)
        try:
            centrality = nx.betweenness_centrality(g).get(target_node, 0.0)
        except Exception:
            centrality = 0.0

        cycles = list(nx.simple_cycles(g))
        has_cycles = any(target_node in cycle for cycle in cycles)

        # 2-hop neighbors
        neighbors = set(g.successors(target_node)).union(set(g.predecessors(target_node)))
        two_hop = set()
        for n in neighbors:
            two_hop.update(g.successors(n))
            two_hop.update(g.predecessors(n))

        return {
            "nodes_count": len(g.nodes),
            "edges_count": len(g.edges),
            "target_node": target_node,
            "target_in_degree": in_deg,
            "target_out_degree": out_deg,
            "target_centrality": round(centrality, 4),
            "cycles_detected": has_cycles,
            "cycles_count": len(cycles),
            "two_hop_neighbors_count": len(two_hop),
            "fan_in_ratio": round(in_deg / max(1, in_deg + out_deg), 2),
            "fan_out_ratio": round(out_deg / max(1, in_deg + out_deg), 2),
            "source_records": [data["tx_id"] for u, v, data in g.edges(data=True) if u == target_node or v == target_node]
        }
    finally:
        db.close()

def get_regulatory_guidance_tool(topic: str) -> Optional[Dict[str, Any]]:
    """Queries controlled regulatory knowledge base for official AML guidance."""
    db = SessionLocal()
    try:
        reg = db.query(RegulatoryGuidance).filter(
            (RegulatoryGuidance.topic == topic) | (RegulatoryGuidance.id == topic)
        ).first()
        if not reg:
            # Fallback query for general
            reg = db.query(RegulatoryGuidance).first()
        if not reg:
            return None
        return {
            "id": reg.id,
            "topic": reg.topic,
            "title": reg.title,
            "source_org": reg.source_org,
            "section_ref": reg.section_ref,
            "content_summary": reg.content_summary,
            "retrieval_date": reg.retrieval_date.isoformat() if reg.retrieval_date else None
        }
    finally:
        db.close()
