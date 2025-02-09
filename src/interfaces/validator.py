from abc import ABC, abstractmethod


class SourceApplicationValidator(ABC):
    @abstractmethod
    def validate(self, source_app: str) -> bool:
        """Validate if the source application is supported"""
        pass
