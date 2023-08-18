from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UserProfile
from .serializers import UserProfileSerializer, \
    SendCodeSerializer, \
    VerifyCodeSerializer
import random
import string
import time


class SendVerificationView(APIView):
    serializer_class = SendCodeSerializer

    @swagger_auto_schema(
        operation_summary='Send verification code to the provided phone number.',
        operation_description="This endpoint sends a 4-digit verification "
                              "code to the specified phone number"
                              "and associates it with the user's profile in the database.",
        manual_parameters=[
            openapi.Parameter(
                'Phone number',
                openapi.IN_QUERY,
                description='Login phone_number',
                type=openapi.TYPE_STRING,
                required=True
            ),
        ]
    )
    def post(self, request):
        """
        Send verification code to the provided phone number.

        This endpoint sends a 4-digit verification
        code to the specified phone number
        and associates it with the user's profile in the database.

        :param request: HTTP POST request
        :return: Response indicating success
        or failure of sending the verification code
        """
        try:
            phone_number = request.query_params.get('Phone number')
            if phone_number is None:
                phone_number = request.data.get('phone_number')
            print(phone_number)
        except AttributeError:
            return Response(
                {
                    'status': 'error',
                    'data': None,
                    'details': 'fom {"phone_number" : int}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not phone_number:
            return Response(
              {
                'status': 'error',
                'data': None,
                'details': 'Phone number is required.'
              },
              status=status.HTTP_400_BAD_REQUEST
            )

        verification_code = ''.join(random.choices(string.digits, k=4))
        time.sleep(2)
        user, created = UserProfile.objects.get_or_create(phone_number=phone_number)
        user.verification_code = verification_code
        user.save()

        return Response(
            {
                'status': 'success',
                'data': None,
                'details': f'Verification code sent. '
                           f'Code - {verification_code}'
            }
        )


class VerifyCodeView(APIView):
    serializer_class = VerifyCodeSerializer

    @swagger_auto_schema(
        operation_summary='Verify phone number.',
        operation_description="This endpoint verifies the "
                              "provided phone number and verification code, "
                              "and activates the user "
                              "if the verification is successful."
                              "If the verification is successful, "
                              "and the user does not have an invite code, "
                              "a random 6-character invite "
                              "code consisting of digits "
                              "and letters is generated for the user.",
        manual_parameters=[
            openapi.Parameter(
                'Phone number',
                openapi.IN_QUERY,
                description='Login phone_number',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'Verification code',
                openapi.IN_QUERY,
                description='Verification phone number',
                type=openapi.TYPE_STRING,
                required=True
            ),
        ]
    )
    def post(self, request):
        """
        Verify phone number and activate user.

        This endpoint verifies the provided phone number and verification code,
        and activates the user if the verification is successful.
        If the verification is successful, and the user does not have an invite code,
        a random 6-character invite code consisting of digits and letters is generated for the user.

        :param request: HTTP POST request
        :return: Response with user profile and verification result
        """
        try:
            phone_number = request.query_params.get('Phone number')
            verification_code = request.query_params.get('Verification code')
            if phone_number is None and verification_code is None:
                phone_number = request.data.get('phone_number')
                verification_code = request.data.get('verification_code')
        except AttributeError:
            return Response(
                {
                    'status': 'error',
                    'data': None,
                    'details': 'fom {'
                               '"phone_number" : int, '
                               '"verification_code" : int'
                               '}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = UserProfile.objects.get(
                phone_number=phone_number,
                verification_code=verification_code
            )
        except UserProfile.DoesNotExist:
            return Response(
                {
                    'status': 'error',
                    'data': None,
                    'details': 'Invalid verification code or phone number.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        user.authorized = True
        if not user.invite_code:
            user.invite_code = ''.join(random.choices(string.digits + string.ascii_letters, k=6))
        user.save()

        serializer = UserProfileSerializer(user)
        return Response(
            {
                'status': 'success',
                'data': serializer.data,
                'details': 'Phone verified.'
            }
        )


class UserProfileView(APIView):

    @swagger_auto_schema(
        operation_summary='User profile.',
        operation_description="This endpoint retrieves the user profile "
                              "of the specified phone number, "
                              "along with the list of invited users "
                              "who used the invite code of the current user."
                              "It demonstrates the user's information "
                              "and displays the invite code "
                              "that has been used."
    )
    def get(self, request, phone_number):
        """
        Retrieve user profile and invited users.

        This endpoint retrieves the user profile of the specified phone number,
        along with the list of invited users who used the invite code of the current user.
        It demonstrates the user's information and displays the invite code that has been used.

        :param request: HTTP GET request
        :param phone_number: Phone number of the user
        :return: Response with user profile and invited users
        """
        current_user = get_object_or_404(UserProfile, phone_number=phone_number)
        invited_users = UserProfile.objects.filter(entered_invite=current_user)
        entered_invite = current_user.entered_invite.invite_code \
            if current_user.entered_invite else None
        invited_phone_numbers = [user.phone_number for user in invited_users]
        return Response(
            {
                'status': 'success',
                'data': {
                    'phone_number': current_user.phone_number,
                    'invite_code': current_user.invite_code,
                    'entered_invite': entered_invite,
                    'invited_users': invited_phone_numbers
                },
                'details': None
            }
        )

    @swagger_auto_schema(
        operation_summary='Activate an invite code for a user.',
        operation_description='This endpoint allows a user '
                              'to activate an invite code.',
        manual_parameters=[
            openapi.Parameter(
                'Invite code',
                openapi.IN_QUERY,
                description='Invite code to activate',
                type=openapi.TYPE_STRING,
                required=True
            ),
        ]
    )
    def put(self, request, phone_number):
        """
        Activate an invite code for a user.

        This endpoint allows a user to activate an invite code.

        :param request: HTTP PUT request
        :param phone_number: Phone number of the user
        :return: Response with activation result
        """
        invite_code = request.query_params.get('Invite code')
        if invite_code is None:
            invite_code = request.data.get('invite_code')
        try:
            user = UserProfile.objects.get(phone_number=phone_number)
        except UserProfile.DoesNotExist:
            return Response(
                {
                    'status': 'error',
                    'data': None,
                    'details': 'User not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if user.invite_code_activated:
            return Response(
                {
                    'status': 'error',
                    'data': None,
                    'details': 'Invite code has already been activated.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if invite_code:
            try:
                invite_user = UserProfile.objects.get(invite_code=invite_code)
                if invite_user == user:
                    return Response(
                        {
                            'status': 'error',
                            'data': None,
                            'details': 'You cannot activate your own invite code.'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                user.entered_invite = invite_user
                user.invite_code_activated = True
                user.save()
                serializer = UserProfileSerializer(user)
                return Response(
                    {
                        'status': 'success',
                        'data': serializer.data,
                        'details': 'Invite code activated.'
                    }
                )
            except UserProfile.DoesNotExist:
                return Response(
                    {
                        'status': 'error',
                        'data': None,
                        'details': 'Invalid invite code.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {
                    'status': 'error',
                    'data': None,
                    'details': 'No invite code provided.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
