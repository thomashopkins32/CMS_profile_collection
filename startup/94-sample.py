#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi: ts=4 sw=4




################################################################################
#  Code for defining a 'Sample' object, which keeps track of its state, and 
# simplifies the task of aligning, measuring, etc.
################################################################################
# Known Bugs:
#  N/A
################################################################################
# TODO:
#  - Search for "TODO" below.
#  - Ability to have a collection of simultaneous motions? (E.g. build up a set
#  of deferred motions?)
################################################################################


import time
import re



class CoordinateSystem(object):
    """
    A generic class defining a coordinate system. Several coordinate systems
    can be layered on top of one another (with a reference to the underlying
    coordinate system given by the 'base_stage' pointer). When motion of a given
    CoordinateSystem is requested, the motion is passed (with coordinate
    conversion) to the underlying stage.
    """
    
    hint_replacements = { 'positive': 'negative',
                         'up': 'down',
                         'left': 'right',
                         'towards': 'away from',
                         'downstream': 'upstream',
                         'inboard': 'outboard',
                         'clockwise': 'counterclockwise',
                         'CW': 'CCW',
                         }


    # Core methods
    ########################################
    
    def __init__(self, name='<unnamed>', base=None, **kwargs):
        '''Create a new CoordinateSystem (e.g. a stage or a sample).
        
        Parameters
        ----------
        name : str
            Name for this stage/sample.
        base : Stage
            The stage on which this stage/sample sits.
        '''        
        
        self.name = name
        self.base_stage = base
        
        
        self.enabled = True
        
        self.md = {}
        self._marks = {}

        self._set_axes_definitions()
        self._init_axes(self._axes_definitions)
        
        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = []
        
        
    def _init_axes(self, axes):
        '''Internal method that generates method names to control the various axes.'''
        
        # Note: Instead of defining CoordinateSystem() having methods '.x', '.xr', 
        # '.y', '.yr', etc., we programmatically generate these methods when the 
        # class (and subclasses) are instantiated.
        # Thus, the Axis() class has generic versions of these methods, which are
        # appropriated renamed (bound, actually) when a class is instantiated.
        
        self._axes = {}
        
        for axis in axes:
            
            axis_object = Axis(axis['name'], axis['motor'], axis['enabled'], axis['scaling'], axis['units'], axis['hint'], self.base_stage, stage=self)
            self._axes[axis['name']] = axis_object
               
            # Bind the methods of axis_object to appropriately-named methods of 
            # the CoordinateSystem() class.
            setattr(self, axis['name'], axis_object.get_position )
            setattr(self, axis['name']+'abs', axis_object.move_absolute )
            setattr(self, axis['name']+'r', axis_object.move_relative )
            setattr(self, axis['name']+'pos', axis_object.get_position )
            setattr(self, axis['name']+'posMotor', axis_object.get_motor_position )
            
            
            setattr(self, axis['name']+'units', axis_object.get_units )
            setattr(self, axis['name']+'hint', axis_object.get_hint )
            setattr(self, axis['name']+'info', axis_object.get_info )
            
            setattr(self, axis['name']+'set', axis_object.set_current_position )
            setattr(self, axis['name']+'o', axis_object.goto_origin )
            setattr(self, axis['name']+'setOrigin', axis_object.set_origin )
            setattr(self, axis['name']+'mark', axis_object.mark )
            
            setattr(self, axis['name']+'scan', axis_object.scan )
            setattr(self, axis['name']+'c', axis_object.center )
            
            
    def comment(self, text, logbooks=None, tags=None, append_md=True, **md):
        '''Add a comment related to this CoordinateSystem.'''
        
        text += '\n\n[comment for CoordinateSystem: {} ({})].'.format(self.name, self.__class__.__name__)
        
        if append_md:
        
            md_current = { k : v for k, v in RE.md.items() } # Global md
            md_current.update(get_beamline().get_md()) # Beamline md

            # Self md
            #md_current.update(self.get_md())
            
            # Specified md
            md_current.update(md)
            
            text += '\n\n\nMetadata\n----------------------------------------'
            for key, value in sorted(md_current.items()):
                text += '\n{}: {}'.format(key, value)
            
        
        logbook.log(text, logbooks=logbooks, tags=tags)
    
    
    def set_base_stage(self, base):
        
        self.base_stage = base
        self._init_axes(self._axes_definitions)
        

    # Convenience/helper methods
    ########################################
    
    
    def multiple_string_replacements(self, text, replacements, word_boundaries=False):
        '''Peform multiple string replacements simultaneously. Matching is case-insensitive.
        
        Parameters
        ----------
        text : str
            Text to return modified
        replacements : dictionary
            Replacement pairs
        word_boundaries : bool, optional
            Decides whether replacements only occur for words.
        '''
        
        # Code inspired from:
        # http://stackoverflow.com/questions/6116978/python-replace-multiple-strings
        # Note inclusion of r'\b' sequences forces the regex-match to occur at word-boundaries.

        if word_boundaries:
            replacements = dict((r'\b'+re.escape(k.lower())+r'\b', v) for k, v in replacements.items())
            pattern = re.compile("|".join(replacements.keys()), re.IGNORECASE)
            text = pattern.sub(lambda m: replacements[r'\b'+re.escape(m.group(0).lower())+r'\b'], text)
            
        else:
            replacements = dict((re.escape(k.lower()), v) for k, v in replacements.items())
            pattern = re.compile("|".join(replacements.keys()), re.IGNORECASE)
            text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
        
        return text
    

    def _hint_replacements(self, text):
        '''Convert a motor-hint into its logical inverse.'''
        
        # Generates all the inverse replacements
        replacements = dict((v, k) for k, v in self.hint_replacements.items())
        replacements.update(self.hint_replacements)
        
        return self.multiple_string_replacements(text, replacements, word_boundaries=True)

        
    # Motion methods
    ########################################
    
    
    def enable(self):
        self.enabled = True
    
    
    def disable(self):
        self.enabled = False
    
    
    def is_enabled(self):
        return self.enabled
    
                          
    def pos(self, verbosity=3):
        '''Return (and print) the positions of all axes associated with this
        stage/sample.'''
        
        out = {}
        for axis_name, axis_object in sorted(self._axes.items()):
            out[axis_name] = axis_object.get_position(verbosity=verbosity)
            #if verbosity>=2: print('') # \n
            
        return out
                  
    def hints(self, verbosity=3):
        '''Return (and print) the hints of all axes associated with this
        stage/sample.'''
        
        out = {}
        for axis_name, axis_object in sorted(self._axes.items()):
            if verbosity>=2: print('{:s}'.format(axis_name))
            out[axis_name] = axis_object.get_hint(verbosity=verbosity)
            if verbosity>=2: print('') # \n
            
        return out
    
    
    def origin(self, verbosity=3):
        '''Returns the origin for axes.'''
        
        out = {}
        for axis_name, axis_object in sorted(self._axes.items()):
            origin = axis_object.get_origin()
            if verbosity>=2: print('{:s} origin = {:.3f} {:s}'.format(axis_name, origin, axis_object.get_units()))
            out[axis_name] = origin
            
        return out
            
        
    def gotoOrigin(self, axes=None):
        '''Go to the origin (zero-point) for this stage. All axes are zeroed,
        unless one specifies the axes to move.'''
        
        # TODO: Guard against possibly buggy behavior if 'axes' is a string instead of a list.
        # (Python will happily iterate over the characters in a string.)
        
        if axes is None:
            axes_to_move = self._axes.values()
            
        else:
            axes_to_move = [self._axes[axis_name] for axis_name in axes]
                
        for axis in axes_to_move:
            axis.goto_origin()
        
        
    def setOrigin(self, axes, positions=None):
        '''Define the current position as the zero-point (origin) for this stage/
        sample. The axes to be considered in this redefinition must be supplied
        as a list.
        
        If the optional positions parameter is passed, then those positions are
        used to define the origins for the axes.'''

        if positions is None:
        
            for axis in axes:
                getattr(self, axis+'setOrigin')()
                
        else:
            for axis, pos in zip(axes, positions):
                getattr(self, axis+'setOrigin')(pos)
    
    
    def gotoAlignedPosition(self):
        '''Goes to the currently-defined 'aligned' position for this stage. If
        no specific aligned position is defined, then the zero-point for the stage
        is used instead.'''
        
        # TODO: Optional offsets? (Like goto mark?)
        
        if 'aligned_position' in self.md and self.md['aligned_position'] is not None:
            for axis_name, position in self.md['aligned_position'].items():
                self._axes[axis_name].move_absolute(position)
        
        else:
            self.gotoOrigin()
            
            

    # Motion logging
    ########################################
            
    def setAlignedPosition(self, axes):
        '''Saves the current position as the 'aligned' position for this stage/
        sample. This allows one to return to this position later. One must
        specify the axes to be considered.

        WARNING: Currently this position data is not saved persistently. E.g. it will 
        be lost if you close and reopen the console.
        '''
        
        positions = {}
        for axis_name in axes:
            positions[axis_name] = self._axes[axis_name].get_position(verbosity=0)
        
        self.attributes['aligned_position'] = positions

            
    def mark(self, label, *axes, **axes_positions):
        '''Set a mark for the stage/sample/etc.
        
        'Marks' are locations that have been labelled, which is useful for 
        later going to a labelled position (using goto), or just to keep track
        of sample information (metadata).
        
        By default, the mark is set at the current position. If no 'axes' are 
        specified, all motors are logged. Alternately, axes (as strings) can 
        be specified. If axes_positions are given as keyword arguments, then 
        positions other than the current position can be specified.        
        '''
        
        positions = {}
        
        if len(axes)==0 and len(axes_positions)==0:
            
            for axis_name in self._axes:
                positions[axis_name] = self._axes[axis_name].get_position(verbosity=0)
                
        else:
            for axis_name in axes:
                positions[axis_name] = self._axes[axis_name].get_position(verbosity=0)
                
            for axis_name, position in axes_positions.items():
                positions[axis_name] = position
        
        self._marks[label] = positions
        
        
    def marks(self, verbosity=3):
        '''Get a list of the current marks on the stage/sample/etc. 'Marks' 
        are locations that have been labelled, which is useful for later
        going to a labelled position (using goto), or just to keep track
        of sample information (metadata).'''
        
        if verbosity>=3:
            print('Marks for {:s} (class {:s}):'.format(self.name, self.__class__.__name__))
        
        if verbosity>=2:
            for label, positions in self._marks.items():
                print(label)
                for axis_name, position in sorted(positions.items()):
                    print('  {:s} = {:.4f} {:s}'.format(axis_name, position, self._axes[axis_name].get_units()))
            
        return self._marks
    
    
    def goto(self, label, verbosity=3, **additional):
        '''Move the stage/sample to the location given by the label. For this
        to work, the specified label must have been 'marked' at some point.
        
        Additional keyword arguments can be provided. For instance, to move 
        3 mm from the left edge:
          sam.goto('left edge', xr=+3.0)
        '''
        
        if label not in self._marks:
            if verbosity>=1:
                print("Label '{:s}' not recognized. Use '.marks()' for the list of marked positions.".format(label))
            return
            
        for axis_name, position in sorted(self._marks[label].items()):
            
            if axis_name+'abs' in additional:
                # Override the marked value for this position
                position = additional[axis_name+'abs']
                del(additional[axis_name+'abs'])
            
            
            #relative = 0.0 if axis_name+'r' not in additional else additional[axis_name+'r']
            if axis_name+'r' in additional:
                relative = additional[axis_name+'r']
                del(additional[axis_name+'r'])
            else:
                relative = 0.0
            
            self._axes[axis_name].move_absolute(position+relative, verbosity=verbosity)


        # Handle any optional motions not already covered
        for command, amount in additional.items():
            if command[-1]=='r':
                getattr(self, command)(amount, verbosity=verbosity)
            elif command[-3:]=='abs':
                getattr(self, command)(amount, verbosity=verbosity)
            else:
                print("Keyword argument '{}' not understood (should be 'r' or 'abs').".format(command))



    # End class CoordinateSystem(object)
    ########################################




