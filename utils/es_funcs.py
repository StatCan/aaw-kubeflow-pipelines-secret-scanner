#!/bin/python3

import os
import getpass
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

def get_es_client(ES_HOST=None, ES_USER=None, ES_PASS=None):
    if ES_HOST is None:
        ES_HOST = os.getenv(
            "ES_HOST",
            default="http://daaas-es-http.daaas.svc.cluster.local:9200"
        )

    if ES_USER is None:
        ES_USER = os.getenv(
            "ES_USER",
            default=getpass.getpass("ElasticSearch User: ")
        )


    if ES_PASS is None:
        ES_PASS = os.getenv(
            "ES_PASS",
            default=getpass.getpass("ElasticSearch Pass: ")
        )

    return Elasticsearch(
        hosts=[ES_HOST],
        http_auth=(ES_USER, ES_PASS)
    )



def upload_to_es(es, documents, index):
    """ Upload documents to a specific elasticsearch index """
    # Create if not exists
    es.indices.create(index=index, ignore=400)

    # Add the index into the document stream
    def indexed():
        for doc in documents:
            doc['_index'] = index
            yield doc

    for success, info in streaming_bulk(es, indexed(), max_retries=2):
        if not success:
            print('A document failed:', info)


if __name__ == '__main__':
    # Just test the connection
    es = get_es_client()
    print(json.dumps(es.indices.get_alias("*"), indent=2))
