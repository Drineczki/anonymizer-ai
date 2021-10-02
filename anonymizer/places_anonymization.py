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
    city_tokens = __preprocess_cities(nlp_results)
    city_anonymizations = __anonymize_cities(city_tokens)

    return city_anonymizations


def __anonymize_cities(city_tokens: t.List[spacy.tokens.Token]) -> t.List[AnonymizationResult]:
    merged_city_tokens: t.List[t.List[spacy.tokens.Token, ...]] = []
    loop_cnt = 0
    while loop_cnt < len(city_tokens):
        if city_tokens[loop_cnt].ent_iob_ == "B":
            full_entity = [city_tokens[loop_cnt]]
            loop_cnt += 1
            if loop_cnt == len(city_tokens):
                break

            while city_tokens[loop_cnt].ent_iob_ == "I":
                full_entity.append(city_tokens[loop_cnt])
                loop_cnt += 1

                if loop_cnt == len(city_tokens):
                    break

            merged_city_tokens.append(full_entity)
            continue

        loop_cnt += 1

    anonymization_results: t.List[AnonymizationResult] = []
    for city_tokens in merged_city_tokens:
        city_text = " ".join([token.text for token in city_tokens])

        anonymization = f"{city_tokens[0].text[0]}."
        res = AnonymizationResult(entity=city_text, anonymization=anonymization)

        anonymization_results.append(res)

    return anonymization_results


def __preprocess_cities(nlp_results: t.Iterable[spacy.tokens.Token]) -> t.List[spacy.tokens.Token]:
    return [token for token in nlp_results if token.ent_type_ == "placeName"]
