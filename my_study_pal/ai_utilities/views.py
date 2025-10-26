from rest_framework import mixins, viewsets, decorators, response
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from my_study_pal.ai_utilities.ai_agents import AIAgentClientManager
from my_study_pal.ai_utilities.models import Settings, AiModel
from my_study_pal.ai_utilities.serializers import UserQuestionSerializer, SettingsSerializer


class ClassifyMessage(CreateAPIView):
    serializer_class = UserQuestionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ai_model = request.user.settings.ai_model
        user_question = serializer.validated_data['user_question']
        classification_data = AIAgentClientManager(ai_agent=ai_model).get_massage_classification_data(user_question,
                                                                                                      self.request.user.id)
        return Response(classification_data)


class SettingsView(mixins.UpdateModelMixin, mixins.RetrieveModelMixin ,viewsets.GenericViewSet):
    serializer_class = SettingsSerializer
    queryset = Settings.objects.all()


    def get_queryset(self):
        return self.queryset.filter( user=self.request.user)

    def get_object(self):
        return self.get_queryset().first()

    def perform_update(self, serializer):
        instance =self.get_object()
        if not instance:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @decorators.action(detail=False, methods=["get"], url_path="", url_name="retrieve")
    def retrieve_settings(self, request, *args, **kwargs):
        """Return the current user's settings."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    @decorators.action(detail=False, methods=["get"])
    def ai_model_choices(self, request, *args, **kwargs):
        models = AiModel.objects.all()
        models_data = [{"key": model.id, "label": f"{model.name} ({model.model})"} for model in models]
        return response.Response(models_data)

    @decorators.action(detail=False, methods=["get"])
    def language_choices(self, request, *args, **kwargs):
        languages = Settings.LanguageChoices.choices
        languages_data = [{"key": language[0], "label": language[0]} for language in languages]
        return response.Response(languages_data)

