from django.db import models
from django.db import models

# Create your models here.
class Control(models.Model):
    name = models.CharField(db_column='FieldName', primary_key=True, max_length=50)
    adjustability = models.CharField(db_column='Adjustibility', max_length=1)
    usage = models.CharField(db_column='Usage', max_length=200)

    def __str__(self):
        return f'Field {self.name} ({self.adjustability}) for forms {self.usage}'

    @classmethod
    def filter_queryset(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()
        return queryset

    @classmethod
    def get_queryset(cls, queryset, user):
        queryset = Diagnosis.filter_queryset(queryset)
        # GraphQL calls with an info object while Rest calls with the user itself
        if isinstance(user, ResolveInfo):
            user = user.context.user
        if settings.ROW_SECURITY and user.is_anonymous:
            return queryset.filter(name='')

        return queryset

    class Meta:
        managed = False
        db_table = 'tblControls'