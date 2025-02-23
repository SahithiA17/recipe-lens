import base64
import string
import os
from django.shortcuts import render
from django.conf import settings
from .forms import ImageUploadForm
from PIL import Image
from .encoder import get_recipes, get_encodings
import json
import numpy as np
from scipy.spatial.distance import cosine
import pickle

# Load the encodings and names from the .txt files (pickle format)
enc_list = None
names_list = None
with open(r'C:\Users\DELL\Downloads\Project_Inverse-Cooking-main\encodings.txt', 'rb') as fp:
    enc_list = pickle.load(fp)
with open(r'C:\Users\DELL\Downloads\Project_Inverse-Cooking-main\enc_names.txt', 'rb') as fp:
    names_list = pickle.load(fp)

print(f"Loaded encodings: {len(enc_list)} encodings")
print(f"Loaded names: {len(names_list)} names")

def check_if_food_image(img):
    """Check if the uploaded image is a food-related image based on encodings."""
    enc = get_encodings(img)
    similarity_list = []

    # Compare with all stored encodings (assuming all stored encodings are food-related)
    for i in enc_list:
        similarity = cosine(i, enc)
        similarity_list.append(1 - similarity)

    # If the similarity score is above a reasonable threshold, consider it food
    max_similarity = max(similarity_list)
    print(f"Max similarity: {max_similarity}")
    if max_similarity > 0.7:  # Adjust threshold as needed
        return True
    return False

def home_page(request):
    raw_image = None
    uploaded_image = None
    recipe_list_to_return = []
    message = None  # For handling non-food image message

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            raw_image = form.cleaned_data['image']
            uploaded_image = base64.b64encode(raw_image.file.read()).decode('ascii')
            raw_image = Image.open(raw_image)

            # Check if the uploaded image is a food image
            if not check_if_food_image(raw_image):
                message = "This is not a food image. Please upload a valid food image."
            else:
                # Process the food image and get recipes
                recipe_list = get_recipes(raw_image)
                if not recipe_list:
                    message = "No matching recipes found for this image."
                else:
                    print(f"Recipes found: {recipe_list}")
                    path_to_json = os.path.join(settings.BASE_DIR, 'WebApp/static/WebApp/indian_recipes.json')
                    x = json.load(open(path_to_json))

                    for i in range(len(recipe_list)):
                        name = recipe_list[i]
                        y = list(filter(lambda x: x["name"] == name, x))
                        if len(y) != 0:
                            y = y[0]
                            image_link = "WebApp/display_images/" + name + "1.jpg"
                            calories = y['calories']
                            cooking_time = y['cooking_time']
                            ingredients = y['ingredients']
                            directions = y['directions']
                            list_to_append = [string.capwords(name), image_link, calories, cooking_time, ingredients, directions]
                            recipe_list_to_return.append(list_to_append)

    else:
        form = ImageUploadForm()

    return render(request, 'WebApp/home.html', {
        'form': form,
        'uploaded_image': uploaded_image,
        'recipe_list_to_return': recipe_list_to_return[:4],
        'similar_recipe_list': recipe_list_to_return[4:10],
        'message': message  # Pass the message to the template
    })
