from django.apps import AppConfig

from core.rights_declaration import RightsDeclaration

MODULE_NAME = "controls"


# Droits, par entite puis par action. Le module n'a qu'une entite, `control` - le
# parametrage des champs de formulaire - et qu'une action, la lecture : rien ici ne
# s'ecrit par GraphQL, `tblControls` est alimentee par l'administration.
# 211001 : premier droit de ce module, dans un bloc neuf. `control` et `control_str`
# n'exigeaient rien, pas meme l'authentification. Donnees de reference de faible
# sensibilite, mais rien ne justifiait l'acces anonyme.
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

    # Droits: constantes, plus surchargeables. Ils ne passent plus par le
    # DEFAULT_CFG ni par ready(): `ModuleConfiguration.get_or_default` ignore
    # desormais toute cle `_perms` stockee en base.
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
