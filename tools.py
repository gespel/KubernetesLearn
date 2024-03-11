import yaml


def convert_to_camel_case(text):
    data = yaml.safe_load(text)

    def to_camel_case(snake_str):
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    def convert_keys(obj):
        if isinstance(obj, dict):
            new_dict = {}
            for key, value in obj.items():
                new_key = to_camel_case(key)
                new_value = convert_keys(value)
                new_dict[new_key] = new_value
            return new_dict
        elif isinstance(obj, list):
            return [convert_keys(item) for item in obj]
        else:
            return obj

    converted_data = convert_keys(data)

    return yaml.dump(converted_data, default_flow_style=False)
