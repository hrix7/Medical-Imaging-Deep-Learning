from pathlib import Path
import re

def test_daily_checks_are_read_only_and_actions_are_pinned():
    text=Path('.github/workflows/validate.yml').read_text()
    assert 'permissions:\n  contents: read' in text
    assert 'persist-credentials: false' in text
    assert 'pull_request:' in text and 'schedule:' in text
    assert 'pull_request_target' not in text and 'write' not in text and 'secrets.' not in text
    actions=re.findall(r'uses:\s+(\S+)',text)
    assert len(actions)==3
    assert all(re.fullmatch(r'actions/[a-z-]+@[0-9a-f]{40}',a) for a in actions)
    assert 'python -m pytest -q' in text and 'cmp outputs/' in text