class Axis(object):
    '''Generic motor axis.
    
    Meant to be used within a CoordinateSystem() or Stage() object.
    '''
    
    def __init__(self, name, motor, enabled, scaling, units, hint, base, stage=None, origin=0.0):
        
        self.name = name
        self.motor = motor
        self.enabled = enabled
        self.scaling = scaling
        self.units = units
        self.hint = hint
        
        self.base_stage = base
        self.stage = stage
        
        self.origin = 0.0
        
        
        
        self._move_settle_max_time = 10.0
        self._move_settle_period = 0.05
        self._move_settle_tolerance = 0.01
        
        
    def cur_to_base(self, position):
        
        base_position = self.get_origin() + self.scaling*position
        
        return base_position
    
    
    def base_to_cur(self, base_position):
        
        position = (base_position - self.get_origin())/self.scaling
        
        return position
            
            
    # Programmatically-defined methods
    ########################################
    # Note: Instead of defining CoordinateSystem() having methods '.x', '.xr', 
    # '.xp', etc., we programmatically generate these methods when the class 
    # (and subclasses) are instantiated.
    # Thus, the Axis() class has generic versions of these methods, which are
    # appropriated renamed (bound, actually) when a class is instantiated.
    def get_position(self, verbosity=3):
        '''Return the current position of this axis (in its coordinate system).
        By default, this also prints out the current position.'''
        
        
        if self.motor is not None:
            base_position = self.motor.position
            
        else:
            verbosity_c = verbosity if verbosity>=4 else 0
            base_position = getattr(self.base_stage, self.name+'pos')(verbosity=verbosity_c)
            
        position = self.base_to_cur(base_position)
        
        
        if verbosity>=2:
            if self.stage:
                stg = self.stage.name
            else:
                stg = '?'

            if verbosity>=5 and self.motor is not None:
                print( '{:s} = {:.3f} {:s}'.format(self.motor.name, base_position, self.get_units()) )
            
            print( '{:s}.{:s} = {:.3f} {:s} (origin = {:.3f})'.format(stg, self.name, position, self.get_units(), self.get_origin()) )
            
            
        return position
    
    
    def get_motor_position(self, verbosity=3):
        '''Returns the position of this axis, traced back to the underlying
        motor.'''
        
        if self.motor is not None:
            return self.motor.position
        
        else:
            return getattr(self.base_stage, self.name+'posMotor')(verbosity=verbosity)
            #return self.base_stage._axes[self.name].get_motor_position(verbosity=verbosity)
    
    
    def move_absolute(self, position=None, wait=True, verbosity=3):
        '''Move axis to the specified absolute position. The position is given
        in terms of this axis' current coordinate system. The "defer" argument
        can be used to defer motions until "move" is called.'''
        
        
        if position is None:
            # If called without any argument, just print the current position
            return self.get_position(verbosity=verbosity)
        
        # Account for coordinate transformation
        base_position = self.cur_to_base(position)
        
        if self.is_enabled():
            
            if self.motor:
                #mov( self.motor, base_position )
                self.motor.user_setpoint.value = base_position
                
            else:
                # Call self.base_stage.xabs(base_position)
                getattr(self.base_stage, self.name+'abs')(base_position, verbosity=0)


            if verbosity>=2:
                if self.stage:
                    stg = self.stage.name
                else:
                    stg = '?'
                
                # Show a realtime output of position
                start_time = time.time()
                current_position = self.get_position(verbosity=0)
                while abs(current_position-position)>self._move_settle_tolerance and (time.time()-start_time)<self._move_settle_max_time:
                    current_position = self.get_position(verbosity=0)
                    print( '{:s}.{:s} = {:5.3f} {:s}      \r'.format(stg, self.name, current_position, self.get_units()), end='')
                    time.sleep(self._move_settle_period)
                    
                    
            if verbosity>=1:
                print( '{:s}.{:s} = {:5.3f} {:s}        '.format(stg, self.name, current_position, self.get_units()))


                
        elif verbosity>=1:
            print( 'Axis %s disabled (stage %s).' % (self.name, self.stage.name) )
        
        
        
    def move_relative(self, move_amount=None, verbosity=3):
        '''Move axis relative to the current position.'''
        
        if move_amount is None:
            # If called without any argument, just print the current position
            return self.get_position(verbosity=verbosity)
        
        target_position = self.get_position(verbosity=0) + move_amount
        
        return self.move_absolute(target_position)
        
    
    def goto_origin(self):
        '''Move axis to the currently-defined origin (zero-point).'''
        
        self.move_absolute(0)
    
    
    def set_origin(self, origin=None):
        '''Sets the origin (zero-point) for this axis. If no origin is supplied,
        the current position is redefined as zero. Alternatively, you can supply
        a position (in the current coordinate system of the axis) that should
        henceforth be considered zero.'''
        
        if origin is None:
            # Use current position
            if self.motor is not None:
                self.origin = self.motor.position
                
            else:
                if self.base_stage is None:
                    print("Error: %s %s has 'base_stage' and 'motor' set to 'None'." % (self.__class__.__name__, self.name))
                else:
                    self.origin = getattr(self.base_stage, self.name+'pos')(verbosity=0)
                    
        else:
            # Use supplied value (in the current coordinate system)
            base_position = self.cur_to_base(origin)
            self.origin = base_position
            
            
    def set_current_position(self, new_position):
        '''Redefines the position value of the current position.'''
        current_position = self.get_position(verbosity=0)
        self.origin = self.get_origin() + (current_position - new_position)*self.scaling
    
    def scan(self):
        print('todo')
        
    def center(self):
        print('todo')
        
    def mark(self, label, position=None, verbosity=3):
        '''Set a mark for this axis. (By default, the current position is
        used.)'''
        
        if position is None:
            position = self.get_position(verbosity=0)
            
        axes_positions = { self.name : position }
        self.stage.mark(label, **axes_positions)
            
        
    


    # Book-keeping
    ########################################
    
    def enable(self):
        self.enabled = True
        
        
    def disable(self):
        self.enabled = False
        
        
    def is_enabled(self):
        
        return self.enabled and self.stage.is_enabled()
    
        
    def get_origin(self):
        
        return self.origin
        
        
    def get_units(self):
        
        if self.units is not None:
            return self.units
        
        else:
            return getattr(self.base_stage, self.name+'units')()


    def get_hint(self, verbosity=3):
        '''Return (and print) the "motion hint" associated with this axis. This
        hint gives information about the expected directionality of the motion.'''
        
        if self.hint is not None:
            s = '%s\n%s' % (self.hint, self.stage._hint_replacements(self.hint))
            if verbosity>=2:
                print(s)
            return s
        
        else:
            return getattr(self.base_stage, self.name+'hint')(verbosity=verbosity)
        
        
    def get_info(self, verbosity=3):
        '''Returns information about this axis.'''
        
        self.get_position(verbosity=verbosity)
        self.get_hint(verbosity=verbosity)

        
    def check_base(self):
        if self.base_stage is None:
            print("Error: %s %s has 'base_stage' set to 'None'." % (self.__class__.__name__, self.name))
        
        
        



