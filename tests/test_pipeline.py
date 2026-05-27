import os

def test_pipeline_json_exists():

    assert os.path.exists(
        "pipelines/pipeline_spec.json"
    )