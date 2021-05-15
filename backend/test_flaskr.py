import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import true
from werkzeug import datastructures

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = 'postgresql://postgres@localhost:5432/'+self.database_name
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paged_questions(self):
        res=self.client().get('/questions?page=2')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'], True)
        self.assertTrue(data['questions'])

    def test_404_questions(self):
        res=self.client().get('/questions?page=1000')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_400_questions(self):
        res=self.client().get('/questions?category=9')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

   
    def test_categories(self):
        res=self.client().get('/categories')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_delete(self):
        question1 = Question(question="the question",answer="answer",difficulty=2,category=3)
        question1.insert()
        res=self.client().delete('/questions/'+str(question1.id))
        data=json.loads(res.data)

        total_questions = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question'], question1.id)
        self.assertEqual(data['total_questions'], total_questions)
    
    def test_404_delete(self):
        res=self.client().delete('/questions/1000')
        data=json.loads(res.data)

        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['message'],'resource not found')
    
    def test_post_question(self):
        res1=self.client().get('/questions')
        data1=json.loads(res1.data)
        count = data1['total_questions']

        res=self.client().post('/questions',json={
            'question':"test1",
            'answer':"test1",
            "category":2,
            "difficulty":1
        })
        data=json.loads(res.data)

        self.assertEqual(data['success'],True)
        self.assertEqual(data['total_questions'],count+1)
        self.assertTrue(data['created_question'])

    def test_400_post_question(self):    
        res=self.client().post('/questions')
        data=json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],400)

    def test_search_question(self):    
        res=self.client().post('/questions/search',json={'searchTerm':'he'})
        data=json.loads(res.data)
        x= 'he'
        selection = Question.query.filter(Question.question.ilike(f'%{x}%')).all()
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['total_questions'],len(selection))
    
    def test_fail_search(self):
        res=self.client().post('/questions/search',json={'searchTerm':[1,2,3]})
        data=json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],400)

    def test_search_category(self):
        res=self.client().get('/categories/1/questions')
        data=json.loads(res.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])


    def test_search_category_404(self):
        res=self.client().get('/categories/100/questions')
        data=json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)

    def test_quiz(self):
        res=self.client().post('/quizzes',json={
            "previous_questions":[],
            "quiz_category":{'id':1}
        })
        data=json.loads(res.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

    def test_quiz_400(self):
        res=self.client().post('/quizzes',json={
            "previous_questions":[],
            "quiz_category":{}
        })
        data=json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],400)        
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()