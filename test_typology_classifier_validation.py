import json
from unittest.mock import patch
from app.agents.nodes.typology_classifier import typology_classifier_node

def test_typology_classifier_validation_cases():
    print("=" * 70)
    print(" 🧪 TESTING TYPOLOGY CLASSIFIER VALIDATION & PAYLOAD PRUNING")
    print("=" * 70)

    base_state = {
        "alert_type": "LARGE_TRANSACTION",
        "trigger_evidence": {
            "transaction": {"amount": 50000.0, "transaction_type": "TRANSFER"},
            "customer": {"occupation": "Trader", "risk_level": "LOW", "account_age_days": 180},
            "accounts": [{"id": "ACC1"}, {"id": "ACC2"}],
            "beneficiaries": [{"id": "BEN1"}, {"id": "BEN2"}],
            "devices": [{"id": "DEV1"}]
        },
        "behavioral_metrics": {"velocity_z_score": 4.5, "pass_through_ratio": 0.8},
        "graph_metrics": {"multi_beneficiary_flag": 1},
        "kyc_notes": "Clean customer"
    }

    # Case 1: Valid Typology Output & Payload Pruning Check
    with patch("app.agents.nodes.typology_classifier.LLMClient") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.generate.return_value = '{"typology": "STRUCTURING", "rationale": "Consecutive deposits under threshold."}'
        
        state = dict(base_state)
        res = typology_classifier_node(state)
        
        # Verify prompt payload pruning
        args, _ = mock_instance.generate.call_args
        sys_p, user_p = args[0], args[1]
        
        assert "accounts" not in user_p, "Raw 'accounts' collection was serialized into LLM payload!"
        assert "beneficiaries" not in user_p, "Raw 'beneficiaries' collection was serialized into LLM payload!"
        assert "devices" not in user_p, "Raw 'devices' collection was serialized into LLM payload!"
        print(" -> Payload Pruning Test:       Passed! Raw collections (accounts, beneficiaries, devices) excluded.")
        
        print(f" -> Valid Typology Test:       Classification = {res['typology_classification']}")
        assert res["typology_classification"] == "STRUCTURING", "Failed to accept valid typology!"

    # Case 2: Malformed JSON Response
    with patch("app.agents.nodes.typology_classifier.LLMClient") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.generate.return_value = '{"typology": "LAYERING", malformed json syntax}'
        
        state = dict(base_state)
        res = typology_classifier_node(state)
        print(f" -> Malformed JSON Test:       Classification = {res['typology_classification']}")
        assert res["typology_classification"] == "UNKNOWN"

    # Case 3: Invalid Typology Value
    with patch("app.agents.nodes.typology_classifier.LLMClient") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.generate.return_value = '{"typology": "INVALID_TYPOLOGY_SCHEME"}'
        
        state = dict(base_state)
        res = typology_classifier_node(state)
        print(f" -> Invalid Typology Test:     Classification = {res['typology_classification']}")
        assert res["typology_classification"] == "UNKNOWN"

    # Case 4: LLM Exception
    with patch("app.agents.nodes.typology_classifier.LLMClient") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.generate.side_effect = RuntimeError("API Rate Limit")
        
        state = dict(base_state)
        res = typology_classifier_node(state)
        print(f" -> LLM Exception Test:        Classification = {res['typology_classification']}")
        assert res["typology_classification"] == "UNKNOWN"

    print("=" * 70)
    print("✅ ALL TYPOLOGY CLASSIFIER VALIDATION & PAYLOAD PRUNING TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    test_typology_classifier_validation_cases()
