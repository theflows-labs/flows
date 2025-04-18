# athena_query

**Factory Class**: `AthenaQueryOperatorFactory`

Factory for creating Athena query operators.

## Parameters

| Parameter | Required | Type | Default | Description | Example |
|-----------|----------|------|---------|-------------|---------|
| query | True | str | N/A | The SQL query to execute in Athena | SELECT * FROM my_table LIMIT 10 |
| database | True | str | N/A | The name of the database to execute the query in | my_database |
| output_location | True | str | N/A | The S3 path where query results will be stored | s3://my-bucket/query-results/ |
| aws_conn_id | False | str | aws_default | The Airflow connection ID for AWS credentials | aws_default |
| region_name | False | str | us-east-1 | The AWS region where Athena is running | us-east-1 |
| workgroup | False | str | primary | The Athena workgroup to use for query execution | primary |
| query_execution_context | False | dict | None | Additional context for query execution | {'Database': 'my_database', 'Catalog': 'AwsDataCatalog'} |
| result_configuration | False | dict | None | Configuration for query results | {'OutputLocation': 's3://my-bucket/query-results/'} |
| client_request_token | False | str | None | Unique token to ensure idempotency | unique-token-123 |
| sleep_time | False | int | 30 | Time to wait between polling for query completion | 30 |
| max_tries | False | int | None | Maximum number of attempts to check query status | 3 |
| check_interval | False | int | 30 | Interval between status checks in seconds | 30 |