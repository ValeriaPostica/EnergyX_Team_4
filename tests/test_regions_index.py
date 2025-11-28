import json
import os


def test_regions_index_has_expected_structure():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    path = os.path.join(root, 'backend', 'data', 'model_data', 'regions_index.json')
    assert os.path.exists(path)

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert isinstance(data, dict)
    assert 'regions' in data
    assert isinstance(data['regions'], list)
    assert len(data['regions']) > 0
    assert 'Chisinau' in data['regions']
