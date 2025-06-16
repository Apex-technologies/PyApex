from PyApex.Common import Send, Receive


class OpticalSwitch():

    def __init__(self, Equipment, SlotNumber=1, Simulation=False):
        '''
        Constructor of a OSW (Optical Switch) equipment.
        Equipment is the AP1000 class of the equipment
        SlotNumber is the number of the slot used by the OSW
        Simulation is a boolean to indicate to the program if it has to run in simulation mode or not
        '''
        self.__Connexion = Equipment.Connexion
        self.__Simulation = Simulation
        self.__SlotNumber = SlotNumber
        self.__Type = self.GetType()
        self.__Path = 0


    def __str__(self):
        '''
        Return the equipment name and the slot number when the 'print()' function is used
        '''
        return "Optical Switch in slot " + str(self.__SlotNumber)
    
    
    def GetSlotNumber(self):
        '''
        Returns the slot number of the module
        '''
        
        return self.__SlotNumber
    
    
    def GetType(self, type="d"):
        '''
        Return the type of the OSW
        if type = 'd' (default), return a digit :
            - 0 for 1X2 or 2X2
            - 1 for 1X4
            - 2 for 1X8
        if type = 's', return a string :
            - "NX2" for 1X2 or 2X2
            - "1X4" for 1X4
            - "1X8" for 1X8
        '''
        from PyApex.Constantes import AP1000_ERROR_SLOT_TYPE_NOT_DEFINED
        from PyApex.Constantes import SimuOSW_SlotID
        from PyApex.Errors import ApexError
        import re
        
        if self.__Simulation:
            ID = SimuOSW_SlotID
        else:
            Command = "SLT[" + str(self.__SlotNumber).zfill(2) + "]:IDN?\n"
            Send(self.__Connexion, Command)
            ID = Receive(self.__Connexion)
        
        if re.findall("x2", ID.split("/")[2].split("-")[3].lower()) != []:
            if type.lower() == "s":
                return "NX2"
            else:
                return 0
        elif re.findall("4", ID.split("/")[2].split("-")[3].lower()) != []:
            if type.lower() == "s":
                return "1X4"
            else:
                return 1
        elif re.findall("8", ID.split("/")[2].split("-")[3].lower()) != []:
            if type.lower() == "s":
                return "1X8"
            else:
                return 2
        else:
            self.__Connexion.close()
            raise ApexError(AP1000_ERROR_SLOT_TYPE_NOT_DEFINED, self.__SlotNumber)


    def SetPath(self, Path):
        '''
        Set path of the OSW equipment
        For 1X2 and 2X2 OSW, Path can be:
            - A string "crossed" or "straight"
            - An integer 0 or 1 (1 = crossed)
            - A boolean (True = crossed)
        For 1X4 OSW, Path can be:
            - A string "A", "B", "C" or "D"
            - An integer 1, 2, 3 or 4
        For 1X8 OSW, Path can be:
            - A string "A", "B", "C", "D", "E", "F", "G" or "H"
            - An integer 1, 2, 3, 4, 5, 6, 7 or 8
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if self.__Type == 0:
            if type(Path) == str:
                if Path.lower() == "crossed":
                    self.__Path = 1
                else:
                    self.__Path = 0
            elif type(Path) == int:
                if Path == 1:
                    self.__Path = 1
                else:
                    self.__Path = 0
            elif type(Path) == bool:
                if Path == True:
                    self.__Path = 1
                else:
                    self.__Path = 0
            else:
                self.__Path = 0
                
            if not self.__Simulation:
                Command = "SWI[" + str(self.__SlotNumber).zfill(2) + "]:CONF" + str(self.__Path) + "\n"
                Send(self.__Connexion, Command)
                
        elif self.__Type == 1:
            if type(Path) == str:
                if Path.lower() == "B":
                    self.__Path = 2
                elif Path.lower() == "C":
                    self.__Path = 3
                elif Path.lower() == "D":
                    self.__Path = 4
                else:
                    self.__Path = 1
            elif type(Path) == int:
                if Path < 1:
                    self.__Path = 1
                elif Path > 4:
                    self.__Path = 4
                else:
                    self.__Path = Path
            else:
                self.__Path = 1
                
            if not self.__Simulation:
                Command = "SWx4x8[" + str(self.__SlotNumber).zfill(2) + "]:OUTx4" + str(self.__Path) + "\n"
                Send(self.__Connexion, Command)
        
        elif self.__Type == 2:
            if type(Path) == str:
                if Path.lower() == "B":
                    self.__Path = 2
                elif Path.lower() == "C":
                    self.__Path = 3
                elif Path.lower() == "D":
                    self.__Path = 4
                elif Path.lower() == "E":
                    self.__Path = 5
                elif Path.lower() == "F":
                    self.__Path = 6
                elif Path.lower() == "G":
                    self.__Path = 7
                elif Path.lower() == "H":
                    self.__Path = 8
                else:
                    self.__Path = 1
            elif type(Path) == int:
                if Path < 1:
                    self.__Path = 1
                elif Path > 8:
                    self.__Path = 8
                else:
                    self.__Path = Path
            else:
                self.__Path = 1
                
            if not self.__Simulation:
                Command = "SWx4x8[" + str(self.__SlotNumber).zfill(2) + "]:OUTx8" + str(self.__Path) + "\n"
                Send(self.__Connexion, Command)


    def GetPath(self):
        '''
        Get path of the OSW equipment.
        Returns an integer
        For 1X2 and 2X2 OSW, returns:
            - 0 for straight
            - 1 for crossed
        For 1X4 OSW, returns:
            - 1, 2, 3 or 4
        For 1X8 OSW, Path can be:
            - 1, 2, 3, 4, 5, 6, 7 or 8
        '''
        from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE, APXXXX_ERROR_ARGUMENT_VALUE
        from PyApex.Errors import ApexError
        
        if self.__Simulation:
            Path = str(self.__Path) + "\n"
        else:
            if self.__Type == 0:
                Command = "SWI[" + str(self.__SlotNumber).zfill(2) + "]:CONF?\n"
                Send(self.__Connexion, Command)
                Path = Receive(self.__Connexion)
            elif self.__Type == 1:
                Command = "SWx4x8[" + str(self.__SlotNumber).zfill(2) + "]:GETx4?\n"
                Send(self.__Connexion, Command)
                Path = Receive(self.__Connexion)[3:]
            elif self.__Type == 2:
                Command = "SWx4x8[" + str(self.__SlotNumber).zfill(2) + "]:GETx8?\n"
                Send(self.__Connexion, Command)
                Path = Receive(self.__Connexion)[3:]
        
        self.__Path = int(Path[:-1])
        
        return self.__Path
