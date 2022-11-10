import os
import time
from typing import Union, Callable, Sequence
from subprocess import Popen
import signal
from enum import IntEnum

from tshared_src.tshared.utils.send_telegram_message import publish_message
from tshared_src.tshared.utils.setup_logger import log


__all__ = [
    "Args",
    "ErrorCode",
    "create_process",
    "run_processes_health_check",
]


Args = Union[str, Sequence, list[str], tuple[str]]
ErrorCode = Union[str, int]


class ServicesErrorCodes(IntEnum):
    # kill -15 <pid>
    # kill -SIGTERM <pid>
    STOPPED = -15


STOPPED_PROCESSES: list = []
REANIMATED_PROCESSES: list = []


def services_list_from_command(command: list[str]):
    try:
        services = " ".join([x for x in command[2:] if not x.startswith('-')])
        _ = services.strip()[0]
    except Exception:
        services = " ".join(command)

    return services


def reanimate(signum, frame):
    for index in range(len(STOPPED_PROCESSES)):

        # reanimation actions
        args = STOPPED_PROCESSES.pop(index)
        process = create_process(args=args)
        REANIMATED_PROCESSES.append(process)

        # send message to telegram
        services = services_list_from_command(args)

        server_env = os.getenv('SERVER_ENVIRONMENT', 'unknown')
        message = {
            'server_environment': server_env,
            'services': services,
            'message': '✅ Service has been reanimated.',
        }
        publish_message(message)


# kill -10 <pid>
# kill -SIGUSR1 <pid>
signal.signal(signal.SIGUSR1, reanimate)


def create_process(args: Args) -> Popen:
    return Popen(args=args)


def stopped_service_action(args: Args, error_code: ErrorCode = None) -> Union[Popen, ErrorCode]:
    error_code = int(error_code) if error_code is not None else error_code
    server_env = os.getenv('SERVER_ENVIRONMENT', 'unknown')
    services = services_list_from_command(args)
    message = {
        'server_environment': server_env,
        'services': services,
        'error_code': error_code
    }

    if error_code == ServicesErrorCodes.STOPPED:
        STOPPED_PROCESSES.append(args)

        message['message'] = '⏸ Service has been stopped.'
        publish_message(message)
        return error_code
    else:
        message['message'] = '⚠ Service has been restarted.'
        publish_message(message)
        return create_process(args)


def run_processes_health_check(processes: list[Popen],
                               first_aid_action: Callable[[Args, ErrorCode], Union[Popen, any]]
                               = stopped_service_action,
                               health_check_period=1,
                               debug=False):
    def check_health(process_return_code) -> bool:
        return process_return_code is None

    while True:
        codes = []
        for index, p in enumerate(processes):
            if not isinstance(p, Popen):
                processes.pop(index)
                continue

            code = p.poll()
            codes.append(code)

            if debug:
                message = f'{" ".join(p.args)} (pid: {p.pid}): return code: {code}'
                log('services').error(message)

            if not check_health(code):
                processes[index] = first_aid_action(p.args, code)

        while REANIMATED_PROCESSES:
            processes.append(REANIMATED_PROCESSES.pop())

        time.sleep(health_check_period)
