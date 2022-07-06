AWS Codepipeline execution status in GitHub
================

This repository contains a CloudFormation template to create a set of resources that allows AWS Codepipeline execution statuses to be shown in GitHub repository

## Prerequisites

- AWS Codepipeline with `source` action configured to track a GitHub repository
- GitHub user with authentication token that is allowed to update build statuses for commits
- AWS SSM parameter named `githubAuthToken` in the same region as the Codepipeline. The parameter should contain GitHub user authentication token

## Resources

[CloudFormation template](./resources.yaml) defines the following resources:
- AWS SNS Topic for Codepipeline status changes notifications
- AWS Customer managed KMS Key to encrypt the SNS topic
- Policy that allows `codestar-notifications` service to push notifications into the SNS topic
- AWS IAM Role for Lambda function with a policy that allows Lambda function to create logs and get AWS Codepipeline execution statuses
- AWS CodeStar notification rule to push notifications into the SNS topic
- AWS Lambda permission that allows SNS service to invoke Lambda functions
- AWS Lambda function to update build statuses in GitHub via POST API requests

As a parameter this template uses AWS Codepipeline name

AWS Lambda function is written in Python. The code is included into CloudFormation template. Also it is duplicated in a [separate file](./function.py)
