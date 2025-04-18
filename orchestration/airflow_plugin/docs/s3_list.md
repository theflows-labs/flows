# s3_list

**Factory Class**: `S3ListOperatorFactory`

Factory for creating S3 list operators.

## Parameters

| Parameter | Required | Type | Default | Description | Example |
|-----------|----------|------|---------|-------------|---------|
| bucket | True | str | N/A | Name of the S3 bucket to list | my-bucket |
| prefix | False | str |  | Prefix to filter objects | path/to/files/ |
| delimiter | False | str |  | Delimiter to use for object grouping | / |
| aws_conn_id | False | str | aws_default | The Airflow connection ID for AWS credentials | aws_default |