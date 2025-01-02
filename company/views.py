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
    

class ComplaintsView(APIView):
    def get(self, request):
        agendas = Complaints.objects.all()
        serializer = ComplaintsSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
 
        serializer = ComplaintsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ComplaintDetailView(APIView):
    def get_object(self, pk):
        try:
            return Complaints.objects.get(pk=pk)
        except Complaints.DoesNotExist:
            return None

    def get(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ComplaintsSerializer(agenda)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ComplaintsSerializer(agenda, data=request.data)
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
    
class QuestionView(APIView):
    def get(self, request):
        agendas = Question.objects.all()
        serializer = QuestionSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
 
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDetailView(APIView):
    def get_object(self, pk):
        try:
            return Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return None

    def get(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionSerializer(agenda)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionSerializer(agenda, data=request.data)
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
    


class CustomerSatisfactionView(APIView):
    def get(self, request):
        agendas = CustomerSatisfaction.objects.all()
        serializer = CustomerSatisfactionSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
       
        serializer = CustomerSatisfactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerSatisfactionDetailView(APIView):
    def get_object(self, pk):
        try:
            return CustomerSatisfaction.objects.get(pk=pk)
        except CustomerSatisfaction.DoesNotExist:
            return None

    def get(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "  not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerSatisfactionSerializer(agenda)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        print(request.data)
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": " not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerSatisfactionSerializer(agenda, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "  not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda.delete()
        return Response({"message": " deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class SupplierAPIView(APIView):
   
    def get(self, request):
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
 
    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SupplierDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Supplier.objects.get(pk=pk)
        except Supplier.DoesNotExist:
            return None

 
    def get(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierSerializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    def put(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        supplier.delete()
        return Response({"message": "Supplier deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class SupplierProblemAPIView(APIView):
 
    def post(self, request):
        serializer = SupplierProblemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def get(self, request):
        supplier_problems = SupplierProblem.objects.all()
        serializer = SupplierProblemSerializer(supplier_problems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SupplierProblemDetailAPIView(APIView):
   
    def get_object(self, pk):
        try:
            return SupplierProblem.objects.get(pk=pk)
        except SupplierProblem.DoesNotExist:
            return None

 
    def get(self, request, pk):
        supplier_problem = self.get_object(pk)
        if supplier_problem is None:
            return Response({"error": "SupplierProblem not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierProblemSerializer(supplier_problem)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
    def put(self, request, pk):
        supplier_problem = self.get_object(pk)
        if supplier_problem is None:
            return Response({"error": "SupplierProblem not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierProblemSerializer(supplier_problem, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  
    def delete(self, request, pk):
        supplier_problem = self.get_object(pk)
        if supplier_problem is None:
            return Response({"error": "SupplierProblem not found"}, status=status.HTTP_404_NOT_FOUND)
        supplier_problem.delete()
        return Response({"message": "SupplierProblem deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
 
class ComplianceAPIView(APIView):
   
    def post(self, request):
        serializer = ComplianceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
    def get(self, request):
        compliances = Compliance.objects.all()
        serializer = ComplianceSerializer(compliances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ComplianceDetailAPIView(APIView):
 
    def get_object(self, pk):
        try:
            return Compliance.objects.get(pk=pk)
        except Compliance.DoesNotExist:
            return None

 
    def get(self, request, pk):
        compliance = self.get_object(pk)
        if compliance is None:
            return Response({"error": "Compliance not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ComplianceSerializer(compliance)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
    def put(self, request, pk):
        compliance = self.get_object(pk)
        if compliance is None:
            return Response({"error": "Compliance not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ComplianceSerializer(compliance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
    def delete(self, request, pk):
        compliance = self.get_object(pk)
        if compliance is None:
            return Response({"error": "Compliance not found"}, status=status.HTTP_404_NOT_FOUND)
        compliance.delete()
        return Response({"message": "Compliance deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
 

class LegalRequirementsAPIView(APIView):
 
    def post(self, request):
        serializer = LegalRequirementsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
    def get(self, request):
        legal_requirements = LegalRequirements.objects.all()
        serializer = LegalRequirementsSerializer(legal_requirements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LegalRequirementsDetailAPIView(APIView):
 
    def get_object(self, pk):
        try:
            return LegalRequirements.objects.get(pk=pk)
        except LegalRequirements.DoesNotExist:
            return None

 
    def get(self, request, pk):
        legal_requirement = self.get_object(pk)
        if legal_requirement is None:
            return Response({"error": "Legal Requirement not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LegalRequirementsSerializer(legal_requirement)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
    def put(self, request, pk):
        legal_requirement = self.get_object(pk)
        if legal_requirement is None:
            return Response({"error": "Legal Requirement not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LegalRequirementsSerializer(legal_requirement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
    def delete(self, request, pk):
        legal_requirement = self.get_object(pk)
        if legal_requirement is None:
            return Response({"error": "Legal Requirement not found"}, status=status.HTTP_404_NOT_FOUND)
        legal_requirement.delete()
        return Response({"message": "Legal Requirement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


from django.shortcuts import get_object_or_404
class ComplianceEvaluationAPIView(APIView):
    def get(self, request, pk=None):
        
        if pk:
            compliance_evaluation = get_object_or_404(ComplianceEvaluation, pk=pk)
            serializer = ComplianceEvaluationSerializer(compliance_evaluation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            compliance_evaluations = ComplianceEvaluation.objects.all()
            serializer = ComplianceEvaluationSerializer(compliance_evaluations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
      
        serializer = ComplianceEvaluationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
      
        compliance_evaluation = get_object_or_404(ComplianceEvaluation, pk=pk)
        serializer = ComplianceEvaluationSerializer(compliance_evaluation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
   
        compliance_evaluation = get_object_or_404(ComplianceEvaluation, pk=pk)
        compliance_evaluation.delete()
        return Response({"message": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
 

class ManagementChangeAPIView(APIView):
    

    def get(self, request, pk=None):
      
        if pk:
            try:
                management_change = ManagementChange.objects.get(pk=pk)
                serializer = ManagementChangeSerializer(management_change)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ManagementChange.DoesNotExist:
                return Response({"error": "ManagementChange not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            management_changes = ManagementChange.objects.all()
            serializer = ManagementChangeSerializer(management_changes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
       
        serializer = ManagementChangeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
       
        try:
            management_change = ManagementChange.objects.get(pk=pk)
            serializer = ManagementChangeSerializer(management_change, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ManagementChange.DoesNotExist:
            return Response({"error": "ManagementChange not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        
        try:
            management_change = ManagementChange.objects.get(pk=pk)
            management_change.delete()
            return Response({"message": "ManagementChange deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ManagementChange.DoesNotExist:
            return Response({"error": "ManagementChange not found"}, status=status.HTTP_404_NOT_FOUND)



class SustainabilityListCreate(APIView):
 
    def get(self, request):
        sustainability = Sustainability.objects.all()
        serializer = SustainabilitySerializer(sustainability, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
    def post(self, request):
        serializer = SustainabilitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SustainabilityDetail(APIView):
 
    def get(self, request, pk):
        try:
            sustainability = Sustainability.objects.get(pk=pk)
        except Sustainability.DoesNotExist:
            raise NotFound("Sustainability record not found.")
        
        serializer = SustainabilitySerializer(sustainability)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
    def put(self, request, pk):
        try:
            sustainability = Sustainability.objects.get(pk=pk)
        except Sustainability.DoesNotExist:
            raise NotFound("Sustainability record not found.")
        
        serializer = SustainabilitySerializer(sustainability, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
    def delete(self, request, pk):
        try:
            sustainability = Sustainability.objects.get(pk=pk)
        except Sustainability.DoesNotExist:
            raise NotFound("Sustainability record not found.")
        
        sustainability.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ProcessActivityListCreate(APIView):
  
    def get(self, request):
        process_activities = ProcessActivity.objects.all()
        serializer = ProcessActivitySerializer(process_activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

  
    def post(self, request):
        serializer = ProcessActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessActivityDetail(APIView):
   
    def get(self, request, pk):
        try:
            process_activity = ProcessActivity.objects.get(pk=pk)
        except ProcessActivity.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        serializer = ProcessActivitySerializer(process_activity)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    def put(self, request, pk):
        try:
            process_activity = ProcessActivity.objects.get(pk=pk)
        except ProcessActivity.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        serializer = ProcessActivitySerializer(process_activity, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk):
        try:
            process_activity = ProcessActivity.objects.get(pk=pk)
        except ProcessActivity.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        process_activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


 
class EnvironmentalAspectView(APIView):
    def get(self, request):
 
        aspects = EnvironmentalAspect.objects.all()
        serializer = EnvironmentalAspectSerializer(aspects, many=True)
        return Response(serializer.data)

    def post(self, request):
 
        serializer = EnvironmentalAspectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


 
class EnvironmentalAspectDetailView(APIView):
    def get(self, request, pk):
        try:
            aspect = EnvironmentalAspect.objects.get(pk=pk)
        except EnvironmentalAspect.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnvironmentalAspectSerializer(aspect)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            aspect = EnvironmentalAspect.objects.get(pk=pk)
        except EnvironmentalAspect.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EnvironmentalAspectSerializer(aspect, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            aspect = EnvironmentalAspect.objects.get(pk=pk)
        except EnvironmentalAspect.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        aspect.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 
class EnvironmentalImpactView(APIView):
    def get(self, request):
   
        impacts = EnvironmentalImpact.objects.all()
        serializer = EnvironmentalImpactSerializer(impacts, many=True)
        return Response(serializer.data)

    def post(self, request):
      
        serializer = EnvironmentalImpactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class EnvironmentalImpactDetailView(APIView):
    def get(self, request, pk):
        try:
            impact = EnvironmentalImpact.objects.get(pk=pk)
        except EnvironmentalImpact.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnvironmentalImpactSerializer(impact)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            impact = EnvironmentalImpact.objects.get(pk=pk)
        except EnvironmentalImpact.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EnvironmentalImpactSerializer(impact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            impact = EnvironmentalImpact.objects.get(pk=pk)
        except EnvironmentalImpact.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        impact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RootCauseView(APIView):
    def get(self, request):
 
        root_causes = RootCause.objects.all()
        serializer = RootCauseSerializer(root_causes, many=True)
        return Response(serializer.data)

    def post(self, request):
  
        serializer = RootCauseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class RootCauseDetailView(APIView):
    def get(self, request, pk):
        try:
            root_cause = RootCause.objects.get(pk=pk)
        except RootCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RootCauseSerializer(root_cause)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            root_cause = RootCause.objects.get(pk=pk)
        except RootCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RootCauseSerializer(root_cause, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            root_cause = RootCause.objects.get(pk=pk)
        except RootCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        root_cause.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


 
class EnvironmentalIncidentsView(APIView):
    def get(self, request):
    
        incidents = EnvironmentalIncidents.objects.all()
        serializer = EnvironmentalIncidentsSerializer(incidents, many=True)
        return Response(serializer.data)

    def post(self, request):
 
        serializer = EnvironmentalIncidentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class EnvironmentalIncidentDetailView(APIView):
    def get(self, request, pk):
        try:
            incident = EnvironmentalIncidents.objects.get(pk=pk)
        except EnvironmentalIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnvironmentalIncidentsSerializer(incident)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            incident = EnvironmentalIncidents.objects.get(pk=pk)
        except EnvironmentalIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnvironmentalIncidentsSerializer(incident, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            incident = EnvironmentalIncidents.objects.get(pk=pk)
        except EnvironmentalIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        incident.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 
class EnvironmentalWasteView(APIView):
    def get(self, request):
       
        wastes = EnvironmentalWaste.objects.all()
        serializer = EnvironmentalWasteSerializer(wastes, many=True)
        return Response(serializer.data)

    def post(self, request):
 
        serializer = EnvironmentalWasteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class EnvironmentalWasteDetailView(APIView):
    def get(self, request, pk):
        try:
            waste = EnvironmentalWaste.objects.get(pk=pk)
        except EnvironmentalWaste.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnvironmentalWasteSerializer(waste)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            waste = EnvironmentalWaste.objects.get(pk=pk)
        except EnvironmentalWaste.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnvironmentalWasteSerializer(waste, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            waste = EnvironmentalWaste.objects.get(pk=pk)
        except EnvironmentalWaste.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        waste.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProcessHealthListCreate(APIView):
  
    def get(self, request):
        process_activities = ProcessHealth.objects.all()
        serializer = ProcessHealthSerializer(process_activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

  
    def post(self, request):
        serializer = ProcessHealthSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessHealthDetail(APIView):
   
    def get(self, request, pk):
        try:
            process_activity = ProcessHealth.objects.get(pk=pk)
        except ProcessHealth.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        serializer = ProcessHealthSerializer(process_activity)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    def put(self, request, pk):
        try:
            process_activity = ProcessHealth.objects.get(pk=pk)
        except ProcessHealth.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        serializer = ProcessHealthSerializer(process_activity, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk):
        try:
            process_activity = ProcessHealth.objects.get(pk=pk)
        except ProcessHealth.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        process_activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
 
class HealthSafetyView(APIView):
    def get(self, request):
       
        hazards = HealthSafety.objects.all()
        serializer = HealthSafetySerializer(hazards, many=True)
        return Response(serializer.data)

    def post(self, request):
       
        serializer = HealthSafetySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class HealthSafetyDetailView(APIView):
    def get(self, request, pk):
        try:
            hazard = HealthSafety.objects.get(pk=pk)
        except HealthSafety.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = HealthSafetySerializer(hazard)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            hazard = HealthSafety.objects.get(pk=pk)
        except HealthSafety.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = HealthSafetySerializer(hazard, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            hazard = HealthSafety.objects.get(pk=pk)
        except HealthSafety.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        hazard.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


 
class RiskAssessmentView(APIView):
    def get(self, request):
      
        assessments = RiskAssessment.objects.all()
        serializer = RiskAssessmentSerializer(assessments, many=True)
        return Response(serializer.data)

    def post(self, request):
       
        serializer = RiskAssessmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class RiskAssessmentDetailView(APIView):
    def get(self, request, pk):
        try:
            assessment = RiskAssessment.objects.get(pk=pk)
        except RiskAssessment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RiskAssessmentSerializer(assessment)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            assessment = RiskAssessment.objects.get(pk=pk)
        except RiskAssessment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RiskAssessmentSerializer(assessment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            assessment = RiskAssessment.objects.get(pk=pk)
        except RiskAssessment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        assessment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthRootCauseView(APIView):
    def get(self, request):
 
        root_causes = HealthRootCause.objects.all()
        serializer = HealthRootCauseSerializer(root_causes, many=True)
        return Response(serializer.data)

    def post(self, request):
  
        serializer = HealthRootCauseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class HealthRootCauseDetailView(APIView):
    def get(self, request, pk):
        try:
            root_cause = HealthRootCause.objects.get(pk=pk)
        except HealthRootCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = HealthRootCauseSerializer(root_cause)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            root_cause = HealthRootCause.objects.get(pk=pk)
        except HealthRootCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = HealthRootCauseSerializer(root_cause, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            root_cause = HealthRootCause.objects.get(pk=pk)
        except HealthRootCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        root_cause.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 
class HealthIncidentsView(APIView):
    def get(self, request):
    
        incidents = HealthIncidents.objects.all()
        serializer = HealthIncidentsSerializer(incidents, many=True)
        return Response(serializer.data)

    def post(self, request):
       
        serializer = HealthIncidentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class HealthIncidentsDetailView(APIView):
    def get(self, request, pk):
        try:
            incident = HealthIncidents.objects.get(pk=pk)
        except HealthIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = HealthIncidentsSerializer(incident)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            incident = HealthIncidents.objects.get(pk=pk)
        except HealthIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = HealthIncidentsSerializer(incident, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            incident = HealthIncidents.objects.get(pk=pk)
        except HealthIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        incident.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


 
class BusinessRiskView(APIView):
    def get(self, request):
        
        risks = BusinessRisk.objects.all()
        serializer = BusinessRiskSerializer(risks, many=True)
        return Response(serializer.data)

    def post(self, request):
      
        serializer = BusinessRiskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class BusinessRiskDetailView(APIView):
    def get(self, request, pk):
        try:
            risk = BusinessRisk.objects.get(pk=pk)
        except BusinessRisk.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BusinessRiskSerializer(risk)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            risk = BusinessRisk.objects.get(pk=pk)
        except BusinessRisk.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BusinessRiskSerializer(risk, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            risk = BusinessRisk.objects.get(pk=pk)
        except BusinessRisk.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        risk.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ReviewTypeView(APIView):
    def get(self, request):
 
        root_causes = ReviewType.objects.all()
        serializer = ReviewTypeSerializer(root_causes, many=True)
        return Response(serializer.data)

    def post(self, request):
  
        serializer = ReviewTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class ReviewTypeDetailView(APIView):
    def get(self, request, pk):
        try:
            root_cause = ReviewType.objects.get(pk=pk)
        except ReviewType.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewTypeSerializer(root_cause)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            root_cause = ReviewType.objects.get(pk=pk)
        except ReviewType.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReviewTypeSerializer(root_cause, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            root_cause = ReviewType.objects.get(pk=pk)
        except ReviewType.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        root_cause.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
 
class EnergyReviewView(APIView):
    def get(self, request):
     
        reviews = EnergyReview.objects.all()
        serializer = EnergyReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
 
        serializer = EnergyReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class EnergyReviewDetailView(APIView):
    def get(self, request, pk):
        try:
            review = EnergyReview.objects.get(pk=pk)
        except EnergyReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnergyReviewSerializer(review)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            review = EnergyReview.objects.get(pk=pk)
        except EnergyReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnergyReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            review = EnergyReview.objects.get(pk=pk)
        except EnergyReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class BaselineReviewView(APIView):
    def get(self, request):
 
        root_causes = BaselineReview.objects.all()
        serializer = BaselineReviewSerializer(root_causes, many=True)
        return Response(serializer.data)

    def post(self, request):
  
        serializer = BaselineReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class BaselineReviewDetailView(APIView):
    def get(self, request, pk):
        try:
            root_cause = BaselineReview.objects.get(pk=pk)
        except BaselineReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BaselineReviewSerializer(root_cause)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            root_cause = BaselineReview.objects.get(pk=pk)
        except BaselineReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BaselineReviewSerializer(root_cause, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            root_cause = BaselineReview.objects.get(pk=pk)
        except BaselineReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        root_cause.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
 

class BaselineView(APIView):
    def get(self, request):
        baselines = Baseline.objects.prefetch_related('enpis').all()
        serializer = BaselineSerializer(baselines, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BaselineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BaselineDetailView(APIView):
    def get(self, request, pk):
        try:
            baseline = Baseline.objects.prefetch_related('enpis').get(pk=pk)
        except Baseline.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BaselineSerializer(baseline)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            baseline = Baseline.objects.get(pk=pk)
        except Baseline.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BaselineSerializer(baseline, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            baseline = Baseline.objects.get(pk=pk)
        except Baseline.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        baseline.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class EnergySourceView(APIView):
    def get(self, request):
     
        reviews = EnergySource.objects.all()
        serializer = EnergySourceSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EnergySourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class EnergySourceDetailView(APIView):
    def get(self, request, pk):
        try:
            root_cause = EnergySource.objects.get(pk=pk)
        except EnergySource.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnergySourceSerializer(root_cause)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            root_cause = EnergySource.objects.get(pk=pk)
        except EnergySource.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EnergySourceSerializer(root_cause, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            root_cause = EnergySource.objects.get(pk=pk)
        except EnergySource.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        root_cause.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
 
class SignificantEnergyListView(APIView):
    def get(self, request):
       
        significant_energies = SignificantEnergy.objects.all()
        serializer = SignificantEnergySerializer(significant_energies, many=True)
        return Response(serializer.data)

    def post(self, request):
      
        serializer = SignificantEnergySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


 
class SignificantEnergyDetailView(APIView):
    def get_object(self, pk):
        try:
            return SignificantEnergy.objects.get(pk=pk)
        except SignificantEnergy.DoesNotExist:
            return None

    def get(self, request, pk):
     
        significant_energy = self.get_object(pk)
        if significant_energy is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SignificantEnergySerializer(significant_energy)
        return Response(serializer.data)

    def put(self, request, pk):      
        significant_energy = self.get_object(pk)
        if significant_energy is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SignificantEnergySerializer(significant_energy, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):        
        significant_energy = self.get_object(pk)
        if significant_energy is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        significant_energy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 

class EnergyImprovementsListCreateAPIView(APIView):
     
    def get(self, request):
        
        energy_improvements = EnergyImprovement.objects.all()
        serializer = EnergyImprovementsSerializer(energy_improvements, many=True)
        return Response(serializer.data)

    def post(self, request):
  
        serializer = EnergyImprovementsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnergyImprovementsDetailAPIView(APIView):
  
    def get(self, request, pk):
        try:
            energy_improvement = EnergyImprovement.objects.get(pk=pk)
        except EnergyImprovement.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnergyImprovementsSerializer(energy_improvement)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            energy_improvement = EnergyImprovement.objects.get(pk=pk)
        except EnergyImprovement.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnergyImprovementsSerializer(energy_improvement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            energy_improvement = EnergyImprovement.objects.get(pk=pk)
        except EnergyImprovement.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        energy_improvement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EnergyActionView(APIView):
    def get(self, request):
        baselines = EnergyAction.objects.prefetch_related('programs').all()
        serializer = EnergyActionSerializer(baselines, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer =EnergyActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EnergyActionDetailView(APIView):
    def get(self, request, pk):
        try:
            baseline = EnergyAction.objects.prefetch_related('programs').get(pk=pk)
        except EnergyAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnergyActionSerializer(baseline)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            baseline = EnergyAction.objects.get(pk=pk)
        except EnergyAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnergyActionSerializer(baseline, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            baseline = EnergyAction.objects.get(pk=pk)
        except EnergyAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        baseline.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class CorrectionCauseView(APIView):
    def get(self, request):
     
        reviews = CorrectionCause.objects.all()
        serializer = CorrectionCauseSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CorrectionCauseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CorrectionCauseDetailView(APIView):
    def get(self, request, pk):
        try:
            review = CorrectionCause.objects.get(pk=pk)
        except CorrectionCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CorrectionCauseSerializer(review)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            review = CorrectionCause.objects.get(pk=pk)
        except CorrectionCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CorrectionCauseSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            review = CorrectionCause.objects.get(pk=pk)
        except CorrectionCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class CorrectiveActionListView(APIView):
 
    def get(self, request):
        corrective_actions = CorrectiveAction.objects.all()
        serializer = CorrectiveActionSerializer(corrective_actions, many=True)
        return Response(serializer.data)

   
    def post(self, request):
        serializer = CorrectiveActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CorrectiveActionDetailView(APIView):
   
    def get(self, request, pk):
        try:
            corrective_action = CorrectiveAction.objects.get(pk=pk)
        except CorrectiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CorrectiveActionSerializer(corrective_action)
        return Response(serializer.data)

  
    def put(self, request, pk):
        try:
            corrective_action = CorrectiveAction.objects.get(pk=pk)
        except CorrectiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CorrectiveActionSerializer(corrective_action, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
    def delete(self, request, pk):
        try:
            corrective_action = CorrectiveAction.objects.get(pk=pk)
        except CorrectiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        corrective_action.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PreventiveActionListCreateView(APIView):
    
    def get(self, request):
        actions = PreventiveAction.objects.all()
        serializer = PreventiveActionSerializer(actions, many=True)
        return Response(serializer.data)

   
    def post(self, request):
        serializer = PreventiveActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PreventiveActionDetailView(APIView):
    
    def get(self, request, pk):
        try:
            action = PreventiveAction.objects.get(pk=pk)
        except PreventiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PreventiveActionSerializer(action)
        return Response(serializer.data)

    
    def put(self, request, pk):
        try:
            action = PreventiveAction.objects.get(pk=pk)
        except PreventiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PreventiveActionSerializer(action, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk):
        try:
            action = PreventiveAction.objects.get(pk=pk)
        except PreventiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        action.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ObjectivesListCreateView(APIView):
     
    def get(self, request):
        objectives = Objectives.objects.all()
        serializer = ObjectivesSerializer(objectives, many=True)
        return Response(serializer.data)

    
    def post(self, request):
        serializer = ObjectivesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObjectivesDetailView(APIView):
    
    def get(self, request, pk):
        try:
            objective = Objectives.objects.get(pk=pk)
        except Objectives.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ObjectivesSerializer(objective)
        return Response(serializer.data)

    
    def put(self, request, pk):
        try:
            objective = Objectives.objects.get(pk=pk)
        except Objectives.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ObjectivesSerializer(objective, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
    def delete(self, request, pk):
        try:
            objective = Objectives.objects.get(pk=pk)
        except Objectives.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        objective.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TargetsPView(APIView):
    def get(self, request):
     
        targets = TargetsP.objects.prefetch_related('programs').all()
        serializer = TargetPSerializer(targets, many=True)
        return Response(serializer.data)

    def post(self, request):
      
        serializer = TargetPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TargetsPDetailView(APIView):
    def get(self, request, pk):
        try:
 
            target = TargetsP.objects.prefetch_related('programs').get(pk=pk)
        except TargetsP.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
 
        serializer = TargetPSerializer(target)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
  
            target = TargetsP.objects.get(pk=pk)
        except TargetsP.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    
        serializer = TargetPSerializer(target, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            
            target = TargetsP.objects.get(pk=pk)
        except TargetsP.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        
        target.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


 

class ConformityCauseView(APIView):
   
    def get(self, request):
        conformity_causes = ConformityCause.objects.all()
        serializer = ConformityCauseSerializer(conformity_causes, many=True)
        return Response(serializer.data)

 
    def post(self, request):
        serializer = ConformityCauseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConformityCauseDetailView(APIView):
 
    def get(self, request, pk):
        try:
            conformity_cause = ConformityCause.objects.get(pk=pk)
        except ConformityCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ConformityCauseSerializer(conformity_cause)
        return Response(serializer.data)

  
    def put(self, request, pk):
        try:
            conformity_cause = ConformityCause.objects.get(pk=pk)
        except ConformityCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConformityCauseSerializer(conformity_cause, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
    def delete(self, request, pk):
        try:
            conformity_cause = ConformityCause.objects.get(pk=pk)
        except ConformityCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        conformity_cause.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 
class ConformityView(APIView):
   
    def get(self, request):
        conformities = Conformity.objects.all()
        serializer = ConformitySerializer(conformities, many=True)
        return Response(serializer.data)

 
    def post(self, request):
        serializer = ConformitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConformityDetailView(APIView):
 
    def get(self, request, pk):
        try:
            conformity = Conformity.objects.get(pk=pk)
        except Conformity.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConformitySerializer(conformity)
        return Response(serializer.data)

    
    def put(self, request, pk):
        try:
            conformity = Conformity.objects.get(pk=pk)
        except Conformity.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConformitySerializer(conformity, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
    def delete(self, request, pk):
        try:
            conformity = Conformity.objects.get(pk=pk)
        except Conformity.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        conformity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 

class ManualView(APIView):
    def get(self, request):
        manuals = Manual.objects.all()
        serializer = ManualSerializer(manuals, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ManualSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManualDetailView(APIView):
    def get(self, request, pk):
        try:
            manual = Manual.objects.get(pk=pk)
        except Manual.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ManualSerializer(manual)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            manual = Manual.objects.get(pk=pk)
        except Manual.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ManualSerializer(manual, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            manual = Manual.objects.get(pk=pk)
        except Manual.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        manual.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class ProcedureView(APIView):
    def get(self, request):
        procedures = Procedure.objects.all()
        serializer = ProcedureSerializer(procedures, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProcedureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcedureDetailView(APIView):
    def get(self, request, pk):
        try:
            procedure = Procedure.objects.get(pk=pk)
        except Procedure.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProcedureSerializer(procedure)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            procedure = Procedure.objects.get(pk=pk)
        except Procedure.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProcedureSerializer(procedure, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            procedure = Procedure.objects.get(pk=pk)
        except Procedure.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        procedure.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
 

class RecordFormatView(APIView):
  
    def get(self, request):
        record_formats = RecordFormat.objects.all()
        serializer = RecordFormatSerializer(record_formats, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RecordFormatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecordFormatDetailView(APIView):
   
    def get(self, request, pk):
        try:
            record_format = RecordFormat.objects.get(pk=pk)
        except RecordFormat.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecordFormatSerializer(record_format)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            record_format = RecordFormat.objects.get(pk=pk)
        except RecordFormat.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecordFormatSerializer(record_format, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            record_format = RecordFormat.objects.get(pk=pk)
        except RecordFormat.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        record_format.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
