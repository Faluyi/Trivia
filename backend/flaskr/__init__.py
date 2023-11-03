import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, paginate_questions

QUESTIONS_PER_PAGE = 10

# def create_app(test_config=None):
  # create and configure the app
app = Flask(__name__)
setup_db(app)

'''
@TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
'''
CORS(app)
'''
@TODO: Use the after_request decorator to set Access-Control-Allow
'''
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
  response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH. DELETE, OPTIONS')
  return response
'''
@TODO: 
Create an endpoint to handle GET requests 
for all available categories.
'''
@app.get('/categories')
def get_categories():
  categories = Category.query.all()
  formatted_categories = [category.format() for category in categories]
  return jsonify({
    'categories': formatted_categories
  })

'''
@TODO: 
Create an endpoint to handle GET requests for questions, 
including pagination (every 10 questions). 
This endpoint should return a list of questions, 
number of total questions, current category, categories. 

TEST: At this point, when you start the application
you should see questions and categories generated,
ten questions per page and pagination at the bottom of the screen for three pages.
Clicking on the page numbers should update the questions. 
'''
@app.get('/questions')
def get_questions():
  questions = Question.query.all()
  
  categories = Category.query.all()
  formatted_categories = [ category.format() for category in categories ]
  
  return jsonify({
    'questions': paginate_questions(request, questions),
    'totalQuestions': len(questions),
    'categories': formatted_categories,
    'currentCategory': ''
  })

'''
@TODO: 
Create an endpoint to DELETE question using a question ID. 

TEST: When you click the trash icon next to a question, the question will be removed.
This removal will persist in the database and when you refresh the page. 
'''
@app.delete('/questions/<int:question_id>')
def delete_question(question_id):
  question = Question.query.filter(Question.id == question_id).one_or_none()
  if question is None:
    abort(404)
   
  else:
    question.delete()
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)
    
    return jsonify({
      'deleted': question_id,
      'questions': current_questions,
      'totalQuestions': len(questions)
    })
  

'''
@TODO: 
Create an endpoint to POST a new question, 
which will require the question and answer text, 
category, and difficulty score.

TEST: When you submit a question on the "Add" tab, 
the form will clear and the question will appear at the end of the last page
of the questions list in the "List" tab.  
'''
@app.post('/questions')
def add_question():
  body = request.get_json()
  question = body.get('question')
  answer = body.get('answer')
  difficulty = body.get('difficulty')
  category = body.get('category')
  
  try:
    question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
    question.insert()
    
    return jsonify({
      'success': True
    })
    
  except:
    abort(422)
    
  
'''
@TODO: 
Create a POST endpoint to get questions based on a search term. 
It should return any questions for whom the search term 
is a substring of the question. 

TEST: Search by any phrase. The questions list will update to include 
only question that include that string within their question. 
Try using the word "title" to start. 
'''
@app.post('/question')
def search_question():
  body = request.get_json()
  search_term = body.get('searchTerm', None)
  
  query = '%{0}%'.format(search_term)
  search = list(Question.query.filter(Question.question.ilike(query)).all())
  response = []
  for res in search:
    question = {
      'id':res.id,
      'question': res.question,
      'answer': res.answer,
      'difficulty': res.difficulty,
      'category': res.category
    }
    response.append(question)
  
 
  return jsonify({
    'question': response,
    'totalQuestion': len(response),
    'currentCategory': ''
        })
'''
@TODO: 
Create a GET endpoint to get questions based on category. 

TEST: In the "List" tab / main screen, clicking on one of the 
categories in the left column will cause only questions of that 
category to be shown. 
'''
@app.get('/categories/<int:category_id>/questions')
def get_questions_in_category(category_id):
  category = Category.query.filter(Category.id == category_id).one_or_none()
  if category is None:
    abort(404)
  
  else:
    type = category.type
    questions = Question.query.filter(Question.category == category_id)
    current_questions = paginate_questions(request, questions)

    return jsonify({
      'questions': current_questions,
      'totalQuestions': len(Question.query.all()),
      'currentCategory': type
    }) 

'''
@TODO: 
Create a POST endpoint to get questions to play the quiz. 
This endpoint should take category and previous question parameters 
and return a random questions within the given category, 
if provided, and that is not one of the previous questions. 

TEST: In the "Play" tab, after a user selects "All" or a category,
one question at a time is displayed, the user is allowed to answer
and shown whether they were correct or not. 
'''
@app.post('/quizzes')
def quiz():
  body = request.get_json()
  previous_questions = body.get('previous_questions')
  quiz_category = body.get('quiz_category')
  category  = Category.query.filter(Category.type == quiz_category).one_or_none()

  if category is None:
    return abort(404)
  
  else:
    category_id = category.id
    questions = Question.query.filter(Question.category == category_id)
    
    for question in questions:
      if question.id not in previous_questions:
        break
      
    return jsonify({
      'question':{
            'id': question.id,
            'question': question.question,
            'answer': question.answer, 
            'difficulty': question.difficulty,
            'category': quiz_category
      }
        })
        
  
  
'''
@TODO: 
Create error handlers for all expected errors 
including 404 and 422. 
'''

@app.errorhandler(404)
def not_found(error):
  return jsonify({
    "success": False,
    "error": 404,
    "message": "resource not found"
  }), 404
  
@app.errorhandler(422)
def unprocessable(error):
  return jsonify({
    "success": False,
    "error": 422,
    "message": "unprocessable"
  }), 422
  
@app.errorhandler(400)
def bad_request(error):
  return jsonify({
    "success": False,
    "error": 400,
    "message": "bad request"
  }), 400
  
@app.errorhandler(405)
def not_found(error):
  return jsonify({
    "success": False,
    "error": 405,
    "message": "resource not found"
  }), 404
  
  
  
  
if __name__ == "__main__":
    app.run(debug=True)

    # curl -X POST http://127.0.0.1:5000 -H "Content-Type:application/json" -d '{"searchTerm": "title"}' 