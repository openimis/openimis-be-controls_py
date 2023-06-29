import os

from django.db import connection
from django.test import TestCase

import graphene
from graphene.test import Client

from controls.models import Control
from controls.schema import Query

class ModelsTestCase(TestCase):
  DEFAULT_NAME = 'a_field'
  DEFAULT_ADJUSTABILITY = Control.Adjustability.OPTIONAL
  DEFAULT_USAGE = 'a_form'

  def setUp(self):
    if "PYTEST_CURRENT_TEST" in os.environ:
      cursor = connection.cursor()
      cursor.execute("CREATE TABLE tblControls (FieldName nvarchar(50) NOT NULL, Adjustibility nvarchar(1) NOT NULL, Usage nvarchar(200) NULL, CONSTRAINT PK_tblControls PRIMARY KEY (FieldName ASC ))")
      print(cursor.fetchall())
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

  def tearDown(self):
    if "PYTEST_CURRENT_TEST" in os.environ:
      cursor = connection.cursor()
      cursor.execute("DROP TABLE tblControls;")
      print(cursor.fetchall())

  def test_query_without_any_control(self):
    client = Client(self.control_schema)
    executed = client.execute(self.query)
    self.assertEqual(executed, {'data': {'control': {'edges': []}}})

  def test_query_with_one_control(self):
    Control.objects.create(
      name=ModelsTestCase.DEFAULT_NAME,
      adjustability=ModelsTestCase.DEFAULT_ADJUSTABILITY,
      usage=ModelsTestCase.DEFAULT_USAGE)

    client = Client(self.control_schema)
    executed = client.execute(self.query)
    self.assertEqual(
      executed,
      {
        'data': {
          'control': {
            'edges': [
              {
                'node': {
                  'name': 'a_field'
                }
              }
            ]
          }
        }
      })

  def test_query_with_several_controls(self):
    for nbr in range(1, 4):
      Control.objects.create(
        name=f'{ModelsTestCase.DEFAULT_NAME}_{nbr}',
        adjustability=ModelsTestCase.DEFAULT_ADJUSTABILITY,
        usage=ModelsTestCase.DEFAULT_USAGE)

    client = Client(self.control_schema)
    executed = client.execute(self.query)
    self.assertEqual(
      executed, 
      {
        'data': {
          'control': {
            'edges': [
              {
                'node': {
                  'name': 'a_field_1'
                }
              },
              {
                'node': {
                  'name': 'a_field_2'
                }
              },
              {
                'node': {
                  'name': 'a_field_3'
                }
              }
            ]
          }
        }
      })



