from flask import Flask, jsonify, render_template, request
'''
Flask - Creates the server itself
jsonify - Turns Python dictionaries into JSON (so that the browswer can understand them)
render_template - loads HTML files from the template folder
request - lets Flask read URL parameters '''
from backend.main import get_dining_halls, get_periods, get_categories, get_food_items, get_nutrition_info
#pulls all of the scraper functions into flask

app = Flask(__name__) #Creates the server and sets up all internal routing. App is the ENTIRE web app

@app.route("/") #When someone visits the homepage, it will run this function
def home():
    return render_template("index.html") #routes the user to index.html, which will be the homepage. Renders templates/index.html

@app.route("/api/halls") #runs the function below when someone goes to /api/halls
def api_halls(): #Creates my very own Cal Dining API
    try:
        return jsonify({"halls": get_dining_halls()}) #returns the list of dining halls. Will be used for drop downs or buttons. jsonify turns it into a JSON file
    except Exception as e: #Exception is the paren class of all error types. Basically says to Catch ANY type of error and store it in the variable e.
        return jsonify({"error": str(e)}), 500 #500 means that it is a Server Error.

@app.route("/api/periods")
def api_periods():
    hall = request.args.get("hall") #reads URL like /api/periods?hall=Crossroads to select a hall
    if not hall:
        return jsonify({"error": "hall parameters required"}), 400 #400 error means that it is the users fault
    try:
        return jsonify({"periods": get_periods(hall)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/categories")
def api_categories():
    hall = request.args.get("hall")
    period = request.args.get("period")
    if not hall or not period:
        return jsonify({"error": "hall and period parameters required"}), 400
    try:
        return jsonify(get_categories(hall, period))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/foods")
def api_foods():
    hall = request.args.get("hall")
    period = request.args.get("period")
    if not hall or not period:
        return jsonify({"error": "hall, period, and category parameters required"}), 400
    try:
        categories = get_categories(hall, period)

        #List of all foods with their category info
        all_foods = []
        for category in categories:
            foods = get_food_items(hall, period, category)
            for food in foods:
                all_foods.append({
                    "name": food,
                    "category": category,
                    "hall": hall,
                    "period": period
                })
    
        return jsonify({"foods": all_foods})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/nutrition")
def api_nutrition():
    hall = request.args.get("hall")
    period = request.args.get("period")
    category = request.args.get("category")
    food = request.args.get("food")
    if not hall or not period or not category or not food:
        return jsonify({"error": "all parameters required"}), 400
    try:
        return jsonify(get_nutrition_info(hall, period, category, food))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
