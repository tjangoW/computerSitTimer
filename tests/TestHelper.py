import datetime

from computerSitTimer.MultiprocessingWithException import ProcessWithException


def run_ability_check_of_not_ending_function(target, args, timeout=None):
    """check if a function can run without error within the given timeout.
        There are possibly better solutions like some decorators out there i guess?
    """
    p = ProcessWithException(target=target, args=args)
    p.start()

    print(datetime.datetime.now())
    p.join(timeout)
    print(datetime.datetime.now())
    p.print_and_raise_if_has_exception()
    # p.kill()  # no kill in 3.6
    p.terminate()
    p.join()
    print(datetime.datetime.now())
