"""



TO PREVENT ANY INCIDENTS:
    LAST EDITED: 2018.07.18.21:15 BY TAMAS
IF YOU EDIT MODIFY THIS PLEASE




"""



from qcodes import VisaInstrument
from qcodes.utils.validators import Numbers

class HM8133(VisaInstrument):
    """
    This is the qcodes driver for the HAMEG HM 8133
    RF-Synthesizer
    """

    # Dictionary for setting up modulation
    _S_TO_MOD={
            "OFF" : "NMO",
            "AMP_400" : "AM1",
            "AMP_1000" : "AM2",
            "AMP_EXT" : "AMX",
            "FRQ_400" : "FM1",
            "FRQ_1000" : "FM2",
            "FRQ_EXT" : "FMX"
            }
    # Dictionary and functions for output, modulation and reference freq getters
    
    # CHECK INSTRUMENT MANUAL PAGE 16 (answer for STA command)
    #string is like "xxx xxx xxx \r" (checked in lab)
    
    _ANSWER_PARSER={
            "OP0" : "Output : OFF",
            "OP1" : "Output : ON",
            "NMO" : "Modulation : OFF",
            "AM1" : "Modulation : AMPLITUDE with INTERNAL 400 Hz",
            "AM2" : "Modulation : AMPLITUDE with INTERNAL 1000 Hz",        
            "AMX" : "Modulation : AMPLITUDE with EXTERNAL",
            "FM1" : "Modulation : FREQUENCY with INTERNAL 400 Hz",
            "FM2" : "Modulation : FREQUENCY with INTERNAL 1000 Hz",
            "FMX" : "Modulation : FREQUENCY with EXTERNAL",
            "RFI" : "Reference frequency : INTERNAL",
            "RFX" : "Reference frequency : EXTERNAL",
        }

    
    
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator=';', **kwargs)
        """
        Parameter setter and getter commands
        """

       # Frequency
        self.add_parameter("frequency",
                           label="Frequency",
                           get_cmd="FRQ?",
                           set_cmd="FRQ;{:.1E}",
                           unit="Hz",
                           vals=Numbers(min_value=1, max_value=1e9))

       # Level in dBm
        self.add_parameter("lvl_dbm",
                           label="Level in dBm",
                           get_cmd="DBM?",
                           set_cmd="DBM;{:+.1E}", #DOES NOT WORK.MIGHT BE COZ OF SIGN
                           unit="dBm",
                           vals=Numbers(min_value=-135, max_value=7))
     
        # Level in Volts
        self.add_parameter("lvl_volts",
                           label="Level in Volts",
                           get_cmd="AMP?",
                           set_cmd="AMP;{:.10E}",
                           unit='V',
                           vals=Numbers(min_value=39.8e-9, max_value=501e-3))

        # Output
        self.add_parameter("output",
                           label="Output ON/OFF",
                           get_cmd="STA",
                           get_parser=self._get_output,
                           set_cmd="OP{}",
                           val_mapping={"OFF": 0,
                                        "ON": 1})
        # Modulation
        self.add_parameter("modulation",
                           label="Output signal modulation. For key strings see self._S_TO_MOD dict.",
                           get_cmd="STA",
                           get_parser=self._get_mod,
                           set_cmd="{}",
                           val_mapping=self._S_TO_MOD)
        
        # Reference frequency internal/external
        self.add_parameter("reference_frequency",
                           label="Sets reference frequency source (internal/external)",
                           get_cmd="STA",
                           get_parser=self._get_ref,
                           set_cmd="RF{}",
                           val_mapping={"INT":"I",
                                        "EXT":"X"})



        """
        Read only state-getter parameters
        """
        # Status
        self.add_parameter("status",
                           label="Status of output, reference frequency and modulation.",
                           get_cmd="STA")
        
        # Version read only
        self.add_parameter("version",
                           label="Version number",
                           get_cmd="VER")
        
        # ID read only
        self.add_parameter("who",
                           label="Type of instrument",
                           get_cmd="ID?")

        # Frequency deviaton
        self.add_parameter("freq_dev",
                           label="Frequency deviaton",
                           get_cmd="FMD?")
        
        # Amplitude deviation
        self.add_parameter("amp_dev",
                           label="Amplitude deviation",
                           get_cmd="AMT?")
        
        # Masterclear function
        self.add_function("mclr", call_cmd="CLR",
                          docstring=("Sets the instrument in the following"
                                     "state: freq = 1 GHz, amp = +7dBm,"
                                     "modulation = off, output = off"
                                     "ref freq = internal."))      
        
#NOT WORKING        
    def _get_output(self,s):
        return self._ANSWER_PARSER[s[0:3]]
    
    def _get_mod(self,s):
        return s[8:11]
    
    def _get_ref(self,s):
        return self._ANSWER_PARSER[s[4:7]]