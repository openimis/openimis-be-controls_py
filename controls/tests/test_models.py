import os

if "PYTEST_CURRENT_TEST" in os.environ:
  import pytest

from django.db import connection
from django.test import TestCase

from controls.models import Control

# Create your tests here.
class ModelsTestCase(TestCase):
  DEFAULT_NAME = 'a_field'
  DEFAULT_ADJUSTABILITY = Control.Adjustability.OPTIONAL
  DEFAULT_USAGE = 'a_form'

  def setUp(self):
    if "PYTEST_CURRENT_TEST" in os.environ:
      cursor = connection.cursor()
      cursor.execute("CREATE TABLE tblControls (FieldName nvarchar(50) NOT NULL, Adjustibility nvarchar(1) NOT NULL, Usage nvarchar(200) NULL, CONSTRAINT PK_tblControls PRIMARY KEY (FieldName ASC ))")
      print(cursor.fetchall())

  def tearDown(self):
    if "PYTEST_CURRENT_TEST" in os.environ:
      cursor = connection.cursor()
      cursor.execute("DROP TABLE tblControls;")
      print(cursor.fetchall())

  def test_basic_creation(self):
    control = Control.objects.create(
      name=ModelsTestCase.DEFAULT_NAME,
      adjustability=ModelsTestCase.DEFAULT_ADJUSTABILITY,
      usage=ModelsTestCase.DEFAULT_USAGE)

    self.assertEqual(control.name, 'a_field')
    self.assertEqual(control.adjustability, Control.Adjustability.OPTIONAL)
    self.assertEqual(control.usage, 'a_form')
    self.assertEqual(str(control), 'Field a_field (Optional) for forms a_form')
