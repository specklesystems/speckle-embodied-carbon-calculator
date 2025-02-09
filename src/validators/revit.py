from src.interfaces.validator import SourceApplicationValidator


class RevitSourceValidator(SourceApplicationValidator):
    """Validates that the source application is Revit"""

    # ℹ️ sourceApplication value for v2: AppName + Version => Revit2024, Revit2023 etc.
    # ℹ️ sourceApplication value for v3: slug => revit
    # ⚠️ We're just working with v3 data - adapt commit_processor for v2 data structure if you want
    # ⚠️ Alternatively, write a model factory that injects the correct CommitProcessor()
    def validate(self, source_app: str) -> bool:
        return source_app == "revit"
