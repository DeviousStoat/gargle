# gargle

```python
from gargle.maybe import maybe_get


some_dict = {
    "key1": {
        "sub_key1": [
            {
                "in_list1": "precious value 1",
            }
        ],
        "sub_key2": {
            "sub_sub_key1": "precious value 2",
        },
    }
}

my_precious_values = {
    "precious_value_1": (
        maybe_get(some_dict, "key1")
        .get("sub_key1")
        .get(0)
        .get("in_list1")
        .from_maybe(default="not found")
    ),
    "precious_value_2": (
        maybe_get(some_dict, "key1")
        .get("sub_key2")
        .get("sub_sub_key1")
        .from_maybe(default="not found")
    ),
    "precious_value_3": (
        maybe_get(some_dict, "key2")
        .get("sub_key2")
        .get("sub_sub_key1")
        .from_maybe(default="not found")
    ),
}

print(my_precious_values)
# {
#    'precious_value_1': 'precious value 1',
#    'precious_value_2': 'precious value 2',
#    'precious_value_3': 'not found'
# }
```
