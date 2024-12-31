import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from rest_framework import generics
from rest_framework.exceptions import NotFound
from django.contrib.auth.hashers import check_password
from django.conf import settings
logger = logging.getLogger(__name__) 
import jwt
from datetime import datetime, timedelta
from accounts.models import *
from django.core.mail import send_mail
from decouple import config  
from rest_framework.generics import ListAPIView
# Create your views here.
class CompanyLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email_address = request.data.get('email')
        password = request.data.get('password')

        if not email_address or not password:
            return Response({'error': 'Email and password must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            company = Company.objects.get(email_address=email_address)

            
            if not check_password(password, company.password):
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

            
            access_payload = {
                'id': company.id,
                'email': company.email_address,
                'exp': datetime.utcnow() + timedelta(days=30),
            }

            access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')

         
            refresh_payload = {
                'id': company.id,
                'email': company.email_address,
                'exp': datetime.utcnow() + timedelta(days=365),
            }

            refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

            return Response({
                'access': access_token,
                'refresh': refresh_token,
            }, status=status.HTTP_200_OK)

        except Company.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        
class UserCreate(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get all users
class UserList(APIView):
    def get(self, request):
        users = Users.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

# Get a user by ID
class UserDetail(APIView):
    def get(self, request, pk):
        try:
            user = Users.objects.get(pk=pk)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)

# Edit a user
class UserUpdate(APIView):
    def put(self, request, pk):
        try:
            user = Users.objects.get(pk=pk)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class UserDelete(APIView):
    def delete(self, request, pk):
        try:
            user = Users.objects.get(pk=pk)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class PolicyDocumentationListView(APIView):
    def get(self, request):
        documentation = PolicyDocumentation.objects.all()
        serializer = DocumentationSerializer(documentation, many=True)
        return Response(serializer.data)

 
class PolicyDocumentationDetailView(APIView):
    def get(self, request, pk):
        try:
            documentation = PolicyDocumentation.objects.get(pk=pk)
        except PolicyDocumentation.DoesNotExist:
            return Response({"error": "Documentation not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = DocumentationSerializer(documentation)
        return Response(serializer.data)

 
class PolicyDocumentationCreateView(APIView):
    def post(self, request):
        serializer = DocumentationSerializer(data=request.data)
        if serializer.is_valid():
       
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class PolicyDocumentationUpdateView(APIView):
    def put(self, request, pk):
        try:
            documentation = PolicyDocumentation.objects.get(pk=pk)
        except PolicyDocumentation.DoesNotExist:
            return Response({"error": "Documentation not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DocumentationSerializer(documentation, data=request.data)
        if serializer.is_valid():
            serializer.save()   
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class PolicyDocumentationDeleteView(APIView):
    def delete(self, request, pk):
        try:
            documentation = PolicyDocumentation.objects.get(pk=pk)
        except PolicyDocumentation.DoesNotExist:
            return Response({"error": "Documentation not found"}, status=status.HTTP_404_NOT_FOUND)
        
        documentation.delete()   
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AddTrainingView(generics.CreateAPIView):
   
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        training = serializer.save()

       
        if training.send_notification:
            self.send_notifications(training)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def send_notifications(self, training):
        
        recipients = set()

       
        if training.evaluation_by:
            recipients.add(training.evaluation_by.email)
        if training.requested_by:
            recipients.add(training.requested_by.email)

         
        attendees = training.training_attendees.all()
        recipients.update(attendee.email for attendee in attendees)

      
        for email in recipients:
            send_mail(
                subject=f"Notification for Training: {training.training_title}",
                message=(
                    f"Dear User,\n\nYou are notified about the training:\n\n"
                    f"Title: {training.training_title}\n"
                    f"Venue: {training.venue}\n"
                    f"Date Planned: {training.date_planned}\n"
                    f"Start Time: {training.start_time}\n"
                    f"End Time: {training.end_time}\n\n"
                    f"Best regards,\nTraining Team"
                ),
                from_email=config('EMAIL_HOST_USER'),  
                recipient_list=[email],
                fail_silently=False,
            )

class TrainingListView(generics.ListAPIView):
   
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer

 
class TrainingDetailView(generics.RetrieveAPIView):
    
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer

 
class EditTrainingView(generics.UpdateAPIView):
   
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer

 
class DeleteTrainingView(generics.DestroyAPIView):
 
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    
class UserTrainingListView(ListAPIView):
    serializer_class = TrainingSerializer
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if not user_id:
            raise NotFound("User ID is required.")
        try:        
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            raise NotFound("User not found.")        
        return Training.objects.filter(training_attendees=user)


class UserTrainingEvaluationView(ListAPIView):
    serializer_class = TrainingSerializer
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if not user_id:
            raise NotFound("User ID is required.")
        try:        
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            raise NotFound("User not found.")        
        return Training.objects.filter(evaluation_by=user)


class EmployeeEvaluationCreateView(generics.CreateAPIView):
    queryset = EmployeeEvaluation.objects.all()
    serializer_class = EmployeeEvaluationSerializer

 
class EmployeeEvaluationListView(generics.ListAPIView):
    queryset = EmployeeEvaluation.objects.all()
    serializer_class = EmployeeEvaluationSerializer

 
class EmployeeEvaluationDetailView(generics.RetrieveAPIView):
    queryset = EmployeeEvaluation.objects.all()
    serializer_class = EmployeeEvaluationSerializer

 
class EmployeeEvaluationUpdateView(generics.UpdateAPIView):
    queryset = EmployeeEvaluation.objects.all()
    serializer_class = EmployeeEvaluationSerializer

 
class EmployeeEvaluationDeleteView(generics.DestroyAPIView):
    queryset = EmployeeSurvey.objects.all()
    serializer_class = EmployeeEvaluationSerializer
    
    
class EmployeeSurveyCreateView(generics.CreateAPIView):
    queryset = EmployeeSurvey.objects.all()
    serializer_class = EmployeeSurveySerializer

 
class EmployeeSurveyListView(generics.ListAPIView):
    queryset = EmployeeSurvey.objects.all()
    serializer_class = EmployeeSurveySerializer

 
class EmployeeSurveyDetailView(generics.RetrieveAPIView):
    queryset = EmployeeSurvey.objects.all()
    serializer_class = EmployeeSurveySerializer

 
class EmployeeSurveyUpdateView(generics.UpdateAPIView):
    queryset = EmployeeSurvey.objects.all()
    serializer_class = EmployeeSurveySerializer

 
class EmployeeSurveyDeleteView(generics.DestroyAPIView):
    queryset = EmployeeSurvey.objects.all()
    serializer_class = EmployeeSurveySerializer
    
    


class AwarenessCreateView(generics.CreateAPIView):
    queryset = AwarenessTraining.objects.all()
    serializer_class = AwarenessSerializer

 
class AwarenessListView(generics.ListAPIView):
    queryset = AwarenessTraining.objects.all()
    serializer_class = AwarenessSerializer

 
class AwarenessDetailView(generics.RetrieveAPIView):
    queryset = AwarenessTraining.objects.all()
    serializer_class = AwarenessSerializer

 
class AwarenessUpdateView(generics.UpdateAPIView):
    queryset = AwarenessTraining.objects.all()
    serializer_class = AwarenessSerializer

 
class AwarenessDeleteView(generics.DestroyAPIView):
    queryset = AwarenessTraining.objects.all()
    serializer_class = AwarenessSerializer
    
    
class AgendaListCreateView(APIView):
   
    def get(self, request):
        agendas = Agenda.objects.all()
        serializer = AgendaSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AgendaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class AgendaDetailView(APIView):
 
    def get_object(self, pk):
        try:
            return Agenda.objects.get(pk=pk)
        except Agenda.DoesNotExist:
            return None

    def get(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AgendaSerializer(agenda)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AgendaSerializer(agenda, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda.delete()
        return Response({"message": "Agenda deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class MeetingListCreateView(APIView):
  
    def get(self, request):
        meetings = Meeting.objects.all()
        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MeetingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeetingDetailView(APIView):
    
    def get_object(self, pk):
        try:
            return Meeting.objects.get(pk=pk)
        except Meeting.DoesNotExist:
            return None

    def get(self, request, pk):
        meeting = self.get_object(pk)
        if not meeting:
            return Response({"error": "Meeting not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MeetingSerializer(meeting)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        meeting = self.get_object(pk)
        if not meeting:
            return Response({"error": "Meeting not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MeetingSerializer(meeting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        meeting = self.get_object(pk)
        if not meeting:
            return Response({"error": "Meeting not found."}, status=status.HTTP_404_NOT_FOUND)
        meeting.delete()
        return Response({"message": "Meeting deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    
class CauseListCreateView(APIView):
   
    def get(self, request):
        agendas = Cause.objects.all()
        serializer = CauseSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CauseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CauseDetailView(APIView):
 
    def get_object(self, pk):
        try:
            return Cause.objects.get(pk=pk)
        except Cause.DoesNotExist:
            return None

    def get(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Cause not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CauseSerializer(agenda)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Cause not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CauseSerializer(agenda, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Cause not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda.delete()
        return Response({"message": "Cause deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class InternalProblemsListCreateView(APIView):
  
    def get(self, request):
        meetings = InternalProblems.objects.all()
        serializer = InternalProblemsSerializer(meetings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = InternalProblemsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InternalProblemsDetailView(APIView):
    
    def get_object(self, pk):
        try:
            return InternalProblems.objects.get(pk=pk)
        except InternalProblems.DoesNotExist:
            return None

    def get(self, request, pk):
        meeting = self.get_object(pk)
        if not meeting:
            return Response({"error": "InternalProblemsnot found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InternalProblemsSerializer(meeting)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        meeting = self.get_object(pk)
        if not meeting:
            return Response({"error": "InternalProblems not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InternalProblemsSerializer(meeting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        meeting = self.get_object(pk)
        if not meeting:
            return Response({"error": "InternalProblems not found."}, status=status.HTTP_404_NOT_FOUND)
        meeting.delete()
        return Response({"message": "InternalProblems deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class CarNumberListCreateView(APIView):
   
    def get(self, request):
        car_numbers = CarNumber.objects.all()
        serializer = CarNumberSerializer(car_numbers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CarNumberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CarNumberDetailView(APIView):
   
    def get_object(self, pk):
        try:
            return CarNumber.objects.get(pk=pk)
        except CarNumber.DoesNotExist:
            return None

    def get(self, request, pk):
        car_number = self.get_object(pk)
        if not car_number:
            return Response({"error": "CarNumber not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CarNumberSerializer(car_number)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        car_number = self.get_object(pk)
        if not car_number:
            return Response({"error": "CarNumber not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CarNumberSerializer(car_number, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        car_number = self.get_object(pk)
        if not car_number:
            return Response({"error": "CarNumber not found."}, status=status.HTTP_404_NOT_FOUND)
        car_number.delete()
        return Response({"message": "CarNumber deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class AuditListCreateView(APIView):
    def get(self, request):
        audits = Audit.objects.all()
        serializer = AuditSerializer(audits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AuditSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuditDetailView(APIView):
    def get_object(self, pk):
        try:
            return Audit.objects.get(pk=pk)
        except Audit.DoesNotExist:
            return None

    def get(self, request, pk):
        audit = self.get_object(pk)
        if not audit:
            return Response({"error": "Audit not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AuditSerializer(audit)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        audit = self.get_object(pk)
        if not audit:
            return Response({"error": "Audit not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AuditSerializer(audit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        audit = self.get_object(pk)
        if not audit:
            return Response({"error": "Audit not found."}, status=status.HTTP_404_NOT_FOUND)
        audit.delete()
        return Response({"message": "Audit deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class InspectionListCreate(APIView):
  
    def get(self, request):
        inspections = Inspection.objects.all()
        serializer = InspectionSerializer(inspections, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InspectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InspectionRetrieveUpdateDelete(APIView):
   
    def get_object(self, pk):
        try:
            return Inspection.objects.get(pk=pk)
        except Inspection.DoesNotExist:
            return None

    def get(self, request, pk):
        inspection = self.get_object(pk)
        if inspection:
            serializer = InspectionSerializer(inspection)
            return Response(serializer.data)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        inspection = self.get_object(pk)
        if inspection:
            serializer = InspectionSerializer(inspection, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        inspection = self.get_object(pk)
        if inspection:
            inspection.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    


class CustomerListCreate(APIView):
  
    def get(self, request):
        inspections = Customer.objects.all()
        serializer = CustomerSerializer(inspections, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerRetrieveUpdateDelete(APIView):
   
    def get_object(self, pk):
        try:
            return Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return None

    def get(self, request, pk):
        inspection = self.get_object(pk)
        if inspection:
            serializer = CustomerSerializer(inspection)
            return Response(serializer.data)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        inspection = self.get_object(pk)
        if inspection:
            serializer = CustomerSerializer(inspection, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        inspection = self.get_object(pk)
        if inspection:
            inspection.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    
class CategoryListCreateView(APIView):
   
    def get(self, request):
        agendas = Category.objects.all()
        serializer = CategorySerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CategoryDetailView(APIView):
 
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(agenda)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(agenda, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda.delete()
        return Response({"message": "Agenda deleted successfully."}, status=status.HTTP_204_NO_CONTENT)