from app.models import Base, engine, ThanksADay, Exchange, Session, DonateAuthor


def ramp_up():
    _s = Session()
    for t in ['большое спасибо', 'большой рахмет']:
        t = ThanksADay(text=t)
        _s.add(t)

    for id, rate in [(398, 1), (643, 5), (840, 360)]:
        e = Exchange(id=id, rate=rate)
        _s.add(e)

    a = DonateAuthor(name='Неизвестный Человек')  # он должен быть #1
    _s.add(a)

    _s.commit()
    _s.close()


def reinit_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    ramp_up()


if __name__ == '__main__':
    reinit_db()
