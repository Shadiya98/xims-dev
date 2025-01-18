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
from datetime import date
from django.contrib.auth import get_user_model


class AdminLoginView(APIView):
    def post(self, request, *args, **kwargs):
        print("request",request.data)
        email = request.data.get('email')
        password = request.data.get('password')

        logger.info(f"Attempting to login user with email: {email}")

        if email is None or password is None:
            return Response({'error': 'Email and password must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_staff and user.is_superuser:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        logger.warning(f"Failed login attempt for user: {email}")
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


 



 

class CreateCompanyView(APIView):
    def post(self, request, *args, **kwargs):
        print("Request data: %s", request.data)
        serializer = CompanySerializer(data=request.data)
        
        if serializer.is_valid():
            company = serializer.save()
           
            company_logo_url = company.company_logo.url if company.company_logo else None
            
            return Response({
                "message": "Company created successfully!",
                "company_id": company.id,
                "company_logo": company_logo_url
            }, status=status.HTTP_201_CREATED)
        else:
            print("serializer.errors", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CompanyListView(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyGetSerializer

class CompanyUpdateView(generics.UpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyUpdateSerializer

    def get_object(self):
        company_id = self.kwargs['id']
        return generics.get_object_or_404(Company, id=company_id)

    def perform_update(self, serializer):
     
        print("Request Data:", self.request.data)
        
 
        serializer.save()

    def update(self, request, *args, **kwargs):
      
        print("Incoming request data:", request.data)
        return super().update(request, *args, **kwargs)


class ChangeCompanyStatusView(APIView):

    def post(self, request, id):
        try:
            company = Company.objects.get(id=id)
        except Company.DoesNotExist:
            raise NotFound("Company not found")

        action = request.data.get('action')   
        
        if action == 'block':
            company.status = 'blocked'
            company.save()
            return Response({"message": "Company has been blocked successfully."}, status=status.HTTP_200_OK)
        
        elif action == 'active':
            company.status = 'active'
            company.save()
            return Response({"message": "Company has been unblocked successfully."}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid action. Use 'block' or 'unblock'."}, status=status.HTTP_400_BAD_REQUEST)
    


class DeleteCompanyView(APIView):
   def delete(self, request,  id):
        try:
            company = Company.objects.get(id= id)
        except Company.DoesNotExist:      
            raise NotFound("Company not found") 
        company.delete()
        return Response({"message": "Company has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class PermissionListView(APIView):
    def get(self, request, *args, **kwargs):
        print("request.data",request.data)
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SingleCompanyListView(generics.ListAPIView):
    serializer_class = CompanySingleSerializer

    def get_queryset(self):
      
        company_id = self.kwargs['id']
       
        try:
            company = Company.objects.get(id=company_id)
            return Company.objects.filter(id=company.id) 
        except Company.DoesNotExist:
            raise NotFound(detail="Company with the given id does not exist")
        
class CompanyCountView(APIView):
  
    def get(self, request, *args, **kwargs):
        company_count = Company.objects.count()
        return Response({"count": company_count}, status=status.HTTP_200_OK)



class SubscriptionListCreateView(APIView):
    def get(self, request):
        subscriptions = Subscription.objects.all()
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class SubscriptionDetailView(APIView):
    def get_object(self, pk):
        try:
            return Subscription.objects.get(pk=pk)
        except Subscription.DoesNotExist:
            return None

    def get(self, request, pk):
        subscription = self.get_object(pk)
        if not subscription:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        subscription = self.get_object(pk)
        if not subscription:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubscriptionSerializer(subscription, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subscription = self.get_object(pk)
        if not subscription:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        subscription.delete()
        return Response({"message": "Subscription deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



class SubscriberListCreateAPIView(generics.ListCreateAPIView):
    queryset = Subscribers.objects.all()
    serializer_class = SubscriberSerializer

    def perform_create(self, serializer):
    
        serializer.save()

 
class SubscriberRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscribers.objects.all()
    serializer_class =   serializer_class = SubscriberSerializerss


 
class ChangeSubscriberStatus(APIView):
    def post(self, request, pk):
        try:
     
            subscriber = Subscribers.objects.get(id=pk)
        except Subscribers.DoesNotExist:
            raise NotFound("Subscriber not found")

     
        action = request.data.get('action')
        
 
        if action == 'block':
            subscriber.status = 'blocked'
            subscriber.save()
            return Response({"message": "Subscriber has been blocked successfully."}, status=status.HTTP_200_OK)
        
        
        elif action == 'active':
            subscriber.status = 'active'
            subscriber.save()
            return Response({"message": "Subscriber has been activated successfully."}, status=status.HTTP_200_OK)
        
        
        return Response({"error": "Invalid action. Use 'block' or 'active'."}, status=status.HTTP_400_BAD_REQUEST)
    


class SubscriptionStatusAPIView(APIView):
    def get(self, request, *args, **kwargs):
        today = date.today()
        
  
        subscriptions = Subscription.objects.all()
        subscription_details = []

        for subscription in subscriptions:
           
            active_subscribers_count = Subscribers.objects.filter(
                plan=subscription,
                status='active',
                expiry_date__gte=today
            ).count()

           
            expired_subscribers_count = Subscribers.objects.filter(
                plan=subscription,
                expiry_date__lt=today
            ).count()

            subscription_details.append({
                "subscription_name": subscription.subscription_name,
                "validity": subscription.validity,
                "active_subscribers_count": active_subscribers_count,
                "expired_subscribers_count": expired_subscribers_count,
            })

        return Response({
            "subscriptions": subscription_details,
        }, status=status.HTTP_200_OK)


class ExpiringfifteenAPIView(APIView):
    def get(self, request):      
        today = timezone.now().date()
        expiration_date = today + timedelta(days=15)     
        subscribers_expiring_soon = Subscribers.objects.filter(expiry_date__lte=expiration_date, expiry_date__gte=today)     
        serializer = SubscriberSerializer(subscribers_expiring_soon, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class ExpiringthirtyAPIView(APIView):
    def get(self, request):      
        today = timezone.now().date()
        expiration_date = today + timedelta(days=30)     
        subscribers_expiring_soon = Subscribers.objects.filter(expiry_date__lte=expiration_date, expiry_date__gte=today)     
        serializer = SubscriberSerializer(subscribers_expiring_soon, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class ExpiringsixtyAPIView(APIView):
    def get(self, request):      
        today = timezone.now().date()
        expiration_date = today + timedelta(days=60)     
        subscribers_expiring_soon = Subscribers.objects.filter(expiry_date__lte=expiration_date, expiry_date__gte=today)     
        serializer = SubscriberSerializer(subscribers_expiring_soon, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class ExpiringninetyAPIView(APIView):
    def get(self, request):      
        today = timezone.now().date()
        expiration_date = today + timedelta(days=90)     
        subscribers_expiring_soon = Subscribers.objects.filter(expiry_date__lte=expiration_date, expiry_date__gte=today)     
        serializer = SubscriberSerializer(subscribers_expiring_soon, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ChangePasswordView(APIView):

    def put(self, request, *args, **kwargs):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')     

        if not new_password or not confirm_password:
            return Response({'error': 'Both new password and confirm password must be provided.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'},
                            status=status.HTTP_400_BAD_REQUEST)      
        User = get_user_model()       
        admin_users = User.objects.filter(is_staff=True, is_superuser=True)

        if not admin_users.exists():
            return Response({'error': 'No admin users found.'},
                            status=status.HTTP_404_NOT_FOUND)
        
        for admin_user in admin_users:        

            if not check_password(current_password, admin_user.password):
                return Response({'error': 'Current password is incorrect.'},
                                status=status.HTTP_400_BAD_REQUEST)          
            admin_user.set_password(new_password)
            admin_user.save()
        return Response({'message': 'Password changed successfully for all admin users.'},
                        status=status.HTTP_200_OK)

 
class ActiveCompanyCountAPIView(APIView):
  
    def get(self, request, *args, **kwargs):
        active_count = Company.objects.filter(status='active').count()
        return Response({'active_company_count': active_count}, status=status.HTTP_200_OK)



class ValidateEmailAndUserIDView(APIView):
    def get(self, request):
        email = request.GET.get('email_address', '')  
        user_id = request.GET.get('user_id', '')  

        if not email and not user_id:
            return Response({'status': 400, 'error': 'Email or User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if email:
            if Company.objects.filter(email_address=email).exists():
                return Response({'status': 200, 'exists': True, 'field': 'email_address'}, status=status.HTTP_200_OK)    
        if user_id:
            if Company.objects.filter(user_id=user_id).exists():
                return Response({'status': 200, 'exists': True, 'field': 'user_id'}, status=status.HTTP_200_OK)       
        return Response({'status': 200, 'exists': False}, status=status.HTTP_200_OK)
    
 

class ValidateEmailView(APIView):
    def get(self, request):
        email_address = request.GET.get('email_address', '')
        
        if not email_address:
            return Response({'status': 400, 'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Company.objects.filter(email_address=email_address).exists():
            return Response({'status': 200, 'exists': True}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 200, 'exists': False}, status=status.HTTP_200_OK)

class ValidatuseridView(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id', '')
        
        if not user_id:
            return Response({'status': 400, 'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Company.objects.filter(user_id=user_id).exists():
            return Response({'status': 200, 'exists': True}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 200, 'exists': False}, status=status.HTTP_200_OK)
        
class AdminDetailsAPIView(APIView):
    

    def get(self, request):
     
        admins = User.objects.filter(is_staff=True)  

     
        serializer = UserSerializer(admins, many=True)

   
        return Response(serializer.data)