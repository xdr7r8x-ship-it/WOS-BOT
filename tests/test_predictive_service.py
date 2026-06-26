import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestPredictiveService:
    def test_predictive_service_import(self):
        from src.services.predictive_service import predictive_service
        assert predictive_service is not None

    def test_predictive_service_has_methods(self):
        from src.services.predictive_service import predictive_service
        assert hasattr(predictive_service, 'start')
        assert hasattr(predictive_service, 'stop')
        assert hasattr(predictive_service, 'scan')
        assert hasattr(predictive_service, 'get_predictions')
