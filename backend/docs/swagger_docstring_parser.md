# Docstring parser

## Overview
## Supported sections
There are now supported four types of sections for docstrings:
* Description
* Parameters
* RequestBody
* Responses

### Description
Lines parsed before first block or json part are considered a part of description. No section name required (~~Description:~~).

### Parameters
Parameters parsed from docstring are compared with method signature.  
From signature we can get:
* name
* type (`str`, `int` or other)
* default value
* required - if signature has no default value parameter considered as required.
```python
async def get(self, fields: str = None, order='order'):
    """
    Get all bookmarks created by user.

    Parameters:
        fields (query): CSV string
            enum: @Bookmark.default_fields
        order (query):
            enum: @Bookmark.allowed_ordering
    """
    ...
```

#### Parameter
```
first_name (body): first name of the person
    required: true
    deprecated: false
    allowEmptyValue: false
    style: form
    explode: true
    allowReserved: false
    example: {"id": 13, "name": "John"}
    schema:
        {
            "type": "object",
            "properties": {
                              "id": {"type": "integer", "format": "int64"},
                              "name": {"type": "string"}
                           },
            "required": ["name"],
            "example": {"name": "Puma", "id": 1}
        }

    enum: @Model.field
    type: integer
    format: uuid
    default: 1
    minimum: 1
    maximum: 3
```
If not fields supplied information from method signature is used.

**OpenAPI specified parameters fields**  
[description](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#parameter-object)
* **required** (bool): 
* **deprecated** (bool):
* **allowEmptyValue** (bool):
* **style** (string):
* **explode** (bool):
* **allowReserved** (bool):
* **example** (any):
* **schema** (json): This parameter is json field that should follow [openAPI specification](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#schema-object) for describing of parameter. If this field specified if completely overrides (without validating) auto-generated schema deducted from method signature.

**Additional for simple parameters (int, float, str)**  
* **enum**: comma separated list of possible values of a parameter. For `enums` available using of links from database model imported to the same file with method.  
*Example of link*: @PhoneBook.connected_fields  
*Example of link for getting list of database model fields*: @Model.FIELDS  
If parameter considered a **comma separated (CSV)** you have to specify it in parameter description in any way (check condition: `summary.find('csv') != -1`).
```
fields (query): This is csv parameter
    enum: 1,2,3
```
* **type**: string, number, integer, boolean, array or object. [Open api types description.](https://swagger.io/docs/specification/data-models/data-types/)
* **default**: default value of a parameter
* **minimum**: minimum value (only for numerical).
* **maximum**: maximum value (only for numerical).
* **format**: format of value representation. For numerical: [float, double, int32, int64], for strings: [**date**, **password**, **byte**, **email**, **uuid** and [*Others*](https://swagger.io/docs/specification/data-models/data-types/)]

### RequestBody
This type of block available for `post`, `put`, `patch` methods.
There are two ways of describing request body:
* Manual description using `json` part of `RequestBody` block.
```
RequestBody:
    request description.
    {
        "name": "bookmark1",
        "app_name": "app1",
        "url": "https://impresaone.int.telmekom.net/applications",
        "color": {"text": "black", "background": "white"},
        "icon": "mega"
    }
```
* Using link to json-file from `test_integrated/documentation` directory
```
RequestBody:
    request description.
    @contacts/POST_201_successfully_add_contact.request_body.json
```
### Responses
Responses described the same way as RequestBody, but there is can be described several response codes for one method. Also, available using of json links.
```
Responses:
    @contacts/POST_401_unauthorized_unsuccessfully_add_contact.json
    @contacts/GET_200_get_all_contacts.json
    201:
        Id of added person
        {"id": "___UUID___"}
```

### Example of method with docstring
```python
async def get(self, page: int = 1, per_page: int = 100, search: str = None, fields: list = None,
              filters: dict = None, order_by: str = None):
    """
    Fetch contacts from addressbook, all or by given criteria in filters

    Parameters:
        page (query): requested page
            example: 1
        per_page (query): maximum items per one-page
            example: 1
        search (query): search term
            example: stefan
        fields (query): list of fields to return
            example: id,first_name
        filters (query): additional filters
            example: first_name__eq = Stefan
        order_by (query): order by criteria
            example: -last_name

    Responses:
        @contacts/POST_401_unauthorized_unsuccessfully_add_contact.json
        @contacts/GET_200_get_all_contacts.json

    """
    ...
```

## Parsing algorithm
To understand parsing algorith important to get familiar with `block` concept.  
`Block` is an atomic part of docstring that parser can understand.
### Block structure
```
name (type): summury        <-- Header
                            <-- Body begin
    description             <--     Full (multyline) description of a current block
    block
    ...                     <--     Every block can include any number of other blocks
    block
        block
            ...             <--     Parsing algorithm supports nesting structure of blocks
    json                    <--     Every block can have atleast one json instance 
                            <-- Body end
```
#### Header
```
name (type): summury
```
* **name** (mandatory) - name of a block.
* **type** (optional) - type of block, puts in round braces.
* **colon** (mandatory) - syntax part of block header.
* **summary** (optional) - short description of a block.

#### Body
Body of a block is parsed using indentation logic. Parser looks for parts have same indentation and considers them belongings of current block.

All part of a body are optional, also empty body is valid as well.
```
    description
    block
    ...        
    block
        block
            ...
    json
^^^^            <-- 4 spaces indentation as example
```
* **description** - Multiline description of a block.
* **block** - Nesting of blocks are available, but will be ignored if does not make sense.
* **json** - Json-part of a block. Syntax of json requires following of the same as it required in python `json.loads` module. In case of syntax error `{"json_parsing_error": <exception_message>}` returned.

#### Example of parsing a docstring

Docstring
```pyhton
example_header = 'NName (TType): SSummary.'
example_block = """
        Example docstring for GET method (first line).
        Second line of description.

        Parameters:
            fields (query):
                enum: @Ticket.default_fields
            page (query): First line of page parameter description.
                Next line of page parameter description.
                enum: 1,2,3
                format: int16
                example: 5
        RequestBody:
            Description text.
            {
                "username": {"type": "number", "example": "john.doe"},
                "password": "topsecret"
            }
    """
```
Raw parsed python `dict` result
```json
{
    "name": "NName",
    "summary": "SSummary.",
    "description": "Example docstring for GET method (first line).\nSecond line of description.\n\n",
    "type": "TType",
    "json": {},
    "blocks": {
        "Parameters": {
            "name": "Parameters", "summary": "", "description": "\n", "type": "", "json": {},
            "blocks": {
                "fields": {"name": "fields", "summary": "", "description": "", "type": "query", "json": {},
                  "blocks": {
                      "enum": {"name": "enum", "summary": "", "description": "@Ticket.default_fields", "type": "", "json": {}, "blocks": {}}}},
                "page": {
                    "name": "page",
                    "summary": "First line of page parameter description.",
                    "description": " First line of page parameter description.\nNext line of page parameter description.\n",
                    "type": "query",
                    "json": {},
                    "blocks": {
                        "enum": {"name": "enum", "summary": "1, 2, 3", "description": "", "type": "", "json": {}, "blocks": {}}}}}},
        "RequestBody": {
            "name": "RequestBody", "summary": "", "description": "\nDescription text.\n\n", "type": "",
            "json": {"username": {"type": "number", "example": "john.doe"}, "password": "topsecret"},
            "blocks": {}
        }}}
```
