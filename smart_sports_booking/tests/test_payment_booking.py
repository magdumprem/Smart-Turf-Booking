import pytest

from app import app, db, User, Ground, Booking, Payment


@pytest.fixture
def client_and_data():
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')
    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(username='alice', email='alice@example.com')
        user.set_password('secret')
        db.session.add(user)
        db.session.commit()

        ground = Ground(
            name='City Turf',
            sport_type='Football',
            location='Downtown',
            price_per_hour=500,
            status='Available'
        )
        db.session.add(ground)
        db.session.commit()

        booking = Booking(
            user_id=user.id,
            ground_id=ground.id,
            booking_date='2026-09-10',
            time_slot='18:00-19:00',
            payment_status='Pending',
            total_amount=50000
        )
        db.session.add(booking)
        db.session.commit()

        payment = Payment(
            booking_id=booking.id,
            user_id=user.id,
            razorpay_order_id='order_test_123',
            amount=booking.total_amount,
            status='pending'
        )
        db.session.add(payment)
        db.session.commit()

        with app.test_client() as client:
            login = client.post('/login', data={'email': 'alice@example.com', 'password': 'secret'})
            assert login.status_code == 302
            yield client, booking.id


def test_payment_success_route_completes_booking(client_and_data):
    client, booking_id = client_and_data

    response = client.get(f'/payment/success/{booking_id}')

    assert response.status_code == 200
    with app.app_context():
        booking = Booking.query.get(booking_id)
        assert booking.payment_status == 'Completed'
