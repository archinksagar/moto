"""OpenSearchServiceServerlessBackend class with methods for supported APIs."""

from typing import Any, Dict, List, Optional, Tuple
from moto.core.base_backend import BaseBackend, BackendDict
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random
from .exceptions import ConflictException, ValidationException, ResourceNotFoundException
import json


class SecurityPolicy(BaseModel):
    def __init__(
        self,
        client_token,
        description,
        name,
        policy: str,
        type,
    ):
        self.client_token = client_token
        self.description = description
        self.name = name
        self.type = type
        self.created_date = int(unix_time() * 1000)
        # update policy # current date default
        self.last_modified_date = int(unix_time() * 1000)
        self.policy = json.loads(policy)
        self.policy_version = mock_random.get_random_string(20)
        if type == "encryption":
            self.resources = [res for rule in self.policy["Rules"]
                              for res in rule["Resource"]]
        else: 
            self.resources = [res for p in self.policy for rule in p["Rules"]
                            for res in rule["Resource"]]
    def to_dict(self) -> Dict[str, Any]:
        dct = {
            "createdDate": self.created_date,
            "description": self.description,
            "lastModifiedDate": self.last_modified_date,
            "name": self.name,
            "policy": self.policy,
            "policyVersion": self.policy_version,
            "type": self.type,
        }
        return {k: v for k, v in dct.items() if v}

    def to_dict_list(self) -> Dict[str, Any]:
        dct = self.to_dict()
        dct.pop("policy")
        return {k: v for k, v in dct.items() if v}


class Collection(BaseModel):
    def __init__(
        self,
        client_token,
        description,
        name,
        standby_replicas,
        tags,
        type,
        policy,
        region,
        account_id
    ):
        self.client_token = client_token
        self.description = description
        self.name = name
        self.standby_replicas = standby_replicas
        self.tags = tags
        self.type = type
        self.id = mock_random.get_random_string(length=20,lower_case=True)
        self.arn = f"arn:aws:aoss:{region}:{account_id}:collection/{self.id}"
        self.created_date = int(unix_time() * 1000)
        self.kms_key_arn = policy["KmsARN"]
        self.last_modified_date = int(unix_time() * 1000)
        self.status = "ACTIVE"

    def to_dict(self) -> Dict[str, Any]:
        dct = {
            "arn": self.arn,
            "createdDate": self.created_date,
            "description": self.description,
            "id": self.id,
            "kmsKeyArn": self.kms_key_arn,
            "lastModifiedDate": self.last_modified_date,
            "name": self.name,
            "standbyReplicas": self.standby_replicas,
            "status": self.status,
            "type": self.type,

        }
        return {k: v for k, v in dct.items() if v}

    def to_dict_list(self) -> Dict[str, Any]:
        dct = {
            "arn": self.arn,
            "id": self.id,
            "name": self.name,
            "status": self.status
        }
        return {k: v for k, v in dct.items() if v}

