# import some stuff
import signal

from loguru import logger
import curio


class SignalHandler:
    """Handles signals for MissionControl."""
    def __init__(self, shutdown_task, shutdown_mode="ask"):
        # setup the shutdown mode, one of "now" | "ask" (default) | "ask soft"
        self._shutdown_task = shutdown_task
        self._shutdown_mode = shutdown_mode

        # setup a signal so that we can catch KeyboardInterrupt/Ctrl-C and handle them async
        self._sigint_event = curio.UniversalEvent()
        signal.signal(signal.SIGINT, self._handle_sigint)

    def _handle_sigint(self, signo, frame):
        """[sync] Callback for signal.signal - communicate sigint to curio with a UniversalEvent."""
        if not self._sigint_event.is_set():
            self._sigint_event.set()

    async def sigint(self):
        """Task (daemonic): wait for sigint/Ctrl-C, [block] confirm quit, resume on declined or await shutdown."""
        try:
            while True:
                await self._sigint_event.wait()
                self._sigint_event.clear()
                if self._shutdown_mode == "now":
                    # signal shutdown as soon as this task picks up the sigint_event it was waiting on
                    await self._shutdown_task()
                elif self._shutdown_mode.startswith("ask"):
                    try:
                        # TODO: this really needs to use some form of async console.readline so it doesn't block :/
                        # atm, this works like a pause while awaiting confirmation or declination to shutdown
                        # because input blocks the Task and thus the curio.Kernel
                        response = input("Ctrl-C! Confirm to end all missions and shutdown mission control? Y/N: ")
                        if response.lower() in ["y", "ye", "yes"]:
                            await self._shutdown_task()
                        else:
                            logger.info("Shutdown declined...")
                    except EOFError as e:
                        # occurs at Ctrl-C/KeyboardInterrupt triggered when the input prompt is open
                        if self._shutdown_mode == "ask soft":
                            # shutdown for the second Ctrl-C that has triggered
                            await self._shutdown_task()
                        else:
                            # ignore the sigint - requiring hard confirmation from user to quit
                            logger.error("Response required, none was given :(")
                else:
                    raise ValueError(f"MissionControl._shutdown_mode must be 'now'|'ask'|'ask soft'")
        except curio.CancelledError as e:
            logger.debug("MissionControl.sigint cancelled")
            raise
