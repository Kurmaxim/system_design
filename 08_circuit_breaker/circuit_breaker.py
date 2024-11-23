from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict

class State(Enum):
    CLOSE = 0
    OPEN = 1
    SEMI_OPEN = 2

FAIL_COUNT = 5
TIME_LIMIT = 5  # in seconds
SUCCESS_LIMIT = 5

class ServiceState:
    def __init__(self, service_name):
        self.state = State.CLOSE
        self.service = service_name
        self.fail_count = 0
        self.success_count = 0
        self.state_time = datetime.now()

class CircuitBreaker:
    def __init__(self):
        self.services = defaultdict(ServiceState)

    def check(self, service_name):
        if service_name not in self.services:
            return True

        ss = self.services[service_name]

        print(f"# circuit breaker: state [{ss.state.value}] fail [{ss.fail_count}] success [{ss.success_count}]")

        if ss.state == State.CLOSE or ss.state == State.SEMI_OPEN:
            return True

        elif ss.state == State.OPEN:
            elapsed_seconds = (datetime.now() - ss.state_time).total_seconds()

            if elapsed_seconds >= TIME_LIMIT:
                print("# circuit breaker: time limit reached")
                ss.state = State.SEMI_OPEN
                ss.success_count = 0
                ss.fail_count = 0
                self.services[service_name] = ss
                return True

            return False

    def fail(self, service_name):
        if service_name not in self.services:
            ss = ServiceState(service_name)
            ss.fail_count = 1
            self.services[service_name] = ss
        else:
            ss = self.services[service_name]
            if ss.state == State.CLOSE:
                ss.state_time = datetime.now()
                ss.fail_count += 1
                if ss.fail_count > FAIL_COUNT:
                    print("# circuit breaker: error limit reached")
                    ss.state = State.OPEN
            elif ss.state == State.SEMI_OPEN:
                ss.state = State.OPEN
                ss.state_time = datetime.now()
                ss.success_count = 0
            self.services[service_name] = ss

    def success(self, service_name):
        if service_name in self.services:
            ss = self.services[service_name]
            if ss.state == State.SEMI_OPEN:
                ss.success_count += 1
                if ss.success_count > SUCCESS_LIMIT:
                    print("# circuit breaker: success limit reached")
                    ss.state = State.CLOSE
                    ss.success_count = 0
                    ss.fail_count = 0
            self.services[service_name] = ss