class Sample_Generic(CoordinateSystem):
    """
    The Sample() classes are used to define a single, individual sample. Each
    sample is created with a particular name, which is recorded during measurements.
    Logging of comments also includes the sample name. Different Sample() classes
    can define different defaults for alignment, measurement, etc.
    """


    # Core methods
    ########################################
    def __init__(self, name, base=None, **md):
        '''Create a new Sample object.
        
        Parameters
        ----------
        name : str
            Name for this sample.
        base : Stage
            The stage/holder on which this sample sits.
        '''               
        
        if base is None:
            base = get_default_stage()
            #print("Note: No base/stage/holder specified for sample '{:s}'. Assuming '{:s}' (class {:s})".format(name, base.name, base.__class__.__name__))
            
        
        super().__init__(name=name, base=base)
        
        self.name = name
        
        
        self.md = {
            'exposure_time' : 1.0 ,
            'measurement_ID' : 1 ,
            }
        self.md.update(md)
        
        self.naming_scheme = ['name', 'extra', 'exposure_time']
        self.naming_delimeter = '_'
        

        # TODO
        #if base is not None:
            #base.addSample(self)
        
        
        self.reset_clock()
        
        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = [ {'name': 'x',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': None,
                            'hint': None,
                            },
                            {'name': 'y',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': None,
                            },
                            #{'name': 'z',
                            #'motor': None,
                            #'enabled': False,
                            #'scaling': +1.0,
                            #'units': 'mm',
                            #'hint': None,
                            #},
                            {'name': 'th',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'deg',
                            'hint': None,
                            },
                            #{'name': 'chi',
                            #'motor': None,
                            #'enabled': True,
                            #'scaling': +1.0,
                            #'units': 'deg',
                            #'hint': None,
                            #},
                            #{'name': 'phi',
                            #'motor': None,
                            #'enabled': True,
                            #'scaling': +1.0,
                            #'units': 'deg',
                            #'hint': None,
                            #},
                            ]          
        

        
    # Metadata methods
    ########################################
    # These involve setting or getting values associated with this sample.
        
    def clock(self):
        '''Return the current value of the "clock" variable. This provides a
        way to set a clock/timer for a sample. For instance, you can call
        "reset_clock" when you initiate some change to the sample. Thereafter,
        the "clock" method lets you check how long it has been since that
        event.'''
        
        clock_delta = time.time() - self.clock_zero
        return clock_delta
        

    def reset_clock(self):
        '''Resets the sample's internal clock/timer to zero.'''
        
        self.clock_zero = time.time()
        
        return self.clock()        
        
        
        
    def get_attribute(self, attribute):
        '''Return the value of the requested md.'''
        
        if attribute in self._axes:
            return self._axes[attribute].get_position(verbosity=0)
        
        if attribute=='name':
            return self.name

        if attribute=='clock':
            return self.clock()


        if attribute in self.md:
            return self.md[attribute]


        replacements = { 
            'id' : 'measurement_ID' ,
            'ID' : 'measurement_ID' ,
            'extra' : 'savename_extra' ,
            }
        
        if attribute in replacements:
            return self.md[replacements[attribute]]
        
        return None
            

    def set_attribute(self, attribute, value):
        '''Arbitrary attributes can be set and retrieved. You can use this to 
        store additional meta-data about the sample.
        
        WARNING: Currently this meta-data is not saved anywhere. You can opt
        to store the information in the sample filename (using "naming").
        '''
        
        self.md[attribute] = value
        
        
    def set_md(self, **md):
        
        self.md.update(md)
        
        
        
    def get_md(self, prefix='sample_', include_marks=True, **md):
        '''Returns a dictionary of the current metadata.
        The 'prefix' argument is prepended to all the md keys, which allows the
        metadata to be grouped with other metadata in a clear way. (Especially,
        to make it explicit that this metadata came from the sample.)'''
        
        # Update internal md
        #self.md['key'] = value

        
        md_return = self.md.copy()
        md_return['name'] = self.name
    
    
        if include_marks:
            for label, positions in self._marks.items():
                md_return['mark_'+label] = positions
    
    
        # Add md that varies over time
        md_return['clock'] = self.clock()
    
        for axis_name, axis in self._axes.items():
            md_return[axis_name] = axis.get_position(verbosity=0)
            md_return['motor_'+axis_name] = axis.get_motor_position(verbosity=0)
        
        
        md_return['savename'] = self.get_savename() # This should be over-ridden by 'measure'
    

        # Include the user-specified metadata
        md_return.update(md)

    
        # Add an optional prefix
        if prefix is not None:
            md_return = { '{:s}{:s}'.format(prefix, key) : value for key, value in md_return.items() }
    
        return md_return
    
    
    
    
        
        
    # Naming scheme methods
    ########################################
    # These allow the user to control how data is named.
        
    def naming(self, scheme=['name', 'extra', 'exposure_time'], delimeter='_'):
        '''This method allows one to define the naming convention that will be
        used when storing data for this sample. The "scheme" variable is an array
        that lists the various elements one wants to store in the filename.
        
        Each entry in "scheme" is a string referring to a particular element/
        value. For instance, motor names can be stored ("x", "y", etc.), the
        measurement time can be stored, etc.'''
        
        self.naming_scheme = scheme
        self.naming_delimeter = delimeter


    def get_naming_string(self, attribute):
        
        # Handle special cases of formatting the text
        
        if attribute in self._axes:
            return '{:s}{:.3f}'.format(attribute, self._axes[attribute].get_position(verbosity=0))
        
        if attribute=='clock':
            return '{:.1f}s'.format(self.get_attribute(attribute))

        if attribute=='exposure_time':
            return '{:.2f}s'.format(self.get_attribute(attribute))

        if attribute=='extra':
            # Note: Don't eliminate this check; it will not be properly handled
            # by the generic call below. When 'extra' is None, we should
            # return None, so that it gets skipped entirely.
            return self.get_attribute('savename_extra')

        if attribute=='spot_number':
            return 'spot{:d}'.format(self.get_attribute(attribute))
        
        
        # Generically: lookup the attribute and convert to string
        
        att = self.get_attribute(attribute)
        if att is None:
            # If the attribute is not found, simply return the text.
            # This allows the user to insert arbitrary text info into the
            # naming scheme.
            return attribute
        
        else:
            return str(att)
        

    def get_savename(self, savename_extra=None):
        '''Return the filename that will be used to store data for the upcoming
        measurement. The method "naming" lets one control what gets stored in
        the filename.'''
        
        if savename_extra is not None:
            self.set_attribute('savename_extra', savename_extra)
        
        attribute_strings = []
        for attribute in self.naming_scheme:
            s = self.get_naming_string(attribute)
            if s is not None:
                attribute_strings.append(s)

        self.set_attribute('savename_extra', None)
        
        savename = self.naming_delimeter.join(attribute_strings)
        
        # Avoid 'dangerous' characters
        savename = savename.replace(' ', '_')
        #savename = savename.replace('.', 'p')
        savename = savename.replace('/', '-slash-')
        
        return savename
    
        
        
    # Logging methods
    ########################################
    
    def comment(self, text, logbooks=None, tags=None, append_md=True, **md):
        '''Add a comment related to this sample.'''
        
        text += '\n\n[comment for sample: {} ({})].'.format(self.name, self.__class__.__name__)
        
        if append_md:
        
            md_current = { k : v for k, v in RE.md.items() } # Global md
            md_current.update(get_beamline().get_md()) # Beamline md

            # Sample md
            md_current.update(self.get_md())
            
            # Specified md
            md_current.update(md)
            
            text += '\n\n\nMetadata\n----------------------------------------'
            for key, value in sorted(md_current.items()):
                text += '\n{}: {}'.format(key, value)
            
        
        logbook.log(text, logbooks=logbooks, tags=tags)
        
        
    def log(self, text, logbooks=None, tags=None, append_md=True, **md):
        
        if append_md:
        
            text += '\n\n\nMetadata\n----------------------------------------'
            for key, value in sorted(md.items()):
                text += '\n{}: {}'.format(key, value)
        
        logbook.log(text, logbooks=logbooks, tags=tags)        
    

    
    # Measurement methods
    ########################################
    
    def get_measurement_md(self, prefix=None, **md):
        
        #md_current = {}
        md_current = { k : v for k, v in RE.md.items() } # Global md
        md_current['detector_sequence_ID'] = caget('XF:11BMB-ES{Det:SAXS}:cam1:FileNumber_RBV')
        
        md_current.update(get_beamline().get_md())
        
        md_current.update(md)

        # Add an optional prefix
        if prefix is not None:
            md_return = { '{:s}{:s}'.format(prefix, key) : value for key, value in md_return.items() }
        
        return md_current

    
    def expose(self, exposure_time=None, verbosity=3, poling_period=0.1, **md):
        '''Internal function that is called to actually trigger a measurement.'''
        
        # TODO: Improve this (switch to Bluesky methods)
        # TODO: Store metadata
        
        if 'measure_type' not in md:
            md['measure_type'] = 'expose'
        self.log('{} for {}.'.format(md['measure_type'], self.name), **md)

        if exposure_time is not None:
            # Prep detector
            caput('XF:11BMB-ES{Det:SAXS}:cam1:AcquireTime', exposure_time)
            caput('XF:11BMB-ES{Det:SAXS}:cam1:AcquirePeriod', exposure_time+0.1)
        
        
        get_beamline().beam.on()
        
        caput('XF:11BMB-ES{Det:SAXS}:cam1:Acquire', 1)
        
        if verbosity>=2:
            start_time = time.time()
            while caget('XF:11BMB-ES{Det:SAXS}:cam1:Acquire')==1 and (time.time()-start_time)<(exposure_time+20):
                percentage = 100*(time.time()-start_time)/exposure_time
                print( 'Exposing {:6.2f} s  ({:3.0f}%)      \r'.format((time.time()-start_time), percentage), end='')
                time.sleep(poling_period)
        else:
            time.sleep(exposure_time)
            
        if verbosity>=3 and caget('XF:11BMB-ES{Det:SAXS}:cam1:Acquire')==1:
            print('Warning: Detector still not done acquiring.')
        
        get_beamline().beam.off()
        
        
    def snap(self, exposure_time=None, extra=None, measure_type='snap', verbosity=3, **md):
        '''Take a quick exposure (without saving data).'''
        
        # TODO: Disable data saving when using 'snap'.
        self.measure(exposure_time=exposure_time, extra=extra, measure_type=measure_type, verbosity=verbosity, **md)
            
        
    def measure(self, exposure_time=None, extra=None, measure_type='measure', verbosity=3, **md):
        '''Measure data by triggering the area detectors.
        
        Parameters
        ----------
        exposure_time : float
            How long to collect data
        extra : string, optional
            Extra information about this particular measurement (which is typically
            included in the savename/filename).
        '''           
        
        if exposure_time is not None:
            self.set_attribute('exposure_time', exposure_time)
        else:
            exposure_time = self.get_attribute('exposure_time')
            
        savename = self.get_savename(savename_extra=extra)
        
        caput('XF:11BMB-ES{Det:SAXS}:cam1:FileName', savename)
        
        if verbosity>=2 and (get_beamline().current_mode != 'measurement'):
            print("WARNING: Beamline is not in measurement mode (mode is '{}')".format(get_beamline().current_mode))
        
        md_current = self.get_md()
        md_current['sample_savename'] = savename
        md_current['measure_type'] = measure_type
        
        md_current.update(self.get_measurement_md())
        md_current['filename'] = '{:s}_{:04d}.tiff'.format(savename, md_current['detector_sequence_ID'])
        md_current.update(md)
        
        self.expose(exposure_time, verbosity=verbosity, **md_current)
        
        
    def measureSpots(self, num_spots=4, translation_amount=0.2, axis='y', exposure_time=None, extra=None, measure_type='measureSpots', **md):
        '''Measure multiple spots on the sample.'''
        
        if 'spot_number' not in self.md:
            self.md['spot_number'] = 1
        
        
        for spot_num in range(num_spots):
        
            self.measure(exposure_time=exposure_time, extra=extra, measure_type=measure_type, **md)
            
            getattr(self, axis+'r')(translation_amount)
            self.md['spot_number'] += 1
        
        
        

    def do(self, step=0):
        '''Performs the "default action" for this sample. This usually means 
        aligning the sample, and taking data.
        
        The 'step' argument can optionally be given to jump to a particular
        step in the sequence.'''
        
        if step<=1:
            self.xo() # goto origin
            #self.gotoAlignedPosition()
            
        #if step<=5:
            #self.align()
            
        if step<=10:
            self.measure()
                
        


