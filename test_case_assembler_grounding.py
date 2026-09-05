import json
from unittest.mock import patch
from app.agents.nodes.case_assembler import case_assembler_node, SYSTEM_PROMPT

def test_case_assembler_grounding_constraints():
    print("=" * 70)
    print(" 🧪 TESTING CASE ASSEMBLER PROMPT GROUNDING & PAYLOAD PRUNING")
    print("=" * 70)

    # 1. Verify Grounding Instructions
    assert "Use ONLY facts present in the supplied InvestigationState evidence" in SYSTEM_PROMPT
    assert "Do NOT invent dates, locations, transaction purposes" in SYSTEM_PROMPT
    assert "Not available in investigation evidence." in SYSTEM_PROMPT
    print(" -> System Prompt Grounding Instructions Verified!")

    # 2. Verify Payload Attributes & Raw Collection Exclusion
    sample_state = {
        "case_id": "CASE_TEST_001",
        "alert_id": "ALERT_TEST_001",
        "alert_type": "LARGE_TRANSACTION",
        "trigger_evidence": {
            "customer": {"occupation": "Trader", "risk_level": "LOW", "account_age_days": 180},
            "accounts": [{"id": "ACC1"}],
            "beneficiaries": [{"id": "BEN1"}],
            "devices": [{"id": "DEV1"}]
        },
        "behavioral_metrics": {"velocity_z_score": 2.5},
        "graph_metrics": {"multi_beneficiary_flag": 1},
        "kyc_notes": "LOW risk profile",
        "typology_classification": "LAYERING",
        "typology_rationale": "High velocity multi-account transfers",
        "final_risk_score": 65.0,
        "decision": "REVIEW",
        "loop_count": 2
    }

    with patch("app.agents.nodes.case_assembler.LLMClient") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.generate.return_value = "## Markdown Dossier Output"

        res = case_assembler_node(sample_state)

        args, _ = mock_instance.generate.call_args
        sys_p, user_p = args[0], args[1]

        # Verify exclusion of raw trigger_evidence collections
        assert "accounts" not in user_p, "Raw 'accounts' collection was serialized into dossier payload!"
        assert "beneficiaries" not in user_p, "Raw 'beneficiaries' collection was serialized into dossier payload!"
        assert "devices" not in user_p, "Raw 'devices' collection was serialized into dossier payload!"
        print(" -> Payload Pruning Test:       Passed! Raw trigger_evidence collections excluded.")

    print("=" * 70)
    print("✅ ALL CASE ASSEMBLER GROUNDING & PAYLOAD PRUNING TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    test_case_assembler_grounding_constraints()
