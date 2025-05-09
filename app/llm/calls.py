import inspect
from typing import Any, List, Dict
from datetime import datetime, timedelta
from mubble import AiohttpClient, Message
import datetime as datetime_module
from tortoise.exceptions import DoesNotExist

from app.llm.decorators import (
    terminate_after_answer,
)  # Декоратор, который нам нужен для замораживания ответа модели
from app.database.slot import Slot
from app.database.service import Service
from app.database.master import Master
from app.database.appointment import Appointment
from app.database.user import User


async def get_free_time_slots(
    min_slot_duration: int, start_date: str, end_date: str
) -> List[Dict[str, Any]]:
    """
    Returns free time slots for employees based on their work schedule.
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Get all available slots within date range
    slots = await Slot.filter(
        date__gte=start.date(), date__lte=end.date(), status="available"
    ).prefetch_related("service", "master")

    # Filter slots by minimum duration
    available_slots = []
    for slot in slots:
        if slot.service.duration >= min_slot_duration:
            available_slots.append(
                {
                    "id": slot.id,
                    "date": slot.date.isoformat(),
                    "time": slot.time.isoformat(),
                    "service": {
                        "id": slot.service.id,
                        "name": slot.service.name,
                        "duration": slot.service.duration,
                        "price": slot.service.price,
                    },
                    "master": {
                        "staff_id": slot.master.id,
                        "name": slot.master.name,
                        "specialization": slot.master.specialization,
                    },
                }
            )

    return available_slots


async def get_services() -> List[Dict[str, Any]]:
    """
    Returns a list of services with their details.
    """

    try:
        # Get all services
        services = await Service.all()

        result = []
        for service in services:
            service_data = {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "price": service.price,
                "duration": service.duration,  # Duration in minutes
            }
            result.append(service_data)

        return result

    except Exception as e:
        return []


async def create_record(
    staff_id: int,
    services: List[Dict[str, Any]],
    client: Dict[str, str],
    datetime: str,
    comment: str,
    message: Message,
) -> Dict[str, Any]:
    """
    Creates a new record with multiple services or single service.
    """
    # Parse datetime
    appointment_datetime = datetime_module.datetime.fromisoformat(datetime)

    # Отримати uid з message
    uid = message.from_user.id  # або message.user_id, якщо структура інша

    # Знайти користувача по uid
    try:
        user = await User.get(uid=uid)
    except DoesNotExist:
        return {
            "error": "Користувача з таким uid не знайдено. Будь ласка, зареєструйтесь спочатку."
        }

    # Оновити телефон, якщо він переданий і ще не збережений
    if client.get("phone") and not user.phone:
        user.phone = client["phone"]
        await user.save()

    # Далі як і було:
    appointments = []
    for service_info in services:
        service = await Service.get(id=service_info["id"])
        slot, _ = await Slot.get_or_create(
            date=appointment_datetime.date(),
            time=appointment_datetime.time(),
            service=service,
            master_id=staff_id,
            defaults={"status": "booked"},
        )
        appointment = await Appointment.create(user=user, slot=slot, status="active")
        appointments.append(appointment)

    return {
        "appointments": [
            {
                "id": app.id,
                "status": app.status,
                "service": {
                    "id": app.slot.service.id,
                    "name": app.slot.service.name,
                    "price": app.slot.service.price,
                    "duration": app.slot.service.duration,
                },
                "master": {
                    "id": (await app.slot.master).id,
                    "name": (await app.slot.master).name,
                },
                "datetime": f"{app.slot.date.isoformat()}T{app.slot.time.isoformat()}",
            }
            for app in appointments
        ]
    }


async def get_staff() -> list[dict]:
    """
    Returns a list of all staff (masters) with their id, name, and specialization.
    """
    masters = await Master.all()
    return [
        {
            "id": master.id,
            "name": master.name,
            "specialization": master.specialization,
        }
        for master in masters
    ]


# Словарь, который содержит все функции из этого файла
# В виде: {"название функции": функция}
# Это нужно для использования в tool_calls
tool_objects = {
    name: func
    for name, func in globals().items()
    if inspect.isfunction(func) and func.__module__ == __name__
}


__all__ = ("tool_objects",)