class SampleTSAXS_Generic(Sample_Generic):
    
    pass


class SampleGISAXS_Generic(Sample_Generic):
    
    def __init__(self, name, base=None, **md):
        
        super().__init__(name=name, base=base, **md)
        self.naming_scheme = ['name', 'extra', 'th', 'exposure_time']
        self.incident_angles_default = [0.08, 0.10, 0.12, 0.15, 0.20]
        
        
    def measureSpots(self, num_spots=2, translation_amount=0.1, axis='x', exposure_time=None, extra=None, measure_type='measureSpots', **md):
        super().measureSpots(num_spots=num_spots, translation_amount=translation_amount, axis=axis, exposure_time=exposure_time, extra=extra, measure_type=measure_type, **md)
    
    
    def measureIncidentAngle(self, angle, exposure_time=None, extra=None, **md):
        
        self.thabs(angle)
        
        self.measure(exposure_time=exposure_time, extra=extra, **md)


    def measureIncidentAngles(self, angles=None, exposure_time=None, extra=None, **md):
        
        if angles is None:
            angles = self.incident_angles_default
        
        for angle in angles:
            self.measureIncidentAngle(angle, exposure_time=exposure_time, extra=extra, **md)
    
    
    def align(self):
        
        # TODO: Check what mode we are in, change if necessary...
        # cms.modeAlignment()
        
        fit_scan(smy, 0.3, 17, fit='sigmoid_r')
        fit_scan(sth, 1.2, 21, fit='gauss')

        fit_scan(smy, 0.2, 17, fit='sigmoid_r')
        fit_scan(sth, 0.8, 21, fit='gauss')
    
    
    def do(self, step=0):
        
        if step<=1:
            self.xo() # goto origin
        
        if step<=5:
            self.align()
        
        if step<=10:
            self.set_attribute('exposure_time', 5.0)
            self.measureIncidentAngles(self.incident_angles_default)
        






