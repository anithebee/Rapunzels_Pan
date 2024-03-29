import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup
import requests
import re

#NUTR CONTENT
def get_nutritional_info_url(food_name):
    base_url = "https://fdc.nal.usda.gov/fdc-app.html#/?query="
    search_url = f"{base_url}{food_name}"

    response = requests.get(search_url)

    if response.status_code == 200:
        if food_name.replace(" ", "%20").lower() in response.url.lower():
            return response.url
        else:
            st.write("No nutritional information found for this food.")
    else:
        st.write("Failed to retrieve search results.")


#ALLERGY SUB

def parse_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    outer_class = 'card-body'
    elements_with_outer_class = soup.find_all(class_=outer_class)
    inner_class = 'col-md-3 sub-details'
    inner_class1 = 'col-md-3 sub-details sub-details-last'
    
    result_list = []

    for element in elements_with_outer_class:
        list1 = []
        inner_elements = element.find_all(class_=inner_class)
        for inner_element in inner_elements:
            list1.append(inner_element.get_text())
        
        inner_elements1 = element.find_all(class_=inner_class1)
        for inner_element1 in inner_elements1:
            list1.append(inner_element1.get_text())
        
        if list1:
            result_list.append(list1)

    return result_list

def allergy_sub(ingredient):
    emptylist = []
    url = f"https://www.foodsubs.com/ingredients/" + ingredient
    response = requests.get(url)
    
    if response.status_code == 200:
        page_text = response.text
        parsed_data = parse_html_content(page_text)

        for item_list in parsed_data:
            st.markdown(f"\n ***Substitute:*** ")
            if len(item_list) > 1:
                newlist = [item.replace(', ', ',').replace(',', ', ') for item in item_list]
                final = ', '.join(newlist)
                st.write(final)
            else:
                st.write(''.join(item_list))
                

    else:
        st.write("Sorry! There are no common substitutes available for this. Please re-enter.")

#RECIPE SEARCH
        
def search_recipe(dish_name):
    query = dish_name.replace(' ', '%20')
    url = f'https://tasty.co/search?q={query}&sort=popular'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        search_string = '/recipe/'
        page_text = response.text
        instances = [i for i in range(len(page_text)) if page_text.startswith(search_string, i)]
        if instances:
            for instance_index in instances:
                next_quote_index = instance_index + len(search_string)
                remaining_text = page_text[next_quote_index:page_text.find('"', next_quote_index)]
                temp = "https://tasty.co/recipe/" + remaining_text
                return temp
    else:
        return "Sorry! A recipe for this dish isn't available. Please re-enter."

