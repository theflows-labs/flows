# Plugin Development Guide

This guide explains how to create new plugins and operators for theflows.

## Plugin Structure

A plugin should follow this structure:
```
plugins/
├── <service_name>/           # e.g., aws, gcp, azure
│   ├── __init__.py
│   ├── <service>/           # e.g., s3, athena, bigquery
│   │   ├── __init__.py
│   │   ├── operators/
│   │   │   ├── __init__.py
│   │   │   └── <operation>.py  # e.g., s3_operations.py
│   │   └── hooks/
│   │       ├── __init__.py
│   │       └── <service>_hook.py
│   └── utils/
│       ├── __init__.py
│       └── <service>_utils.py
```

## Creating a New Operator

1. Create a new operator factory class that inherits from `OperatorFactory`
2. Define the `TASK_TYPE` class variable
3. Implement the required methods:
   - `get_operator_class()`
   - `create_operator()`
   - `get_required_parameters()`
   - `get_optional_parameters()`

Example:
```python
class MyOperatorFactory(OperatorFactory):
    TASK_TYPE = "my_operation"
    
    @classmethod
    def get_operator_class(cls, task_type: str) -> Type[BaseOperator]:
        if task_type == cls.TASK_TYPE:
            return MyOperator
        raise ValueError(f"Unknown task type: {task_type}")
    
    def create_operator(self, task_config: TaskConfiguration, dag) -> BaseOperator:
        config_details = self._parse_config_details(task_config.config_details)
        return self.get_operator_class(task_config.task_type)(
            task_id=task_config.task_id,
            dag=dag,
            **config_details
        )
    
    @classmethod
    def get_required_parameters(cls) -> List[str]:
        return ["param1", "param2"]
    
    @classmethod
    def get_optional_parameters(cls) -> Dict[str, Any]:
        return {
            "optional_param1": "default_value1",
            "optional_param2": "default_value2"
        }
```

## Parameter Documentation

Each operator factory should document its parameters using the following methods:

1. `get_required_parameters()`: Returns a list of required parameter names
2. `get_optional_parameters()`: Returns a dictionary of optional parameters and their default values
3. `get_parameter_descriptions()`: Returns a dictionary of parameter descriptions

Example:
```python
@classmethod
def get_parameter_descriptions(cls) -> Dict[str, str]:
    return {
        "param1": "Description of param1",
        "param2": "Description of param2",
        "optional_param1": "Description of optional_param1",
        "optional_param2": "Description of optional_param2"
    }
```

## Best Practices

1. **Parameter Validation**:
   - Always validate required parameters
   - Provide sensible defaults for optional parameters
   - Document all parameters and their types

2. **Error Handling**:
   - Use specific exception types
   - Provide clear error messages
   - Log errors appropriately

3. **Testing**:
   - Write unit tests for each operator
   - Test parameter validation
   - Test error cases

4. **Documentation**:
   - Document all public methods
   - Include examples in docstrings
   - Keep README files up to date

## Example Plugin

See the AWS plugin (`plugins/aws/`) for a complete example of:
- Plugin structure
- Operator implementation
- Parameter documentation
- Error handling
- Testing 