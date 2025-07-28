import os
import torch
import cv2
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from .forms import ImageForm
from .models import Image
from ultralytics import YOLO

model=YOLO('model_detection/yolov8n.pt')

def home(request):
    return render(request, "authenticate/home.html")

def login_view(request):
    if request.method == "POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user) 
            return redirect('home')  
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "authenticate/login.html")
    return render(request, "authenticate/login.html")

def signup(request):
    if request.method == "POST":
        print("Signup form submitted")
        username = request.POST['username']
        employee_id = request.POST['employee-id']
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']

        print(f"Received data: {username}, {employee_id}, {email}, {password}, {password1}")

        if password == password1:
            User = get_user_model()
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                print("Username already exists.")
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                print("Email already exists.")
                return redirect('signup')
            else:
                myuser = User.objects.create_user(username=username, email=email, password=password)
                myuser.save()
                messages.success(request, "Your account has been registered successfully.")
                print("User created successfully.")
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    print("User authenticated successfully.")
                    return redirect('login')
                else:
                    messages.error(request, "Authentication failed.")
                    print("Authentication failed.")
                    return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
            print("Passwords do not match.")
            return redirect('signup')
    return render(request, "authenticate/signup.html")


# def uploadimg(request):
#     if request.method == "POST":
#         form = ImageForm(request.POST, request.FILES)
#         if(form.is_valid()):
#             form.save()
#     form  = ImageForm()
#     img = Image.objects.all().order_by('-date')
#     return render(request, "authenticate/uploadimg.html", {'img':img, 'form':form})


def uploadimg(request):
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save()  # Save the uploaded image
            
            # Get the file path of the uploaded image
            img_path = image_instance.image.path

            # Run YOLOv8 model on the uploaded image
            results = model(img_path)  # YOLOv8 automatically processes the image
            
            # Parse the results (bounding boxes, labels, etc.)
            predictions = results[0].boxes.xyxy.cpu().numpy()  # Bounding box coordinates
            class_names = results[0].names  # Class names
            confidences = results[0].boxes.conf.cpu().numpy()  # Confidence scores

            # Add predictions and image path to context for rendering
            img = Image.objects.all().order_by('-date')
            return render(request, "authenticate/uploadimg.html", {
                'img': img, 
                'form': form, 
                'predictions': zip(predictions, confidences, class_names),
                'image_url': image_instance.image.url  # For displaying the image
            })
    
    form = ImageForm()
    img = Image.objects.all().order_by('-date')
    return render(request, "authenticate/uploadimg.html", {'img': img, 'form': form})


