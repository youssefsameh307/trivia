from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  def pageit(request, selection):
    page = request.args.get('page',1,type=int)
    start = (page - 1)* QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [q.format() for q in selection]
    paged_questions = questions[start:min(end,len(selection))]

    return paged_questions

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
  @app.route('/questions',methods=['GET'])   #done
  def get_questions():
      category = request.args.get('category',0,type=int)

      try:
        if category==0:
          quests = Question.query.order_by(Question.id).all()
        else:
          quests = Question.query.filter_by(category=category).order_by(Question.id).all()
        all_Categories=Category.query.all()
      except:
        abort(500)

      paged_questions=pageit(request,quests)

      categories={}
      for cat in all_Categories:
          id = cat.id
          title = cat.type
          categories[id]=title


      if len(all_Categories)<category:
        abort(400)
      if len(paged_questions) == 0:
        abort(404)

     

      return jsonify({
        'success': True,
        'questions':paged_questions,
        'total_questions':len(quests),
        'current_category':category,
        'categories':categories
      })

  @app.route('/categories', methods=['GET'])  #done
  def get_categories():
      try:
        all_Categories=Category.query.all()
      except:
        abort(500)
     
      
      if len(all_Categories)==0:
        abort(404)
      else:
        categories={}
        for cat in all_Categories:
          id = cat.id
          title = cat.type
          categories[id]=title
      return jsonify({
        "success":True,
        "categories":categories
      })





  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:q_id>', methods=['DELETE'])  #done but lower page count by one if total drops from 21 to 20 fro example
  def delete_questions(q_id):
      
      try:
        the_q = Question.query.get(q_id)
        print(the_q)
      except:
        abort(500)
      if the_q == None:
        abort(404)
      deleted_id = q_id
      try:
        the_q.delete()
      except:
        abort(500)

      category = request.args.get('category',0,type=int)

      try:
        if category==0:
          quests = Question.query.order_by(Question.id).all()
        else:
          quests = Question.query.filter_by(category=category).order_by(Question.id).all()
        all_Categories=Category.query.all()
      except:
        abort(500)

      
      paged_questions=pageit(request,quests)

      
      categories={}
      for cat in all_Categories:
        id = cat.id
        title = cat.type
        categories[id]=title

      if len(all_Categories)<category:
          abort(400)
      if len(paged_questions) == 0:
        abort(404)

      

      return jsonify({
        'success': True,
        'deleted_question':deleted_id,
        'questions':paged_questions,
        'total_questions':len(quests),
        'current_category':category,
        'categories':categories
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
  @app.route('/questions', methods=['POST'])  #done
  def post_questions():
      data = request.get_json()
      try:
        question = data['question']
        answer = data['answer']
        category = data['category']
        difficulty = data['difficulty']
      except:
        abort(400)
      try:
        new_question=Question(question=question,answer=answer,category=category,difficulty=difficulty)
        new_question.insert()
      except:
        abort(500)
    
      
      category = request.args.get('category',0,type=int)

      try:
        if category==0:
          quests = Question.query.order_by(Question.id).all()
        else:
          quests = Question.query.filter_by(category=category).order_by(Question.id).all()
        all_Categories=Category.query.all()
      except:
        abort(500)

      paged_questions=pageit(request,quests)

      
      categories={}
      for cat in all_Categories:
          id = cat.id
          title = cat.type
          categories[id]=title


      if len(all_Categories)<category:
        abort(400)
      if len(paged_questions) == 0:
        abort(404)

      
      
      return jsonify({
        'success': True,
        'created_question':new_question.id,
        'questions':paged_questions,
        'total_questions':len(quests),
        'current_category':category,
        'categories':categories
      })

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search',methods=['post'])  #done
  def search():
    category = request.args.get('category',0,type=int)

    try:
      searchterm = '%' + request.get_json()['searchTerm']+'%'
    except:
      abort(400)
    try:
      if category == 0:
        selection = Question.query.filter(Question.question.ilike(searchterm)).all()
      else:
        selection = Question.query.filter(Question.question.ilike(searchterm),Question.category==category).all()
      all_Categories=Category.query.all()
    except:
      abort(500)
    questions=pageit(request,selection)

    categories={}
    for cat in all_Categories:
        id = cat.id
        title = cat.type
        categories[id]=title

    return jsonify({
      'success': True,
      'questions':questions,
      "current_category":category,
      "categories":categories,
      "total_questions":len(selection)
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  @app.route('/categories/<int:category_id>/questions', methods=['GET']) #done
  def get_question_by_category(category_id):
      if category_id>6:
        abort(404)
      
      try:
        if(category_id==0):
          selection = Question.query.all()
        else:
          selection = Question.query.filter_by(category=category_id).all()
      except:
        abort(500)

      if len(selection)==0:
        abort(404)
      
      try:
        questions = pageit(request,selection)
      except:
        abort(400)      
      
      return jsonify({
        "success":True,
        "questions":questions,
        "total_questions":len(selection),
        "current_category":category_id,

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
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_questions():
      data = request.get_json()
      try:
        previous_questions = data['previous_questions']
        quiz_category=data['quiz_category']['id']
        print(data['quiz_category'])
      except:
        abort(400)
      if quiz_category == 0:
        selection = Question.query.filter(Question.id.notin_(list(previous_questions))).all()
      else:
        selection = Question.query.filter(Question.category == quiz_category,Question.id.notin_(previous_questions)).all()

      if len(selection)==0:
        random_question=None
      else:
        random_question=random.choice(selection).format()

      return jsonify({
        "success":True,
        "question":random_question
      })
  '''
  @TODO: 
  Create error handlers for all expected errors  
  including 404 and 422. 
  '''
  @app.errorhandler(404)     #done 
  def not_found(error):
      return jsonify({
          "success":False,
          "error":404,
          "message":'resource not found'
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success":False,
          "error":422,
          "message":"unprocessable"
      }),422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success":False,
          "error":400,
          "message":"bad request"
      }),400

  @app.errorhandler(500)
  def internal_error(error):
      return jsonify({
          "success":False,
          "error":500,
          "message":"internal server error"
      }),500
  
  @app.errorhandler(405)
  def not_allowed(error):
      return jsonify({
          "success":False,
          "error":405,
          "message":"method not allowed"
      }),405

  return app

    