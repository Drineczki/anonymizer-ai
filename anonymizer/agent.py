import os
import typing as t
from dataclasses import dataclass

import spacy


@dataclass
class AnonymizationResult:
    entity: str
    anonymization: str


class DocumentAnonymizer:
    def __init__(self, spacy_pipeline_path: str):
        self.nlp = spacy.load(spacy_pipeline_path, disable=["tagger", "textcat", "parser"])

    def anonymize(self, text: str) -> t.List[AnonymizationResult]:
        text = self._preprocess(text)
        nlp_results = self.nlp(text)

        return nlp_results

    def _preprocess(self, text: str) -> str:
        text = text.strip()

        return text
