from django.apps import AppConfig


class TargetManagementConfig(AppConfig):
    name = 'target_management'

    def ready(self):
        import target_management.signals
        pass
