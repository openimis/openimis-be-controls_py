from django.db import models

from core import models as core_models


class Control(models.Model):
    class Adjustability(models.TextChoices):
        OPTIONAL = 'O', 'Optional'
        MANDATORY = 'M', 'Mandatory'
        HIDDEN = 'N', 'Hidden'
        REQUIRED = 'R', 'Required'

    name = models.CharField(db_column='FieldName', primary_key=True, max_length=50)
    adjustability = models.CharField(db_column='Adjustibility',
                                     choices=Adjustability.choices,
                                     default=Adjustability.OPTIONAL,
                                     max_length=1)
    usage = models.CharField(db_column='Usage', max_length=200)

    def __str__(self):
        return f'Field {self.name} ({self.adjustability}) for forms {self.usage}'

    @classmethod
    def get_rights(cls, action):
        """
        The rights governing an action on a field setting.

        Redeclares nothing: the rights table is `controls.apps.DJANGO_PERMS`, by
        entity then by action, and `configured_perms` reads the *configured* value
        there - the one ModuleConfiguration may have overridden - and not the declared
        default. This model is only the access point. Returns None for an undeclared
        action, so that the caller fails closed.
        """
        from controls.apps import configured_perms

        return configured_perms("control", action)

    @classmethod
    def filter_queryset(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()
        return queryset

    @classmethod
    def get_queryset(cls, queryset, user):
        queryset = Control.filter_queryset(queryset)

        return queryset

    class Meta:
        managed = False
        db_table = 'tblControls'


class MobileEnrollmentMutation(core_models.UUIDModel, core_models.ObjectMutation):
    policy = models.ForeignKey("policy.Policy", models.DO_NOTHING, related_name='mobile_enrollment_mutations')
    mutation = models.ForeignKey("core.MutationLog", models.DO_NOTHING, related_name='mobile_enrollments')

    class Meta:
        managed = True
        db_table = "mobile_MobileEnrollmentMutation"
