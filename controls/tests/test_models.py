from django.db import connection
from django.test import TestCase

from controls.models import Control

# Create your tests here.
class ModelsTestCase(TestCase):
  DEFAULT_NAME = 'a_field'
  DEFAULT_ADJUSTABILITY = Control.Adjustability.OPTIONAL
  DEFAULT_USAGE = 'a_form'

  def test_basic_creation(self):
    control = Control.objects.create(
      name=ModelsTestCase.DEFAULT_NAME,
      adjustability=ModelsTestCase.DEFAULT_ADJUSTABILITY,
      usage=ModelsTestCase.DEFAULT_USAGE)

    self.assertEqual(control.name, 'a_field')
    self.assertEqual(control.adjustability, Control.Adjustability.OPTIONAL)
    self.assertEqual(control.usage, 'a_form')
    self.assertEqual(str(control), 'Field a_field (Optional) for forms a_form')
