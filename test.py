import forkme
import logging
from time import sleep
from multiprocessing.pool import ThreadPool
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from elizabeth import Personal

def wait_engine():
    engine = create_engine(
        'mysql://root:admin@proxysql/proxysql_test',
        echo=True,
        encoding='utf-8'
    )

    while True:
        try:
            engine.execute("SELECT 1")
            return engine
        except Exception as e:
            logging.exception("MySQL not awailable retrying")
            sleep(5)

defaults = Personal()
Base = declarative_base()
Session = sessionmaker()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), index=True, default=defaults.username)
    fullname = Column(String(40), index=True, default=defaults.full_name)
    password = Column(String(40), index=True, default=defaults.password)

    def __repr__(self):
       return "<User(name='%s', fullname='%s', password='%s')>" % (self.name, self.fullname, self.password)


def data_generator(i):
    session = Session()

    with session.begin_nested():
        session.add(User())

    session.commit()


def main():
    forkme.fork(4)
    pool = ThreadPool(8)

    engine = wait_engine()
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)

    for _ in pool.imap_unordered(data_generator, range(100)):
        pass


if __name__ == '__main__':
    main()
