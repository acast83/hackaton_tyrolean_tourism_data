# Universal table

## Creating endpoint
```python
async def get(
    self,

    filters: dict = None,
    fields: str = None,
    order_by: str = '-created',

    no_paginate: bool = False,
    page: int = 1,
    per_page: int = 50,
    force_limit: int = None,

    include_columns_in_response: bool = True,
    include_menus_in_response: bool = True,
    search: str = None
):
    pass
```

### Use base get
### Modify model
