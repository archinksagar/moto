"""Unit tests for opensearchserverless-supported APIs."""
import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

# See our Development Tips on writing tests for hints on how to write good tests:
# http://docs.getmoto.org/en/latest/docs/contributing/development_tips/tests.html


ENCRYPTION_POLICY="""
        {
            "Rules":[
                {
                    "ResourceType":"collection",
                    "Resource":[
                        "collection/col-foobar",
                        "collection/col-foobar1"
                    ]
                }
            ],
            "AWSOwnedKey":false,
            "KmsARN":"arn:aws:kms:ap-southeast-1:123456789012:key/4c1731d6-5435-ed4d-be13-d53411a7cfbd"
        }
        """
NETWORK_POLICY="""
                [
                    {
                        "Rules":[
                            {
                                "ResourceType":"collection",
                                "Resource":[
                                    "collection/nwk-foobar1",
                                    "collection/nwk-foobar2"
                                ]
                            },
                            {
                                "ResourceType":"collection",
                                "Resource":[
                                    "collection/nwk-foobar3"
                                ]
                            }
                        ],
                        "AllowFromPublic":false,
                        "SourceVPCEs":[
                            "vpce-03cf101d15c3bff53"
                        ]
                    },
                    {
                        "Rules":[
                            {
                                "ResourceType":"collection",
                                "Resource":[
                                    "collection/nwk-foobar4"
                                ]
                            }
                        ],
                        "AllowFromPublic":false,
                        "SourceVPCEs":[
                            "vpce-03cf101d15c3bff53"
                        ]
                    }
                ]
                """
@mock_aws
def test_create_security_policy():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    resp = client.create_security_policy(
            description='Encryption policy for foobar collection',
            name='policy-foobar',
            policy=ENCRYPTION_POLICY,
            type='encryption'
        )
    assert "createdDate" in resp["securityPolicyDetail"]
    assert "description" in resp["securityPolicyDetail"]
    assert "lastModifiedDate" in resp["securityPolicyDetail"]
    assert "name" in resp["securityPolicyDetail"]
    assert "policy" in resp["securityPolicyDetail"]
    assert "policyVersion" in resp["securityPolicyDetail"]
    assert "type" in resp["securityPolicyDetail"]

