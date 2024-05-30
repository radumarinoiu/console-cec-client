import traceback

from htpc_cec_client.constants import EventTypes, EventTargets, EVENT_TYPE_KEY, EVENT_TARGET_KEY, EVENT_VALUE_KEY
from htpc_cec_server.libcec import CECClient, CECCommands


class ConsoleManager:
    instance = None
    _powered_on = False

    _event_reactions = dict()

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
            try:
                cls.instance._event_reactions = {
                    # Power on events
                    (EventTypes.POWER_OTHER_EVENT, EventTargets.DISPLAY_STATE, True): cls.instance.power_on,
                    (EventTypes.POWER_OTHER_EVENT, EventTargets.MONITOR_STATE, True): cls.instance.power_on,
                    (EventTypes.POWER_STATUS_CHANGE, EventTargets.POWER_STATE, True): cls.instance.power_on,
                    (EventTypes.POWER_RESUME_MANUALLY, "N/A", True): cls.instance.power_on,
                    (EventTypes.POWER_RESUME_AUTOMATIC, "N/A", True): cls.instance.power_on,

                    # Power off events
                    (EventTypes.POWER_OTHER_EVENT, EventTargets.DISPLAY_STATE, False): cls.instance.power_off,
                    (EventTypes.POWER_OTHER_EVENT, EventTargets.MONITOR_STATE, False): cls.instance.power_off,
                    (EventTypes.POWER_STATUS_CHANGE, EventTargets.POWER_STATE, False): cls.instance.power_off,
                    (EventTypes.POWER_SUSPEND, "N/A", True): cls.instance.power_off,
                }
            except Exception:
                cls.instance = None
                raise
        return cls.instance

    def dispatch_event(self, event):
        return self._event_reactions.get(
            (event[EVENT_TYPE_KEY], event[EVENT_TARGET_KEY], bool(event[EVENT_VALUE_KEY])),
            lambda: print("No event found")
        )()

    @property
    def powered_on(self):
        return self._powered_on

    def power_on(self):
        # if self.powered_on:
        #     print("Already powered on")
        #     return
        self._powered_on = True
        CECClient().ProcessCECCommands(CECCommands.SWITCH_TO_GAME.value)

    def power_off(self):
        # if not self.powered_on:
        #     print("Already powered off")
        #     return
        self._powered_on = False
        CECClient().ProcessCECCommands(CECCommands.SWITCH_TO_SHIELD.value)
