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

        people_anonymization = self._anonymize_people(
            [token for token in nlp_results if token.ent_type_ == "persName"]
        )
        people_anonymization = self._postprocess_people_anonymizations(
            people_anonymization, nlp_results
        )

        return [*people_anonymization]

    def _preprocess(self, text: str) -> str:
        text = text.strip()
        return text

    def _anonymize_people(
        self, people_tokens: t.Iterable[spacy.tokens.Token]
    ) -> t.List[AnonymizationResult]:
        if len(people_tokens) == 0:
            return []

        merged_tokens: t.List[t.List[spacy.tokens.Token, ...]] = []

        loop_cnt = 0
        while loop_cnt < len(people_tokens):
            if people_tokens[loop_cnt].ent_iob_ == "B":
                full_entity = [people_tokens[loop_cnt]]
                loop_cnt += 1

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

            anonymization = f"{first_anonymization_char}. {second_anonymization_char}."
            res = AnonymizationResult(entity=person_text, anonymization=anonymization)

            anonymization_results.append(res)

        return anonymization_results
