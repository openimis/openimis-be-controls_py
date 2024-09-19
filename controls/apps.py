from django.apps import AppConfig

MODULE_NAME = "controls"

DEFAULT_CFG = {
    "gql_mutation_create_families_perms": ['101002'],
    "gql_mutation_update_families_perms": ['101003'],
    "gql_mutation_create_insurees_perms": ["101102"],
    "gql_mutation_update_insurees_perms": ["101103"],
    "gql_mutation_create_policies_perms": ['101202'],
    "gql_mutation_edit_policies_perms": ['101203'],
    "gql_mutation_renew_policies_perms": ["101205"],
    "gql_mutation_create_premiums_perms": ["101302"],
    "gql_mutation_update_premiums_perms": ["101303"],
}


class ControlsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = MODULE_NAME

    gql_mutation_create_families_perms = []
    gql_mutation_update_families_perms = []
    gql_mutation_create_insurees_perms = []
    gql_mutation_update_insurees_perms = []
    gql_mutation_create_policies_perms = []
    gql_mutation_edit_policies_perms = []
    gql_mutation_renew_policies_perms = []
    gql_mutation_create_premiums_perms = []
    gql_mutation_update_premiums_perms = []

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._load_config(cfg)

    @classmethod
    def _load_config(cls, cfg):
        """
        Load all config fields that match current AppConfig class fields, all custom fields have to be loaded separately
        """
        for field in cfg:
            if hasattr(ControlsConfig, field):
                setattr(ControlsConfig, field, cfg[field])
