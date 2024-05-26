import time
from enum import Enum
from libcec import pyCecClient


DENON_ADDRESS = "3.0.0.0"


def get_denon_child_address(child_count):
    major_address_bit = DENON_ADDRESS.split(".")[0]
    return  f"{major_address_bit}.{child_count}.0.0"


class DenonInputs(Enum):
    CBL_SAT = get_denon_child_address(1)
    MEDIA_PLAYER = get_denon_child_address(2)
    BLU_RAY = get_denon_child_address(3)
    GAME = get_denon_child_address(4)
    AUX1 = get_denon_child_address(5)
    AUX2 = get_denon_child_address(6)


DEVICE_ADDRESSES = {
    DenonInputs.CBL_SAT.value: "TV Cable",
    DenonInputs.MEDIA_PLAYER.value: "Shield Media Player",
    DenonInputs.BLU_RAY.value: "Blu-Ray Player",
    DenonInputs.GAME.value: "Game Console",
    DenonInputs.AUX1.value: "AUX1",
    DenonInputs.AUX2.value: "AUX2",
}


# logging callback
def log_callback(level, time, message):
    return lib.LogCallback(level, time, message)

# key press callback
def key_press_callback(key, duration):
    return lib.KeyPressCallback(key, duration)

# command callback
def command_callback(cmd):
    print("[command received] " + cmd)
    split_cmd = cmd[3:].split(":")
    # print(split_cmd[0], split_cmd[1], split_cmd[0] == "5f", split_cmd[1] == "80")
    if split_cmd[0] == "5f" and split_cmd[1] == "80":
        from_address = ".".join([digit for part in split_cmd[2:4] for digit in part])
        to_address = ".".join([digit for part in split_cmd[4:6] for digit in part])
        print(
            f"[AV Receiver - Routing Change] Changed from "
            f"{DEVICE_ADDRESSES.get(from_address, from_address)} to {DEVICE_ADDRESSES.get(to_address, to_address)}"
        )

if __name__ == '__main__':
    # initialise libCEC
    lib = pyCecClient()
    lib.SetLogCallback(log_callback)
    lib.SetKeyPressCallback(key_press_callback)
    lib.SetCommandCallback(command_callback)
    lib.InitLibCec()

    lib.ProcessCommandTx("15:44:69:04")
    lib.ProcessCommandTx("14:36")

    while True:
        time.sleep(1)
