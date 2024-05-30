from enum import Enum

import cec
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


class CECCommands(Enum):
    TURN_ON_TV = ["10:04", "15:04"]
    SWITCH_TO_SHIELD = ["14:44:40"]
    SWITCH_TO_GAME = ["10:04", "15:04", "15:44:69:04", "14:36"]


class CECClient:
    instance = None
    adapter = "/dev/cec0"
    cecconfig = cec.libcec_configuration()
    lib = {}
    # don't enable debug logging by default
    log_level = cec.CEC_LOG_WARNING
    show_all_commands = False

    # create a new libcec_configuration
    def SetConfiguration(self):
        self.instance.cecconfig.strDeviceName   = "pyLibCec"
        self.instance.cecconfig.bActivateSource = 0
        self.instance.cecconfig.deviceTypes.Add(cec.CEC_DEVICE_TYPE_RECORDING_DEVICE)
        self.instance.cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT
        self.instance.cecconfig.SetLogCallback(self.on_log_callback)
        self.instance.cecconfig.SetCommandCallback(self.on_command_callback)

    # initialise libCEC
    def InitLibCec(self):
        self.instance.lib = cec.ICECAdapter.Create(self.instance.cecconfig)
        # print libCEC version and compilation information
        print("libCEC version " + self.instance.lib.VersionToString(self.instance.cecconfig.serverVersion) + " loaded: " + self.instance.lib.GetLibInfo())

        if not self.instance.lib.Open(self.adapter):
            raise RuntimeError("Failed opening a connection to the CEC Adapter")

    # display the addresses controlled by libCEC
    def ProcessCommandSelf(self):
        addresses = self.instance.lib.GetLogicalAddresses()
        strOut = "Addresses controlled by libCEC: "
        x = 0
        notFirst = False
        while x < 15:
            if addresses.IsSet(x):
                if notFirst:
                    strOut += ", "
                strOut += self.instance.lib.LogicalAddressToString(x)
                if self.instance.lib.IsActiveSource(x):
                    strOut += " (*)"
                notFirst = True
            x += 1
        print(strOut)

    # send an active source message
    def ProcessCommandActiveSource(self):
        self.instance.lib.SetActiveSource()

    # send a standby command
    def ProcessCommandStandby(self):
        self.instance.lib.StandbyDevices(cec.CECDEVICE_BROADCAST)

    # send a custom command
    def ProcessCommandTx(self, data):
        cmd = self.instance.lib.CommandFromString(data)
        print("transmit " + data)
        if not self.instance.lib.Transmit(cmd):
            raise RuntimeError("Failed sending message")

    def ProcessCECCommands(self, data):
        for command in data:
            self.ProcessCommandTx(command)

    # scan the bus and display devices that were found
    def ProcessCommandScan(self):
        print("requesting CEC bus information ...")
        strLog = "CEC bus information\n===================\n"
        addresses = self.instance.lib.GetActiveDevices()
        activeSource = self.instance.lib.GetActiveSource()
        x = 0
        while x < 15:
            if addresses.IsSet(x):
                vendorId        = self.instance.lib.GetDeviceVendorId(x)
                physicalAddress = self.instance.lib.GetDevicePhysicalAddress(x)
                active          = self.instance.lib.IsActiveSource(x)
                cecVersion      = self.instance.lib.GetDeviceCecVersion(x)
                power           = self.instance.lib.GetDevicePowerStatus(x)
                osdName         = self.instance.lib.GetDeviceOSDName(x)
                strLog += "device #" + str(x) +": " + self.instance.lib.LogicalAddressToString(x)  + "\n"
                strLog += "address:       " + str(physicalAddress) + "\n"
                strLog += "active source: " + str(active) + "\n"
                strLog += "vendor:        " + self.instance.lib.VendorIdToString(vendorId) + "\n"
                strLog += "CEC version:   " + self.instance.lib.CecVersionToString(cecVersion) + "\n"
                strLog += "OSD name:      " + osdName + "\n"
                strLog += "power status:  " + self.instance.lib.PowerStatusToString(power) + "\n\n\n"
            x += 1
        print(strLog)

    # logging callback
    def on_log_callback(self, level, time, message):
        if level > self.log_level:
            return

        if level == cec.CEC_LOG_ERROR:
            levelstr = "ERROR:   "
        elif level == cec.CEC_LOG_WARNING:
            levelstr = "WARNING: "
        elif level == cec.CEC_LOG_NOTICE:
            levelstr = "NOTICE:  "
        elif level == cec.CEC_LOG_TRAFFIC:
            levelstr = "TRAFFIC: "
        elif level == cec.CEC_LOG_DEBUG:
            levelstr = "DEBUG:   "

        print(levelstr + "[" + str(time) + "]     " + message)

    def on_command_callback(self, cmd):
        if self.show_all_commands:
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

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
            cls.instance.SetConfiguration()
            cls.instance.InitLibCec()
        return cls.instance


CECClient()  # Instantiate Singleton
