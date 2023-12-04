"""BackupBackend class with methods for supported APIs."""

from moto.core import BaseBackend, BackendDict, BaseModel

class BackupPlan(BaseModel):
    pass
class BackupVault(BaseModel):
    def __init__(
        self,
        backup_vault_name: str,
    ):
        self.backup_vault_name = backup_vault_name
        self.backup_vault_arn = f"arn:aws:backup:{region}:{account_id}:vault:aBackupVault"

class BackupBackend(BaseBackend):
    """Implementation of Backup APIs."""

    def __init__(self, region_name, account_id):
        super().__init__(region_name, account_id)

    # add methods from here

    def create_backup_plan(self, backup_plan, backup_plan_tags, creator_request_id):
        # implement here
        return backup_plan_id, backup_plan_arn, creation_date, version_id, advanced_backup_settings
    
    def create_backup_vault(self, backup_vault_name, backup_vault_tags, encryption_key_arn, creator_request_id):
        # implement here
        return backup_vault_name, backup_vault_arn, creation_date
    

backup_backends = BackendDict(BackupBackend, "backup")
