from datetime import date
from typing import List, Dict, Any
from psycopg2 import extras
from database import get_connection
from models import StateFarmModel, LivestockTypeModel, LivestockPopulationModel


class LivestockRepository:
    """Репозиторий для выполнения CRUD-операций в базе данных животноводства.

    Содержит статические методы для работы с таблицами совхозов,
    видов скота и истории их поголовья.
    """

    # --- INSERT МЕТОДЫ (Добавление данных) ---

    @staticmethod
    def insert_farm(farm: StateFarmModel) -> None:
        """Добавляет один совхоз в базу данных.

        Args:
            farm (StateFarmModel): Pydantic-модель с данными совхоза.
        """
        query = """
            INSERT INTO state_farms (farm_name, district_name, chairman_name) 
            VALUES (%s, %s, %s);
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (farm.farm_name, farm.district_name, farm.chairman_name)
                )

    @staticmethod
    def insert_many_farms(farms: List[StateFarmModel]) -> None:
        """Пакетно добавляет список совхозов в базу данных.

        Использует оптимизированный метод executemany для снижения
        нагрузки на сеть и СУБД.

        Args:
            farms (List[StateFarmModel]): Список моделей совхозов для вставки.
        """
        query = """
            INSERT INTO state_farms (farm_name, district_name, chairman_name) 
            VALUES (%s, %s, %s);
        """
        data = [
            (f.farm_name, f.district_name, f.chairman_name)
            for f in farms
        ]
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(query, data)

    @staticmethod
    def insert_livestock(item: LivestockTypeModel) -> None:
        """Добавляет один вид скота в базу данных.

        Args:
            item (LivestockTypeModel): Модель данных вида и породы скота.
        """
        query = "INSERT INTO livestock_types (type_name, breed) VALUES (%s, %s);"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (item.type_name, item.breed))

    @staticmethod
    def insert_many_livestock(items: List[LivestockTypeModel]) -> None:
        """Пакетно добавляет список видов скота в базу данных.

        Args:
            items (List[LivestockTypeModel]): Список моделей видов скота.
        """
        query = "INSERT INTO livestock_types (type_name, breed) VALUES (%s, %s);"
        data = [(item.type_name, item.breed) for item in items]
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(query, data)

    @staticmethod
    def insert_population(pop: LivestockPopulationModel) -> None:
        """Добавляет одну запись о поголовье скота в историю.

        Args:
            pop (LivestockPopulationModel): Модель исторической записи поголовья.
        """
        query = """
            INSERT INTO livestock_population 
            (farm_code, cattle_code, stat_date, head_count) 
            VALUES (%s, %s, %s, %s);
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (pop.farm_code, pop.cattle_code, pop.stat_date, pop.head_count)
                )

    @staticmethod
    def insert_many_populations(populations: List[LivestockPopulationModel]) -> None:
        """Пакетно добавляет исторические записи о поголовье скота.

        Args:
            populations (List[LivestockPopulationModel]): Список моделей поголовья.
        """
        query = """
            INSERT INTO livestock_population 
            (farm_code, cattle_code, stat_date, head_count) 
            VALUES (%s, %s, %s, %s);
        """
        data = [
            (p.farm_code, p.cattle_code, p.stat_date, p.head_count)
            for p in populations
        ]
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(query, data)

    # --- SELECT МЕТОДЫ (Выборка данных) ---

    @staticmethod
    def get_all_from_table(table_name: str) -> List[Dict[str, Any]]:
        """Выбирает абсолютно все строки из указанной таблицы.

        Для безопасности применяется белый список (White-list) имен таблиц,
        предотвращающий SQL-инъекции через динамическое имя таблицы.

        Args:
            table_name (str): Название целевой таблицы в БД.

        Returns:
            List[Dict[str, Any]]: Список строк, где каждая строка представлена
                в виде словаря формата {название_колонки: значение}.

        Raises:
            ValueError: Если переданное имя таблицы отсутствует в белом списке.
        """
        valid_tables = ['state_farms', 'livestock_types', 'livestock_population']
        if table_name not in valid_tables:
            raise ValueError(f"Недопустимое имя таблицы: '{table_name}'")

        query = f"SELECT * FROM {table_name};"
        with get_connection() as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute(query)
                return cur.fetchall()

    @staticmethod
    def get_farms_by_district(district_name: str) -> List[Dict[str, Any]]:
        """Выбирает совхозы, относящиеся к указанному району области.

        Args:
            district_name (str): Название района для фильтрации.

        Returns:
            List[Dict[str, Any]]: Список словарей с данными отфильтрованных совхозов.
        """
        query = "SELECT * FROM state_farms WHERE district_name = %s;"
        with get_connection() as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute(query, (district_name,))
                return cur.fetchall()

    @staticmethod
    def get_joined_report() -> List[Dict[str, Any]]:
        """Формирует сложный соединенный аналитический отчет.

        Объединяет таблицы поголовья, совхозов и видов скота для получения
        полной текстовой информации. Сортирует по дате сбора данных (по убыванию).

        Returns:
            List[Dict[str, Any]]: Набор данных со столбцами: farm_name,
                district_name, type_name, breed, stat_date, head_count.
        """
        query = """
            SELECT 
                sf.farm_name, 
                sf.district_name, 
                lt.type_name, 
                lt.breed, 
                lp.stat_date, 
                lp.head_count
            FROM livestock_population lp
            JOIN state_farms sf ON lp.farm_code = sf.farm_code
            JOIN livestock_types lt ON lp.cattle_code = lt.cattle_code
            ORDER BY lp.stat_date DESC;
        """
        with get_connection() as conn:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute(query)
                return cur.fetchall()

    # --- UPDATE МЕТОДЫ (Обновление данных) ---

    @staticmethod
    def update_farm_chairman(farm_code: int, new_chairman: str) -> None:
        """Обновляет ФИО председателя конкретного совхоза.

        Args:
            farm_code (int): Идентификатор (ID) изменяемого совхоза.
            new_chairman (str): Новые ФИО председателя совхоза.
        """
        query = "UPDATE state_farms SET chairman_name = %s WHERE farm_code = %s;"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (new_chairman, farm_code))

    @staticmethod
    def update_population_count(
        farm_code: int,
        cattle_code: int,
        stat_date: date,
        new_count: int
    ) -> None:
        """Обновляет количество поголовья для определенной исторической записи.

        Идентифицирует запись по ее составному первичному ключу.

        Args:
            farm_code (int): Идентификатор совхоза.
            cattle_code (int): Идентификатор вида скота.
            stat_date (date): Точная дата фиксации статистики.
            new_count (int): Новое значение численности поголовья.
        """
        query = """
            UPDATE livestock_population 
            SET head_count = %s 
            WHERE farm_code = %s AND cattle_code = %s AND stat_date = %s;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (new_count, farm_code, cattle_code, stat_date)
                )

    # --- DELETE МЕТОДЫ (Удаление данных) ---

    @staticmethod
    def delete_population_by_date(target_date: date) -> None:
        """Удаляет все записи о поголовье за указанную дату.

        Args:
            target_date (date): Дата, за которую необходимо очистить статистику.
        """
        query = "DELETE FROM livestock_population WHERE stat_date = %s;"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (target_date,))

    @staticmethod
    def truncate_table(table_name: str) -> None:
        """Полностью и безвозвратно удаляет все данные из указанной таблицы.

        Использует инструкцию TRUNCATE CASCADE для сохранения ссылочной
        целостности на уровне СУБД (автоматически очищает зависимые строки).
        Применяет белый список имен таблиц для безопасности.

        Args:
            table_name (str): Название очищаемой таблицы.

        Raises:
            ValueError: Если переданное имя таблицы отсутствует в белом списке.
        """
        valid_tables = ['state_farms', 'livestock_types', 'livestock_population']
        if table_name not in valid_tables:
            raise ValueError(f"Недопустимое имя таблицы: '{table_name}'")

        query = f"TRUNCATE TABLE {table_name} CASCADE;"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)