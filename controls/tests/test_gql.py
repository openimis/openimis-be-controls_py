import os

from django.db import connection
from django.test import TestCase

import graphene
from graphene.test import Client

from controls.models import Control
from controls.schema import Query


# `Query.control` exige desormais un droit, comme son jumeau `control_str` : le champ
# etait le seul point d'entree du module sans controle. Ces tests appelaient
# `client.execute(...)` sans contexte du tout - ils ne passaient que grace a cette
# absence de garde. `Query._check_permissions` ne lit que `user.id` et
# `user.has_perms`, d'ou ce doublure minimal plutot qu'un utilisateur complet (les
# reglages de test du module n'installent que `controls`).
class _StubUser:
  def __init__(self, granted=True):
    self.id = 1
    self._granted = granted

  def has_perms(self, perm_list, **kwargs):
    return self._granted


class _StubContext:
  def __init__(self, user):
    self.user = user


AUTHORIZED = _StubContext(_StubUser(granted=True))
UNAUTHORIZED = _StubContext(_StubUser(granted=False))

class ModelsTestCase(TestCase):
  DEFAULT_NAME = 'a_field'
  DEFAULT_ADJUSTABILITY = Control.Adjustability.OPTIONAL
  DEFAULT_USAGE = 'a_form'


  LOCAL_TEST_DATA_NAME = [DEFAULT_NAME]
  FULL_TEST_DATA_NAME = ['Age', 'AntenatalAmountLeft', 'ApprovalOfSMS',
    'BeneficiaryCard', 'Ceiling1', 'Ceiling2', 'CHFID', 'ClaimAdministrator',
    'Confirmation', 'ConfirmationNo', 'ConsultationAmountLeft',
    'ContributionCategory', 'CurrentAddress', 'CurrentDistrict',
    'CurrentMunicipality', 'CurrentVillage', 'Ded1', 'Ded2', 'DeliveryAmountLeft',
    'DistrictOfFSP', 'DOB', 'Education', 'ExpiryDate', 'FamilyType',
    'FirstServicePoint', 'FSP', 'FSPCategory', 'FSPDistrict', 'Gender',
    'GuaranteeNo', 'HFLevel', 'HospitalizationAmountLeft', 'IdentificationNumber',
    'IdentificationType', 'InsureeEmail', 'LastName', 'lblItemCode', 'lblItemCodeL',
    'lblItemLeftL', 'lblItemMinDate', 'lblServiceLeft', 'lblServiceMinDate',
    'MaritalStatus', 'OtherNames', 'PermanentAddress', 'PolicyStatus', 'Poverty',
    'ProductCode', 'Profession', 'RegionOfFSP', 'Relationship',
    'SurgeryAmountLeft', 'TotalAdmissionsLeft', 'TotalAmount', 'TotalAntenatalLeft',
    'TotalConsultationsLeft', 'TotalDelivieriesLeft', 'TotalSurgeriesLeft',
    'TotalVisitsLeft', 'Vulnerability']

  def generate_expected(self, names):
    return {
        'data': {
          'control': {
            'edges': [
              {
                'node': {
                  'name': name
                }
              } for name in names
            ]
          }
        }
      }

  def setUp(self):
    self.query = """
    {
      control{
        edges{
          node{
            name
          }
        }
      }
    }
    """
    self.control_schema = graphene.Schema(query=Query)
    self.maxDiff = None
    self.isolated_tests = "PYTEST_CURRENT_TEST" in os.environ
    self.controls = []

  def tearDown(self):
    if isinstance(self.controls, list) and len(self.controls)>0:
      for control in self.controls:
        if control.name:
          control.delete()
        else:
          pass

  # def test_query_without_any_new_control(self):
  #   client = Client(self.control_schema)
  #   executed = client.execute(self.query, context=AUTHORIZED)
  #   self.assertEqual(executed, self.generate_expected([] if self.isolated_tests else self.FULL_TEST_DATA_NAME))

  def test_query_with_one_control(self):


    client = Client(self.control_schema)
    before_executed = client.execute(self.query, context=AUTHORIZED)
    self.controls.append(
      Control.objects.create(
        name=ModelsTestCase.DEFAULT_NAME,
        adjustability=ModelsTestCase.DEFAULT_ADJUSTABILITY,
        usage=ModelsTestCase.DEFAULT_USAGE))
    executed = client.execute(self.query, context=AUTHORIZED)
    self.assertEqual(
      len(before_executed['data']['control']['edges'])+ 1,
      len(executed['data']['control']['edges']) )
    self.tearDown()

  def test_query_with_several_controls(self):
    TEST_DATA_NAMES = []
    client = Client(self.control_schema)
    before_executed = client.execute(self.query, context=AUTHORIZED)
    for nbr in range(1, 4):
      name = f'{ModelsTestCase.DEFAULT_NAME}_{nbr}'
      self.controls.append(
        Control.objects.create(
          name=name,
          adjustability=ModelsTestCase.DEFAULT_ADJUSTABILITY,
          usage=ModelsTestCase.DEFAULT_USAGE))
      TEST_DATA_NAMES.append(name)

    executed = client.execute(self.query, context=AUTHORIZED)
    self.assertEqual(
      len(before_executed['data']['control']['edges'])+ 3,
      len(executed['data']['control']['edges']) )

    self.tearDown()

  def test_query_without_the_right_is_refused(self):
    """Le champ `control` etait expose sans aucun droit : il ne doit plus l'etre."""
    client = Client(self.control_schema)
    executed = client.execute(self.query, context=UNAUTHORIZED)
    self.assertIn('errors', executed)
    self.assertIn('Unauthorized', str(executed['errors']))
    self.assertIsNone(executed.get('data', {}).get('control'))
