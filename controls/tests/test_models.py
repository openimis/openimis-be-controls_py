from django.test import TestCase
from django.core.exceptions import ValidationError

from controls.models import Control


class ModelsTestCase(TestCase):
    DEFAULT_NAME = 'a_field'
    DEFAULT_ADJUSTABILITY = Control.Adjustability.OPTIONAL
    DEFAULT_USAGE = 'a_form'

    def test_basic_creation(self):
        control = Control.objects.create(
            name=self.DEFAULT_NAME,
            adjustability=ModelsTestCase.DEFAULT_ADJUSTABILITY,
            usage=self.DEFAULT_USAGE)

        self.assertEqual(control.name, self.DEFAULT_NAME)
        self.assertEqual(control.adjustability, Control.Adjustability.OPTIONAL)
        self.assertEqual(control.usage, self.DEFAULT_USAGE)
        self.assertEqual(str(control), 'Field a_field (O) for forms a_form')

    def test_invalid_adjustability(self):
        invalid_adjustability_values = [
            'H',
            'Hidden',
            'None',
            'F',
        ]
        for invalid_value in invalid_adjustability_values:
            control = Control.objects.create(
                name=f'{ModelsTestCase.DEFAULT_NAME}_{invalid_value}',
                adjustability=invalid_value,
                usage=ModelsTestCase.DEFAULT_USAGE)
            with self.assertRaises(ValidationError) as context:
                control.clean_fields()

        valid_adjustability_values = [
            'O',
            'N',
            'M',
            'R'
        ]
        for valid_value in valid_adjustability_values:
            control = Control.objects.create(
                name=f'{ModelsTestCase.DEFAULT_NAME}_{valid_value}',
                adjustability=valid_value,
                usage=ModelsTestCase.DEFAULT_USAGE)
            try:
                control.clean_fields()
            except ValidationError:
                self.fail(f'A ValidationError has been raised for value {valid_value} when it shouldn\'t')
