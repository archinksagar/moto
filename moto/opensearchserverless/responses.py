"""Handles incoming opensearchserverless requests, invokes methods, returns responses."""
import json

from moto.core.responses import BaseResponse
from .models import opensearchserverless_backends


class OpenSearchServiceServerlessResponse(BaseResponse):
    """Handler for OpenSearchServiceServerless requests and responses."""

    def __init__(self):
        super().__init__(service_name="opensearchserverless")

    @property
    def opensearchserverless_backend(self):
        """Return backend instance specific for this region."""

        return opensearchserverless_backends[self.current_account][self.region]
    
    def create_security_policy(self):
        params = json.loads(self.body)
        client_token = params.get("clientToken")
        description = params.get("description")
        name = params.get("name")
        policy = params.get("policy")
        type = params.get("type")
        security_policy_detail = self.opensearchserverless_backend.create_security_policy(
            client_token=client_token,
            description=description,
            name=name,
            policy=policy,
            type=type,
        )
        return json.dumps(dict(securityPolicyDetail=security_policy_detail.to_dict()))
        
    def get_security_policy(self):
        params = json.loads(self.body)
        name = params.get("name")
        type = params.get("type")
        security_policy_detail = self.opensearchserverless_backend.get_security_policy(
            name=name,
            type=type,
        )
        return json.dumps(dict(securityPolicyDetail=security_policy_detail.to_dict()))

    def list_security_policies(self):
        params = json.loads(self.body)
        resource = params.get("resource")
        type = params.get("type")
        security_policy_summaries = self.opensearchserverless_backend.list_security_policies(
            resource=resource,
            type=type,
        )
        return json.dumps(dict(securityPolicySummaries=[sp.to_dict_list() for sp in security_policy_summaries]))
    
    def update_security_policy(self):
        params = json.loads(self.body)
        client_token = params.get("clientToken")
        description = params.get("description")
        name = params.get("name")
        policy = params.get("policy")
        policy_version = params.get("policyVersion")
        type = params.get("type")
        security_policy_detail = self.opensearchserverless_backend.update_security_policy(
            client_token=client_token,
            description=description,
            name=name,
            policy=policy,
            policy_version=policy_version,
            type=type,
        )
        return json.dumps(dict(securityPolicyDetail=security_policy_detail.to_dict()))


    def create_collection(self):
        params = json.loads(self.body)
        client_token = params.get("clientToken")
        description = params.get("description")
        name = params.get("name")
        standby_replicas = params.get("standbyReplicas")
        tags = params.get("tags")
        type = params.get("type")
        create_collection_detail = self.opensearchserverless_backend.create_collection(
            client_token=client_token,
            description=description,
            name=name,
            standby_replicas=standby_replicas,
            tags=tags,
            type=type,
        )
        return json.dumps(dict(createCollectionDetail=create_collection_detail.to_dict()))

    def list_collections(self):
        params = json.loads(self.body)
        collection_filters = params.get("collectionFilters")
        collection_summaries = self.opensearchserverless_backend.list_collections(
            collection_filters=collection_filters,
        )
        return json.dumps(dict(collectionSummaries=[cs.to_dict_list() for cs in collection_summaries]))
    

    def create_vpc_endpoint(self):
        params = self._get_params()
        client_token = params.get("clientToken")
        name = params.get("name")
        security_group_ids = params.get("securityGroupIds")
        subnet_ids = params.get("subnetIds")
        vpc_id = params.get("vpcId")
        create_vpc_endpoint_detail = self.opensearchserverless_backend.create_vpc_endpoint(
            client_token=client_token,
            name=name,
            security_group_ids=security_group_ids,
            subnet_ids=subnet_ids,
            vpc_id=vpc_id,
        )
        # TODO: adjust response
        return json.dumps(dict(createVpcEndpointDetail=create_vpc_endpoint_detail))
    
    def tag_resource(self):
        params = self._get_params()
        resource_arn = params.get("resourceArn")
        tags = params.get("tags")
        self.opensearchserverless_backend.tag_resource(
            resource_arn=resource_arn,
            tags=tags,
        )
        # TODO: adjust response
        return json.dumps(dict())
    
    def untag_resource(self):
        params = self._get_params()
        resource_arn = params.get("resourceArn")
        tag_keys = params.get("tagKeys")
        self.opensearchserverless_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        # TODO: adjust response
        return json.dumps(dict())
    
    def update_collection(self):
        params = self._get_params()
        client_token = params.get("clientToken")
        description = params.get("description")
        id = params.get("id")
        update_collection_detail = self.opensearchserverless_backend.update_collection(
            client_token=client_token,
            description=description,
            id=id,
        )
        # TODO: adjust response
        return json.dumps(dict(updateCollectionDetail=update_collection_detail))
    
    def delete_collection(self):
        params = self._get_params()
        client_token = params.get("clientToken")
        id = params.get("id")
        delete_collection_detail = self.opensearchserverless_backend.delete_collection(
            client_token=client_token,
            id=id,
        )
        # TODO: adjust response
        return json.dumps(dict(deleteCollectionDetail=delete_collection_detail))
    
    def delete_security_policy(self):
        params = self._get_params()
        client_token = params.get("clientToken")
        name = params.get("name")
        type = params.get("type")
        self.opensearchserverless_backend.delete_security_policy(
            client_token=client_token,
            name=name,
            type=type,
        )
        # TODO: adjust response
        return json.dumps(dict())
    
    def delete_vpc_endpoint(self):
        params = self._get_params()
        client_token = params.get("clientToken")
        id = params.get("id")
        delete_vpc_endpoint_detail = self.opensearchserverless_backend.delete_vpc_endpoint(
            client_token=client_token,
            id=id,
        )
        # TODO: adjust response
        return json.dumps(dict(deleteVpcEndpointDetail=delete_vpc_endpoint_detail))
    
    def update_vpc_endpoint(self):
        params = self._get_params()
        add_security_group_ids = params.get("addSecurityGroupIds")
        add_subnet_ids = params.get("addSubnetIds")
        client_token = params.get("clientToken")
        id = params.get("id")
        remove_security_group_ids = params.get("removeSecurityGroupIds")
        remove_subnet_ids = params.get("removeSubnetIds")
        update_vpc_endpoint_detail = self.opensearchserverless_backend.update_vpc_endpoint(
            add_security_group_ids=add_security_group_ids,
            add_subnet_ids=add_subnet_ids,
            client_token=client_token,
            id=id,
            remove_security_group_ids=remove_security_group_ids,
            remove_subnet_ids=remove_subnet_ids,
        )
        # TODO: adjust response
        return json.dumps(dict(updateVpcEndpointDetail=update_vpc_endpoint_detail))


