"""
Garde-fous sur la declaration des droits de `controls`.

Meme structure que `core` et `claim` : `DJANGO_PERMS` par entite puis par action,
`_PERM_CFG` qui en derive les cles de config, et `Control.get_rights` qui n'est qu'un
point d'acces.

Ce que ces tests protegent est silencieux plutot que bruyant :
  * `has_perms([])` renvoie True, donc une liste de droits vide n'interdit rien : elle
    accorde la lecture du parametrage a tout le monde, y compris anonymement - ce qui
    etait exactement l'etat de `control` et `control_str` avant 211001 ;
  * une cle de config sans attribut de classe n'est jamais chargee par `_load_config`
    et sa lecture leve AttributeError - le droit devient inapplicable ;
  * l'entier est ce que porte un role (`RoleRight.right_id`) : en changer un revoque
    l'acces de tous les roles qui le detiennent.
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

# Le catalogue de l'assemblage, pas celui du paquet : les modules sont installes depuis
# un arbre separe, donc il se resout depuis BASE_DIR.
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
        Le nom `query` doit etre celui que django genere au post_migrate
        (`<app_label>.view_<model>`), sinon il ne pourra jamais etre accorde.
        """
        model = django_apps.get_model("controls", "Control")
        self.assertEqual(
            DJANGO_PERMS["control"]["query"][0],
            f"{model._meta.app_label}.view_{model._meta.model_name}",
        )

    def test_every_declared_right_id_is_in_the_permissions_map(self):
        """
        La carte est ce depuis quoi le solution builder seme les roles : un identifiant
        absent ne peut etre accorde a personne.
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