#DISH IDEAS
def get_recipe_ingredients(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ingredients_section = soup.find('div', class_='ingredients__section')
        if ingredients_section:
            ingredients_list = ingredients_section.find_all('li', class_='ingredient')
            ingredients = [ingredient.get_text(strip=True) for ingredient in ingredients_list]
            return ingredients
    return []

def subtract_ingredient(ingredient, recipe_url):
    ingredients = get_recipe_ingredients(recipe_url)
    if ingredients:
        # WE PRAY FOR PARTIAL MATCH <333
        for idx, item in enumerate(ingredients):
            if re.search(ingredient, item, re.IGNORECASE):
                ingredients.pop(idx)
                return ingredients
        print(f"The ingredient '{ingredient}' is not present in the recipe.")
    else:
        print("Failed to retrieve recipe ingredients.")
    return []

def parser_recipe(ingredient, url):
    query = ingredient.replace(' ', '%20')
    response = requests.get(url + query)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        search_string = '/recipe/'
        page_text = response.text
        instances = [i for i in range(len(page_text)) if page_text.startswith(search_string, i)]
        if instances:
            for instance_index in instances:
                next_quote_index = instance_index + len(search_string)
                remaining_text = page_text[next_quote_index:page_text.find('"', next_quote_index)]
                recipe_url = f"https://tasty.co{search_string}{remaining_text}"
                recipe_response = requests.get(recipe_url)
                if recipe_response.status_code == 200:
                    recipe_soup = BeautifulSoup(recipe_response.text, 'html.parser')
                    ingredients_section = recipe_soup.find('div', class_='ingredients__section')
                    if ingredients_section:
                        ingredients_list = ingredients_section.find_all('li', class_='ingredient')
                        ingredients = [ingredient.get_text(strip=True) for ingredient in ingredients_list]
                        ingredients = subtract_ingredient(ingredient, recipe_url)
                        return recipe_url, remaining_text, ingredients
        return "No Recipe Found", "", []
    else:
        return "No Recipe Found", "", []

websites = [
    "https://tasty.co/search?q=",
    "https://www.allrecipes.com/search/results/?wt=",
    "https://www.foodnetwork.com/search/",
    "https://www.yummly.com/recipes?q=",
    "https://www.epicurious.com/search/",
    "https://www.bbcgoodfood.com/search/recipes?q="
]
#NUTR REQUIREMENTS CLASS
class Nutr:
    def __init__(self, calories, carbs, fats, proteins):
        self.calories = calories
        self.proteins = proteins
        self.carbs = carbs
        self.fats = fats
    def __str__(self):
        return f'Calories: {self.calories} kCal, \nCarbohydrates: {self.carbs} g, \nFats: {self.fats} kCal, \nProteins: {self.proteins} g'

#MAIN
st.set_page_config(page_title="Rapunzel's Pan", page_icon = ":cooking:")
left, center, right = st.columns([1,3,1])
with center:
    st.title("Rapunzel's Pan")
    st.header("Welcome :ribbon::cooking:🥝:bowl_with_spoon:")

st.write("Have ingredients but no idea what dish to make? Use our recipe finder! Allergies? Use the substitute generator! A page for all your culinary needs - \n Anita and Riti.")
st.divider()
#allergy

allergy = st.button("Food Substitutes", help="One-stop tool to gathering substitutes for allergies and more!")
ingredient = st.text_input("Want to find substitutes for ingredients? Enter an ingredient here: ")
if ingredient:
    
    with st.expander("List of Substitutes"):
        allergy_sub(ingredient)

st.divider()
#recipe
recipes = st.button("Recipe Finder", help="Provides the best recipes for your dishes!")
recsearch = st.text_input("Want to find a good recipe for a dish? Enter a dish here: ")
recipe_link = search_recipe(recsearch)
if recsearch:
    with st.expander("URL: "):
        st.write(recipe_link)
st.divider()
#nutr req

req = st.button("Nutritional Requirements", help = "Find out your average daily nutritional requirements!")
age = st.number_input("Enter your age: ", step=1)
gender = st.text_input("Enter Gender (F/M): ")
gender = gender.lower()

#nutr req ranges
toddler = Nutr(1000, 130, 35, 13)
child = Nutr(1200, 130, 30, 19)
preteen = Nutr(1600, 130, 30, 34)
mteenager = Nutr(2800, 130, 30, 46)
fteenager = Nutr(2300, 130, 30, 46)
mYA = Nutr(2700, 130, 30, 56)
fYA = Nutr(1800, 130, 30, 46)
madult = Nutr(2200, 130, 30, 46)
fadult = Nutr(2000, 130, 30, 56)
msenior = Nutr(2000, 130, 30, 56)
fsenior = Nutr(1600, 130, 30, 46)

#nutr req outputs
with st.expander("Your Average Daily Nutritional Requirement: "):
    if age in range(1, 4):
        st.write("Average Daily Nutritional Requirements for Toddlers (Ages 1-3): ")
        st.write(toddler.__str__())
    if age in range(4, 9):
        st.write("Average Daily Nutritional Requirements for Children (Ages 4-8): ")
        st.write(child.__str__())
    if age in range(9, 14):
        st.write("Average Daily Nutritional Requirements for Preteens (Ages 9-13): ")
        st.write(preteen.__str__())
    if age in range(14, 19) and (gender=="m" or gender=="male"):
        st.write("Average Daily Nutritional Requirements for Male Teenagers (Ages 14-18): ")
        st.write(mteenager.__str__())
    if age in range(14, 19) and (gender=="f" or gender=="female"):
        st.write("Average Daily Nutritional Requirements for Female Teenagers (Ages 14-18): ")
        st.write(fteenager.__str__())
    if age in range(19, 31) and (gender=="m" or gender=="male"):
        st.write("Average Daily Nutritional Requirements in Male Young Adults (Ages 19-30): ")
        st.write(mYA.__str__())
    if age in range(19, 31) and (gender=="f" or gender=="female") :
        st.write("Average Daily Nutritional Requirements in Female Young Adults (Ages 19-30): ")
        st.write(fYA.__str__())
    if age in range(31, 51) and (gender=="m" or gender=="male") :
        st.write("Average Daily Nutritional Requirements in Male Adults (Ages 31-50 ): ")
        st.write(madult.__str__())
    if age in range(31, 51) and (gender=="f" or gender=="female") :
        st.write("Average Daily Nutritional Requirements in Female Adults (Ages 31-50 ): ")
        st.write(fadult.__str__())
    if age>=51 and (gender=="m" or gender=="male"):
        st.write("Average Daily Nutritional Requirements for Males aged 51+: ")
        st.write(msenior.__str__())
    if age>=51 and (gender=="f" or gender=="female"):
        st.write("Average Daily Nutritional Requirements for Females aged 51+: ")
        st.write(fsenior.__str__())
    
st.divider()
#dish ideas
dishideas = st.button("Dish Ideas", help="Stuck with random ingredients? Find recipe ideas!")
dishinputnum = st.number_input("Enter the number of ingredients you have: ", step=1)
ingredients = []
if dishinputnum:
    for i in range(dishinputnum):
        ingredient = st.text_input(f"Enter ingredient #{i + 1}: ")
        ingredients.append(ingredient) 
        
for ingredient in ingredients:
    st.divider()
    st.write(f"\n***Recipe using*** {ingredient}:")  # Changed "for" to "using"
    with st.expander("Recipes: "):
        for website in websites:
            if website == "https://tasty.co/search?q=":
                recipe_url, recipe_name, recipe_ingredients = parser_recipe(ingredient, website)
                if recipe_url != "No Recipe Found":
                    st.write(f"Recipe from Tasty: {recipe_name} ({recipe_url})")
                    st.write("Additional ingredients required:")  # Changed "Ingredients:" to "Additional ingredients required:"
                    for index, ingredient in enumerate(recipe_ingredients, start=1):
                        st.write(f"{index}. {ingredient}")
                    break
            else:
                recipe_url, recipe_name, recipe_ingredients = parser_recipe(ingredient, website)
                if recipe_url != "No Recipe Found":
                    st.write(f"Recipe from {website}: {recipe_name} ({recipe_url})")
                    st.write("Additional ingredients required:")  # Changed "Ingredients:" to "Additional ingredients required:"
                    for index, ingredient in enumerate(recipe_ingredients, start=1):
                        st.write(f"{index}. {ingredient}")
                    break
        else:
            st.write("No recipe found on any website for this ingredient.")

st.divider()

#nutr content
nutrcontent = st.button("Nutritional Content", help="Don't know the nutritional value of your food? Enter a dish or ingredient and find out!")
food_name = st.text_input("Enter the name of the food/ingredient/dish: ")

nutritional_info_url = get_nutritional_info_url(food_name)
with st.expander("URL: "):
    if nutritional_info_url:
        st.write("***Nutritional information URL:***", nutritional_info_url)


#images
st.divider()

image = Image.open("Pascal.png")
image2 = Image.open("Pan.png")
left_co, last_co = st.columns(2)
with left_co:
    st.image(image)
with last_co:
    st.image(image2)
