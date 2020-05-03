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

    @app.route('/categories')
    def retrieve_categories():
        '''
        Create an endpoint to handle GET requests
        for all available categories.
        '''
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

    @app.route('/questions')
    def retrieve_questions():
        '''
        Create an endpoint to handle GET requests for questions,
        including pagination (every 10 questions).
        This endpoint should return a list of questions,
        number of total questions, current category, categories.
        '''
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

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        '''
        Create an endpoint to DELETE question using a question ID.
        '''
        question = Question.query.filter(Question.id == id).one_or_none()
        if question is None:
            abort(422)

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
    def post_search_question():
        print(request.get_data())
        submission = request.get_json()
        print(submission)
        search_term = submission.get('searchTerm', None)
        if search_term is None:
            ''' 
            Create an endpoint to POST a new question, 
            which will require the question and answer text, 
            category, and difficulty score.
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
            Create a POST endpoint to get questions based on a search term. 
            It should return any questions for whom the search term 
            is a substring of the question. 
            '''
            try:
                selection = Question.query.filter(Question.question.ilike("%" + search_term + "%")).order_by(
                    Question.id).all()
                total_questions = len(selection)
                current_questions = paginate_questions(request, selection)

                # categories
                categories = Category.query.order_by(Category.id).all()
                dict_categories = {}
                for category in categories:
                    dict_categories[category.id] = category.type
            except:
                abort(422)

            if (len(current_questions) == 0):
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': total_questions,
                'categories': dict_categories,
                'current_category': None
            })

    @app.route('/categories/<int:id>/questions')
    def retrieve_questions_by_category(id):
        '''
        Create a GET endpoint to get questions based on category.
        '''
        # categories
        try:
            categories = Category.query.order_by(Category.id).all()
            dict_categories = {}
            for category in categories:
                dict_categories[category.id] = category.type
        except:
            abort(422)

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

    @app.route('/quizzes', methods=['POST'])
    def retrieve_quizzes():
        '''
        Create a POST endpoint to get questions to play the quiz.
        This endpoint should take category and previous question parameters
        and return a random questions within the given category,
        if provided, and that is not one of the previous questions.
        '''
        print(request.get_data())
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)
        print(previous_questions)
        print(quiz_category)
        if previous_questions is None or quiz_category is quiz_category is None:
            abort(422)

        try:
            questions = Question.query.filter(Question.category == quiz_category['id']).order_by(Question.id).all()
        except:
            abort(422)

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
