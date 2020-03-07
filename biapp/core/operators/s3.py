import boto3
import glob
import os

import biapp.core.logger.log as log
from biapp.settings.config import AWS_REGION

logger = log.setup_custom_logger(__name__)


class S3Operator:

    def __init__(self):

        self.client = self.create_s3_client()

    def create_s3_client(self):

        client = boto3.client('s3', region_name=AWS_REGION)

        logger.info('Client created')
        return client

    def create_bucket(self, bucket_name):

        try:
            response = self.client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
            )

            logger.info(f'{bucket_name} created')
            return response

        except self.client.exceptions.BucketAlreadyOwnedByYou:
            logger.info(
                f"'{bucket_name}' already exists!"
            )

    def deploy_code(self, bucket):

        directory = f'{os.path.join(os.getcwd())}{os.sep}'
        extensions = ('cfg', 'py')

        try:
            for ext in extensions:

                for root, subdirs, files in os.walk(directory):
                    files = glob.glob(os.path.join(root, f'*.{ext}'))

                    for f in files:
                        relative_path = root.replace(directory, '')
                        filename = os.path.basename(f)
                        s3_path = os.path.join(relative_path, filename)
                        s3_path = s3_path.replace(os.sep, '/')

                        self.client.upload_file(
                            os.path.join(root, f),
                            bucket,
                            s3_path,
                        )

                        logger.info(f'{s3_path} written to S3')

        except Exception as err:
            raise(err)

    def list_bucket(self, bucket, prefix=''):

        response = self.client.list_objects_v2(
            Bucket=bucket,
            Delimiter='',
            EncodingType='url',
            MaxKeys=10,
            Prefix=prefix,
            FetchOwner=False,
            RequestPayer='requester'
        )

        if response:
            return response['Contents']
