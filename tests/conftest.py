"""Record collection independently of passing assertions for the CI report gate."""
import json
from pathlib import Path


def pytest_collection_finish(session):
    path = Path(session.config.rootpath) / 'reports' / 'collected-tests.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(item.nodeid for item in session.items)), encoding='utf-8')