@mock_aws
def test_create_security_policy_invalid_type():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    with pytest.raises(ClientError) as exc:
        client.create_security_policy(
            name='policy-foobar',
            policy=ENCRYPTION_POLICY,
            type='fake type'
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "ValidationException"

@mock_aws
def test_create_security_policy_same_token():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    client.create_security_policy(
            clientToken="token1",
            name='policy-foobar',
            policy=ENCRYPTION_POLICY,
            type='encryption'
        )
    with pytest.raises(ClientError) as exc:
        client.create_security_policy(
            clientToken="token1",
            name='policy-foobar2',
            policy=ENCRYPTION_POLICY,
            type='encryption'
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "ConflictException"

@mock_aws
def test_create_security_policy_same_name_and_type():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    client.create_security_policy(
            name='policy-foobar',
            policy=ENCRYPTION_POLICY,
            type='encryption'
        )
    with pytest.raises(ClientError) as exc:
        client.create_security_policy(
            name='policy-foobar',
            policy=ENCRYPTION_POLICY,
            type='encryption'
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "ConflictException"


@mock_aws
def test_get_security_policy():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    client.create_security_policy(
        description='Encryption policy for foobar collection',
        name='policy-foobar',
        policy=ENCRYPTION_POLICY,
        type='encryption'
    )
    resp = client.get_security_policy(
        name='policy-foobar',
        type='encryption'
    )
    sp_detail = resp["securityPolicyDetail"]
    assert "createdDate" in sp_detail
    assert "description" in sp_detail
    assert "lastModifiedDate" in sp_detail
    assert "name" in sp_detail
    assert sp_detail["name"] == "policy-foobar"
    assert "policy" in sp_detail
    assert "policyVersion" in sp_detail
    assert "type" in sp_detail

@mock_aws
def test_get_security_policy_invalid_name():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    client.create_security_policy(
            name='policy-foo',
            policy=ENCRYPTION_POLICY,
            type='encryption'
        )
    with pytest.raises(ClientError) as exc:
        client.get_security_policy(
            name='policy-bar',
            type='encryption'
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "ResourceNotFoundException"

@mock_aws
def test_list_security_policies():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    network_policy = """
                [{
                    "Rules":[
                        {
                            "ResourceType":"collection",
                            "Resource":[
                                "collection/nwk-foobar5"
                            ]
                        }
                    ],
                    "AllowFromPublic":false,
                    "SourceVPCEs":[
                        "vpce-03cf101d15c3bff53"
                    ]
                }]
                """
    client.create_security_policy(
            name='policy-foobar1',
            policy=NETWORK_POLICY,
            type='network'
        )
    client.create_security_policy(
            name='policy-foobar2',
            policy=network_policy,
            type='network'
        )
    resp = client.list_security_policies(
        type="network"
    )
    assert len(resp["securityPolicySummaries"]) == 2

@mock_aws
def test_list_security_policies_with_resource():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    network_policy = """
                [{
                    "Rules":[
                        {
                            "ResourceType":"collection",
                            "Resource":[
                                "collection/nwk-foobar5"
                            ]
                        }
                    ],
                    "AllowFromPublic":false,
                    "SourceVPCEs":[
                        "vpce-03cf101d15c3bff53"
                    ]
                }]
                """
    client.create_security_policy(
            name='policy-foobar1',
            policy=NETWORK_POLICY,
            type='network'
        )
    client.create_security_policy(
            name='policy-foobar2',
            policy=network_policy,
            type='network'
        )
    resp = client.list_security_policies(
        resource = [
            "collection/nwk-foobar4",
            "collection/nwk-foobar5"
        ],
        type="network"
    )
    assert len(resp["securityPolicySummaries"]) == 2
    assert resp["securityPolicySummaries"][0]["name"] == "policy-foobar1"
    assert resp["securityPolicySummaries"][1]["name"] == "policy-foobar2"

@mock_aws
def test_update_security_policy():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    client.create_security_policy(
        name='policy-foobar1',
        policy=ENCRYPTION_POLICY,
        type='encryption'
    )
    resp_get = client.get_security_policy(
        name='policy-foobar1',
        type='encryption'
    )
    policy_version = resp_get["securityPolicyDetail"]["policyVersion"]
    encryption_policy="""
        {
            "Rules":[
                {
                    "ResourceType":"collection",
                    "Resource":[
                        "collection/col-foobar1"
                    ]
                }
            ],
            "AWSOwnedKey":false,
            "KmsARN":"arn:aws:kms:ap-southeast-1:012345678910:key/ca87b5af-88cd-4f06-82d2-2d6b1589aff9"
        }
        """
    resp = client.update_security_policy(
        clientToken='abc124',
        description='Encryption policy for foobar collection',
        name='policy-foobar1',
        policy=encryption_policy,
        policyVersion=policy_version,
        type='encryption'
    )
    sp_detail = resp["securityPolicyDetail"]
    assert sp_detail["policy"]["Rules"][0]["Resource"][0] == "collection/col-foobar1"
    assert "createdDate" in sp_detail
    assert "description" in sp_detail
    assert "lastModifiedDate" in sp_detail
    assert "name" in sp_detail
    assert "policy" in sp_detail
    assert "policyVersion" in sp_detail
    assert "type" in sp_detail

@mock_aws
def test_update_security_policy_same_token():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    client.create_security_policy(
            name='policy-foobar',
            policy=ENCRYPTION_POLICY,
            type='encryption'
        )
    resp_get = client.get_security_policy(
        name='policy-foobar',
        type='encryption'
    )
    client.update_security_policy(
        clientToken='token1',
        name='policy-foobar',
        policy=ENCRYPTION_POLICY,
        policyVersion=resp_get["securityPolicyDetail"]["policyVersion"],
        type='encryption'
    )
    with pytest.raises(ClientError) as exc:
        client.update_security_policy(
            clientToken='token1',
            name='policy-foobar',
            policy=ENCRYPTION_POLICY,
            policyVersion=resp_get["securityPolicyDetail"]["policyVersion"],
            type='encryption'
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "ConflictException"

@mock_aws
def test_update_security_policy_invalid_policy_version():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    client.create_security_policy(
            name='policy-foobar',
            policy=ENCRYPTION_POLICY,
            type='encryption'
        )
    with pytest.raises(ClientError) as exc:
        client.update_security_policy(
            name='policy-foobar',
            policy=ENCRYPTION_POLICY,
            policyVersion="cjChd5QGsCepf8oibj0C",
            type='encryption'
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "ValidationException"

@mock_aws
def test_update_security_policy_invalid_name():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    with pytest.raises(ClientError) as exc:
        client.update_security_policy(
            name='policy-foobar',
            policy=ENCRYPTION_POLICY,
            policyVersion="cjChd5QGsCepf8oibj0C",
            type='encryption'
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "ResourceNotFoundException"

@mock_aws
def test_create_collection():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    client.create_security_policy(
        name='policy-foobar',
        policy=ENCRYPTION_POLICY,
        type='encryption'
    )
    resp = client.create_collection(
        clientToken='abc111',
        description='Collection for foobar',
        name='col-foobar',
        standbyReplicas='ENABLED',
        tags=[
            {
                'key': 'key1',
                'value': 'value1'
            },
        ],
        type='SEARCH'
    )
    collection_detail = resp["createCollectionDetail"]
    assert 'arn' in collection_detail
    assert 'createdDate' in collection_detail
    assert 'description' in collection_detail
    assert 'id' in collection_detail
    assert 'kmsKeyArn' in collection_detail
    assert 'lastModifiedDate' in collection_detail
    assert 'name' in collection_detail
    assert 'standbyReplicas' in collection_detail
    assert 'status' in collection_detail
    assert 'type' in collection_detail

@mock_aws
def test_create_collection_same_token():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    client.create_security_policy(
        name='policy-foobar',
        policy=ENCRYPTION_POLICY,
        type='encryption'
    )
    client.create_collection(
        clientToken='token1',
        name='col-foobar'
    )
    with pytest.raises(ClientError) as exc:
        client.create_collection(
            clientToken='token1',
            name='col-foobar'
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "ConflictException"

@mock_aws
def test_create_collection_with_no_policy():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    with pytest.raises(ClientError) as exc:
        client.create_collection(
            clientToken='token1',
            name='col-foobar'
        )
    err = exc.value.response["Error"]
    assert err["Code"] == "ValidationException"


@mock_aws
def test_list_collections():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    client.create_security_policy(
        name='policy-foobar',
        policy=ENCRYPTION_POLICY,
        type='encryption'
    )
    client.create_collection(
        name='col-foobar',
        type='SEARCH'
    )
    client.create_collection(
        name='col-foobar1',
        type='TIMESERIES'
    )
    resp = client.list_collections()
    assert len(resp["collectionSummaries"]) == 2
    collection_summary = resp["collectionSummaries"][0]
    assert "arn" in collection_summary
    assert "id" in collection_summary
    assert "name" in collection_summary
    assert "status" in collection_summary

@mock_aws
def test_list_collections_with_name():
    client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
    client.create_security_policy(
        name='policy-foobar',
        policy=ENCRYPTION_POLICY,
        type='encryption'
    )
    client.create_collection(
        name='col-foobar',
        type='SEARCH'
    )
    client.create_collection(
        name='col-foobar1',
        type='TIMESERIES'
    )
    resp = client.list_collections(
        collectionFilters={
            'name': 'col-foobar'
        },
    )
    assert len(resp["collectionSummaries"]) == 1
    assert resp["collectionSummaries"][0]["name"] == 'col-foobar'

# @mock_aws
# def test_create_vpc_endpoint():
#     client = boto3.client("opensearchserverless", region_name="eu-west-1")
#     resp = client.create_vpc_endpoint()

#     raise Exception("NotYetImplemented")







# # @mock_aws
# # def test_tag_resource():
# #     client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
# #     resp = client.tag_resource()

# #     raise Exception("NotYetImplemented")


# # @mock_aws
# # def test_untag_resource():
# #     client = boto3.client("opensearchserverless", region_name="us-east-2")
# #     resp = client.untag_resource()

# #     raise Exception("NotYetImplemented")





# # @mock_aws
# # def test_update_collection():
# #     client = boto3.client("opensearchserverless", region_name="eu-west-1")
# #     resp = client.update_collection()

# #     raise Exception("NotYetImplemented")


# # @mock_aws
# # def test_delete_collection():
# #     client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
# #     resp = client.delete_collection()

# #     raise Exception("NotYetImplemented")


# # @mock_aws
# # def test_delete_security_policy():
# #     client = boto3.client("opensearchserverless", region_name="eu-west-1")
# #     resp = client.delete_security_policy()

# #     raise Exception("NotYetImplemented")


# # @mock_aws
# # def test_delete_vpc_endpoint():
# #     client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
# #     resp = client.delete_vpc_endpoint()

# #     raise Exception("NotYetImplemented")


# # @mock_aws
# # def test_update_vpc_endpoint():
# #     client = boto3.client("opensearchserverless", region_name="ap-southeast-1")
# #     resp = client.update_vpc_endpoint()

# #     raise Exception("NotYetImplemented")

