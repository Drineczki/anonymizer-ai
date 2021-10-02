import typing as t

import spacy
import yaml

import anonymizer.constants as c
from anonymizer.result import AnonymizationResult


def anonymize_places(nlp_results: t.Iterable[spacy.tokens.Token]) -> t.List[AnonymizationResult]:
    city_tokens = __preprocess_cities(nlp_results)
    city_anonymizations = __anonymize_cities(city_tokens)
    geoloc_tokens = __preprocess_geoloc(nlp_results)
    geoloc_anonymizations = __anonymize_geoloc(geoloc_tokens)

    return [*city_anonymizations, *geoloc_anonymizations]


def __preprocess_cities(nlp_results: t.Iterable[spacy.tokens.Token]) -> t.List[spacy.tokens.Token]:
    BACKTRACK_WINDOW = 5

    city_tokens = []
    loop_cnt = 0
    while loop_cnt < len(nlp_results):
        if nlp_results[loop_cnt].ent_type_ == "placeName":
            if nlp_results[loop_cnt].ent_iob_ == "B":
                check_result = True
                for i in range(1, BACKTRACK_WINDOW + 1):
                    backtracked_index = loop_cnt - i
                    if backtracked_index >= 0:
                        check_result = (
                            check_result
                            and not nlp_results[backtracked_index].lemma_
                            in c.PUBLIC_PLACES_ENTITIES
                        )

                if check_result:
                    city_tokens.append(nlp_results[loop_cnt])

                loop_cnt += 1
                while loop_cnt < len(nlp_results) and nlp_results[loop_cnt].ent_iob_ == "I":
                    if check_result:
                        city_tokens.append(nlp_results[loop_cnt])
                    loop_cnt += 1
                continue

        loop_cnt += 1

    return city_tokens


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
    for tokens in merged_city_tokens:
        city_text = " ".join([token.text for token in tokens])

        anonymization = f"{tokens[0].text[0]}."
        lemmas = set([token.lemma_ for token in tokens])
        region_lemmas = set(["gmina", "powiat", "wojewodztwie"])
        if len(region_lemmas.intersection(lemmas)) != 0:
            geoloc_name = tokens[0].text
            anonymization = f"{geoloc_name} (...)"

        res = AnonymizationResult(entity=city_text, anonymization=anonymization, anon_type="place")

        anonymization_results.append(res)

    return anonymization_results


def __preprocess_geoloc(nlp_results: t.Iterable[spacy.tokens.Token]) -> t.List[spacy.tokens.Token]:
    return [token for token in nlp_results if token.ent_type_ == "geogName"]


def __anonymize_geoloc(geoloc_tokens: t.List[spacy.tokens.Token]) -> t.List[AnonymizationResult]:
    merged_geoloc_tokens: t.List[t.List[spacy.tokens.Token, ...]] = []
    loop_cnt = 0
    while loop_cnt < len(geoloc_tokens):
        if geoloc_tokens[loop_cnt].ent_iob_ == "B":
            full_entity = [geoloc_tokens[loop_cnt]]
            loop_cnt += 1
            if loop_cnt == len(geoloc_tokens):
                break

            while geoloc_tokens[loop_cnt].ent_iob_ == "I":
                full_entity.append(geoloc_tokens[loop_cnt])
                loop_cnt += 1

                if loop_cnt == len(geoloc_tokens):
                    break

            if loop_cnt == len(geoloc_tokens):
                merged_geoloc_tokens.append(full_entity)
                break

            # ul. case
            if geoloc_tokens[loop_cnt].ent_iob_ == "B" and geoloc_tokens[loop_cnt - 1].text == ".":
                full_entity.append(geoloc_tokens[loop_cnt])
                loop_cnt += 1
                if loop_cnt == len(geoloc_tokens):
                    break

                while geoloc_tokens[loop_cnt].ent_iob_ == "I":
                    full_entity.append(geoloc_tokens[loop_cnt])
                    loop_cnt += 1

                    if loop_cnt == len(geoloc_tokens):
                        break

            merged_geoloc_tokens.append(full_entity)
            continue

        loop_cnt += 1

    anonymization_results: t.List[AnonymizationResult] = []
    geoloc_lemmas = set(["plac", "skwer", "park", "rondo"])
    for tokens in merged_geoloc_tokens:
        geoloc_text = " ".join([token.text for token in tokens])

        anonymization = ""
        lemmas = set([token.lemma_ for token in tokens])
        if "ul" in [token.text for token in tokens]:
            anonymization = "ul. (...)"
        elif len(geoloc_lemmas.intersection(lemmas)) != 0:
            geoloc_name = tokens[0].text
            anonymization = f"{geoloc_name} (...)"
        else:
            for token in tokens:
                if token.text[0].isupper():
                    anonymization = f"{anonymization} {token.text[0]}."
                    break
                anonymization = f"{anonymization} {token.text}"

        res = AnonymizationResult(
            entity=geoloc_text.replace("ul . ", "ul. "),
            anonymization=anonymization,
            anon_type="geoloc",
        )

        anonymization_results.append(res)

    return anonymization_results
