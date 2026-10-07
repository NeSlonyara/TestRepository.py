import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple

# --- Энкапы и Базовые Классы ---

class CabinClass(Enum):
    ECONOMY = "Эконом"
    BUSINESS = "Бизнес"
    FIRST = "Первый"

class Airport:
    def __init__(self, code: str, name: str, city: str):
        self.code = code
        self.name = name
        self.city = city

    def __repr__(self):
        return f"{self.code} ({self.city})"

class Seat:
    def __init__(self, seat_id: str, cabin_class: CabinClass):
        self.seat_id = seat_id
        self.cabin_class = cabin_class
        self.is_booked = False
        self.passenger_name = None

    def __repr__(self):
        status = "Занято" if self.is_booked else "Свободно"
        return f"{self.seat_id} ({self.cabin_class.value}): {status}"

class CabinConfiguration:
    def __init__(self, cabin_class: CabinClass, rows: int, seats_per_row: int):
        self.cabin_class = cabin_class
        self.rows = rows
        self.seats_per_row = seats_per_row
        self.seats: List[Seat] = []
        self._generate_seats()

    def _generate_seats(self):
        # Буквы для нумерации мест (пропускаем 'I', чтобы не путать с '1')
        letters = "ABCDEFGHJK" 
        for r in range(1, self.rows + 1):
            for c in range(self.seats_per_row):
                if c < len(letters):
                    seat_id = f"{r}{letters[c]}"
                    self.seats.append(Seat(seat_id, self.cabin_class))

class Flight:
    def __init__(self, flight_id: str, origin: Airport, destination: Airport, 
                 departure_time: datetime.datetime, duration: datetime.timedelta):
        self.flight_id = flight_id
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.duration = duration
        self.cabins: List[CabinConfiguration] = []
        
        # Дополнительные условия
        self.special_conditions = {
            "meals": True,          # Питание
            "extra_baggage": False, # Доп. багаж
            "wifi": True            # Wi-Fi
        }

    def add_cabin(self, cabin_config: CabinConfiguration):
        self.cabins.append(cabin_config)

    def get_all_seats(self) -> List[Seat]:
        return [seat for cabin in self.cabins for seat in cabin.seats]

    def get_available_seats(self, cabin_class: Optional[CabinClass] = None) -> List[Seat]:
        seats = self.get_all_seats()
        if cabin_class:
            seats = [s for s in seats if s.cabin_class == cabin_class]
        return [s for s in seats if not s.is_booked]

    def print_seat_map(self):
        print(f"\n{'='*40}")
        print(f"ПЛАН САЛОНА РЕЙСА: {self.flight_id}")
        print(f"{'='*40}")
        for cabin in self.cabins:
            print(f"\n--- Класс: {cabin.cabin_class.value.upper()} ---")
            # Группируем места по рядам
            rows_dict = {}
            for seat in cabin.seats:
                row_num = int(''.join(filter(str.isdigit, seat.seat_id)))
                rows_dict.setdefault(row_num, []).append(seat)
            
            for row_num in sorted(rows_dict.keys()):
                row_str = ""
                for seat in sorted(rows_dict[row_num], key=lambda s: s.seat_id):
                    # Визуализация: [X] - занято, [O] - свободно
                    icon = "X" if seat.is_booked else "O"
                    row_str += f"{seat.seat_id}:[{icon}] "
                print(row_str)
        print(f"{'='*40}\n")


# --- Основная Система Авиакомпании ---

