import typing as t

import spacy

import anonymizer.constants as c
from anonymizer.result import AnonymizationResult


def anonymize_numerics(
    matches_results: t.List[tuple], doc: t.Iterable[spacy.tokens.Token]
) -> t.List[AnonymizationResult]:
    if len(matches_results) == 0:
        return []

    anonymizations = []
    for match_id, start, end in matches_results:
        span = doc[start : end]

        anonymization = "(...)"
        if span[0].text in ["KRS", "VIN"]:
            anonymization = f"{span[0].text} {anonymization}"
        elif span[0].text == "PESEL":
            anonymization = f"{span[0].text}: {anonymization}"

        anonymizations.append(
            AnonymizationResult(entity=span.text, anonymization=anonymization, anon_type="numerical")
        )

    return anonymizations
