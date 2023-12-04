"""Handles incoming backup requests, invokes methods, returns responses."""
import json

from moto.core.responses import BaseResponse
from .models import backup_backends


class BackupResponse(BaseResponse):
    """Handler for Backup requests and responses."""

    def __init__(self):
        super().__init__(service_name="backup")

    @property
    def backup_backend(self):
        """Return backend instance specific for this region."""
        return backup_backends[self.current_account][self.region]

    # add methods from here

    
    def create_backup_plan(self):
        params = self._get_params()
        backup_plan = params.get("BackupPlan")
        backup_plan_tags = params.get("BackupPlanTags")
        creator_request_id = params.get("CreatorRequestId")
        backup_plan_id, backup_plan_arn, creation_date, version_id, advanced_backup_settings = self.backup_backend.create_backup_plan(
            backup_plan=backup_plan,
            backup_plan_tags=backup_plan_tags,
            creator_request_id=creator_request_id,
        )
        # TODO: adjust response
        return json.dumps(dict(backupPlanId=backup_plan_id, backupPlanArn=backup_plan_arn, creationDate=creation_date, versionId=version_id, advancedBackupSettings=advanced_backup_settings))

    
    def create_backup_vault(self):
        params = self._get_params()
        backup_vault_name = params.get("BackupVaultName")
        backup_vault_tags = params.get("BackupVaultTags")
        encryption_key_arn = params.get("EncryptionKeyArn")
        creator_request_id = params.get("CreatorRequestId")
        backup_vault_name, backup_vault_arn, creation_date = self.backup_backend.create_backup_vault(
            backup_vault_name=backup_vault_name,
            backup_vault_tags=backup_vault_tags,
            encryption_key_arn=encryption_key_arn,
            creator_request_id=creator_request_id,
        )
        # TODO: adjust response
        return json.dumps(dict(backupVaultName=backup_vault_name, backupVaultArn=backup_vault_arn, creationDate=creation_date))
# add templates from here
