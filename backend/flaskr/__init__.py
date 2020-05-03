import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
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
  
  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/*": {"origins": "*"}})

  '''
  Use the after_request decorator to set Access-Control-Allow
  '''



  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.order_by(Category.id).all()

    dict_categories = {}
    for category in categories:
      dict_categories[category.id] = category.type

    if len(dict_categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': dict_categories,
      'total_categories': len(dict_categories)
    })

  ''' 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_questions():

    # questions
    selection = Question.query.order_by(Question.id).all()
    total_questions = len(selection)
    current_questions = paginate_questions(request, selection)

    # categories
    categories = Category.query.order_by(Category.id).all()
    dict_categories = {}
    for category in categories:
      dict_categories[category.id] = category.type

    if (len(current_questions) == 0):
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': total_questions,
      'categories': dict_categories,
      'current_category': None
    })


  '''
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):

    question = Question.query.filter(Question.id == id).one_or_none()
    if question is None:
      abort(404)

    try:
      question.delete()

      # questions
      selection = Question.query.order_by(Question.id).all()
      total_questions = len(selection)
      current_questions = paginate_questions(request, selection)


      # categories
      categories = Category.query.order_by(Category.id).all()
      dict_categories = {}
      for category in categories:
        dict_categories[category.id] = category.type

      return jsonify({
        'success': True,
        'questions': current_questions,
        'deleted': question.id,
        'total_questions': total_questions,
        'categories': dict_categories,
        'current_category': None
      })
    except:
      abort(422)

  @app.route('/questions', methods=['POST'])
  def post_question():
    submission = request.get_json()
    search_term = submission.get('searchTerm', None)
    if search_term is None:
      ''' 
      Create an endpoint to POST a new question, 
      which will require the question and answer text, 
      category, and difficulty score.

      TEST: When you submit a question on the "Add" tab, 
      the form will clear and the question will appear at the end of the last page
      of the questions list in the "List" tab.  
      '''
      try:
        # get submission
        question = submission.get('question', '')
        answer = submission.get('answer', '')
        difficulty = submission.get('difficulty', 1)
        category = submission.get('category', 1)

        # insert question
        new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
        new_question.insert()

        # questions
        selection = Question.query.order_by(Question.id).all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        # categories
        categories = Category.query.order_by(Category.id).all()
        dict_categories = {}
        for category in categories:
          dict_categories[category.id] = category.type

        return jsonify({
          'success': True,
          'created': new_question.id,
          'questions': current_questions,
          'total_questions': total_questions,
          'categories': dict_categories,
          'current_category': None
        })

      except:
        abort(422)
    else:
      '''
      @TODO: 
      Create a POST endpoint to get questions based on a search term. 
      It should return any questions for whom the search term 
      is a substring of the question. 

      TEST: Search by any phrase. The questions list will update to include 
      only question that include that string within their question. 
      Try using the word "title" to start. 
      '''
      # questions
      try:
        selection = Question.query.filter(Question.question.ilike("%" + search_term + "%")).order_by(Question.id).all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        # categories
        categories = Category.query.order_by(Category.id).all()
        dict_categories = {}
        for category in categories:
          dict_categories[category.id] = category.type

        if (len(current_questions) == 0):
          abort(404)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': total_questions,
          'categories': dict_categories,
          'current_category': None
        })

      except:
        abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def retrieve_questions_by_category(id):

    # categories
    categories = Category.query.order_by(Category.id).all()
    dict_categories = {}
    for category in categories:
      dict_categories[category.id] = category.type
    if dict_categories.get(id, None) is None:
      abort(404)

    try:
      # questions
      selection = Question.query.filter(Question.category == id).order_by(Question.id).all()
      total_questions = len(selection)
      current_questions = paginate_questions(request, selection)

      # if (len(current_questions) == 0):
      #   abort(404)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': total_questions,
        'categories': dict_categories,
        'current_category': id
      })
    except:
      abort(422)

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
  @app.route('/quizzes', methods=['POST'])
  def retrieve_quizzes():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    
    if previous_questions is None or quiz_category is quiz_category is None:
      abort(422)

    questions = Question.query.filter(Question.category == quiz_category['id']).order_by(Question.id).all()

    question = None

    while len(questions) > 0:
      question = random.choice(questions)
      if question.id in previous_questions:
        questions.remove(question)
        question = None
      else:
        break

    if question is not None:
      formatted_question = question.format()
    else:
      formatted_question = None
    return jsonify({
      'success': True,
      'question': formatted_question
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
  
  return app