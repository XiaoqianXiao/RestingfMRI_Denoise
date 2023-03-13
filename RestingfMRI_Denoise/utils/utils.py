from os.path import exists
import json
import jsonschema
import copy
import typing as t
import re
from bids.layout import parse_file_entities, writing


_pipeline_valid_keys = ["name", "descrtiption", "confounds"]
type_checker = jsonschema.Draft4Validator.VALIDATORS

def load_pipeline_from_json(json_path: str) -> dict:
    """
    Loads json file and prepares it for further use (e.g. assures proper types interpretation)
    :param json_path: path to json file
    :return: jsonlike dictionary
    """
    if json_path.startswith('{\n'):
        js = json.loads(json_path) 
    elif not exists(json_path):
        raise IOError(f"File '{json_path}' does not exists!")
    else:
        with open(json_path, 'r') as json_file:
            js = json.load(json_file)
    js = swap_booleans(js, inplace=True)
    return js

def extract_pipeline_from_path(path: str) -> str:
    match = re.search(r'(?<=pipeline-)(.*?)(?=_)', path)
    if match is not None:
        return match.group()
    return ""

def is_booleanlike(value) -> bool:
    """
    Checks if argument is bool or string with 'true' or 'false' value.
    :param value: argument to check
    :return: True if argument is booleanlike, false if not
    """
    if isinstance(value, bool):
        return True
    if not isinstance(value, str):
        return False
    if value.lower() == "true" or value.lower() == "false":
        return True

def cast_bool(value) -> bool:
    """
    Tries to cast value to bool.
    Raises ValueError if value is ambiguous.
    Raises TypeError for unsupported types.
    :param value: value to cast
    :return: bool
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            raise ValueError("Ambiguous value of " + value)
    else:
        raise TypeError("Unsupported type of {} with value {}"
                        .format(type(value), value))


def swap_booleans(dictionary: dict, inplace: bool=True) -> dict:  # TODO: Extend functionality to lists too
    """
    Recursively iterates on dictionary and swaps booleanlike values with proper booleans.
    :param dictionary: input dictionary
    :param inplace: if True modifies inplace, if False creates deepcopy before changes
    :return: dictionary with swaped values
    """
    if not inplace:
        dictionary = copy.deepcopy(dictionary)
    for key in dictionary.keys():
        if isinstance(dictionary[key], dict):
            dictionary[key] = swap_booleans(dictionary[key], inplace=inplace)
        elif is_booleanlike(dictionary[key]):
            dictionary[key] = cast_bool(dictionary[key])
    return dictionary

def is_IcaAROMA(pipeline: dict) -> bool:
    return cast_bool(pipeline["aroma"])


def parse_file_entities_with_pipelines(filename, entities=None, config=None,
                                       include_unmatched=False) -> t.Dict[str, str]:
    """
    bids.extract_pipelines_from_path extended with ability to
    """
    et_dict = parse_file_entities(filename, entities, config, include_unmatched)
    pipeline = extract_pipeline_from_path(filename)
    if pipeline:
        et_dict['pipeline'] = pipeline
    return et_dict


def is_entity_subset(entity_superset: t.Dict[str, str], entity_subset: t.Dict[str, str]) -> bool:
    """
    Checks if all key values in subset are in superset
    Args:
        entity_superset: bigger dict
        entity_subset: smaller dict
    Returns: true if all key-values pairs from entity_subset are in entity_superset
    """
    return all(entity_superset.get(entity_key) == entity_value for entity_key, entity_value in entity_subset.items())


def build_path(entities, path_patterns, strict=False):
    path = writing.build_path(entities, path_patterns, strict)
    if path is not None:
        return path
    else:
        raise ValueError(f"Unable to build path with given entities: {entities}\n and path pattern {path_patterns}")


def assert_all_entities_equal(entities: t.List[t.Dict[str, str]], *entities_names: str) -> None:
    if len(entities) == 0:
        return
    for name in entities_names:
        first = entities[0].get(name)
        if any(entity.get(name) != first for entity in entities):
            raise AssertionError(f"Not all entities equal for key: {name}\n"
                                 f"{[entitie.get(name) for entitie in entities]}")

if __name__ == '__main__':
    dicto = load_pipeline_from_json("../pipelines/pipeline-24HMP_8Phys_spikes-FD2.json")
    print(dicto)
    print(swap_booleans(dicto, True))
