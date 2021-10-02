from dataclasses import dataclass


@dataclass
class AnonymizationResult:
    entity: str
    anonymization: str
