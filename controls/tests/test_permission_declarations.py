"""
Guard rails on `controls`' rights declaration.

Same structure as `core` and `claim`: `DJANGO_PERMS` by entity then by action,
`_PERM_CFG` deriving the config keys from it, and `Control.get_rights` which is only an
access point.

What these tests protect against is silent rather than loud:
  * `has_perms([])` returns True, so an empty rights list forbids nothing: it grants
    reading the settings to everybody, anonymously included - which is exactly the
    state `control` and `control_str` were in before 211001;
  * a config key with no class attribute is never loaded by `_load_config` and reading
    it raises AttributeError - the right becomes unenforceable;
  * the integer is what a role carries (`RoleRight.right_id`): changing one revokes
    access for every role that holds it.
"""

import json
from pathlib import Path

from django.apps import apps as django_apps
from django.conf import settings
from django.test import TestCase

from controls.apps import (
    DJANGO_PERMS,
    ControlsConfig,
    _PERM_CFG,
    configured_perms,
    django_perms,
    perms,
)
from controls.models import Control

# The identifiers as deployed. Changing one is incompatible with the existing roles:
# this test has to be updated *and* the new right granted.
EXPECTED_RIGHTS = {
    "gql_query_controls_perms": ["211001"],
}

# The assembly's catalogue, not the package's: the modules are installed from a
# separate tree, so it is resolved from BASE_DIR.
PERMISSIONS_MAP = Path(settings.BASE_DIR) / "permissions_map.json"


class ControlsPermissionDeclarationTestCase(TestCase):
    def test_right_ids_unchanged(self):
        self.assertEqual(
            {key: getattr(ControlsConfig, key) for key in EXPECTED_RIGHTS},
            EXPECTED_RIGHTS,
        )

    def test_perm_cfg_covers_every_declared_action(self):
        declared = {
            (entity, action)
            for entity, actions in DJANGO_PERMS.items()
            for action in actions
        }
        self.assertEqual(set(_PERM_CFG.values()), declared)

    def test_perm_cfg_matches_config_attributes(self):
        """`_load_config` ignores the keys with no class attribute."""
        missing = [key for key in _PERM_CFG if not hasattr(ControlsConfig, key)]
        self.assertEqual(missing, [])

    def test_no_right_list_is_empty(self):
        empty = [key for key in _PERM_CFG if not getattr(ControlsConfig, key)]
        self.assertEqual(empty, [])

    def test_attributes_carry_the_declared_right(self):
        """
        The rights are constants set from DJANGO_PERMS: the attribute must equal the
        declaration, without going through the config.
        """
        for key, (entity, action) in _PERM_CFG.items():
            with self.subTest(key=key):
                self.assertEqual(getattr(ControlsConfig, key), perms(entity, action))

    def test_django_permission_names_are_unique(self):
        seen = {}
        for entity, actions in DJANGO_PERMS.items():
            for action, (name, _) in actions.items():
                seen.setdefault(name, []).append(f"{entity}.{action}")
        shared = {name: who for name, who in seen.items() if len(who) > 1}
        self.assertEqual(shared, {})

    def test_crud_django_names_match_the_real_model(self):
        """
        The `query` name has to be the one django generates at post_migrate
        (`<app_label>.view_<model>`), otherwise it can never be granted.
        """
        model = django_apps.get_model("controls", "Control")
        self.assertEqual(
            DJANGO_PERMS["control"]["query"][0],
            f"{model._meta.app_label}.view_{model._meta.model_name}",
        )

    def test_every_declared_right_id_is_in_the_permissions_map(self):
        """
        The map is what the solution builder seeds the roles from: a missing identifier
        can be granted to nobody.
        """
        catalog = set(json.loads(PERMISSIONS_MAP.read_text(encoding="utf-8")).values())
        missing = sorted(
            {
                rid
                for _, actions in DJANGO_PERMS.items()
                for _, (_, right_id) in actions.items()
                for rid in [str(right_id)]
                if rid not in catalog
            }
        )
        self.assertEqual(missing, [])

    def test_unknown_entity_or_action_raises(self):
        with self.assertRaises(KeyError):
            perms("nosuchentity", "query")
        with self.assertRaises(KeyError):
            perms("control", "nosuchaction")
        with self.assertRaises(KeyError):
            django_perms("control", "nosuchaction")

    # --- the access point through the model -------------------------------
    def test_model_exposes_every_action_of_its_entity(self):
        for action in DJANGO_PERMS["control"]:
            with self.subTest(action=action):
                self.assertEqual(
                    Control.get_rights(action), configured_perms("control", action)
                )
                self.assertTrue(Control.get_rights(action))

    def test_model_returns_none_for_an_undeclared_action(self):
        """None means "no rule": the caller must fail closed."""
        self.assertIsNone(Control.get_rights("nosuchaction"))

    def test_model_reads_the_configured_value_not_the_declared_default(self):
        """
        ModuleConfiguration may override a right; the check must read the configured
        value, where `perms()` returns the declared default.
        """
        original = ControlsConfig.gql_query_controls_perms
        try:
            ControlsConfig.gql_query_controls_perms = ["999999"]
            self.assertEqual(Control.get_rights("query"), ["999999"])
            self.assertEqual(perms("control", "query"), ["211001"])
        finally:
            ControlsConfig.gql_query_controls_perms = original
