import yaml
import os

def test_openenv_yaml_exists():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "openenv.yaml")
    assert os.path.exists(path)

def test_openenv_yaml_valid_yaml():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "openenv.yaml")
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    assert data["name"] == "MedTriage-Env"
    assert "tasks" in data
    assert len(data["tasks"]) == 3
