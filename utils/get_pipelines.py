#!/bin/python3

import kfp
import yaml
import json

def get_pipelines(client):
    """ Get all pipelines. Returns

    Iterator[dict], with schema {
        "pipeline": pipeline,
        "version" : version,
        "yaml"    : get_yaml(version)
    }
    """

    def pipeline_groups():
        """ Get all 'top-level' pipelines, e.g. groups of pipeline versions """
        pager = client.list_pipelines('', page_size=50, sort_by='')
        yield from pager.pipelines

        while pager.next_page_token is not None:
            pager = client.list_pipelines(pager.next_page_token, page_size=50, sort_by='')
            yield from pager.pipelines

    def pipeline_versions(pipeline):
        """ Get all versions of a specific pipeline """
        versions = client.list_pipeline_versions(pipeline.id, page_size=50)
        if versions.versions is not None:
            yield from versions.versions
        while versions.next_page_token is not None:
            versions = client.list_pipeline_versions(
                pipeline.id,
                page_token=versions.next_page_token,
                page_size=50
            )
            yield from versions.versions

    def get_yaml(version):
        """ Get the workflow from a pipeline version """
        template = client.pipelines.get_pipeline_version_template(version.id)
        return yaml.load(template.template, Loader=yaml.BaseLoader)

    # Finally yield stuff
    for pipeline in pipeline_groups():
        for version in pipeline_versions(pipeline):
            yield {
                "pipeline" : pipeline,
                "version"  : version,
                "yaml_data": get_yaml(version)
            }


def format_pipeline(pipeline: dict = {}, version: dict = {}, yaml_data: dict = {}, lazy=False):
    """ Simplify the json """
    d =  {
        "pipeline_name": pipeline.name,
        "pipeline_id": pipeline.id,
        "pipeline_description": pipeline.description,
        "pipeline_created_at": pipeline.created_at,
        "version_name": version.name,
        "version_id": version.id,
        "version_created_at": version.created_at,
    }

    if lazy:
        # thunk it up
        d['yaml_data'] = lambda: yaml.dump(yaml_data)
    else:
        d['yaml_data'] = yaml.dump(yaml_data)

    return d


if __name__ == '__main__':
    c = kfp.Client()
    for pipeline in get_pipelines(c):
        print(pipeline)
        print()