class Stage(CoordinateSystem):
    
    pass


class SampleStage(Stage):
    
    def __init__(self, name='SampleStage', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = [ {'name': 'x',
                            'motor': smx,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves stage left/outboard (beam moves right on sample)',
                            },
                            {'name': 'y',
                            'motor': smy,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves stage up (beam moves down on sample)',
                            },
                            {'name': 'th',
                            'motor': sth,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'deg',
                            'hint': 'positive tilts clockwise (positive incident angle)',
                            },
                        ]     
            



class Holder(Stage):
    '''The Holder() classes are used to define bars/stages that hold one or more 
    samples. This class can thus help to keep track of coordinate conversions, 
    to store the positions of multiple samples, and to automate the measurement 
    of multiple samples.'''

    # Core methods
    ########################################

    def __init__(self, name='Holder', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
        self._samples = {}

    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = [ {'name': 'x',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves stage left/outboard (beam moves right on sample)',
                            },
                            {'name': 'y',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves stage up (beam moves down on sample)',
                            },
                            {'name': 'th',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'deg',
                            'hint': 'positive tilts clockwise (positive incident angle)',
                            },
                        ]  

    # Sample management
    ########################################
    
    def addSample(self, sample, sample_number=None):
        '''Add a sample to this holder/bar.'''
        
        if sample_number is None:
            if len(self._samples)==0:
                sample_number = 1
            else:
                ki = [ int(key) for key in self._samples.keys() ]
                sample_number = np.max(ki) + 1
                
                
        if sample_number in self._samples.keys():
            print('Warning: Sample number {} is already defined on holder "{:s}". Use "replaceSample" if you are sure you want to eliminate the existing sample from the holder.'.format(sample_number, self.name) )
            
        else:
            self._samples[sample_number] = sample
            
        self._samples[sample_number] = sample
        
        sample.set_base_stage(self)
        sample.md['holder_sample_number'] = sample_number


    def removeSample(self, sample_number):
        '''Remove a particular sample from this holder/bar.'''
        
        del self._samples[sample_number]
        
    
    def removeSamplesAll(self):
        
        self._samples = {}
        

    def replaceSample(self, sample, sample_number):
        '''Replace a given sample on this holder/bar with a different sample.'''
        
        self.removeSample(sample_number)
        self.addSample(sample, sample_number)
                
                
    def getSample(self, sample_number, verbosity=3):
        '''Return the requested sample object from this holder/bar.
        
        One can provide an integer, in which case the corresponding sample
        (from the holder's inventory) is returned. If a string is provided, 
        the closest-matching sample (by name) is returned.'''
        
        if type(sample_number) is int:
            if sample_number not in self._samples:
                if verbosity>=1:
                    print('Error: Sample {} not defined.'.format(sample_number))
                return None
            
            sample_match = self._samples[sample_number]

            if verbosity>=3:
                print('{}: {:s}'.format(sample_number, sample_match.name))
            
            return sample_match
        
            
        elif type(sample_number) is str:
            
            # First search for an exact name match
            matches = 0
            sample_match = None
            sample_i_match = None
            for sample_i, sample in sorted(self._samples.items()):
                if sample.name==sample_number:
                    matches += 1
                    if sample_match is None:
                        sample_match = sample
                        sample_i_match = sample_i
                    
            if matches==1:
                if verbosity>=3:
                    print('{}: {:s}'.format(sample_i_match, sample_match.name))
                return sample_match
                    
            elif matches>1:
                if verbosity>=2:
                    print('{:d} exact matches for "{:s}", returning sample {}: {:s}'.format(matches, sample_number, sample_i_match, sample_match.name))
                return sample_match
            
            
            # Try to find a 'start of name' match
            for sample_i, sample in sorted(self._samples.items()):
                if sample.name.startswith(sample_number):
                    matches += 1
                    if sample_match is None:
                        sample_match = sample
                        sample_i_match = sample_i
                        
            if matches==1:
                if verbosity>=3:
                    print('Beginning-name match: {}: {:s}'.format(sample_i_match, sample_match.name))
                return sample_match
                    
            elif matches>1:
                if verbosity>=2:
                    print('{:d} beginning-name matches for "{:s}", returning sample {}: {:s}'.format(matches, sample_number, sample_i_match, sample_match.name))
                return sample_match
            
            # Try to find a substring match
            for sample_i, sample in sorted(self._samples.items()):
                if sample_number in sample.name:
                    matches += 1
                    if sample_match is None:
                        sample_match = sample
                        sample_i_match = sample_i
                        
            if matches==1:
                if verbosity>=3:
                    print('Substring match: {}: {:s}'.format(sample_i_match, sample_match.name))
                return sample_match
                    
            elif matches>1:
                if verbosity>=2:
                    print('{:d} substring matches for "{:s}", returning sample {}: {:s}'.format(matches, sample_number, sample_i_match, sample_match.name))
                return sample_match
            
            if verbosity>=1:
                print('No sample has a name matching "{:s}"'.format(sample_number))
            return None
            
            
        else:
            
            print('Error: Sample designation "{}" not understood.'.format(sample_number))
            return None
    
    
    def getSamples(self, range=None, verbosity=3):
        '''Get the list of samples associated with this holder.
        
        If the optional range argument is provided (2-tuple), then only sample
        numbers within that range (inclusive) are run. If range is instead a 
        string, then all samples with names that match are returned.'''
        
        samples = []
        
        if range is None:
            for sample_number in sorted(self._samples):
                samples.append(self._samples[sample_number])
                
        elif type(range) is list:
            start, stop = range
            for sample_number in sorted(self._samples):
                if sample_number>=start and sample_number<=stop:
                    samples.append(self._samples[sample_number])
                    
        elif type(range) is str:
            for sample_number, sample in sorted(self._samples.items()):
                if range in sample.name:
                    samples.append(sample)
        
        else:
            if verbosity>=1:
                print('Range argument "{}" not understood.'.format(range))
            
            
        return samples
        
        
    def listSamples(self):
        '''Print a list of the current samples associated with this holder/
        bar.'''
        
        for sample_number, sample in sorted(self._samples.items()):
            print( '{}: {:s}'.format(sample_number, sample.name) )
        

    def gotoSample(self, sample_number):
        
        sample = self.getSample(sample_number, verbosity=0)
        sample.gotoAlignedPosition()
        
        return sample
        
        
    # Action (measurement) methods
    ########################################
                           
    def doSamples(self, range=None):
        '''Activate the default action (typically measurement) for all the samples.
        
        If the optional range argument is provided (2-tuple), then only sample
        numbers within that range (inclusive) are run. If range is instead a 
        string, then all samples with names that match are returned.'''
        
        for sample in self.getSamples(range=range):
            sample.do()
                



class PositionalHolder(Holder):
    '''This class is a sample holder that is one-dimensional. E.g. a bar with a
    set of samples lined up, or a holder with a set number of slots for holding
    samples. This class thus helps to associate each sample with its position
    on the bar.'''

    # Core methods
    ########################################

    def __init__(self, name='PositionalHolder', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
        self._positional_axis = 'x'

        
    # Sample management
    ########################################

    def slot(self, sample_number):
        '''Moves to the selected slot in the holder.'''
        
        getattr(self, self._positional_axis+'abs')( self.get_slot_position(sample_number) )
        
    
    def get_slot_position(self, slot):
        '''Return the motor position for the requested slot number.'''
        # This method should be over-ridden in sub-classes, so as to properly
        # implement the positioning appropriate for that holder.
        
        position = 0.0 + slot*1.0
        
        return position
        
        
    def addSampleSlot(self, sample, slot):
        '''Adds a sample to the specified "slot" (defined/numbered sample 
        holding spot on this holder).'''
        
        self.addSample(sample, sample_number=slot)
        sample.setOrigin( [self._positional_axis], [self.get_slot_position(slot)] )

                
    def listSamplesPositions(self):
        '''Print a list of the current samples associated with this holder/
        bar.'''
        
        for sample_number, sample in self._samples.items():
            pos = getattr(sample, self._positional_axis+'pos')(verbosity=0)
            print( '%s: %s (%s = %.3f)' % (str(sample_number), sample.name, self._positional_axis, pos) )



class CapillaryHolder(PositionalHolder):
    '''This class is a sample holder that has 15 slots for capillaries.'''

    # Core methods
    ########################################

    def __init__(self, name='CapillaryHolder', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
        self._positional_axis = 'x'
        
        self.x_spacing = 6.342 # 3.5 inches / 14 spaces
        
        # Set the x and y origin to be the center of slot 8
        self.xsetOrigin(0.00)
        self.ysetOrigin(0.00)
                
                
    def get_slot_position(self, slot):
        '''Return the motor position for the requested slot number.'''
        
        return self.x_spacing*(slot-8)
        

stg = SampleStage()
def get_default_stage():
    return stg




if False:
    # For testing:
    # %run -i /opt/ipython_profiles/profile_collection/startup/94-sample.py
    sam = SampleGISAXS_Generic('testing_of_code')
    sam.mark('here')
    #sam.mark('XY_field', 'x', 'y')
    #sam.mark('specified', x=1, th=0.1)
    #sam.naming(['name', 'extra', 'clock', 'th', 'exposure_time', 'id'])
    #sam.thsetOrigin(0.5)
    #sam.marks()
    
    
    hol = CapillaryHolder(base=stg)
    hol.addSampleSlot( SampleGISAXS_Generic('test_sample_01'), 1.0 )
    hol.addSampleSlot( SampleGISAXS_Generic('test_sample_02'), 3.0 )
    hol.addSampleSlot( SampleGISAXS_Generic('test_sample_03'), 5.0 )
    
    sam = hol.getSample(1)


    
