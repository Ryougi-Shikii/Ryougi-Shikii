from datetime import datetime
import uuid

# ===================== Strong Classes =====================

class User:
    """Strong class representing a registered user."""
    def __init__(self, name: str, email: str, password: str, phone: str):
        self.user_id   = str(uuid.uuid4())
        self.name      = name
        self.email     = email
        self._password = password   # stored as hash in production
        self.phone     = phone

    def login(self, email: str, password: str) -> bool:
        return self.email == email and self._password == password

    def update_profile(self, name=None, phone=None):
        if name:  self.name  = name
        if phone: self.phone = phone

    def __repr__(self):
        return f"User({self.name}, {self.email})"


class Train:
    # Strong class representing a train.
    def __init__(self, train_no: str, train_name: str, 
                 source: str, destination: str, total_seats: int):
        self.train_no    = train_no
        self.train_name  = train_name
        self.source      = source
        self.destination = destination
        self.total_seats = total_seats
        self.seats       = []       # list of Seat objects

    def get_available_seats(self, seat_class: str) -> int:
        return sum(1 for s in self.seats 
                   if s.class_type == seat_class 
                   and s.status == "AVAILABLE")

    def __repr__(self):
        return f"Train({self.train_no} - {self.train_name})"


class Station:
    # Strong class representing a railway station.
    def __init__(self, code: str, name: str, city: str):
        self.station_code = code
        self.station_name = name
        self.city         = city

    def __repr__(self):
        return f"Station({self.station_code} - {self.station_name})"


# ===================== Weak Classes =====================

class Seat:
    # Weak class — existence depends on Train.
    def __init__(self, seat_no: str, class_type: str, train: Train):
        self.seat_id    = str(uuid.uuid4())
        self.seat_no    = seat_no
        self.class_type = class_type   # 1AC | 2AC | 3AC | SL | GEN
        self.status     = "AVAILABLE"
        self.train      = train        # owning Train object

    def reserve(self):
        if self.status != "AVAILABLE":
            raise ValueError("Seat is not available.")
        self.status = "RESERVED"

    def release(self):
        self.status = "AVAILABLE"

    def __repr__(self):
        return f"Seat({self.seat_no}, {self.class_type}, {self.status})"


class Passenger:
    """Weak class — existence depends on Booking."""
    def __init__(self, name: str, age: int, 
                 gender: str, berth_pref: str):
        self.passenger_id = str(uuid.uuid4())
        self.name         = name
        self.age          = age
        self.gender       = gender
        self.berth_pref   = berth_pref  # LOWER | MIDDLE | UPPER

    def __repr__(self):
        return f"Passenger({self.name}, {self.age}, {self.gender})"


class Payment:
    """Weak class — existence depends on Booking."""
    def __init__(self, amount: float, mode: str, booking):
        self.payment_id     = str(uuid.uuid4())
        self.amount         = amount
        self.mode           = mode          # CARD | UPI | NET_BANKING
        self.status         = "PENDING"
        self.transaction_id = None
        self.booking        = booking

    def process(self) -> bool:
        # In production: call Payment Gateway API here
        self.transaction_id = "TXN" + str(uuid.uuid4())[:8].upper()
        self.status = "SUCCESS"
        return True

    def __repr__(self):
        return f"Payment({self.payment_id}, {self.amount}, {self.status})"


class Booking:
    """Weak class — existence depends on User and Train."""
    def __init__(self, user: User, train: Train, 
                 journey_date: str, seat_class: str):
        self.booking_id   = str(uuid.uuid4())
        self.booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status       = "PENDING"
        self.user         = user
        self.train        = train
        self.journey_date = journey_date
        self.seat_class   = seat_class
        self.passengers   = []
        self.payment      = None
        self.pnr          = None

    def add_passenger(self, passenger: Passenger):
        self.passengers.append(passenger)

    def confirm_booking(self):
        self.status = "CONFIRMED"
        self.pnr    = "PNR" + str(uuid.uuid4().int)[:10]

    def cancel(self):
        self.status = "CANCELLED"
        return Cancellation(self)

    def __repr__(self):
        return f"Booking({self.booking_id}, PNR={self.pnr}, {self.status})"


class Ticket:
    """Weak class — existence depends on Booking."""
    def __init__(self, booking: Booking):
        self.ticket_id = str(uuid.uuid4())
        self.pnr       = booking.pnr
        self.issue_date = datetime.now().strftime("%Y-%m-%d")
        self.booking   = booking
        self.qr_code   = f"QR_{self.pnr}"

    def generate_pdf(self) -> str:
        # In production: use reportlab to generate PDF
        return f"E-Ticket PDF for PNR {self.pnr} generated successfully."

    def __repr__(self):
        return f"Ticket(PNR={self.pnr})"


class Cancellation:
    """Weak class — existence depends on Booking."""
    def __init__(self, booking: Booking):
        self.cancel_id    = str(uuid.uuid4())
        self.cancel_date  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.booking      = booking
        self.refund_amount = self._calculate_refund()

    def _calculate_refund(self) -> float:
        # Simplified refund logic (75% refund)
        fare = self.booking.payment.amount if self.booking.payment else 0
        return fare * 0.75

    def __repr__(self):
        return f"Cancellation({self.cancel_id}, Refund=Rs.{self.refund_amount})"


# ===================== Demo Execution =====================

if __name__ == "__main__":
    # 1. Create strong objects
    user  = User("Sumit Kumar", "sumit@email.com", "pass1234", "8447530991")
    train = Train("12345", "Rajdhani Express", "Delhi", "Mumbai", 500)
    seat  = Seat("S1-L1", "3AC", train)
    train.seats.append(seat)

    # 2. Booking workflow
    booking   = Booking(user, train, "2026-05-01", "3AC")
    passenger = Passenger("Sumit Kumar", 22, "Male", "LOWER")
    booking.add_passenger(passenger)

    # 3. Payment
    payment = Payment(1450.0, "UPI", booking)
    payment.process()
    booking.payment = payment

    # 4. Confirm & generate ticket
    booking.confirm_booking()
    ticket = Ticket(booking)

    # 5. Display results
    print("=== Railway Reservation System — Forward Engineering Demo ===")
    print(user)
    print(train)
    print(booking)
    print(ticket)
    print(ticket.generate_pdf())
    print(f"Available 3AC seats: {train.get_available_seats('3AC')}")