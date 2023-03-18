from django.apps import AppConfig


class CaseManagementConfig(AppConfig):
    name = 'case_management'

    def ready(self):
        import case_management.signals
        pass
