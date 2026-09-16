import pytest
from trading_lab.dashboard import DashboardGenerator
from trading_lab.services import LabService
from trading_lab.store import SqliteStore


@pytest.fixture
def store(tmp_path):
    db_path = tmp_path / "test.db"
    store = SqliteStore(db_path)
    from trading_lab.migrations import apply_migrations
    with store.connection() as conn:
        apply_migrations(conn)
    return store


@pytest.fixture
def lab(store):
    lab_service = LabService(store)
    lab_service.initialize()
    return lab_service


def test_dashboard_generation(lab):
    dashboard = DashboardGenerator(lab)
    html = dashboard.generate_html()
    
    # Assert critical read-only pieces are present
    assert "<title>Trading Lab Dashboard</title>" in html
    assert "System Status" in html
    assert "Virtual Balance" in html
    assert "Recent Trades" in html
    assert "Recent Audit Events" in html
    assert "LAB_INITIALIZED" in html  # from initialize()

    # Ensure no forms/mutations exist in the dashboard layout
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
