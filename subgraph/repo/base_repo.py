from libs.db_mysql import db_session as Session

class BaseRepository():
    def __init__(self, session: Session):
        self.session = session
        self.name = self.__class__.__name__

    def create(self, entity):
        raise NotImplementedError()

    def update(self, entity):
        raise NotImplementedError()