class AirlineSystem:
    def __init__(self):
        self.airports: Dict[str, Airport] = {}
        self.flights: List[Flight] = []

    def add_airport(self, code: str, name: str, city: str):
        if code in self.airports:
            print(f"Аэропорт {code} уже существует.")
            return
        self.airports[code] = Airport(code, name, city)
        print(f"Аэропорт {code} ({city}) успешно добавлен.")

    def add_flight(self, flight_id: str, origin_code: str, dest_code: str, 
                   departure_time: datetime.datetime, duration_hours: float):
        if origin_code not in self.airports or dest_code not in self.airports:
            print("Ошибка: Аэропорт вылета или прибытия не найден.")
            return
        
        duration = datetime.timedelta(hours=duration_hours)
        flight = Flight(flight_id, self.airports[origin_code], self.airports[dest_code], 
                        departure_time, duration)
        self.flights.append(flight)
        print(f"Рейс {flight_id} добавлен.")
        return flight

    def configure_flight(self, flight_id: str, cabin_class: CabinClass, rows: int, seats_per_row: int):
        flight = self._get_flight(flight_id)
        if flight:
            cabin = CabinConfiguration(cabin_class, rows, seats_per_row)
            flight.add_cabin(cabin)
            print(f"Конфигурация класса '{cabin_class.value}' добавлена к рейсу {flight_id}.")

    def set_special_conditions(self, flight_id: str, **kwargs):
        flight = self._get_flight(flight_id)
        if flight:
            flight.special_conditions.update(kwargs)

    def book_seat(self, flight_id: str, passenger_name: str, cabin_class: CabinClass, seat_id: str) -> bool:
        flight = self._get_flight(flight_id)
        if not flight:
            return False

        for seat in flight.get_all_seats():
            if seat.seat_id == seat_id and seat.cabin_class == cabin_class:
                if seat.is_booked:
                    print(f"Ошибка: Место {seat_id} уже забронировано.")
                    return False
                seat.is_booked = True
                seat.passenger_name = passenger_name
                print(f"Успех: {passenger_name} забронировал место {seat_id} ({cabin_class.value}) на рейс {flight_id}.")
                return True
        
        print(f"Ошибка: Место {seat_id} в классе {cabin_class.value} не найдено.")
        return False

    def search_flights(self, origin_code: str, dest_code: str, date: datetime.date) -> List[Flight]:
        results = [
            f for f in self.flights
            if f.origin.code == origin_code 
            and f.destination.code == dest_code 
            and f.departure_time.date() == date
        ]
        return sorted(results, key=lambda f: f.departure_time)

    def search_flights_with_adjacent_seats(self, origin_code: str, dest_code: str, 
                                           date: datetime.date, count: int, 
                                           cabin_class: CabinClass) -> List[Tuple[Flight, List[Seat]]]:
        """Поиск рейсов, где есть 'count' свободных мест рядом в одном ряду."""
        available_flights = self.search_flights(origin_code, dest_code, date)
        results = []
        
        for flight in available_flights:
            for cabin in flight.cabins:
                if cabin.cabin_class == cabin_class:
                    adjacent_seats = self._find_adjacent_seats_in_cabin(cabin, count)
                    if adjacent_seats:
                        results.append((flight, adjacent_seats))
                        break # Нашли места в этом рейсе, идем к следующему
        return results

    def search_flights_by_time_preference(self, origin_code: str, dest_code: str, 
                                          date: datetime.date, start_hour: int, end_hour: int) -> List[Flight]:
        """Поиск рейсов в заданный временной диапазон (например, утро: 6-12)."""
        all_flights = self.search_flights(origin_code, dest_code, date)
        return [f for f in all_flights if start_hour <= f.departure_time.hour < end_hour]

    # --- Вспомогательные методы ---

    def _get_flight(self, flight_id: str) -> Optional[Flight]:
        for f in self.flights:
            if f.flight_id == flight_id:
                return f
        print(f"Рейс {flight_id} не найден.")
        return None

    def _find_adjacent_seats_in_cabin(self, cabin: CabinConfiguration, count: int) -> List[Seat]:
        rows_dict = {}
        for seat in cabin.seats:
            row_num = int(''.join(filter(str.isdigit, seat.seat_id)))
            rows_dict.setdefault(row_num, []).append(seat)
        
        for row_num in sorted(rows_dict.keys()):
            row_seats = sorted(rows_dict[row_num], key=lambda s: s.seat_id)
            consecutive = []
            for seat in row_seats:
                if not seat.is_booked:
                    consecutive.append(seat)
                    if len(consecutive) == count:
                        return consecutive
                else:
                    consecutive = [] # Сброс, если ряд прерывается занятым местом
        return []


# --- ДЕМОНСТРАЦИЯ РАБОТЫ СИСТЕМЫ ---

