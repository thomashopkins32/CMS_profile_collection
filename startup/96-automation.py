#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi: ts=4 sw=4




################################################################################
#  Classes for controlling the robotics and automation on the beamline.
################################################################################
# Known Bugs:
#  N/A
################################################################################
# TODO:
#  Search for "TODO" below.
################################################################################





class SampleExchangeRobot(Stage):
    
    def __init__(self, name='SampleExchangeRobot', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
        self._sample = None
        
        # The region can be:
        #  'safe' : arm won't collid with anything, it is near the (+,+,+) limit of its travel.
        #  'parking' : arm is close to the parking lot (movement may hit a sample)
        #  'stage' : arm is close to the sample stage/stack (movement may collide with stack, on-axis camera, or downstream window)
        #  'undefined' : position is unknown (do not assume it is safe to move!)
        self._region = 'undefined'
        
        
        
        # self.yabs(-82.0) # Good height for 'slotted approach'
        # self.yabs(-77.0) # Good height for 'grip' (grip-screws sitting at bottom of wells)
        # self.yabs(-67.0) # Good height for 'hover' (sample held above stage)
        self._delta_y_hover = 10.0
        self._delta_y_slot = 5.0
        
        self._position_safe = [0, -82.0, -94.8, 0.0, -90] # x, y, z, r, phi
        self._position_safe_rotate = [0, -82.0, -15.0, 0.0, -90] # x, y, z, r, phi
        self._position_sample_gripped = [-101, -77, -94.8, 18.0, -90] # x, y, z, r, phi
        
        
        self._position_stg_exchange = [] # smx, smy
        self._position_stg_measure = [] # smx, smy
        

        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = [ {'name': 'x',
                            'motor': armx,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves left/outboard',
                            },
                            {'name': 'r',
                            'motor': armr,
                            #'motor': strans,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves radial arm outwards',
                            },        
                            {'name': 'y',
                            'motor': army,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves arm up',
                            },
                            {'name': 'z',
                            'motor': armz,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves arm downstream',
                            },
                            {'name': 'phi',
                            'motor': armphi,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves arm downstream',
                            },
                            
                        ]      
                            
                            
    def guessRegion(self):
        '''Determine where the arm is located.'''
        
        # TODO
        pass
                            
                            
    def home(self, verbosity=3, delays=0.5):
        '''Home the axes, so that one can now trust the position values.'''
        
        if not self.checkSafe():
            return
        

        # army to positive limit (moves arm to top of vertical range); set this to be zero
        caput('XF:11BMB-ES{SM:1-Ax:Y}Start:Home-Cmd', 1)
        sleep(delays)
        while army.moving:
            sleep(delays)
        
        # armx to positive limit; set this to be zero
        caput('XF:11BMB-ES{SM:1-Ax:X}Start:Home-Cmd', 1)
        sleep(delays)
        while armx.moving:
            sleep(delays)
        
        # Rotate arm so that it doesn't collide when doing a +z scan
        self.phiabs(-90) # gripper pointing -x (towards sample stack)
        sleep(delays)
        while armphi.moving:
            sleep(delays)
        
        
        # armz to positive limit (moves arm to downstream of range); set this to be zero
        caput('XF:11BMB-ES{SM:1-Ax:Z}Start:Home-Cmd', 1)
        sleep(delays)
        while armz.moving:
            sleep(delays)
        
        
        #caput('XF:11BMB-ES{SM:1-Ax:ArmR}Mtr.HOMF',1) # armr home forward
        #caput('XF:11BMB-ES{SM:1-Ax:ArmR}Mtr.HOMR',1) # armr home reverse
        sleep(delays)
        while self._axes['r'].motor.moving:
            sleep(delays)
        
        
        
        self.zabs(-15, verbosity=verbosity) # This is far enough that the arm can rotate without colliding with the downstream wall
        self.phiabs(-180, verbosity=verbosity) # gripper pointing -z (towards parking lot; upstream)
        
        self._region = 'safe'
        
        
    def checkSafe(self):

        if self._region is not 'safe':
            print("ERROR: Robot arm must start in the 'safe' region of the chamber (current region is '{}'). Move the robot to the safe region (and/or set _region to 'safe').".format(self._region))
            return False
        
        return True
        
        
    def sequenceArmSafe(self, verbosity=3):
        
        if not self.checkSafe():
            return
        
        self.zabs(-25, verbosity=verbosity) # self._position_safe_rotate[2]
        self.phiabs(-180)
        self.yabs(-1)
        self.xabs(-1)
        
        
        
    def sequencePutSampleOntoStage(self, verbosity=3):
        
        if self._sample is None:
            print("ERROR: No sample currently being gripped by robot arm.")
            return
        
        if not self.checkSafe():
            return
        
        
        x, y, z, r, phi = self._position_sample_gripped
        
        # TODO: Move sample stage
        
        # Pre-align the arm in (y,z)
        if abs(self.phipos(verbosity=0)-phi)>0.5:
            self.zabs(-25, verbosity=verbosity) # self._position_safe_rotate[2]
            self.phiabs(phi, verbosity=verbosity)
        self.zabs(z, verbosity=verbosity)
        self.yabs(y+self._delta_y_hover, verbosity=verbosity)
        
        self._region = 'stage'
        # Push the sample out so that it is hovering above the stage
        mov([armx, self._axes['r'].motor], [x, r])
        
        # Move sample down (-y)
        self.yr(-self._delta_y_hover, verbosity=verbosity) # Now in contact with stage
        
        # De-grip
        self.yr(-self._delta_y_slot, verbosity=verbosity)
        self._sample = None
        
        # Move away from stage
        x, y, z, r, phi = self._position_safe
        mov([armx, self._axes['r'].motor], [x, r])
        self._region = 'safe'
        

    def sequenceGetSampleFromStage(self, verbosity=3):
        
        if self._sample is not None:
            print("ERROR: There is already a sample being gripped by robot arm (sample {}.".format(self._sample.name))
            return
        
        if not self.checkSafe():
            return
        
        
        # TODO: Move sample stage
        
        x, y, z, r, phi = self._position_sample_gripped
        
        # Pre-align the arm in (y,z)
        if abs(self.phipos(verbosity=0)-phi)>0.5:
            self.zabs(-25, verbosity=verbosity) # self._position_safe_rotate[2]
            self.phiabs(phi, verbosity=verbosity)
        self.zabs(z, verbosity=verbosity)
        self.yabs(y-self._delta_y_slot, verbosity=verbosity)
        
        self._region = 'stage'
        # Move arm so that it is slotted over the sample
        self.xabs(x, verbosity=verbosity)
        self.rabs(r, verbosity=verbosity)
        
        # Grip sample
        self.yr(+self._delta_y_slot, verbosity=verbosity)
        # Pick sample up (+y)
        self.yr(+self._delta_y_hover, verbosity=verbosity)
        
        # Move away from stage
        x, y, z, r, phi = self._position_safe
        mov([armx, self._axes['r'].motor], [x, r])
        self._region = 'safe'
        
        
        
    def sequencePrepPark(self, verbosity=3):
        '''Rotate the arm so that it is 'pointed' at the parking lot.'''
        
        if not self.checkSafe():
            return
        
        phi_park = -180
        
        if abs(self.phipos(verbosity=0)-(phi_park))>0.5:
            x, y, z, r, phi = self._position_safe_rotate
            self.zabs(z, verbosity=verbosity)
            self.xabs(x, verbosity=verbosity)
            self.rabs(r, verbosity=verbosity)
            
            self.phiabs(phi_park, verbosity=verbosity)
            
            
    def sequenceParkSample(self, parking_spot, verbosity=3):
        
        if self._sample is None:
            print("ERROR: No sample currently being gripped by robot arm.")
            return
        
        if not self.checkSafe():
            return
        
        
        # TODO: Implement moving to correct parking spot in (x,y)
        
        
        self._region = 'parking'
        self.zabs(-80, verbosity=verbosity) # TODO: Fix
        
        # Move sample down (-y)
        self.yr(-self._delta_y_hover, verbosity=verbosity) # Now in contact with parking spot
        
        # De-grip
        self.yr(-self._delta_y_slot, verbosity=verbosity)
        self._sample = None
        
        # Move away
        self.zabs(-25, verbosity=verbosity)
        self._region = 'safe'
        
        
    def sequenceUnparkSample(self, parking_spot, verbosity=3):
        
        if self._sample is not None:
            print("ERROR: There is already a sample being gripped by robot arm (sample {}.".format(self._sample.name))
            return
        
        if not self.checkSafe():
            return
        
        
        # TODO: Check parking spot is free
        
        
        # TODO: Implement moving to correct parking spot in (x,y)
        
        
        self._region = 'parking'
        self.zabs(-80, verbosity=verbosity) # TODO: Fix
        
        # Grip sample
        self.yr(+self._delta_y_slot, verbosity=verbosity)
        # Pick sample up (+y)
        self.yr(+self._delta_y_hover, verbosity=verbosity)
        # self._sample = TODO
        
        
        # Move away
        self.zabs(-25, verbosity=verbosity)
        self._region = 'safe'
        
            

        
        
        
        
        

class Queue(object):
    """
    Holds the current state of the sample queue, allowing samples settings
    to be 'extracted'; or even allowing a particular sample to be physically
    loaded.
    """
    
    pass




robot = SampleExchangeRobot()
