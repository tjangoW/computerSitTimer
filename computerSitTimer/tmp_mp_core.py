
class UiCoreInterface:
    """
    Simple center processor of user input.
    Doing a stupid implementation without async

    """
    ui_s: Dict[str, Union[MainTray, PopUp]]
    timer: CountDowner

    def __init__(self, timer_time: timedelta):
        self.timer = CountDowner(duration=timer_time)
        self.ui_s = {"tray": MainTray(self.timer), "popup": PopUp(self.timer)}

    def run(self):
        msg_to_tray = Queue(5)
        msg_to_popup = Queue(5)
        msg_to_core = Queue(5)

        processes = {"tray": ProcessWithException(target=self.ui_s["tray"].run, args=(msg_to_core,)),
                     "popup": ProcessWithException(target=self.ui_s["popup"].run, args=(msg_to_core,))}

        def start_popup_proc():
            if processes["popup"].is_alive():
                return
            if processes["popup"].exitcode is not None:
                # previous run is done
                processes["popup"].join(timeout=Const.TIMEOUT_POPUP)  # just to tie things up
                processes["popup"] = ProcessWithException(target=self.ui_s["popup"].run, args=(msg_to_core,))
            processes["popup"].start()

        processes["tray"].start()
        while True:
            has_notification, time_str, seconds_left = self.timer.get_updates()
            if has_notification:
                start_popup_proc()
                self.timer.done_and_turn_off_noti()

            sleep(Const.timeout_core)
            for proc in processes.values():
                proc.print_and_raise_if_has_exception()
