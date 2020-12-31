import time

class Meeting(object):

    def __init__(self, conn, meeting_name, expire_mins=90):
        self._r = conn
        self.name = meeting_name
        self.expire_mins = 90

    @property
    def _mkey(self):
        return self.name + '_key'

    def _users(self, mini='-inf', maxi='+inf'):
        return self._r.zrangebyscore(self._mkey, mini, maxi) or []

    @property
    def users(self):
        return sorted(self._users())

    @property
    def queue(self):
        return self._users(mini=0)

    @property
    def seconds_remaining(self):
        return self._r.ttl(self._mkey)

    def add_user(self, user, score=-1, update=False):
        # xx will only update records; nx will only insert
        # This forces the API to create users before queueing them
        # It also allows users to "rejoin" a meeting (and have
        # add_user called again) without losing their place in the queue
        kwargs = {'xx' if update else 'nx': True}
        ret = self._r.zadd(self._mkey, {user: score}, **kwargs)
        self._r.expire(self._mkey, self.expire_mins * 60)
        return ret

    def remove_user(self, user):
        return self._r.zrem(self._mkey, user)

    def toggle_user(self, user):
        if self.is_queued(user):
            self.dequeue_user(user)
        else:
            self.queue_user(user)

    def queue_user(self, user):
        self.add_user(user, time.time(), update=True)

    def dequeue_user(self, user):
        self.add_user(user, score=-1, update=True)

    def is_queued(self, user):
        score = self._r.zscore(self._mkey, user)
        return score is not None and score > 0
