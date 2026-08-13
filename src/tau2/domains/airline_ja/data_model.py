from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from tau2.domains.airline_ja.utils import AIRLINE_DB_PATH
from tau2.environment.db import DB

FlightType = Literal["往復", "片道"]
CabinClass = Literal["ビジネス", "エコノミー", "ベーシックエコノミー"]
Insurance = Literal["yes", "no"]


MembershipLevel = Annotated[
    Literal["ゴールド会員", "シルバー会員", "一般会員"], Field(description="会員レベル")
]


class AirportCode(BaseModel):
    iata: str = Field(description="IATAコード")  # IATA code
    city: str = Field(description="都市名")  # City name


AirportInfo = Annotated[list[AirportCode], Field(description="空港情報")]  # Airport information


class Name(BaseModel):
    first_name: str = Field(description="人物の名")  # The person's first name
    last_name: str = Field(description="人物の姓")  # The person's last name


class Address(BaseModel):
    address1: str = Field(description="住所1行目")  # Primary address line
    address2: Optional[str] = Field(
        None, description="住所2行目（任意）"  # Secondary address line (optional)
    )
    city: str = Field(description="市区町村")  # City name
    country: str = Field(description="国名")  # Country name
    state: str = Field(description="都道府県名")  # State or province name
    zip: str = Field(description="郵便番号")  # Postal code


# 支払い関連モデル  # Payment Related Models
class Payment(BaseModel):
    payment_id: str = Field(description="支払いの一意識別子")  # Unique identifier for the payment
    amount: int = Field(description="支払い金額（円）")  # Payment amount in JPY


class PaymentMethodBase(BaseModel):
    source: str = Field(description="支払い方法の種別")  # Type of payment method
    id: str = Field(description="支払い方法の一意識別子")  # Unique identifier for the payment method


class CreditCard(PaymentMethodBase):
    source: Literal["クレジットカード"] = Field(
        description="クレジットカードによる支払い方法"
    )
    brand: str = Field(description="クレジットカードのブランド（例：visa、mastercard）")  # Credit card brand (e.g., visa, mastercard)
    last_four: str = Field(description="クレジットカードの下4桁")  # Last four digits of the credit card


class GiftCard(PaymentMethodBase):
    source: Literal["ギフトカード"] = Field(
        description="ギフトカードによる支払い方法"
    )
    amount: float = Field(description="ギフトカードの残高")  # Gift card value amount
    id: str = Field(description="ギフトカードの一意識別子")  # Unique identifier for the gift card


class Certificate(PaymentMethodBase):
    source: Literal["旅行クーポン"] = Field(
        description="旅行クーポンによる支払い方法"
    )
    amount: float = Field(description="旅行クーポンの残高")  # Certificate value amount


PaymentMethod = Union[CreditCard, GiftCard, Certificate]


class Passenger(BaseModel):
    first_name: str = Field(description="乗客の名前（名）")  # Passenger's first name
    last_name: str = Field(description="乗客の名前（姓）")  # Passenger's last name
    dob: str = Field(description="生年月日（YYYY-MM-DD形式）")  # Date of birth in YYYY-MM-DD format


SeatPrices = Annotated[
    dict[CabinClass, int], Field(description="各座席クラスの価格")  # Prices for different cabin classes
]
AvailableSeats = Annotated[
    dict[CabinClass, int],
    Field(description="各座席クラスの空席数"),  # Available seats for different cabin classes
]


class FlightDateStatusAvailable(BaseModel):
    status: Literal["予約可能"] = Field(
        description="フライトが予約可能な状態であることを示す"
    )
    available_seats: AvailableSeats = Field(description="座席クラス別の空席数")  # Available seats by class
    prices: SeatPrices = Field(description="座席クラス別の現在価格")  # Current prices by class


class FlightDataStatusOnTime(BaseModel):
    status: Literal["定刻"] = Field(description="フライトが定刻であることを示す")
    estimated_departure_time_jst: str = Field(
        description="JSTでの推定出発時刻（YYYY-MM-DDTHH:MM:SS形式、例：2024-05-15T06:04:00）"  # Estimated departure time in JST in the format YYYY-MM-DDTHH:MM:SS, e.g 2024-05-15T06:04:00
    )
    estimated_arrival_time_jst: str = Field(
        description="JSTでの推定到着時刻（YYYY-MM-DDTHH:MM:SS形式、例：2024-05-15T07:30:00）"  # Estimated arrival time in JST in the format YYYY-MM-DDTHH:MM:SS, e.g 2024-05-15T07:30:00
    )


