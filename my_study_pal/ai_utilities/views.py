from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from my_study_pal.ai_utilities.ai_agents import AIAgentClientManager
from my_study_pal.ai_utilities.serializers import UserQuestionSerializer


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

