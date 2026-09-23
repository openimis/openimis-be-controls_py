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
        Les droits regissant une action sur un parametrage de champ.

        Ne redeclare rien : la table des droits est `controls.apps.DJANGO_PERMS`, par
        entite puis par action, et `configured_perms` y lit la valeur *configuree* -
        celle que ModuleConfiguration a pu surcharger - et non le defaut declare. Ce
        modele n'est que le point d'acces. Renvoie None pour une action non declaree,
        pour que l'appelant echoue ferme.
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
