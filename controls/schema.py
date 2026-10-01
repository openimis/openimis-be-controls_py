import graphene
from django.db.models import Q
from graphene_django.filter import DjangoFilterConnectionField

from django.contrib.auth.models import AnonymousUser

from controls.apps import ControlsConfig
from controls.gql_mutations import MobileEnrollmentMutation
from controls.gql_queries import ControlGQLType
from controls.models import Control


class Query(graphene.ObjectType):
    control = DjangoFilterConnectionField(ControlGQLType)
    control_str = DjangoFilterConnectionField(
        ControlGQLType,
        str=graphene.String()
    )

    # `control` had no resolver at all, and `ControlGQLType` has neither
    # `get_queryset` nor `ScopedQuerysetMixin`: so the model's `Control.get_queryset`
    # was never called either. The form settings were readable with no right at all,
    # anonymously included, while their twin `control_str` is guarded just below. Same
    # check for both.
    def resolve_control(self, info, **kwargs):
        Query._check_permissions(info.context.user)
        return Control.objects.all()

    def resolve_control_str(self, info, **kwargs):
        Query._check_permissions(info.context.user)
        search_str = kwargs.get('str')
        if search_str is not None:
            return Control.objects \
                .filter(
                Q(adjustability__icontains=search_str) | Q(name__icontains=search_str) | Q(usage__icontains=search_str))
        else:
            return Control.objects


    @staticmethod
    def _check_permissions(user):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                ControlsConfig.gql_query_controls_perms):
            raise PermissionError("Unauthorized")


class Mutation(graphene.ObjectType):
    mobile_enrollment = MobileEnrollmentMutation.Field()
