import typing as t

import spacy
import yaml

import anonymizer.constants as c
from anonymizer.result import AnonymizationResult


def __load_assets(assets_file: str) -> t.List[str]:
    with open(assets_file, "r") as yaml_file:
        asset = yaml.load(yaml_file, Loader=yaml.Loader)

    return asset["places"]


PUBLIC_PLACES_ENTITIES: t.List[str] = __load_assets(c.PUBLIC_ENTITIES_YAML)


def anonymize_places(nlp_results: t.Iterable[spacy.tokens.Token]) -> t.List[AnonymizationResult]:
    anonymization_results = nlp_results

    return anonymization_results
