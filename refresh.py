from app.models import Base, engine, ThanksADay, Session


def ramp_up():
    if not ThanksADay.q.count():
        _s = Session()
        for t in ['большое спасибо', 'большой рахмет']:
            t = ThanksADay(text=t)
            _s.add(t)
        _s.commit()
        _s.close()
        del _s


if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    ramp_up()