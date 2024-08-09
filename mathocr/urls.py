from django.contrib import admin
from django.urls import path
from ocr.views import upload_image, image_detail, get_text_data, get_empty_text_images, submit_feedback, register, login, upload_imageweb_web

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload-image/', upload_image, name='upload_image'),
    path('', upload_imageweb_web, name='webupload-image'),
    path('submit-feedback/<int:image_id>/', submit_feedback, name='submit_feedback'),
    path('image/<int:image_id>/', image_detail, name='image_detail'),
    path('get-text-data/<int:image_id>/', get_text_data, name='get_text_data'),
    path('get_empty_text_images/', get_empty_text_images, name='get_empty_text_images'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
]