if __name__ == "__main__":
    # Инициализация системы
    system = AirlineSystem()
    
    # 1. Добавляем аэропорты
    system.add_airport("SVO", "Шереметьево", "Москва")
    system.add_airport("JFK", "Джон Кеннеди", "Нью-Йорк")
    system.add_airport("LHR", "Хитроу", "Лондон")
    
    # Даты для тестов (сегодня и завтра)
    today = datetime.date(2026, 10, 7)
    tomorrow = datetime.date(2026, 10, 8)
    
    # 2. Добавляем рейсы
    # Рейс 1: Москва -> Нью-Йорк (утренний)
    f1 = system.add_flight("SU101", "SVO", "JFK", datetime.datetime(2026, 10, 7, 9, 30), 10.5)
    # Рейс 2: Москва -> Нью-Йорк (вечерний)
    f2 = system.add_flight("SU102", "SVO", "JFK", datetime.datetime(2026, 10, 7, 21, 0), 10.5)
    # Рейс 3: Москва -> Лондон
    f3 = system.add_flight("SU201", "SVO", "LHR", datetime.datetime(2026, 10, 7, 14, 0), 4.0)

    # 3. Устанавливаем конфигурацию мест
    # Для SU101: 2 ряда бизнеса (4 места в ряду), 5 рядов эконома (6 мест в ряду)
    system.configure_flight("SU101", CabinClass.BUSINESS, 2, 4)
    system.configure_flight("SU101", CabinClass.ECONOMY, 5, 6)
    
    # Для SU102: только эконом
    system.configure_flight("SU102", CabinClass.ECONOMY, 10, 6)
    
    # Для SU201: 1 ряд бизнеса, 3 ряда эконома
    system.configure_flight("SU201", CabinClass.BUSINESS, 1, 4)
    system.configure_flight("SU201", CabinClass.ECONOMY, 3, 6)

    # 4. Задаем специальные условия
    system.set_special_conditions("SU101", meals=True, extra_baggage=True, wifi=False)
    system.set_special_conditions("SU201", meals=True, extra_baggage=False, wifi=True)

    # 5. Бронируем несколько мест для теста
    system.book_seat("SU101", "Иван Иванов", CabinClass.BUSINESS, "1A")
    system.book_seat("SU101", "Петр Петров", CabinClass.BUSINESS, "1B")
    system.book_seat("SU101", "Анна Смирнова", CabinClass.ECONOMY, "3C")
    system.book_seat("SU101", "Олег Сидоров", CabinClass.ECONOMY, "3D") # Заняли место между 3C и 3E

    # 6. Печатаем план салона для SU101
    f1.print_seat_map()

    # 7. Поиск ближайших рейсов по направлению
    print("\n--- Поиск рейсов SVO -> JFK на сегодня ---")
    flights_svo_jfk = system.search_flights("SVO", "JFK", today)
    for f in flights_svo_jfk:
        print(f"Рейс {f.flight_id} | Вылет: {f.departure_time.strftime('%H:%M')} | "
              f"Свободно мест: {len(f.get_available_seats())}")

    # 8. Поиск рейсов с несколькими местами РЯДОМ (Доп. возможность)
    print("\n--- Поиск рейсов SVO -> JFK, где есть 2 места рядом в Экономе ---")
    adjacent_results = system.search_flights_with_adjacent_seats("SVO", "JFK", today, 2, CabinClass.ECONOMY)
    for flight, seats in adjacent_results:
        seat_ids = ", ".join([s.seat_id for s in seats])
        print(f"Рейс {flight.flight_id}: Найдены места рядом: {seat_ids}")

    # 9. Поиск с учетом временных предпочтений (Доп. возможность)
    print("\n--- Поиск утренних рейсов (с 06:00 до 12:00) SVO -> JFK ---")
    morning_flights = system.search_flights_by_time_preference("SVO", "JFK", today, 6, 12)
    for f in morning_flights:
        print(f"Утренний рейс: {f.flight_id} в {f.departure_time.strftime('%H:%M')}")

    # 10. Проверка специальных условий (Доп. возможность)
    print("\n--- Проверка спец. условий для рейса SU101 ---")
    print(f"Питание: {'Да' if f1.special_conditions['meals'] else 'Нет'}")
    print(f"Доп. багаж: {'Да' if f1.special_conditions['extra_baggage'] else 'Нет'}")
    print(f"Wi-Fi: {'Да' if f1.special_conditions['wifi'] else 'Нет'}")