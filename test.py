import time
import redis
from unittest import TestCase
from meeting import Meeting

class MeetingTestCase(TestCase):

    def setUp(self):
        r = redis.StrictRedis(
            host='localhost',
            port=6379,
            password='',
            decode_responses=True
        )
        r.flushall()

        self.m = Meeting(r, 'All hands')

    def test_initializaiton(self):
        self.assertEqual(self.m.users, [])
        self.assertEqual(self.m.queue, [])

    def test_adding_removing_users(self):
        self.m.add_user('Zach')
        self.m.add_user('Zach')
        self.assertEqual(self.m.users, ['Zach'])

        self.m.add_user('Maggie')
        # Alpha sorted
        self.assertEqual(self.m.users, ['Maggie', 'Zach'])

        self.m.remove_user('Zach')
        self.assertEqual(self.m.users, ['Maggie'])

    def test_queueing(self):
        self.m.add_user('Chris')
        self.m.add_user('Bob')
        self.m.add_user('Bob')
        self.m.queue_user('Bob')
        self.m.queue_user('Bob')
        self.assertEqual(self.m.queue, ['Bob'])

        self.m.add_user('Alice')
        self.m.queue_user('Alice')
        self.assertEqual(self.m.queue, ['Bob', 'Alice'])

        self.assertTrue(self.m.is_queued('Bob'))
        self.assertFalse(self.m.is_queued('Maggie'))
        self.assertFalse(self.m.is_queued('Zach'))

        self.m.add_user('Chris')
        self.m.queue_user('Chris')
        self.m.add_user('Chris')
        self.assertEqual(self.m.queue, ['Bob', 'Alice', 'Chris'])

        self.m.dequeue_user('Alice')
        self.assertEqual(self.m.queue, ['Bob', 'Chris'])

    def test_expiration(self):
        self.m.add_user('Chris')
        expr1 = self.m.seconds_remaining
        time.sleep(1)
        expr2 = self.m.seconds_remaining
        self.assertEqual(expr1, self.m.expire_mins*60)
        self.assertTrue(expr2<expr1)

        # touching the queue resets expiration
        self.m.queue_user('Chris')
        expr3 = self.m.seconds_remaining
        self.assertEqual(expr1, expr3)

    def test_toggles(self):
        self.m.add_user('Chris')
        self.m.add_user('Bob')
        self.m.queue_user('Bob')
        self.m.queue_user('Chris')

        self.m.toggle_user('Susan')
        self.assertEqual(self.m.queue, ['Bob', 'Chris'])
        self.m.add_user('Susan')
        self.assertEqual(self.m.queue, ['Bob', 'Chris'])
        self.m.toggle_user('Susan')
        self.assertEqual(self.m.queue, ['Bob', 'Chris', 'Susan'])
        self.m.toggle_user('Susan')
        self.assertEqual(self.m.queue, ['Bob', 'Chris'])
