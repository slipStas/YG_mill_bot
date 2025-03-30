from employee_group import EmployeeGroup


class Employee:
    name: str
    second_name: str
    phone_number: str
    telegram_id: int
    group: EmployeeGroup

    def __init__(self, name: str, second_name: str, phone_number: str, telegram_id: int):
        self.name = name
        self.second_name = second_name
        self.phone_number = phone_number
        self.telegram_id = telegram_id
        self.group = EmployeeGroup.employee.value

    def get_info(self):
        return self.name, self.second_name, self.phone_number, self.telegram_id, self.group
