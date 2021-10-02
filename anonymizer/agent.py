import typing as t

import spacy

import anonymizer.people_anonymization as peo_anon
import anonymizer.places_anonymization as pla_anon
from anonymizer.result import AnonymizationResult


class DocumentAnonymizer:
    def __init__(self, spacy_pipeline_path: str):
        self.nlp = spacy.load(spacy_pipeline_path, disable=["tagger", "textcat", "parser"])

    def anonymize(self, text: str) -> t.List[AnonymizationResult]:
        text = self._preprocess(text)
        nlp_results = self.nlp(text)

        if len(nlp_results) == 0:
            return []

        people_anonymization = peo_anon.anonymize_people(nlp_results)
        place_anonymization = pla_anon.anonymize_places(nlp_results)

        return self._postprocess([*people_anonymization, *place_anonymization])

    def _preprocess(self, text: str) -> str:
        text = text.strip()
        return text

    def _postprocess(self, raw_outputs: t.List[AnonymizationResult]) -> t.List[AnonymizationResult]:
        postprocessed = [
            AnonymizationResult(
                entity=output.entity.replace(" - ", "-"),
                anonymization=output.anonymization,
                anon_type=output.anon_type,
            )
            for output in raw_outputs
        ]

        return postprocessed
