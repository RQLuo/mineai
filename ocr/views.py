from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UploadedImage
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render
import random
import json
from django.utils import timezone
from django.db.models import Q

@csrf_exempt
def submit_feedback(request, image_id):
    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        try:
            uploaded_image = UploadedImage.objects.get(pk=image_id)
            uploaded_image.feedback = feedback
            uploaded_image.save()
            return JsonResponse({'success': True})
        except UploadedImage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)
    else:
        return JsonResponse({'message': 'Only POST requests are allowed'}, status=405)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user_id = random.randint(-2**32 + 1, 2**32 - 1)
        if not User.objects.filter(username=username).exists():
            if password:
                user = User.objects.create_user(username=username, password=password, id=user_id)
                user.save()
                return JsonResponse({'message': 'User created successfully', 'user_id': user_id})
            else:
                return JsonResponse({'message': 'password are required'}, status=400)
        else:
            return JsonResponse({'message': 'Username already exists'}, status=400)
    else:
        return JsonResponse({'message': 'Only POST requests are allowed'}, status=405)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            return JsonResponse({'message': 'Login successful', 'user_id': user.id})
        else:
            return JsonResponse({'message': 'Invalid credentials'}, status=401)
    else:
        return JsonResponse({'message': 'Only POST requests are allowed'}, status=405)


@csrf_exempt
def image_detail(request, image_id):
    if request.method == 'GET':
        image = get_object_or_404(UploadedImage, pk=image_id)
        image_data = image.image.read()
        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(image.image.name)
        return response
    elif request.method == 'POST':
        image = get_object_or_404(UploadedImage, pk=image_id)
        text_data = request.POST.get('text_data')
        if text_data:
            image.processing_result = text_data
            image.save()
            return JsonResponse({'status': 'success', 'message': 'Text data uploaded successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Missing text data'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        image_file = request.FILES.get('image')
        uploaded_image = UploadedImage(user_id=user_id, image=image_file)
        uploaded_image.save()
        image_id = uploaded_image.id
        return JsonResponse({'status': 'success', 'message': 'Image uploaded', 'image_id': image_id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def upload_imageweb_web(request):
    # 测试版自动登录
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    username = ip_address
    password = ip_address
    user = authenticate(username=username, password=password)
    if user is None:
        user = User.objects.create_user(username=username, password=password)
        user.save()
    twenty_four_hours_ago = timezone.now() - timezone.timedelta(hours=24)
    total_upload_count = UploadedImage.objects.filter(user_id=user.id).count()
    upload_count = UploadedImage.objects.filter(user_id=user.id, uploaded_at__gte=twenty_four_hours_ago).count()
    like_count = UploadedImage.objects.filter(Q(user_id=user.id) & Q(uploaded_at__gte=twenty_four_hours_ago) & (Q(feedback="1") | Q(feedback="0"))).count()
    nonfeedback_count = UploadedImage.objects.filter(Q(user_id=user.id) & Q(uploaded_at__gte=twenty_four_hours_ago) & Q(feedback__isnull=True)).count()
    used_count = 2 * nonfeedback_count - upload_count + 1.5 * like_count
    updated_data = {
        'feedback_count': upload_count - nonfeedback_count - like_count,
        'like_count': like_count,
        'left_count': 10 - used_count,
        'total_upload_count': total_upload_count,
    }
    if request.method == 'POST':
        if used_count >= 10:
            return JsonResponse({'message': 'Upload limit exceeded'}, status=400)
        image_file = request.FILES.get('image')
        uploaded_image = UploadedImage(user_id=user.id, image=image_file)
        uploaded_image.save()
        image_id = uploaded_image.id
        return JsonResponse({'image_id': image_id})
    return render(request, 'upload_image.html', updated_data)

def get_text_data(request, image_id):
    if request.method == 'GET':
        image = get_object_or_404(UploadedImage, pk=image_id)
        text_data = image.processing_result
        if text_data:
            return JsonResponse({'status': 'success', 'text_data': text_data})
        else:
            return JsonResponse({'status': 'error', 'message': 'Text data not available for this image'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_empty_text_images(request):
    if request.method == 'GET':
        empty_text_images = UploadedImage.objects.filter(processing_result__isnull=True).values_list('id', flat=True)
        return JsonResponse({'status': 'success', 'empty_text_image_ids': list(empty_text_images)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


