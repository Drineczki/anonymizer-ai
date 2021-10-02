import typing as t

import spacy
import yaml

from anonymizer.result import AnonymizationResult


def __load_assets(assets_file: str) -> t.List[str]:
    with open(assets_file, "r") as yaml_file:
        asset = yaml.load(yaml_file, Loader=yaml.Loader)

    return asset["people"]


PEOPLE_PUBLIC_ENTITIES: t.List[str] = __load_assets("./anonymizer/assets/public_entities.yaml")


def anonymize_people(nlp_results: t.Iterable[spacy.tokens.Token]) -> t.List[AnonymizationResult]:
    if len(nlp_results) == 0:
        return []

    people_tokens = preprocess(nlp_results)
    if len(people_tokens) == 0:
        return []

    merged_tokens: t.List[t.List[spacy.tokens.Token, ...]] = []

    loop_cnt = 0
    while loop_cnt < len(people_tokens):
        if people_tokens[loop_cnt].ent_iob_ == "B":
            full_entity = [people_tokens[loop_cnt]]
            loop_cnt += 1
            if loop_cnt == len(people_tokens):
                break

            while people_tokens[loop_cnt].ent_iob_ == "I":
                full_entity.append(people_tokens[loop_cnt])
                loop_cnt += 1

                if loop_cnt == len(people_tokens):
                    break

            merged_tokens.append(full_entity)
            continue

        loop_cnt += 1

    anonymization_results: t.List[AnonymizationResult] = []

    for person_tokens in merged_tokens:
        person_text = " ".join([token.text for token in person_tokens])

        first_anonymization_char = person_tokens[0].text[0]
        second_anonymization_char = person_tokens[-1].text.split("-")[-1][0]

        anonymization = (
            f"{first_anonymization_char}. {second_anonymization_char}."
            if len(person_tokens) > 1
            else f"{first_anonymization_char}."
        )
        res = AnonymizationResult(entity=person_text, anonymization=anonymization)

        anonymization_results.append(res)

    return anonymization_results


def preprocess(nlp_results: t.Iterable[spacy.tokens.Token]) -> t.List[spacy.tokens.Token]:
    BACKTRACK_WINDOW = 10

    people_tokens = []
    loop_cnt = 0
    while loop_cnt < len(nlp_results):
        if nlp_results[loop_cnt].ent_type_ == "persName":
            if nlp_results[loop_cnt].ent_iob_ == "B":
                check_result = True
                for i in range(1, BACKTRACK_WINDOW + 1):
                    backtracked_index = loop_cnt - i
                    if backtracked_index >= 0:
                        check_result = (
                            check_result
                            and not nlp_results[backtracked_index].lemma_
                            in PEOPLE_PUBLIC_ENTITIES
                        )

                if check_result:
                    people_tokens.append(nlp_results[loop_cnt])

                loop_cnt += 1
                while loop_cnt < len(nlp_results) and nlp_results[loop_cnt].ent_iob_ == "I":
                    if check_result:
                        people_tokens.append(nlp_results[loop_cnt])
                    loop_cnt += 1
                continue

        loop_cnt += 1

    return people_tokens
