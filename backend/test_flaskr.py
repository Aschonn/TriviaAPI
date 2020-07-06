import os #allows us to use different operating systems
import unittest #provides tools for constructing and running tests
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'postgres', 'mypassword','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # sample question for use in tests
        self.new_question = {
            'question': 'Which four states make up the 4 Corners region of the US?',
            'answer': 'Colorado, New Mexico, Arizona, Utah',
            'difficulty': 3,
            'category': '3'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()


    #********tests************

    def tearDown(self):
        """Executed after reach test"""
        pass

    
    
    
    def test_get_paginated_questions(self):
        """Tests question pagination success"""

        # get response and load data
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

   
   
   
   
    def test_404_request_beyond_valid_page(self):
        
        # send request with bad page data, load response
        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'It was not found')

    
    
    
    def test_delete_question(self):
        
        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],
                            category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()

        question_id = question.id

        questions_before = Question.query.all()

        # delete the question and store response
        response = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(response.data)

        # see if the question has been deleted
        question = Question.query.filter(Question.id == 1).one_or_none()

        # check status code and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertTrue(len(questions_before) - len(questions_after) == 1)
        self.assertEqual(question, None)

    
    
    
    def test_create_new_question(self):
        """Tests question creation success"""

        g#grab and create
        questions_before = Question.query.all()
        response = self.client().post('/questions', json=self.new_question)
        
        # load response data, get number after post, and see if the question has been created
        data = json.loads(response.data)
        questions_after = Question.query.all()
        question = Question.query.filter_by(id=data['created']).one_or_none()

        # check status code and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(questions_after) - len(questions_before) == 1)
        self.assertIsNotNone(question)

    
    
    
    
    
    def test_422_if_question_creation_fails(self):
        """Tests question creation failure 422"""

        # get questions
        questions_before = Question.query.all()

        # create blank json question
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        # number after post
        questions_after = Question.query.all()

        # check status code and success message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(len(questions_after) == len(questions_before))

    
    
    
    
    
    
    def test_search_questions(self):
        """Tests search questions success"""

        # send post request with search term
        response = self.client().post('/questions',json={'searchTerm': 'egyptians'})

        # load response
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['questions'][0]['id'], 23)




    def test_404_if_search_questions_fails(self):
        """Tests search questions failure 404"""

        # send post request with search term that should fail
        response = self.client().post('/questions',
                                      json={'searchTerm': 'abcdefghijk'})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    
    
    
    
    def test_get_questions_by_category(self):
        """Tests getting questions by category success"""

        # send request with category id 1 for science
        response = self.client().get('/categories/1/questions')

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    
    
    
    
    
    def test_400_if_questions_by_category_fails(self):
        """Tests getting questions by category failure 400"""

        # send request with category id 100
        response = self.client().get('/categories/100/questions')

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    
    
    
    
    
    def test_play_quiz_game(self):
        """Tests playing quiz game success"""

        # send post request with category and previous questions
        response = self.client().post('/quizzes',
                                      json={'previous_questions': [20, 21],
                                            'quiz_category': {'type': 'Science', 'id': '1'}})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 1)
        self.assertNotEqual(data['what is os moduleestion']['id'], 21)

    
    
    
    
    
    def test_play_quiz_fails(self):
        """Tests playing quiz game failure 400"""

        # send post request without json data
        response = self.client().post('/quizzes', json={})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()