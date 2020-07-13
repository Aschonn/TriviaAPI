import os
from flask import Flask, request, abort, jsonify
from sqlalchemy.sql.expression import func, select
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


#**********************pagination function********************

def paginate(request, selection, QUESTIONS_PER_PAGE):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

#**********************Create app function********************

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''@TODO: Set up CORS. Allow '*' for origins.'''

  CORS(app, resources={'/': {"origins": "*"}})

  '''@TODO: Use the after_request decorator to set Access-Control-Allow'''

  @app.after_request
  def after_request(response):
    """ Set Access Control """
    response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods','GET, POST, PATCH, DELETE, OPTIONS')
    return response

#**********************get categories********************

  @app.route('/categories')
  def get_all_categories():

      #grab all avaiable categories
      categories = Category.query.all()
      
      #format to match front end
      categories_dict={}
      
      #iterate through all categories puts them in a dict
      for category in categories:
        categories_dict[category.id]=category.type

      if categories_dict == None or len(categories_dict) == 0:
        abort(404)

      #return success response
      return jsonify({
        'success':True,
        'categories':categories_dict
      }),200


#**********************get questions********************

  @app.route('/questions')
  def get_questions():

      # get all questions, paginated, and categories
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate(request, selection, QUESTIONS_PER_PAGE)
      total_questions = len(selection)
      
      #get all cat
      categories = Category.query.order_by(Category.id).all()
      categories_dict = {}
  
      #format to match front end
      for category in categories:
        categories_dict[category.id] = category.type


      # return 404 if there are no questions for the page number
      if (len(current_questions) == 0):
        abort(404)

      # return values if there are no errors
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': total_questions,
        'categories': categories_dict
      }), 200

#**********************Delete Question********************

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):

    try:
      #grab all questions
      question = Question.query.get(id)      


      #if no questions abort 422
      if question is None:
        abort(422)
      
      #else delete
      else:
        question.delete()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate(request, selection,QUESTIONS_PER_PAGE)

      #json 
      return jsonify({
        'success': True,
        'deleted': id,
        }), 200

    except Exception:
      abort(422)

#**********************Post Question********************

  @app.route('/questions', methods=['POST'])
  def create_question():

    # Get json data from request
    data = request.get_json()
    
    # get individual data from json data
    new_question = data.get('question', '')
    new_answer = data.get('answer', '')
    new_difficulty = data.get('difficulty', '')
    new_category = data.get('category', '')
     
    # If no data appears abort 422
    if ((new_question == '') or (new_answer == '') or (new_difficulty == '') or (new_category == '')):
      abort(422)
    
    try:
      # Create a new question instance
      question_record = Question(question=new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
      
      # save question
      question_record.insert()
       
      # return success message
      return jsonify({
        'status_code':200,
        'success': True,
        'message': 'Question successfully created!'
      })
      
    except Exception:
      # return 422 status code if error
      
      print("Error is here")
      print("exception",sys.exc_info())
      abort(422)

  #**********************Post Questions********************
      
  @app.route('/questions/search', methods=['POST'])
  def search_questions():

    # Get search term from request data
    data = request.get_json()
    search_term = data.get('searchTerm', '')
    # Return 422 status code if empty search term is sent
    if search_term == '':
      abort(422)
    try:
      # get all questions that has the search term substring
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

      # if there are no questions for search term return 404
      if len(questions) == 0:
        abort(404)

      # paginate questions
      paginated_question = paginate(request, questions,QUESTIONS_PER_PAGE)
      # return response if successful
      return jsonify({
        'success': True,
        'questions': paginated_question,
        'total_questions': len(Question.query.all())
      }), 200

    except Exception:
      # This error code is returned when 404 abort
      # raises exception from try block
      abort(404)

  
  #**********************Get question by category********************    

  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    """This endpoint handles getting questions by category"""

    # get the category by id
    category = Category.query.filter_by(id=id).one_or_none()

    # abort 400 for bad request if category isn't found
    if (category is None):
      abort(422)

    questions = Question.query.filter_by(category=id).all()
    # paginate questions
    paginated_question = paginate(request, questions,QUESTIONS_PER_PAGE)

    # return the results
    return jsonify({
      'success': True,
      'questions': paginated_question,
      'total_questions': len(questions),
      'current_category': category.type
    })

#**********************Quizzes********************

  @app.route("/quizzes",methods=["POST"])
  def get_quiz_questions():

    #get data
    body = request.get_json()

    #get previous and category
    previous = body.get('previous_questions')
    category = body.get('quiz_category')

    #abort 400 if category or previous is None
    if category is None or previous is None:
        abort(400)

    #will go into all category 
    if (category['id'] == 0):
        questions = Question.query.all()
    else:
    #go into specific category
        questions = Question.query.filter_by(category=category['id']).all()

    #total questions
    total = len(questions)

    #get random question
    def get_random_question():
        return questions[random.randrange(0, total, 1)]

    #cheks if question has been used
    def check_if_used(question):
        used = False
        for x in previous:
            if (x == question.id):
                used = True

        return used

    question = get_random_question()

    while (check_if_used(question)):
        question = get_random_question()

        if (len(previous) == total):
            return jsonify({
                'success': True
            })

    return jsonify({
        'success': True,
        'question': question.format()
    })


#**********************ERRORS********************

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request error'
    }), 400


  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found'
    }), 404


  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'An error has occured, please try again'
    }), 500


  @app.errorhandler(422)
  def unprocesable_entity(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable entity'
    }), 422

  return app
