import typing as t

import spacy

import anonymizer.people_anonymization as peo_anon
import anonymizer.places_anonymization as pla_anon
import anonymizer.internet_anonymization as inter_anon
import anonymizer.numerical_anonymization as num_anon
from anonymizer.result import AnonymizationResult


class DocumentAnonymizer:

    # fmt: off
    NUMERIC_ANONYMIZATION_PATTERNS = [
        [{"TEXT": "KRS"}, {"LIKE_NUM": True}],  # KRS
        [{"TEXT": {"REGEX": "[0-9]{11}"}}],   # PESEL
        # [{"TEXT": "nr. rej."}, {"TEXT": {"REGEX": "[A-Z]{2, 3}"}}],  # Car plate
    ]

    INTERNET_ANONYMIZATION_PATTERNS = [
        [{"LIKE_EMAIL": True}],
        [{"LIKE_URL": True}]
    ]
    # fmt: on

    def __init__(self, spacy_pipeline_path: str):
        # Natural Language Processing pipeline
        self.nlp = spacy.load(spacy_pipeline_path, disable=["tagger", "textcat", "parser"])

        # Rule-based matching
        self.matcher = spacy.matcher.Matcher(self.nlp.vocab)
        self.matcher.add("numerical", DocumentAnonymizer.NUMERIC_ANONYMIZATION_PATTERNS)
        self.matcher.add("internet", DocumentAnonymizer.INTERNET_ANONYMIZATION_PATTERNS)

    def anonymize(self, text: str) -> t.List[AnonymizationResult]:
        text = self._preprocess(text)
        nlp_results = self.nlp(text)

        if len(nlp_results) == 0:
            return []

        people_anonymizations = self._postprocess(peo_anon.anonymize_people(nlp_results))
        places_anonymizations = self._postprocess(pla_anon.anonymize_places(nlp_results))

        matches = self.matcher(nlp_results)
        internet_matches = [
            match for match in matches if self.nlp.vocab.strings[match[0]] == "internet"
        ]
        internet_anonymizations = inter_anon.anonymize_internet(internet_matches, doc=nlp_results)

        numerical_matches = [
            match for match in matches if self.nlp.vocab.strings[match[0]] == "numerical"
        ]
        numeric_anonymizations = num_anon.anonymize_numerics(numerical_matches, doc=nlp_results)
        print(matches)
        return [
            *people_anonymizations,
            *places_anonymizations,
            *internet_anonymizations,
            *numeric_anonymizations,
        ]

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
