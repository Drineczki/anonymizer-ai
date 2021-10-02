import typing as t

import spacy

import anonymizer.constants as c
from anonymizer.result import AnonymizationResult


def anonymize_internet(
    matches_results: t.List[tuple], doc: t.Iterable[spacy.tokens.Token]
) -> t.List[AnonymizationResult]:
    if len(matches_results) == 0:
        return []

    anonymizations = []
    for match_id, start, end in matches_results:
        span = doc[start]

        anonymizations.append(
            AnonymizationResult(entity=span.text, anonymization="(...)", anon_type="internet")
        )

    return anonymizations
