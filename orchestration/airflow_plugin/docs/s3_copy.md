# s3_copy

**Factory Class**: `S3CopyObjectOperatorFactory`

Factory for creating S3 copy object operators.

## Parameters

| Parameter | Required | Type | Default | Description | Example |
|-----------|----------|------|---------|-------------|---------|
| source_bucket_key | True | str | N/A | The key of the source object to copy | path/to/source/file.txt |
| dest_bucket_key | True | str | N/A | The key of the destination object | path/to/destination/file.txt |
| source_bucket_name | False | str | None | Name of the source bucket | my-source-bucket |
| dest_bucket_name | False | str | None | Name of the destination bucket | my-dest-bucket |
| aws_conn_id | False | str | aws_default | The Airflow connection ID for AWS credentials | aws_default |
| verify | False | bool | None | Whether to verify SSL certificates | True |