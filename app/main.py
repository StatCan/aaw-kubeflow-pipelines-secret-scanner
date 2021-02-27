#!/bin/python3

import os

import kfp
from utils.secret_scan import traversal, detect_secret
from utils.get_pipelines import get_pipelines, format_pipeline
from utils.es_funcs import get_es_client, upload_to_es
import sys

ES_INDEX_NAME = os.getenv(
    'ES_INDEX_NAME',
    default='kubeflow-pipeline-secrets'
)

def scan_all(documents, workflow_key='yaml_data'):
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


    The final result is a flattened version of all of this,
    which is elastic-search friendly.
    """
    counts = { k: 0 for k in ("docs", "keys", "secrets", "entropy") }
    for doc in documents:
        counts['docs'] += 1
        for (path, key) in traversal(doc[workflow_key]):
            counts['keys'] += 1
            (severity, desc) = detect_secret(path, key)
            if severity == 1:
                counts['entropy'] += 1
            elif severity >= 2:
                counts['secrets'] += 1

            flattened = {
                **format_pipeline(**doc, lazy=True),
                **{
                    'secret_' + k: v
                    for (k,v) in desc.items()
                },
                "severity": severity,
            }
            # Too much info.
            #del flattened['yaml_data']
            yield flattened

    print("""
    Summary
    =======

        Pipeline Versions Scanned: {docs}
        Keys Scanned: {keys}

    Results
    =======

        Potential Secrets: {entropy}
        LIKELY SECRETS: {secrets}

    """.format(**counts), file=sys.stderr)

if __name__ == '__main__':

    # Wait for istio
    import time
    time.sleep(15)

    # Go!
    es = get_es_client()

    def log_whats_needed(docs):
        """
        We only will attach the yamls if there's a detected secret.
        Otherwise it's kinda overkill.

        NOTE: The incoming `yaml_data` is a thunk, not yaml yet.
        """
        for doc in docs:
            if doc['severity'] > 0:
                doc['yaml_data'] = doc['yaml_data']()
            else:
                del doc['yaml_data']
            yield doc

    exposed_secrets = log_whats_needed(scan_all(get_pipelines(kfp.Client())))

    print("Starting upload...")
    upload_to_es(es, exposed_secrets, ES_INDEX_NAME)
    print("Done.")
