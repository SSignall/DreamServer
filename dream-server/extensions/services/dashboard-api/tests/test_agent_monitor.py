"""Tests for agent_monitor.py — throughput metrics and data classes."""

from datetime import datetime, timedelta

from agent_monitor import ThroughputMetrics, AgentMetrics, ClusterStatus


class TestThroughputMetrics:

    def test_empty_stats(self):
        tm = ThroughputMetrics()
        stats = tm.get_stats()
        assert stats["current"] == 0
        assert stats["average"] == 0
        assert stats["peak"] == 0
        assert stats["history"] == []

    def test_add_sample_updates_stats(self):
        tm = ThroughputMetrics()
        tm.add_sample(10.0)
        tm.add_sample(20.0)
        tm.add_sample(30.0)

        stats = tm.get_stats()
        assert stats["current"] == 30.0
        assert stats["average"] == 20.0
        assert stats["peak"] == 30.0
        assert len(stats["history"]) == 3

    def test_prunes_old_data(self):
        tm = ThroughputMetrics(history_minutes=5)

        # Insert an old data point by manipulating the list directly
        old_time = (datetime.now() - timedelta(minutes=10)).isoformat()
        tm.data_points.append({"timestamp": old_time, "tokens_per_sec": 99.0})

        # Adding a new sample triggers pruning
        tm.add_sample(10.0)

        assert len(tm.data_points) == 1
        assert tm.data_points[0]["tokens_per_sec"] == 10.0

    def test_history_capped_at_30_points(self):
        tm = ThroughputMetrics()
        for i in range(50):
            tm.add_sample(float(i))

        stats = tm.get_stats()
        assert len(stats["history"]) == 30


class TestAgentMetrics:

    def test_to_dict_keys(self):
        am = AgentMetrics()
        d = am.to_dict()
        assert set(d.keys()) == {
            "session_count", "tokens_per_second",
            "error_rate_1h", "queue_depth", "last_update",
        }

    def test_to_dict_types(self):
        am = AgentMetrics()
        d = am.to_dict()
        assert isinstance(d["session_count"], int)
        assert isinstance(d["tokens_per_second"], float)
        assert isinstance(d["last_update"], str)


class TestClusterStatus:

    def test_to_dict_defaults(self):
        cs = ClusterStatus()
        d = cs.to_dict()
        assert d["nodes"] == []
        assert d["total_gpus"] == 0
        assert d["active_gpus"] == 0
        assert d["failover_ready"] is False
