import graphene
from django.db.models import Q
from graphene_django.filter import DjangoFilterConnectionField

from controls.gql_mutations import MobileEnrollmentMutation
from controls.gql_queries import ControlGQLType
from controls.models import Control


class Query(graphene.ObjectType):
    control = DjangoFilterConnectionField(ControlGQLType)
    control_str = DjangoFilterConnectionField(
        ControlGQLType,
        str=graphene.String()
    )

    def resolve_control_str(self, info, **kwargs):
        search_str = kwargs.get('str')
        if search_str is not None:
            return Control.objects \
                .filter(
                Q(adjustability__icontains=search_str) | Q(name__icontains=search_str) | Q(usage__icontains=search_str))
        else:
            return Control.objects


class Mutation(graphene.ObjectType):
    mobile_enrollment = MobileEnrollmentMutation.Field()
