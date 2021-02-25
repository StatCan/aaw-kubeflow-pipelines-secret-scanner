#!/bin/python3

import os

import kfp
from utils.secret_scan import traversal, detect_secret
from utils.get_pipelines import get_pipelines, format_pipeline
from utils.es_funcs import get_es_client, upload_to_es

ES_INDEX_NAME = 'kubeflow-pipeline-secrets'

def scan_all(documents, workflow_key='yaml'):
    """
    SCHEMAS:

    documents :: Generator of these
    {
        "pipeline": pipeline,
        "version" : version,
        "yaml"    : get_yaml(version) # <- This is a dict
    }

    format_pipeline renders the `yaml` field as a formatted yaml string.
    It also removes extraneous fields from pipeline and version.

    {
        "pipeline": {
            "name": pipeline.name,
            "id": pipeline.id,
            "description": pipeline.description,
            "created_at": pipeline.created_at,
        },
        "version": {
            "name": version.name,
            "id": version.id,
            "created_at": version.created_at,
        },
        "yaml": yaml.dump(yaml_data),
    }

    We obviously add the secret infor to this. The secret
    description includes:
    {
        "key": human_path,
        'violation': f'Exceeded max entropy {h} > {max_entropy}',
        'entropy': h,
        'value': mask(value)
    }
    """
    for doc in documents:
        for (path, key) in traversal(doc[workflow_key]):
            (severity, desc) = detect_secret(path, key)
            yield {
                **format_pipeline(**doc),
                "secret": {
                     **desc,
                    "severity": severity,
                }
            }



if __name__ == '__main__':
    exposed_secrets = scan_all(get_pipelines(kfp.Client()))
    #es = get_es_client()