class FlightDataStatusFlying(BaseModel):
    status: Literal["運航中"] = Field(description="フライトが運航中であることを示す")
    actual_departure_time_jst: str = Field(
        description="JSTでの実際の出発時刻（YYYY-MM-DDTHH:MM:SS形式、例：2024-05-15T06:04:00）"  # Actual departure time in JST in the format YYYY-MM-DDTHH:MM:SS, e.g 2024-05-15T06:04:00
    )
    estimated_arrival_time_jst: str = Field(
        description="JSTでの推定到着時刻（YYYY-MM-DDTHH:MM:SS形式、例：2024-05-15T07:30:00）"  # Estimated arrival time in JST in the format YYYY-MM-DDTHH:MM:SS, e.g 2024-05-15T07:30:00
    )


class FlightDateStatusLanded(BaseModel):
    status: Literal["着陸済"] = Field(description="フライトが着陸済みであることを示す")
    actual_departure_time_jst: str = Field(
        description="JSTでの実際の出発時刻（YYYY-MM-DDTHH:MM:SS形式、例：2024-05-15T06:04:00）"  # Actual departure time in JST in the format YYYY-MM-DDTHH:MM:SS, e.g 2024-05-15T06:04:00
    )
    actual_arrival_time_jst: str = Field(
        description="JSTでの実際の到着時刻（YYYY-MM-DDTHH:MM:SS形式、例：2024-05-15T07:30:00）"  # Actual arrival time in JST in the format YYYY-MM-DDTHH:MM:SS, e.g 2024-05-15T07:30:00
    )


class FlightDateStatusCancelled(BaseModel):
    status: Literal["キャンセル済"] = Field(description="フライトがキャンセルされたことを示す")


class FlightDateStatusDelayed(BaseModel):
    status: Literal["遅延"] = Field(description="フライトが遅延していることを示す")
    estimated_departure_time_jst: str = Field(
        description="JSTでの推定出発時刻（YYYY-MM-DDTHH:MM:SS形式、例：2024-05-15T06:04:00）"  # Estimated departure time in JST in the format YYYY-MM-DDTHH:MM:SS, e.g 2024-05-15T06:04:00
    )
    estimated_arrival_time_jst: str = Field(
        description="JSTでの推定到着時刻（YYYY-MM-DDTHH:MM:SS形式、例：2024-05-15T07:30:00）"  # Estimated arrival time in JST in the format YYYY-MM-DDTHH:MM:SS, e.g 2024-05-15T07:30:00
    )


FlightDateStatus = Union[
    FlightDateStatusAvailable,
    FlightDateStatusLanded,
    FlightDateStatusCancelled,
    FlightDateStatusDelayed,
    FlightDataStatusFlying,
    FlightDataStatusOnTime,
]


class FlightBase(BaseModel):
    flight_number: str = Field(description="フライトの一意識別子")  # Unique flight identifier
    origin: str = Field(description="出発空港のIATAコード")  # IATA code for origin airport
    destination: str = Field(description="到着空港のIATAコード")  # IATA code for destination airport


class Flight(FlightBase):
    scheduled_departure_time_jst: str = Field(
        description="JSTでの定刻出発時刻（HH:MM:SS形式、例：06:00:00）"  # Scheduled departure time in JST in the format HH:MM:SS, e.g 06:00:00
    )
    scheduled_arrival_time_jst: str = Field(
        description="JSTでの定刻到着時刻（HH:MM:SS形式、例：07:00:00）"  # Scheduled arrival time in JST in the format HH:MM:SS, e.g 07:00:00
    )
    dates: Dict[str, FlightDateStatus] = Field(
        description="日付別のフライトステータス（YYYY-MM-DD）"  # Flight status by date (YYYY-MM-DD)
    )


class DirectFlight(FlightBase):
    status: Literal["予約可能"] = Field(
        description="フライトが予約可能な状態であることを示す"
    )
    scheduled_departure_time_jst: str = Field(
        description="JSTでの定刻出発時刻（HH:MM:SS形式、例：06:00:00）"  # Scheduled departure time in JST in the format HH:MM:SS, e.g 06:00:00
    )
    scheduled_arrival_time_jst: str = Field(
        description="JSTでの定刻到着時刻（HH:MM:SS形式、例：07:00:00）"  # Scheduled arrival time in JST in the format HH:MM:SS, e.g 07:00:00
    )
    date: Optional[str] = Field(
        description="フライト日付（YYYY-MM-DD形式）", default=None  # Flight date in YYYY-MM-DD format
    )
    available_seats: AvailableSeats = Field(description="座席クラス別の空席数")  # Available seats by class
    prices: SeatPrices = Field(description="座席クラス別の現在価格")  # Current prices by class


