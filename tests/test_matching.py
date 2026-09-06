from types import SimpleNamespace
from backend.matching import score_pair

def test_same_item_scores_above_unrelated():
    lost=SimpleNamespace(title="Black HP laptop",description="Black HP laptop with scratch",location="Library",category="Electronics")
    found=SimpleNamespace(title="HP black laptop",description="Black HP laptop found with scratch",location="Library",category="Electronics")
    unrelated=SimpleNamespace(title="Blue umbrella",description="Blue umbrella",location="Canteen",category="Accessories")
    assert score_pair(lost,found) > score_pair(lost,unrelated)
