from django.apps import AppConfig

from core.rights_declaration import RightsDeclaration

MODULE_NAME = "controls"


# Rights, by entity then by action. The module has only one entity, `control` - the
# form field settings - and a single action, reading: nothing here is written through
# GraphQL, `tblControls` being filled by the administration.
# 211001: the first right of this module, in a fresh block. `control` and `control_str`
# required nothing, not even authentication. Low-sensitivity reference data, but
# nothing justified anonymous access.
DJANGO_PERMS = {
    "control": {
        "query": ("controls.view_control", 211001),
    },
}

_PERM_CFG = {
    "gql_query_controls_perms": ("control", "query"),
}

RIGHTS = RightsDeclaration(MODULE_NAME, DJANGO_PERMS, _PERM_CFG)

perms = RIGHTS.perms
django_perms = RIGHTS.django_perm_names
configured_perms = RIGHTS.configured
require = RIGHTS.require


DEFAULT_CFG = {}


class ControlsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = MODULE_NAME

    # Rights: constants, no longer overridable. They go neither through DEFAULT_CFG
    # nor through ready(): `ModuleConfiguration.get_or_default` now ignores any
    # `_perms` key stored in the database.
    gql_query_controls_perms = RIGHTS.perms("control", "query")

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