class OpenSearchServiceServerlessBackend(BaseBackend):
    """Implementation of OpenSearchServiceServerless APIs."""

    def __init__(self, region_name, account_id):
        super().__init__(region_name, account_id)

        self.collections: Dict[str, Collection] = dict()
        self.security_policies: Dict[str, SecurityPolicy] = dict()

    def create_security_policy(self, client_token, description, name, policy, type) -> SecurityPolicy:
        if not client_token:
            client_token = mock_random.get_random_string(10)
        if client_token in list(
            sp.client_token for sp in list(self.security_policies.values())
        ):
            raise ConflictException(
                msg="The request uses the same client token as a previous, but non-identical request. Do not reuse a client token with different requests, unless the requests are identical"
            )
        if (name, type) in list(
            (sp.name, sp.type) for sp in list(self.security_policies.values())
        ):
            raise ConflictException(
                msg=f"Policy with name {name} and type {type} already exists"
            )
        if type not in ["encryption", "network"]:
            raise ValidationException(
                msg=f"1 validation error detected: Value '{type}' at 'type' failed to satisfy constraint: Member must satisfy enum value set: [encryption, network]"
            )

        security_policy = SecurityPolicy(
            client_token=client_token,
            description=description,
            name=name,
            policy=policy,
            type=type,
        )
        self.security_policies[security_policy.client_token] = security_policy
        return security_policy

    def get_security_policy(self, name, type):
        security_policy_detail = ""
        for sp in list(self.security_policies.values()):
            if sp.name == name and sp.type == type:
                security_policy_detail = sp
        if not security_policy_detail:
            raise ResourceNotFoundException(
                msg=f"Policy with name {name} and type {type} is not found")
        return security_policy_detail

    def list_security_policies(self, resource, type):
        """
        Pagination is not yet implemented
        """
        security_policy_summaries = []
        if resource:
            for res in resource:
                security_policy_summaries.extend([sp for sp in list(
                    self.security_policies.values()) if res in sp.resources and type == sp.type])
        else:
            security_policy_summaries = [sp for sp in list(
                self.security_policies.values()) if sp.type == type]
        return security_policy_summaries

    def update_security_policy(self, client_token, description, name, policy, policy_version, type):
        security_policy_detail = ""
        if not client_token:
            client_token = mock_random.get_random_string(10)
        if client_token in list(
            sp.client_token for sp in list(self.security_policies.values())
        ):
            raise ConflictException(
                msg="The request uses the same client token as a previous, but non-identical request. Do not reuse a client token with different requests, unless the requests are identical"
            )
        for sp in list(self.security_policies.values()):  
            if sp.name == name and sp.type == type:
                if sp.policy_version == policy_version:
                    security_policy_detail = sp
                else:
                    raise ValidationException(
                        msg=f"Policy version specified in the request refers to an older version and policy has since changed"
                    )
                
        if not security_policy_detail:
            raise ResourceNotFoundException(
                msg=f"Policy with name {name} and type {type} is not found")
        
        last_modified_date = security_policy_detail.last_modified_date
        if security_policy_detail.policy != json.loads(policy):
            last_modified_date = int(unix_time() * 1000)
            # Updating policy version
            policy_version = mock_random.get_random_string(20)

        security_policy_detail.client_token=client_token
        security_policy_detail.description=description
        security_policy_detail.name=name
        security_policy_detail.policy=json.loads(policy)
        security_policy_detail.last_modified_date=last_modified_date
        security_policy_detail.policy_version=policy_version
        return security_policy_detail


    def create_collection(self, client_token, description, name, standby_replicas, tags, type) -> Collection:
        policy = ""
        if not client_token:
            client_token = mock_random.get_random_string(10)
        if client_token in list(
            sp.client_token for sp in list(self.collections.values())
        ):
            raise ConflictException(
                msg="The request uses the same client token as a previous, but non-identical request. Do not reuse a client token with different requests, unless the requests are identical"
            )
        
        for sp in list(self.security_policies.values()):
            if f"collection/{name}" in sp.resources:
                policy = sp.policy
        if not policy:
            raise ValidationException(
                msg=f"No matching security policy of encryption type found for collection name: {name}. Please create security policy of encryption type for this collection."
            )

        collection = Collection(
            client_token=client_token,
            description=description,
            name=name,
            standby_replicas=standby_replicas,
            tags=tags,
            type=type,
            policy=policy,
            region=self.region_name,
            account_id=self.account_id
        )
        self.collections[collection.name] = collection
        return collection

    def list_collections(self, collection_filters):
        """
        Pagination is not yet implemented
        """
        collection_summaries = []
        if (collection_filters) and ("name" in collection_filters):
            collection_summaries = [collection for collection in list(
            self.collections.values()) if collection.name == collection_filters["name"]]
        else:
            collection_summaries = [collection for collection in list(
                self.collections.values())]
        return collection_summaries

    def create_vpc_endpoint(self, client_token, name, security_group_ids, subnet_ids, vpc_id):
        # implement here
        return create_vpc_endpoint_detail

    

    def tag_resource(self, resource_arn, tags):
        # implement here
        return

    def untag_resource(self, resource_arn, tag_keys):
        # implement here
        return





    def delete_collection(self, client_token, id):
        # implement here
        return delete_collection_detail

    def delete_security_policy(self, client_token, name, type):
        # implement here
        return

    def delete_vpc_endpoint(self, client_token, id):
        # implement here
        return delete_vpc_endpoint_detail

    def update_vpc_endpoint(self, add_security_group_ids, add_subnet_ids, client_token, id, remove_security_group_ids, remove_subnet_ids):
        # implement here
        return update_vpc_endpoint_detail


opensearchserverless_backends = BackendDict(
    OpenSearchServiceServerlessBackend, "opensearchserverless")
