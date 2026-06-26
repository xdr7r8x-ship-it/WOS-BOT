import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (
    init_database,
    generate_code_hash,
    add_retry_job,
    get_due_retry_jobs,
    update_retry_job,
    get_retry_job_count,
    DATABASE_PATH,
    now_iso,
)
from datetime import datetime, timedelta


class TestRetryJobs:
    @pytest.fixture(autouse=True)
    def setup_database(self):
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()
        init_database()
        yield
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()

    def test_add_retry_job(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        result = add_retry_job("123", code_hash, "111111", "NETWORK_ERROR")
        assert result is True

    def test_get_due_retry_jobs_empty(self):
        jobs = get_due_retry_jobs()
        assert len(jobs) == 0

    def test_get_due_retry_jobs(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        past_time = (datetime.utcnow() - timedelta(seconds=10)).isoformat()
        add_retry_job("123", code_hash, "111111", "NETWORK_ERROR", next_retry_at=past_time)
        jobs = get_due_retry_jobs()
        assert len(jobs) == 1

    def test_update_retry_job_status(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        past_time = (datetime.utcnow() - timedelta(seconds=10)).isoformat()
        add_retry_job("123", code_hash, "111111", "NETWORK_ERROR", next_retry_at=past_time)
        jobs = get_due_retry_jobs()
        job_id = jobs[0]["id"]
        update_retry_job(job_id, "DONE")
        jobs = get_due_retry_jobs()
        assert len(jobs) == 0

    def test_retry_job_count(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        add_retry_job("123", code_hash, "111111", "NETWORK_ERROR")
        count = get_retry_job_count()
        assert count == 1

    def test_retry_job_unique_constraint(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        add_retry_job("123", code_hash, "111111", "NETWORK_ERROR")
        result = add_retry_job("123", code_hash, "111111", "NETWORK_ERROR")
        assert result is False