class ReservationFlight(FlightBase):
    date: str = Field(description="フライト日付（YYYY-MM-DD形式）")  # Flight date in YYYY-MM-DD format
    price: int = Field(description="フライトの価格（円）")  # Flight price in JPY.


class FlightInfo(BaseModel):
    flight_number: str = Field(description="フライト番号（例：'HAT001'）")  # Flight number, such as 'HAT001'.
    date: str = Field(
        description="フライトの日付（'YYYY-MM-DD'形式、例：'2024-05-01'）"  # The date for the flight in the format 'YYYY-MM-DD', such as '2024-05-01'.
    )


class User(BaseModel):
    user_id: str = Field(description="ユーザーの一意識別子")  # Unique identifier for the user
    name: Name = Field(description="ユーザーの氏名")  # User's full name
    address: Address = Field(description="ユーザーの住所情報")  # User's address information
    email: str = Field(description="ユーザーのメールアドレス")  # User's email address
    dob: str = Field(
        description="ユーザーの生年月日（YYYY-MM-DD形式、例：1990-04-05）"  # User's date of birth in the format YYYY-MM-DD, e.g 1990-04-05
    )
    payment_methods: Dict[str, PaymentMethod] = Field(
        description="ユーザーの登録済み支払い方法"  # User's saved payment methods
    )
    saved_passengers: List[Passenger] = Field(
        description="ユーザーの登録済み乗客情報"  # User's saved passenger information
    )
    membership: MembershipLevel = Field(description="ユーザーの会員レベル")  # User's membership level
    reservations: List[str] = Field(description="ユーザーの予約IDリスト")  # List of user's reservation IDs


# 予約モデル  # Reservation Models
class Reservation(BaseModel):
    reservation_id: str = Field(description="予約の一意識別子")  # Unique identifier for the reservation
    user_id: str = Field(description="予約したユーザーのID")  # ID of the user who made the reservation
    origin: str = Field(description="旅行出発地のIATAコード")  # IATA code for trip origin
    destination: str = Field(description="旅行目的地のIATAコード")  # IATA code for trip destination
    flight_type: FlightType = Field(description="旅行の種別")  # Type of trip
    cabin: CabinClass = Field(description="選択した座席クラス")  # Selected cabin class
    flights: List[ReservationFlight] = Field(
        description="予約に含まれるフライトのリスト"  # List of flights in the reservation
    )
    passengers: List[Passenger] = Field(
        description="予約の乗客リスト"  # List of passengers on the reservation
    )
    payment_history: List[Payment] = Field(
        description="この予約の支払い履歴"  # History of payments for this reservation
    )
    created_at: str = Field(
        description="予約作成日時（YYYY-MM-DDTHH:MM:SS形式）"  # Timestamp when reservation was created in the format YYYY-MM-DDTHH:MM:SS
    )
    total_baggages: int = Field(description="予約の手荷物総数")  # Total number of bags in reservation
    nonfree_baggages: int = Field(description="予約の有料手荷物数")  # Number of paid bags in reservation
    insurance: Insurance = Field(description="旅行保険の加入有無")  # Whether travel insurance was purchased
    status: Optional[Literal["キャンセル済"]] = Field(
        description="予約のステータス", default=None
    )


class FlightDB(DB):
    """全フライト・ユーザー・予約のデータベース。"""  # Database of all flights, users, and reservations.

    flights: Dict[str, Flight] = Field(
        description="フライト番号でインデックスされた全フライトの辞書"  # Dictionary of all flights indexed by flight number
    )
    users: Dict[str, User] = Field(
        description="ユーザーIDでインデックスされた全ユーザーの辞書"  # Dictionary of all users indexed by user ID
    )
    reservations: Dict[str, Reservation] = Field(
        description="予約IDでインデックスされた全予約の辞書"  # Dictionary of all reservations indexed by reservation ID
    )

    def get_statistics(self) -> dict[str, Any]:
        """データベースの統計情報を取得する。"""  # Get the statistics of the database.
        num_flights = len(self.flights)
        num_flights_instances = sum(
            len(flight.dates) for flight in self.flights.values()
        )
        num_users = len(self.users)
        num_reservations = len(self.reservations)
        return {
            "num_flights": num_flights,
            "num_flights_instances": num_flights_instances,
            "num_users": num_users,
            "num_reservations": num_reservations,
        }


def get_db():
    return FlightDB.load(AIRLINE_DB_PATH)


if __name__ == "__main__":
    db = get_db()
    print(db.get_statistics())
