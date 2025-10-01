from aiogram.fsm.state import State, StatesGroup

class SaffConnectionOrderStates(StatesGroup):
    waiting_client_phone = State()
    selecting_region = State()
    selecting_connection_type = State()
    selecting_tariff = State()
    entering_address = State()
    confirming_connection = State()

class SaffTechnicianOrderStates(StatesGroup):
    selecting_technician = State()
    problem_description = State()
    waiting_client_phone = State()
    selecting_region = State()
    entering_address = State()
    confirming_connection = State()

class ManagerExportStates(StatesGroup):
    selecting_export_type = State()
    selecting_export_format = State()
