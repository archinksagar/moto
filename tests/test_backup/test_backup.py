"""Unit tests for backup-supported APIs."""
import boto3

from moto import mock_backup

# See our Development Tips on writing tests for hints on how to write good tests:
# http://docs.getmoto.org/en/latest/docs/contributing/development_tips/tests.html

@mock_backup
def test_create_backup_plan():
    client = boto3.client("backup", region_name="eu-west-1")
    resp = client.create_backup_plan(
                BackupPlan={
                    'BackupPlanName': 'backupplan-foobar',
                    'Rules': [
                        {
                            'RuleName': 'foobar',
                            'TargetBackupVaultName': response['BackupVaultName'],
                            'ScheduleExpression': 'cron(0 5 ? * * *)',
                            'Lifecycle': {
                                'DeleteAfterDays': 14,
                            },
                        },
                    ],
                },
                BackupPlanTags={
                    'foo': 'bar',
                },
            )

    raise Exception("NotYetImplemented")


@mock_backup
def test_create_backup_vault():
    client = boto3.client("backup", region_name="eu-west-1")
    resp = client.create_backup_vault(
        BackupVaultName='backupvault-foobar',
            BackupVaultTags={
                'foo': 'bar',
            },
        )

    raise Exception("NotYetImplemented")
