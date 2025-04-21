# TheFlows - Airflow DAG Management System

TheFlows is a comprehensive system for managing Apache Airflow DAGs through a user-friendly interface. It allows users to create, edit, and manage DAGs using a visual flow builder, with support for various task types and dependencies.

## Features

- Visual Flow Builder for creating Airflow DAGs
- Support for multiple task types:
  - AWS S3 Operations (List, Copy, Delete, Put)
  - AWS Athena Queries
  - Bash Commands
  - More operators coming soon...
- Dependency Management between tasks
- YAML-based DAG configuration
- API for DAG management
- Web UI for visual DAG creation

## Project Structure
theflows/
├── api/ # Flask API server
├── ui/ # React-based web interface
├── orchestration/ # Airflow plugin and DAG management
│ ├── airflow_plugin/ # Custom Airflow plugin
│ │ ├── plugins/ # Task type implementations
│ │ └── plugin_core/# Core plugin functionality
│ └── plugins/ # Additional plugins
├── core/ # Core business logic and models
├── config/ # Configuration files
├── metadata/ # Metadata storage
└── storage/ # Data storage

## Prerequisites

- Python 3.8+
- Node.js 14+
- Apache Airflow 2.0+
- PostgreSQL

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/theflows.git
cd theflows
```

2. Set up Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install UI dependencies:
```bash
cd ui
npm install
```

4. Configure environment variables:
```bash
# API Configuration
export FLASK_APP=api/app.py
export FLASK_ENV=development
export DATABASE_URL=postgresql://username:password@localhost:5432/theflows

# AWS Configuration (if using AWS features)
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=your_region
```

## Running the Application

1. Start the API server:
```bash
cd api
flask run
```

2. Start the UI development server:
```bash
cd ui
npm start
```

3. Install Airflow plugin:
```bash
cp -r orchestration/airflow_plugin/* $AIRFLOW_HOME/plugins/
```

## Creating a DAG

1. Access the web interface at `http://localhost:3000`
2. Navigate to "Flow Builder"
3. Design your workflow using the visual interface
4. Export the DAG configuration as YAML

Example YAML configuration:
```yaml
version: "1.0"
flow_id: "sample_s3_flow"
tasks:
  - name: "list_s3_files"
    type: "s3_list"
    description: "List files in S3 bucket"
    config:
      bucket: "my-bucket"
      prefix: "data/"
  - name: "process_data"
    type: "athena_query"
    description: "Process data using Athena"
    config:
      query: "SELECT * FROM my_table"
      database: "my_database"
      output_location: "s3://my-bucket/query-results/"
dependencies:
  process_data: ["list_s3_files"]
metadata:
  created_at: "2024-03-20T10:00:00Z"
  updated_at: "2024-03-20T10:00:00Z"
```

## Available Task Types

### AWS S3 Operations

#### S3 List Operation
- Type: `s3_list`
- Required Parameters:
  - `bucket`: S3 bucket name
- Optional Parameters:
  - `prefix`: File prefix to filter results
  - `delimiter`: Delimiter for hierarchical listing

#### S3 Copy Operation
- Type: `s3_copy`
- Required Parameters:
  - `source_bucket_key`: Source file path
  - `dest_bucket_key`: Destination file path

#### S3 Delete Operation
- Type: `s3_delete`
- Required Parameters:
  - `bucket`: S3 bucket name
  - `key`: File path to delete

#### S3 Put Operation
- Type: `s3_put`
- Required Parameters:
  - `bucket`: S3 bucket name
  - `key`: File path
  - `data`: Content to upload

### AWS Athena Operations

#### Athena Query
- Type: `athena_query`
- Required Parameters:
  - `query`: SQL query to execute
  - `database`: Athena database name
  - `output_location`: S3 location for query results

### Bash Operations

#### Bash Command
- Type: `bash_command`
- Required Parameters:
  - `command`: Command to execute
- Optional Parameters:
  - `env`: Environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation
2. Create an issue in the GitHub repository
3. Contact the development team

## Roadmap

- [ ] Add support for more task types
- [ ] Implement task type versioning
- [ ] Add flow templates
- [ ] Enhance error handling and validation
- [ ] Implement user authentication and authorization
- [ ] Add support for custom plugins