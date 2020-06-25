import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#**********************pagination function********************

def paginate(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  # set up CORS, allowing all origins
  CORS(app, resources={'/': {'origins': '*'}})

  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
      return response

#**********************GET CATEGORY********************

  @app.route('/categories')
  def get_categories():


    # get all categories
    categories = Category.query.all()
    
    #dict is unchangable, unordered, and indexed
    categories_dict = {}
    
    #iterate through and put the category type as the id
    for category in categories:
        categories_dict[category.id] = category.type

    # if none or 0 abort
    if categories_dict == None or len(categories_dict) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'categories': categories_dict
    })

#**********************GET QUESTION********************

  @app.route('/questions')
  def get_questions():

    # get all questions, paginate,  and total
    selection = Question.query.all()
    current_questions = paginate(request, selection)
    total = len(selection)

    # get all categories and add to dict
    categories = Category.query.all()
    categories_dict = {}
    
    
    #iterate through and put the category type as the id
    for category in categories:
        categories_dict[category.id] = category.type

        
    if len(current_questions) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': total,
        'categories': categories_dict
    })

    
      
#**********************DELETE QUESTION********************



  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):

      try:
        question = Question.query.filter_by(id=id).one_or_none()

        if question is None:
            abort(404)

        question.delete()

        return jsonify({
            'success': True,
            'deleted': id
        })

      except:
        abort(422)

    
    #**********************CREATE QUESTION********************
    
    
  @app.route('/questions', methods=['POST'])
  def post_question():

    # load user input 
    body = request.get_json()

    # if search term is present
    if body.get('searchTerm'):
        search_term = body.get('searchTerm')

        # query the database using search term
        selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        # if no result found return 404 error
        if len(selection) == 0:
            abort(404)

        # paginate results
        paginated = paginate(request, selection)

        # return results
        return jsonify({
            'success': True,
            'questions': paginated,
            'total_questions': len(Question.query.all())
        })
    
    else:

        # ensure all fields have data
        if (new_question is None) or (new_answer is None) or (new_difficulty is None) or (new_category is None):
            abort(422)

        try:
            # create new question
            question = Question(question=body.get('question'), 
                                answer=body.get('answer'),
                                difficulty=body.get('difficulty'),
                                category=body.get('category')
                                )
            
            #insert, paginate, and get total
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            total = len(Question.query.all())

            # return data to view
            return jsonify({
                'success': True,
                'created': question.id,
                'question_created': question.question,
                'questions': current_questions,
                'total_questions': total
            })

        except:
            abort(422)

    
    #**********************GET QUESTIONS FROM SPECIFIC CATEGORY********************
    
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):

      # get the category by id and total
      category = Category.query.filter_by(id=id).one_or_none()
      total = len(Question.query.all())

      # abort 400 for bad request 
      if not category:
          abort(400)

      # get the matching questions
      selection = Question.query.filter_by(category=category.id).all()

      # paginate the selection
      paginated = paginate(request, selection)

      # return the results
      return jsonify({
          'success': True,
          'questions': paginated,
          'total_questions': total,
          'current_category': category.type
      })

    
    #**********************QUIZZES********************
    
  @app.route('/quizzes', methods=['POST'])
  def get_random_quiz_question():

      # load the request body, get previous questions, get the category, and total
      body = request.get_json()
      previous = body.get('previous_questions')
      category = body.get('quiz_category')
      total = len(questions)

      if category is None or previous is None:
          abort(400)

      if category['id'] == 0:
          questions = Question.query.all()
      else:
          questions = Question.query.filter_by(category=category['id']).all()

      # picks a random question
      def get_random_question():
          return questions[random.randrange(0, len(questions), 1)]

      # get random question
      question = get_random_question()

      # checks to see if question has already been used
      def check_if_used(question):
          used = False
          for item in previous:
              if (item == question.id):
                  used = True

          return used



      # check if used, execute until unused question found
      while check_if_used(question):
          question = get_random_question()

          # if all questions have been tried, return without question
          # necessary if category has <5 questions
          if len(previous) == total:
              return jsonify({
                  'success': True
              })

      # return the question
      return jsonify({
          'success': True,
          'question': question.format()
      })

#**********************ERROR HANDLERS********************


  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400
    
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

  @app.errorhandler(500)
  def internal_service_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "Internal Service Error"
    }), 500

  return app