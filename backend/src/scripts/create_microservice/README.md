# Create Microservice Script
## Usage
### Creating a new service
```commandline
python create_microservice.py --name new_service_name --lookups "path/to/lookups.json"
```

### Adding lookups to existing project 
```commandline
python create_microservice.py --name name_of_existing_service --lookups "path/to/lookups.json"
```
note: To add lookups to existing service this service has to have template placeholders inserted.

### Getting help
```commandline
python create_microservice.py --help 
```
### Test mode
Creates service but changes for shared files will be applied to the copies of those files
```commandline
python create_microservice.py --name new_service_name --lookups "path/to/lookups.json" --test_mode
```
## Preparation of old service for adding lookups
In the following files list you have to insert template placeholders:
1. `tshared/ipc/service_name.py`
  * add to the bottom of the file with no indentation:  
  ```
  # {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
  ```
2. `tshared/lookups/cache.py`
  * add after imports with no indentation:  
  ```
  # {{ import_ipc }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
  ```
  * add after all lookup classes with no indentation:  
  ```
  # {{ lookup }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
  ```

3. `tshared/test.py`
  * inside `initialize_lookups_svc_service_name()` function, with function body indentation  
  ```
  # {{ lookup_get_service_name }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
  ```
  * after `initialize_lookups_svc_service_name()` function, with same indentations as other init functions signatures  
  ```
  # {{ function_body }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
  ```
  * inside `initialize_lookups()` after last if statement with same indentations as other if statements  
  ```
  # {{ function_call }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
  ```

4. `svc_service_name/service_name/api/lookups.py`
  * add inside `tbl2model` dictionary with same indentation as others items (4 spaces):  
  ```
  # {{ tbl2model }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
  ```

5. `svc_service_name/service_name/models/lookups.py`
  * add after all models with no indentation:  
  ```
  # {{ lookup_model }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
  ```

6. `tests_integration/test_service_name.py`
  * add inside `expected_result` set with same indentation as other items:  
  ```
  # {{ lookup_name }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
  ```


## Requirements
* python 3.9 or higher
* jinja2
* click
* pyyaml