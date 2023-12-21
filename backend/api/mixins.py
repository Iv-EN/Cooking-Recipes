from django.db.models import Model, Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)


class AddDelViewMixin:
    """Методы для добавления/удаления объекта связи между моделями."""

    add_serializer: ModelSerializer | None = None

    def _create_relation(self, model: Model, obj_id: int | str) -> Response:
        """Добавление связи М2М между объектами."""
        if model.__name__ == 'Subscriptions':
            queryset = self.queryset
        else:
            queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=obj_id)
        try:
            model(None, obj.pk, self.request.user.pk).save()
        except IntegrityError:
            return Response(
                {'error': 'Действие уже выполнено.'},
                status=HTTP_400_BAD_REQUEST,
            )
        serializer: ModelSerializer = self.add_serializer(obj)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def _delete_relation(self, model: Model, q: Q) -> Response:
        """Удаление связи М2М между объектами."""
        deleted, _ = (model.objects.filter(q).delete())
        if not deleted:
            return Response(
                {'error': f'{model.__name__} не существует'},
                status=HTTP_400_BAD_REQUEST,
            )
        return Response(status=HTTP_204_NO_CONTENT)
