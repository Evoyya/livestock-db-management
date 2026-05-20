from datetime import date
import database
from models import StateFarmModel, LivestockTypeModel, LivestockPopulationModel
from repository import LivestockRepository
def run_insert_demo(repo: LivestockRepository) -> None:
    """Демонстрирует работу функций добавления записей (одиночных и массовых).

    Args:
        repo (LivestockRepository): Экземпляр репозитория для работы с БД.
    """
    print("=== 2. ТЕСТИРОВАНИЕ ФУНКЦИЙ ДОБАВЛЕНИЯ (INSERT) ===")
    # Тест одиночной вставки
    farm_single = StateFarmModel(
        farm_name="Заря",
        district_name="Ленинский",
        chairman_name="Иванов И.И."
    )
    repo.insert_farm(farm_single)

    cattle_single = LivestockTypeModel(
        type_name="Коровы",
        breed="Голштинская"
    )
    repo.insert_livestock(cattle_single)

    # Так как это первые записи, база присвоит им farm_code=1 и cattle_code=1
    pop_single = LivestockPopulationModel(
        farm_code=1,
        cattle_code=1,
        stat_date=date(2024, 12, 1),
        head_count=500
    )
    repo.insert_population(pop_single)
    print("[OK] Одиночные записи успешно добавлены в таблицы.")

    # Тест массовой вставки (executemany)
    farms_pack = [
        StateFarmModel(
            farm_name="Вперед",
            district_name="Кировский",
            chairman_name="Petrov П.П."
        ),
        StateFarmModel(
            farm_name="Светлый путь",
            district_name="Ленинский",
            chairman_name="Сидоров С.С."
        )
    ]
    repo.insert_many_farms(farms_pack)

    cattle_pack = [
        LivestockTypeModel(type_name="Свиньи", breed="Крупная белая"),
        LivestockTypeModel(type_name="Овцы", breed="Меринос")
    ]
    repo.insert_many_livestock(cattle_pack)

    # Добавляем исторические данные за разные временные периоды
    pop_pack = [
        LivestockPopulationModel(
            farm_code=1, cattle_code=1,
            stat_date=date(2025, 12, 1), head_count=550
        ),
        LivestockPopulationModel(
            farm_code=2, cattle_code=2,
            stat_date=date(2024, 11, 15), head_count=1200
        ),
        LivestockPopulationModel(
            farm_code=3, cattle_code=1,
            stat_date=date(2026, 1, 10), head_count=400
        )
    ]
    repo.insert_many_populations(pop_pack)
    print("[OK] Пакеты данных успешно вставлены через executemany.\n")
def run_select_demo(repo: LivestockRepository) -> None:
    """Демонстрирует работу параметризованных выборок и сложных соединений.

    Args:
        repo (LivestockRepository): Экземпляр репозитория для работы с БД.
    """
    print("=== 3. ТЕСТИРОВАНИЕ ВЫБОРКИ ДАННЫХ (SELECT) ===")
    print("Список всех зарегистрированных совхозов:")
    all_farms = repo.get_all_from_table("state_farms")
    for farm in all_farms:
        print(f"  - Код: {farm['farm_code']} | "
              f"Название: '{farm['farm_name']}' | "
              f"Район: {farm['district_name']}")
    target_district = "Ленинский"
    print(f"\nФильтрация совхозов по району '{target_district}':")
    for farm in repo.get_farms_by_district(target_district):
        print(f"  - {farm['farm_name']} (Председатель: {farm['chairman_name']})")
    print("\nПолный аналитический отчет по поголовью (сложный JOIN):")
    for row in repo.get_joined_report():
        print(f"  Совхоз: {row['farm_name']} ({row['district_name']}) | "
              f"Вид скота: {row['type_name']} [{row['breed']}] | "
              f"Дата сбора: {row['stat_date']} | "
              f"Поголовье: {row['head_count']} гол.", end='\n')

def run_update_demo(repo: LivestockRepository) -> None:
    """Демонстрирует обновление полей таблиц с фиксацией изменений.

    Args:
        repo (LivestockRepository): Экземпляр репозитория для работы с БД.
    """
    print("=== 4. ТЕСТИРОВАНИЕ ОБНОВЛЕНИЯ ДАННЫХ (UPDATE) ===")
    # Обновление текстового поля в справочнике совхозов
    test_farm_code = 1
    new_chairman = "Новый Председатель Н.П."
    print(f"Изменяем руководителя для совхоза с кодом {test_farm_code}...")
    repo.update_farm_chairman(test_farm_code, new_chairman)
    # Обновление численного значения поголовья по составному ключу
    test_date = date(2025, 12, 1)
    new_count = 999
    print(f"Корректируем поголовье на дату {test_date} значением {new_count}...")
    repo.update_population_count(
        farm_code=1,
        cattle_code=1,
        stat_date=test_date,
        new_count=new_count
    )
    print("\nПроверка точечных изменений через итоговый отчет:")
    for row in repo.get_joined_report():
        if row['farm_name'] == 'Заря' and row['stat_date'] == test_date:
            print(f"  -> Проверка строки: {row['farm_name']} | "
                  f"Новое поголовье: {row['head_count']}")
    print("[OK] Этап обновления успешно завершен.\n")


def run_delete_demo(repo: LivestockRepository) -> None:
    """Демонстрирует удаление данных и соблюдение ссылочной целостности.

    Args:
        repo (LivestockRepository): Экземпляр репозитория для работы с БД.
    """
    print("=== 5. ТЕСТИРОВАНИЕ УДАЛЕНИЯ ДАННЫХ (DELETE) ===")
    # Очистка логов за конкретную дату
    target_delete_date = date(2024, 11, 15)
    print(f"Удаление статистики поголовья за дату: {target_delete_date}...")
    repo.delete_population_by_date(target_delete_date)
    remaining_records = len(repo.get_all_from_table("livestock_population"))
    print(f"Оставшееся количество записей в истории: {remaining_records}")
    # Демонстрация TRUNCATE CASCADE
    print("\nВыполнение полной очистки таблицы видов скота через CASCADE...")
    repo.truncate_table("livestock_types")
    # Проверяем, удалились ли связанные данные в таблице поголовья автоматически
    farms_left = len(repo.get_all_from_table("state_farms"))
    types_left = len(repo.get_all_from_table("livestock_types"))
    pop_left = len(repo.get_all_from_table("livestock_population"))
    print(f"Осталось строк в state_farms: {farms_left}")
    print(f"Осталось строк в livestock_types: {types_left}")
    print(f"Осталось строк в livestock_population (зависимая таблица): {pop_left}")
    print("[OK] Ссылочная целостность (ON DELETE CASCADE) успешно отработала.\n")
def main() -> None:
    """Главная управляющая функция приложения."""
    print("=== НАЧАЛО ВЫПОЛНЕНИЯ СЦЕНАРИЯ ЛАБОРАТОРНОЙ РАБОТЫ ===\n")
    # Шаг 1: Инициализация структуры таблиц базы данных
    print("=== 1. ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ===")
    database.create_tables()
    print("[OK] Таблицы успешно пересозданы.\n")
    # Создание объекта репозитория данных
    repo = LivestockRepository()
    # Поочередный запуск изолированных этапов тестирования
    run_insert_demo(repo)
    run_select_demo(repo)
    run_update_demo(repo)
    run_delete_demo(repo)
    print("=== ВСЕ ЭТАПЫ ПРОГРАММЫ УСПЕШНО ВЫПОЛНЕНЫ ===")

if __name__ == '__main__':
    main()