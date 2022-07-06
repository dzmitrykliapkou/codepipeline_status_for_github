from __future__ import print_function

import json
import boto3
import os
import urllib3
from base64 import b64encode

codepipeline_client = boto3.client('codepipeline')
integration_token = os.environ['INTEGRATION_AUTH_TOKEN']

region = os.environ['AWS_REGION']

def lambda_handler(event, context):
    message = event['Records'][0]['Sns']['Message']
    data = json.loads(message)

    #Push only notifications about Pipeline Execution State Changes
    if data.get("detailType") != "CodePipeline Pipeline Execution State Change":
        return()

    response = codepipeline_client.get_pipeline_execution(
        pipelineName=data['detail']['pipeline'],
        pipelineExecutionId=data['detail']['execution-id']
    )

    short_commit_od = response['pipelineExecution']['artifactRevisions'][0]['revisionId'][0:7]
    commit_id = response['pipelineExecution']['artifactRevisions'][0]['revisionId']
    revision_url = response['pipelineExecution']['artifactRevisions'][0]['revisionUrl']

    if "FullRepositoryId=" in revision_url:
        repo_id = revision_url.split("FullRepositoryId=")[1].split("&")[0]
    else: #gitbub v1 integration
        repo_id = revision_url.split("/")[3] + "/" + revision_url.split("/")[4]

    if data['detail']['state'].upper() in [ "SUCCEEDED" ]:
        state = "success"
    elif data['detail']['state'].upper() in [ "STARTED", "STOPPING", "STOPPED", "SUPERSEDED" ]:
        state = "pending"
    else:
        state = "error"

    url = "https://api.github.com/repos/" + repo_id + "/statuses/" + commit_id

    build_status={}
    build_status['state'] = state
    if data['detail']['state'].upper() in ["FAILED"]:
        build_status['context'] = "CodePipeline: {}".format(data['additionalAttributes']['failedActions'][0]['action'])
    else:
        build_status['context'] = "CodePipeline"
    build_status['description'] = data['detail']['pipeline']
    build_status['target_url'] = "https://" + region + ".console.aws.amazon.com/codesuite/codepipeline/pipelines/" + data['detail']['pipeline'] + "/executions/" + data['detail']['execution-id'] + "?region="+region

    http = urllib3.PoolManager()
    r = http.request('POST', url,
    headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'Curl/0.1', 'Authorization' : 'token %s' %  integration_token},
    body=json.dumps(build_status).encode('utf-8')
    )

    return message
