"""Toolkit for the airline reservation system."""

from copy import deepcopy
from typing import List, Optional

from loguru import logger

from tau2.domains.airline_ja.data_model import (
    AirportCode,
    AirportInfo,
    CabinClass,
    Certificate,
    DirectFlight,
    Flight,
    FlightDateStatus,
    FlightDateStatusAvailable,
    FlightDB,
    FlightInfo,
    FlightType,
    Insurance,
    Passenger,
    Payment,
    Reservation,
    ReservationFlight,
    User,
)
from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool

# TODO: Add an abstract base class for the tools


class AirlineTools(ToolKitBase):  # Tools
    """All the tools for the airline domain."""

    db: FlightDB

    def __init__(self, db: FlightDB) -> None:
        super().__init__(db)

    def _get_user(self, user_id: str) -> User:
        """Get user from database."""
        if user_id not in self.db.users:
            raise ValueError(f"User {user_id} not found")
        return self.db.users[user_id]

    def _get_reservation(self, reservation_id: str) -> Reservation:
        """Get reservation from database."""
        if reservation_id not in self.db.reservations:
            raise ValueError(f"Reservation {reservation_id} not found")
        return self.db.reservations[reservation_id]

    def _get_flight(self, flight_number: str) -> Flight:
        """Get flight from database."""
        if flight_number not in self.db.flights:
            raise ValueError(f"Flight {flight_number} not found")
        return self.db.flights[flight_number]

    def _get_flight_instance(self, flight_number: str, date: str) -> FlightDateStatus:
        """Get flight instance from database."""
        flight = self._get_flight(flight_number)
        if date not in flight.dates:
            raise ValueError(f"Flight {flight_number} not found on date {date}")
        return flight.dates[date]

    def _get_flights_from_flight_infos(
        self, flight_infos: List[FlightInfo]
    ) -> list[FlightDateStatus]:
        """Get the flight from the reservation."""
        flights = []
        for flight_info in flight_infos:
            flights.append(
                self._get_flight_instance(flight_info.flight_number, flight_info.date)
            )
        return flights

    def _get_new_reservation_id(self) -> str:
        """Get a new reservation id.
        Assume each task makes at most 3 reservations

        Returns:
            A new reservation id.

        Raises:
            ValueError: If too many reservations are made.
        """
        for reservation_id in ["HATHAT", "HATHAU", "HATHAV"]:
            if reservation_id not in self.db.reservations:
                return reservation_id
        raise ValueError("Too many reservations")

    def _get_new_payment_id(self) -> str:
        """Get a new payment id.
        Assume each task makes at most 3 payments

        Returns:
            A new payment id.
        """
        return [3221322, 3221323, 3221324]

    def _get_datetime(self) -> str:
        """Get the current datetime."""
        return "2024-05-15T15:00:00"

    def _search_direct_flight(
        self,
        date: str,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        leave_after: Optional[str] = None,
    ) -> list[DirectFlight]:
        """Search for direct flights

        Args:
            date: The date of the flight in the format 'YYYY-MM-DD', such as '2024-01-01'.
            origin: The origin city airport in three letters, such as 'HND'.
            destination: The destination city airport in three letters, such as 'KIX'.
            leave_after: The time to leave after the flight, such as '15:00:00'.
        """
        results = []
        for flight in self.db.flights.values():
            check = (
                (origin is None or flight.origin == origin)
                and (destination is None or flight.destination == destination)
                and (date in flight.dates)
                and (flight.dates[date].status == "予約可能")
                and (
                    leave_after is None
                    or flight.scheduled_departure_time_jst >= leave_after
                )
            )
            if check:
                direct_flight = DirectFlight(
                    flight_number=flight.flight_number,
                    origin=flight.origin,
                    destination=flight.destination,
                    status="予約可能",
                    scheduled_departure_time_jst=flight.scheduled_departure_time_jst,
                    scheduled_arrival_time_jst=flight.scheduled_arrival_time_jst,
                    available_seats=flight.dates[date].available_seats,
                    prices=flight.dates[date].prices,
                )
                results.append(direct_flight)
        return results

    def _payment_for_update(
        self, user: User, payment_id: str, total_price: int
    ) -> Optional[Payment]:
        """
        Process payment for update reservation

        Args:
            user: The user to process payment for.
            payment_id: The payment id to process.
            total_price: The total price to process.
            reservation: The reservation to process payment for.

        Raises:
            ValueError: If the payment method is not found.
            ValueError: If the certificate is used to update reservation.
            ValueError: If the gift card balance is not enough.
        """
        # Check payment
        if payment_id not in user.payment_methods:
            raise ValueError("Payment method not found")
        payment_method = user.payment_methods[payment_id]
        if payment_method.source == "旅行クーポン":
            raise ValueError("旅行クーポンは予約変更には使用できません")
        elif (
            payment_method.source == "ギフトカード" and payment_method.amount < total_price
        ):
            raise ValueError("ギフトカードの残高が不足しています")

        # Deduct payment
        if payment_method.source == "ギフトカード":
            payment_method.amount -= total_price

        payment = None
        # Create payment if total price is not 0
        if total_price != 0:
            payment = Payment(
                payment_id=payment_id,
                amount=total_price,
            )
        return payment

    @is_tool(ToolType.WRITE)
    def book_reservation(
        self,
        user_id: str,
        origin: str,
        destination: str,
        flight_type: FlightType,
        cabin: CabinClass,
        flights: List[FlightInfo | dict],
        passengers: List[Passenger | dict],
        payment_methods: List[Payment | dict],
        total_baggages: int,
        nonfree_baggages: int,
        insurance: Insurance,
    ) -> Reservation:
        """
        予約を行います。

        Args:
            user_id: 予約を行うユーザーのID（例: 'sara_doe_496'）。
            origin: 出発都市のIATAコード（例: 'ITM'）。
            destination: 到着都市のIATAコード（例: 'HND'）。
            flight_type: フライトの種類（例: '片道'、'往復'）。
            cabin: 座席クラス（例: 'ベーシックエコノミー'、'エコノミー'、'ビジネス'）。
            flights: 各フライト（区間）の詳細情報を含むオブジェクトの配列。
            passengers: 各乗客の詳細情報を含むオブジェクトの配列。
            payment_methods: 各支払い方法の詳細情報を含むオブジェクトの配列。
            total_baggages: 予約する手荷物の総数。
            nonfree_baggages: 予約する有料手荷物の数。
            insurance: 保険適用の有無。
        """
            # user_id: The ID of the user to book the reservation such as 'sara_doe_496'`.
            # origin: The IATA code for the origin city such as 'SFO'.
            # destination: The IATA code for the destination city such as 'JFK'.
            # flight_type: The type of flight such as 'one_way' or 'round_trip'.
            # cabin: The cabin class such as 'basic_economy', 'economy', or 'business'.
            # flights: An array of objects containing details about each piece of flight.
            # passengers: An array of objects containing details about each passenger.
            # payment_methods: An array of objects containing details about each payment method.
            # total_baggages: The total number of baggage items to book the reservation.
            # nonfree_baggages: The number of non-free baggage items to book the reservation.
            # insurance: Whether the reservation has insurance.
        if all(isinstance(flight, dict) for flight in flights):
            flights = [FlightInfo(**flight) for flight in flights]
        if all(isinstance(passenger, dict) for passenger in passengers):
            passengers = [Passenger(**passenger) for passenger in passengers]
        if all(isinstance(payment_method, dict) for payment_method in payment_methods):
            payment_methods = [
                Payment(**payment_method) for payment_method in payment_methods
            ]
        user = self._get_user(user_id)
        reservation_id = self._get_new_reservation_id()

        reservation = Reservation(
            reservation_id=reservation_id,
            user_id=user_id,
            origin=origin,
            destination=destination,
            flight_type=flight_type,
            cabin=cabin,
            flights=[],
            passengers=deepcopy(passengers),
            payment_history=deepcopy(payment_methods),
            created_at=self._get_datetime(),
            total_baggages=total_baggages,
            nonfree_baggages=nonfree_baggages,
            insurance=insurance,
        )

        # Update flights and calculate price
        total_price = 0
        all_flights_date_data: list[FlightDateStatusAvailable] = []

        for flight_info in flights:
            flight_number = flight_info.flight_number
            flight = self._get_flight(flight_number)
            flight_date_data = self._get_flight_instance(
                flight_number=flight_number, date=flight_info.date
            )
            # Checking flight availability
            if not isinstance(flight_date_data, FlightDateStatusAvailable):
                raise ValueError(
                    f"Flight {flight_number} not available on date {flight_info.date}"
                )
            # Checking seat availability
            if flight_date_data.available_seats[cabin] < len(passengers):
                raise ValueError(f"Not enough seats on flight {flight_number}")
            # Calculate price
            price = flight_date_data.prices[cabin]
            # Update reservation
            reservation.flights.append(
                ReservationFlight(
                    origin=flight.origin,
                    destination=flight.destination,
                    flight_number=flight_number,
                    date=flight_info.date,
                    price=price,
                )
            )
            all_flights_date_data.append(flight_date_data)
            total_price += price * len(passengers)

        # Add insurance fee
        if insurance == "yes":
            total_price += 4500 * len(passengers)

        # Add baggage fee
        total_price += 7500 * nonfree_baggages

        for payment_method in payment_methods:
            payment_id = payment_method.payment_id
            amount = payment_method.amount
            if payment_id not in user.payment_methods:
                raise ValueError(f"Payment method {payment_id} not found")

            user_payment_method = user.payment_methods[payment_id]
            if user_payment_method.source in {"ギフトカード", "旅行クーポン"}:
                if user_payment_method.amount < amount:
                    raise ValueError(
                        f"Not enough balance in payment method {payment_id}"
                    )

        total_payment = sum(payment.amount for payment in payment_methods)
        if total_payment != total_price:
            raise ValueError(
                f"Payment amount does not add up, total price is {total_price}, but paid {total_payment}"
            )

        # if checks pass, deduct payment
        for payment_method in payment_methods:
            payment_id = payment_method.payment_id
            amount = payment_method.amount
            user_payment_method = user.payment_methods[payment_id]
            if user_payment_method.source == "ギフトカード":
                user_payment_method.amount -= amount
            elif user_payment_method.source == "旅行クーポン":
                user.payment_methods.pop(payment_id)

        # Update DB
        for flight_date_data in all_flights_date_data:
            flight_date_data.available_seats[cabin] -= len(passengers)
        self.db.reservations[reservation_id] = reservation
        self.db.users[user_id].reservations.append(reservation_id)
        return reservation

    @is_tool(ToolType.GENERIC)
    def calculate(self, expression: str) -> str:
        # Calculate the result of a mathematical expression.

        # Args:
        #     expression: The mathematical expression to calculate, such as '2 + 2'. The expression can contain numbers, operators (+, -, *, /), parentheses, and spaces.
        """
        数式の結果を計算します。

        Args:
            expression: 計算する数式（例: '2 + 2'）。数式には数値、演算子（+, -, *, /）、括弧、スペースを含めることができます。

        Returns:
            The result of the mathematical expression.

        Raises:
            ValueError: If the expression is invalid.
        """
        if not all(char in "0123456789+-*/(). " for char in expression):
            raise ValueError("Invalid characters in expression")
        return str(round(float(eval(expression, {"__builtins__": None}, {})), 2))

    @is_tool(ToolType.WRITE)
    def cancel_reservation(self, reservation_id: str) -> Reservation:
        """
        すべての予約をキャンセルします。

        Args:
            reservation_id: 予約ID（例: '8JX2WO'）。

        Returns:
            The updated reservation.

        Raises:
            ValueError: If the reservation is not found.
        """
        reservation = self._get_reservation(reservation_id)
        logger.debug(reservation.model_dump_json(indent=4))
        # reverse the payment
        refunds = []
        for payment in reservation.payment_history:
            refunds.append(
                Payment(
                    payment_id=payment.payment_id,
                    amount=-payment.amount,
                )
            )
        reservation.payment_history.extend(refunds)
        reservation.status = "キャンセル済"
        logger.debug(self._get_reservation(reservation_id).model_dump_json(indent=4))
        # Release seats
        logger.warning("Seats release not implemented for cancellation!!!")
        return reservation

    @is_tool(ToolType.READ)
    def get_reservation_details(self, reservation_id: str) -> Reservation:
        """
        予約の詳細情報を取得します。

        Args:
            reservation_id: 予約ID（例: '8JX2WO'）。

        Returns:
            The reservation details.

        Raises:
            ValueError: If the reservation is not found.
        """
        return self._get_reservation(reservation_id)

    @is_tool(ToolType.READ)
    def get_user_details(self, user_id: str) -> User:
        """
        ユーザーの予約情報を含む詳細情報を取得すします。

        Args:
            user_id: ユーザーID（例: 'sara_doe_496'）。

        Returns:
            The user details.

        Raises:
            ValueError: If the user is not found.
        """
        return self._get_user(user_id)

    @is_tool(ToolType.READ)
    def list_all_airports(self) -> AirportInfo:  # DONE
        """利用可能なすべての空港のリストを取得します。

        Returns:
            A dictionary mapping IATA codes to AirportInfo objects.
        """
        return [
            AirportCode(iata="HND", city="羽田"),
            AirportCode(iata="NRT", city="成田"),
            AirportCode(iata="IBR", city="茨城"),
            AirportCode(iata="ITM", city="伊丹"),
            AirportCode(iata="KIX", city="関西"),
            AirportCode(iata="FUK", city="福岡"),
            AirportCode(iata="KKJ", city="北九州"),
            AirportCode(iata="HSG", city="佐賀"),
            AirportCode(iata="CTS", city="新千歳"),
            AirportCode(iata="OKD", city="丘珠"),
            AirportCode(iata="OKA", city="那覇"),
            AirportCode(iata="NGO", city="中部"),
            AirportCode(iata="SDJ", city="仙台"),
            AirportCode(iata="HIJ", city="広島"),
            AirportCode(iata="KMJ", city="熊本"),
            AirportCode(iata="MYJ", city="松山"),
            AirportCode(iata="KOJ", city="鹿児島"),
            AirportCode(iata="FSZ", city="静岡"),
            AirportCode(iata="UKB", city="神戸"),
            AirportCode(iata="NGS", city="長崎"),
        ]

    @is_tool(ToolType.READ)
    def search_direct_flight(
        self, origin: str, destination: str, date: str
    ) -> list[DirectFlight]:
        """
        特定の日にちにおける2つの都市間の直行便を検索する。

        Args:
            origin: 3文字の出発地空港コード（例: 'HND'）。
            destination: 3文字の目的地空港コード（例: 'KIX'）。
            date: 'YYYY-MM-DD' 形式のフライト日程（例: '2024-01-01'）。

        Returns:
            The direct flights between the two cities on the specific date.
        """
        return self._search_direct_flight(
            date=date, origin=origin, destination=destination
        )

    @is_tool(ToolType.READ)
    def search_onestop_flight(
        self, origin: str, destination: str, date: str
    ) -> list[tuple[DirectFlight, DirectFlight]]:
        """
        特定の日にちにおける2つの都市間の経由便（1回乗り継ぎ）を検索します。

        Args:
                origin: 3文字の出発地空港コード（例: 'HND'）。
                destination: 3文字の目的地空港コード（例: 'KIX'）。
                date: 'YYYY-MM-DD' 形式のフライト日程（例: '2024-05-01'）。

        Returns:
            A list of pairs of DirectFlight objects.
        """
        results = []
        for result1 in self._search_direct_flight(
            date=date, origin=origin, destination=None
        ):
            result1.date = date
            date2 = (
                f"2024-05-{int(date[-2:]) + 1}"
                if "+1" in result1.scheduled_arrival_time_jst
                else date
            )
            # TODO: flight1.scheduled_arrival_time_jst could have a +1?
            for result2 in self._search_direct_flight(
                date=date2,
                origin=result1.destination,
                destination=destination,
                leave_after=result1.scheduled_arrival_time_jst,
            ):
                result2.date = date2
                results.append([result1, result2])
        return results

    @is_tool(ToolType.WRITE)
    def send_certificate(self, user_id: str, amount: int) -> str:
        """
        ユーザーに旅行クーポンを送付します。慎重に実行すること！

        Args:
                user_id: 予約を行うユーザーのID（例: 'sara_doe_496'）。
                amount: 送付する旅行クーポンの金額。

        Returns:
            A message indicating the certificate was sent.

        Raises:
            ValueError: If the user is not found.
        """
        user = self._get_user(user_id)

        # add a certificate, assume at most 3 cases per task
        for payment_id in [f"certificate_{id}" for id in self._get_new_payment_id()]:
            if payment_id not in user.payment_methods:
                new_payment = Certificate(
                    id=payment_id,
                    amount=amount,
                    source="旅行クーポン",
                )
                user.payment_methods[payment_id] = new_payment
                return f"Certificate {payment_id} added to user {user_id} with amount {amount}."
        raise ValueError("Too many certificates")

    # @is_tool(ToolType.THINK)
    # def think(self, thought: str) -> str:
    #     """
    #     Use the tool to think about something.
    #     It will not obtain new information or change the database, but just append the thought to the log.
    #     Use it when complex reasoning or some cache memory is needed.

    #     Args:
    #         thought: A thought to think about.

    #     Returns:
    #         Empty string
    #     """
    #     return ""

    @is_tool(ToolType.GENERIC)
    def transfer_to_human_agents(self, summary: str) -> str:
        """
        ユーザーの問題の概要を添えて、人間のエージェントにユーザーを転送します。
        以下の条件の場合のみ転送してください：
        -  ユーザーが明示的に人間のエージェントを求めた場合
        -  ポリシーおよび利用可能なツールでは、ユーザーの問題を解決できない場合

        Args:
                summary: ユーザーの問題の概要。

        Returns:
            A message indicating the user has been transferred to a human agent.
        """
        return "Transfer successful"

    @is_tool(ToolType.WRITE)
    def update_reservation_baggages(
        self,
        reservation_id: str,
        total_baggages: int,
        nonfree_baggages: int,
        payment_id: str,
    ) -> Reservation:
        """
        予約の手荷物情報を更新します。

        Args:
            reservation_id: 予約ID（例: 'ZFA04Y'）
            total_baggages: 予約に含まれる手荷物の変更後の総数。
            nonfree_baggages: 予約に含まれる手荷物のうち、変更後の有料手荷物の個数。
            payment_id: ユーザープロフィールに保存されている決済ID（例: 'credit_card_7815826'、'gift_card_7815826'、'certificate_7815826'）。

        Returns:
            The updated reservation.

        Raises:
            ValueError: If the reservation is not found.
            ValueError: If the user is not found.
            ValueError: If the payment method is not found.
            ValueError: If the certificate cannot be used to update reservation.
            ValueError: If the gift card balance is not enough.
        """
        reservation = self._get_reservation(reservation_id)
        user = self._get_user(reservation.user_id)

        # Calculate price
        total_price = 7500 * max(0, nonfree_baggages - reservation.nonfree_baggages)

        # Create payment
        payment = self._payment_for_update(user, payment_id, total_price)
        if payment is not None:
            reservation.payment_history.append(payment)

        # Update reservation
        reservation.total_baggages = total_baggages
        reservation.nonfree_baggages = nonfree_baggages

        return reservation

    @is_tool(ToolType.WRITE)
    def update_reservation_flights(
        self,
        reservation_id: str,
        cabin: CabinClass,
        flights: List[FlightInfo | dict],
        payment_id: str,
    ) -> Reservation:
        """
        予約のフライト情報を更新します。

        Args:
                reservation_id: 予約ID（例: 'ZFA04Y'）。
                cabin: 予約の座席クラス。
                flights: 新しい予約**全体**における各フライトの詳細を含むオブジェクトの配列。経路が変更されていない場合でも、配列に含める必要があります。
                payment_id: ユーザープロフィールに保存されている決済ID（例: 'credit_card_7815826'、'gift_card_7815826'、'certificate_7815826'）。
        Returns:
            The updated reservation.

        Raises:
            ValueError: If the reservation is not found.
            ValueError: If the user is not found.
            ValueError: If the payment method is not found.
            ValueError: If the certificate cannot be used to update reservation.
            ValueError: If the gift card balance is not enough.
        """
        if all(isinstance(flight, dict) for flight in flights):
            flights = [FlightInfo(**flight) for flight in flights]
        reservation = self._get_reservation(reservation_id)
        user = self._get_user(reservation.user_id)

        # update flights and calculate price
        total_price = 0
        reservation_flights = []
        for flight_info in flights:
            # if existing flight, keep it
            matching_reservation_flight = next(
                (
                    reservation_flight
                    for reservation_flight in reservation.flights
                    if reservation_flight.flight_number == flight_info.flight_number
                    and reservation_flight.date == flight_info.date
                    and cabin == reservation.cabin
                ),
                None,
            )
            if matching_reservation_flight:
                total_price += matching_reservation_flight.price * len(
                    reservation.passengers
                )
                reservation_flights.append(matching_reservation_flight)
                continue

            # If new flight:
            flight = self._get_flight(flight_info.flight_number)
            # Check flight availability
            flight_date_data = self._get_flight_instance(
                flight_number=flight_info.flight_number,
                date=flight_info.date,
            )
            if not isinstance(flight_date_data, FlightDateStatusAvailable):
                raise ValueError(
                    f"Flight {flight_info.flight_number} not available on date {flight_info.date}"
                )

            # Check seat availability
            if flight_date_data.available_seats[cabin] < len(reservation.passengers):
                raise ValueError(
                    f"Not enough seats on flight {flight_info.flight_number}"
                )

            # Calculate price and add to reservation
            reservation_flight = ReservationFlight(
                flight_number=flight_info.flight_number,
                date=flight_info.date,
                price=flight_date_data.prices[cabin],
                origin=flight.origin,
                destination=flight.destination,
            )
            total_price += reservation_flight.price * len(reservation.passengers)
            reservation_flights.append(reservation_flight)

        # Deduct amount already paid for reservation
        total_price -= sum(flight.price for flight in reservation.flights) * len(
            reservation.passengers
        )

        # Create payment
        payment = self._payment_for_update(user, payment_id, total_price)
        if payment is not None:
            reservation.payment_history.append(payment)

        # Update reservation
        reservation.flights = reservation_flights
        reservation.cabin = cabin  # This was missing from original TauBench

        # Do not make flight database update here, assume it takes time to be updated # TODO: So this means that we don't update the seats here. What about in cancel_reservation?
        return reservation

    @is_tool(ToolType.WRITE)
    def update_reservation_passengers(
        self, reservation_id: str, passengers: List[Passenger | dict]
    ) -> Reservation:
        """
        予約の乗客情報を更新します。

        Args:
            reservation_id: 予約ID（例: 'ZFA04Y'）。
            passengers: 各乗客の詳細を含むオブジェクトの配列。

        Returns:
            The updated reservation.

        Raises:
            ValueError: If the reservation is not found.
            ValueError: If the number of passengers does not match.
        """
        if all(isinstance(passenger, dict) for passenger in passengers):
            passengers = [Passenger(**passenger) for passenger in passengers]
        reservation = self._get_reservation(reservation_id)
        logger.info(len(passengers))
        logger.info(len(reservation.passengers))
        if len(passengers) != len(reservation.passengers):
            raise ValueError("Number of passengers does not match")
        reservation.passengers = deepcopy(passengers)
        return reservation

    @is_tool(ToolType.READ)
    def get_flight_status(self, flight_number: str, date: str) -> str:
        """
        フライトの運航状況を取得します。

        Args:
            flight_number: フライト番号。
            date: フライトの日付。

        Returns:
            The status of the flight.

        Raises:
            ValueError: If the flight is not found.
        """
        return self._get_flight_instance(flight_number, date).status


if __name__ == "__main__":
    from tau2.domains.airline_ja.utils import AIRLINE_DB_PATH

    airline = AirlineTools(FlightDB.load(AIRLINE_DB_PATH))
    print(airline.get_statistics())
