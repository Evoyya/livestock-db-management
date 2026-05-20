from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
class StateFarmModel(BaseModel):
    """Модель данных, представляющая совхоз области.

    Attributes:
        farm_code (Optional[int]): Уникальный идентификатор (первичный ключ)
            совхоза. Генерируется автоматически базой данных при вставке.
            По умолчанию None.
        farm_name (str): Официальное название совхоза. Обязательное поле,
            длина от 1 до 100 символов.
        district_name (Optional[str]): Название района, к которому относится
            совхоза. Максимальная длина — 100 символов. По умолчанию None.
        chairman_name (Optional[str]): Фамилия и инициалы председателя
            совхоза. Максимальная длина — 100 символов. По умолчанию None.
    """
    farm_code: Optional[int] = Field(
        default=None,
        description="Уникальный код совхоза (PK)"
    )
    farm_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название совхоза"
    )
    district_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Название района области"
    )
    chairman_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="ФИО председателя совхоза"
    )

class LivestockTypeModel(BaseModel):
    """Модель данных, представляющая вид и породу скота.

    Attributes:
        cattle_code (Optional[int]): Уникальный идентификатор (первичный ключ)
            вида скота. Генерируется автоматически БД. По умолчанию None.
        type_name (str): Название вида скота (например, 'Коровы', 'Свиньи').
            Обязательное поле, длина от 1 до 100 символов.
        breed (Optional[str]): Порода скота (например, 'Голштинская').
            Максимальная длина — 100 символов. По умолчанию None.
    """

    cattle_code: Optional[int] = Field(
        default=None,
        description="Уникальный код вида скота (PK)"
    )
    type_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название вида скота"
    )
    breed: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Порода скота"
    )

class LivestockPopulationModel(BaseModel):
    """Модель данных для фиксации поголовья скота в совхозе на определенную дату.

    Описывает исторические данные о численности конкретного вида скота
    в конкретном совхозе. Использует составной первичный ключ на уровне БД.

    Attributes:
        farm_code (int): Идентификатор совхоза. Внешний ключ (FK),
            ссылающийся на таблицу state_farms.
        cattle_code (int): Идентификатор вида скота. Внешний ключ (FK),
            ссылающийся на таблицу livestock_types.
        stat_date (date): Дата фиксации статистических данных (сбора информации).
        head_count (int): Численность поголовья скота. Обязательное
            неотрицательное целое число (>= 0).
    """

    farm_code: int = Field(
        ...,
        description="Код совхоза (FK)"
    )
    cattle_code: int = Field(
        ...,
        description="Код вида скота (FK)"
    )
    stat_date: date = Field(
        ...,
        description="Дата сбора статистических данных"
    )
    head_count: int = Field(
        ...,
        ge=0,
        description="Количество голов (только неотрицательные значения)"
    )