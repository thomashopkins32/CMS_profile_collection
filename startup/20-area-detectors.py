#import time as ttime  # tea time
#from datetime import datetime
from ophyd import (ProsilicaDetector, SingleTrigger,
                   TIFFPlugin, ImagePlugin, DetectorBase,
                   HDF5Plugin, AreaDetector, EpicsSignal, EpicsSignalRO,
                   ROIPlugin, TransformPlugin, ProcessPlugin, PilatusDetector,
                   ProsilicaDetectorCam, PilatusDetectorCam, StatsPlugin)
from ophyd.areadetector.cam import AreaDetectorCam
from ophyd.areadetector.base import ADComponent, EpicsSignalWithRBV
from ophyd.areadetector.filestore_mixins import FileStoreTIFFIterativeWrite
from ophyd import Component as Cpt, Signal
from ophyd.utils import set_and_wait
from nslsii.ad33 import SingleTriggerV33,  StatsPluginV33
#import filestore.api as fs


#class Elm(SingleTrigger, DetectorBase):
 #   pass




class TIFFPluginWithFileStore(TIFFPlugin, FileStoreTIFFIterativeWrite):
    pass

class ProsilicaDetectorCamV33(ProsilicaDetectorCam):
    '''This is used to update the standard prosilica to AD33.
    '''
    wait_for_plugins = Cpt(EpicsSignal, 'WaitForPlugins',
                           string=True, kind='config')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs['wait_for_plugins'] = 'Yes'

    def ensure_nonblocking(self):
        self.stage_sigs['wait_for_plugins'] = 'Yes'
        for c in self.parent.component_names:
            cpt = getattr(self.parent, c)
            if cpt is self:
                continue
            if hasattr(cpt, 'ensure_nonblocking'):
                cpt.ensure_nonblocking()

class Pilatus2M(SingleTrigger, PilatusDetector):
    image = Cpt(ImagePlugin, 'image1:')
    stats1 = Cpt(StatsPlugin, 'Stats1:')
    stats2 = Cpt(StatsPlugin, 'Stats2:')
    stats3 = Cpt(StatsPlugin, 'Stats3:')
    stats4 = Cpt(StatsPlugin, 'Stats4:')
    stats5 = Cpt(StatsPlugin, 'Stats5:')
    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')
    proc1 = Cpt(ProcessPlugin, 'Proc1:')

    tiff = Cpt(TIFFPluginWithFileStore,
               suffix='TIFF1:',
               write_path_template='/GPFS/xf11bm/Pilatus2M/%Y/%m/%d/',
               root='/GPFS/xf11bm')

    def setExposureTime(self, exposure_time, verbosity=3):
        caput('XF:11BMB-ES{Det:PIL2M}:cam1:AcquireTime', exposure_time)
        caput('XF:11BMB-ES{Det:PIL2M}:cam1:AcquirePeriod', exposure_time+0.1)


class StandardProsilica(SingleTrigger, ProsilicaDetector):
    # tiff = Cpt(TIFFPluginWithFileStore,
    #           suffix='TIFF1:',
    #           write_path_template='/XF11ID/data/')
    image = Cpt(ImagePlugin, 'image1:')
    stats1 = Cpt(StatsPluginV33, 'Stats1:')
    stats2 = Cpt(StatsPluginV33, 'Stats2:')
    stats3 = Cpt(StatsPluginV33, 'Stats3:')
    stats4 = Cpt(StatsPluginV33, 'Stats4:')
    stats5 = Cpt(StatsPluginV33, 'Stats5:')
    trans1 = Cpt(TransformPlugin, 'Trans1:')
    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')
    proc1 = Cpt(ProcessPlugin, 'Proc1:')



class StandardProsilicaV33(SingleTriggerV33, ProsilicaDetector):
    # tiff = Cpt(TIFFPluginWithFileStore,
    #           suffix='TIFF1:',
    #           write_path_template='/XF11ID/data/')
    cam = Cpt(ProsilicaDetectorCamV33, 'cam1:')
    image = Cpt(ImagePlugin, 'image1:')
    stats1 = Cpt(StatsPluginV33, 'Stats1:')
    stats2 = Cpt(StatsPluginV33, 'Stats2:')
    stats3 = Cpt(StatsPluginV33, 'Stats3:')
    stats4 = Cpt(StatsPluginV33, 'Stats4:')
    stats5 = Cpt(StatsPluginV33, 'Stats5:')
    trans1 = Cpt(TransformPlugin, 'Trans1:')
    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')
    proc1 = Cpt(ProcessPlugin, 'Proc1:')

class PilatusDetectorCamV33(PilatusDetectorCam):
    '''This is used to update the standard prosilica to AD33.
    '''
    wait_for_plugins = Cpt(EpicsSignal, 'WaitForPlugins',
                           string=True, kind='config')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs['wait_for_plugins'] = 'Yes'

    def ensure_nonblocking(self):
        self.stage_sigs['wait_for_plugins'] = 'Yes'
        for c in self.parent.component_names:
            cpt = getattr(self.parent, c)
            if cpt is self:
                continue
            if hasattr(cpt, 'ensure_nonblocking'):
                cpt.ensure_nonblocking()



class Pilatus(SingleTrigger, PilatusDetector):
    image = Cpt(ImagePlugin, 'image1:')
    stats1 = Cpt(StatsPluginV33, 'Stats1:')
    stats2 = Cpt(StatsPluginV33, 'Stats2:')
    stats3 = Cpt(StatsPluginV33, 'Stats3:')
    stats4 = Cpt(StatsPluginV33, 'Stats4:')
    stats5 = Cpt(StatsPluginV33, 'Stats5:')
    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')
    proc1 = Cpt(ProcessPlugin, 'Proc1:')

    tiff = Cpt(TIFFPluginWithFileStore,
               suffix='TIFF1:',
               write_path_template='/GPFS/xf11bm/Pilatus300/%Y/%m/%d/',
               root='/GPFS/xf11bm')

    def setExposureTime(self, exposure_time, verbosity=3):
        caput('XF:11BMB-ES{Det:SAXS}:cam1:AcquireTime', exposure_time)
        caput('XF:11BMB-ES{Det:SAXS}:cam1:AcquirePeriod', exposure_time+0.1)

class PilatusV33(SingleTriggerV33, PilatusDetector):
    cam = Cpt(PilatusDetectorCamV33, 'cam1:')
    image = Cpt(ImagePlugin, 'image1:')
    stats1 = Cpt(StatsPluginV33, 'Stats1:')
    stats2 = Cpt(StatsPluginV33, 'Stats2:')
    stats3 = Cpt(StatsPluginV33, 'Stats3:')
    stats4 = Cpt(StatsPluginV33, 'Stats4:')
    stats5 = Cpt(StatsPluginV33, 'Stats5:')
    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')
    proc1 = Cpt(ProcessPlugin, 'Proc1:')


    tiff = Cpt(TIFFPluginWithFileStore,
               suffix='TIFF1:',
               write_path_template='/GPFS/xf11bm/Pilatus300/%Y/%m/%d/',
               root='/GPFS/xf11bm')

    def setExposureTime(self, exposure_time, verbosity=3):
        self.cam.acquire_time.put(exposure_time)
        self.cam.acquire_period.put(exposure_time+.1)
        #caput('XF:11BMB-ES{Det:SAXS}:cam1:AcquireTime', exposure_time)
        #caput('XF:11BMB-ES{Det:SAXS}:cam1:AcquirePeriod', exposure_time+0.1)



class Pilatus2M(SingleTrigger, PilatusDetector):

    image = Cpt(ImagePlugin, 'image1:')
    stats1 = Cpt(StatsPluginV33, 'Stats1:')
    stats2 = Cpt(StatsPluginV33, 'Stats2:')
    stats3 = Cpt(StatsPluginV33, 'Stats3:')
    stats4 = Cpt(StatsPluginV33, 'Stats4:')
    stats5 = Cpt(StatsPluginV33, 'Stats5:')
    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')
    proc1 = Cpt(ProcessPlugin, 'Proc1:')

    trans1 = Cpt(TransformPlugin, 'Trans1:')

    tiff = Cpt(TIFFPluginWithFileStore,
               suffix='TIFF1:',
               write_path_template='/GPFS/xf11bm/Pilatus2M/%Y/%m/%d/',
               root='/GPFS/xf11bm')

    def setExposureTime(self, exposure_time, verbosity=3):
        # how to do this with stage_sigs (warning, need to change this every time
        # if you set)
        # RE(pilatus2M.setEposure(1))   ---format 
        #self.cam.stage_sigs['acquire_time'] = exposure_time
        #self.cam.stage_sigs['acquire_period'] = exposure_time+.1

        yield from mv(self.cam.acquire_time, exposure_time, self.cam.acquire_period, exposure_time+0.1)
        #yield from mv(self.cam.acquire_period, exposure_time+0.1)
        
        #self.cam.acquire_time.put(exposure_time)
        #self.cam.acquire_period.put(exposure_time+.1)
        ##caput('XF:11BMB-ES{Det:PIL2M}:cam1:AcquireTime', exposure_time)
        #caput('XF:11BMB-ES{Det:PIL2M}:cam1:AcquirePeriod', exposure_time+0.1)

class Pilatus2MV33(SingleTriggerV33, PilatusDetector):
    cam = Cpt(PilatusDetectorCamV33, 'cam1:')
    image = Cpt(ImagePlugin, 'image1:')
    stats1 = Cpt(StatsPluginV33, 'Stats1:')
    stats2 = Cpt(StatsPluginV33, 'Stats2:')
    stats3 = Cpt(StatsPluginV33, 'Stats3:')
    stats4 = Cpt(StatsPluginV33, 'Stats4:')
    stats5 = Cpt(StatsPluginV33, 'Stats5:')
    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')
    proc1 = Cpt(ProcessPlugin, 'Proc1:')
    trans1 = Cpt(TransformPlugin, 'Trans1:')

    tiff = Cpt(TIFFPluginWithFileStore,
               suffix='TIFF1:',
               write_path_template='/GPFS/xf11bm/Pilatus2M/%Y/%m/%d/',
               root='/GPFS/xf11bm')

    def setExposureTime(self, exposure_time, verbosity=3):
        yield from mv(self.cam.acquire_time, exposure_time, self.cam.acquire_period, exposure_time+0.1)
        #self.cam.acquire_time.put(exposure_time)
        #self.cam.acquire_period.put(exposure_time+.1)
        #caput('XF:11BMB-ES{Det:PIL2M}:cam1:AcquireTime', exposure_time)
        #caput('XF:11BMB-ES{Det:PIL2M}:cam1:AcquirePeriod', exposure_time+0.1)

'''
    #def _cms_error_condition_print(self, extra, value=None, print_gets=False):
        ##https://github.com/NSLS-II/ophyd/blob/master/ophyd/signal.py

        #if hasattr(self, '_kludge_state') and self._kludge_state:
            ## This check prevents the system from getting into
            ## an infinite loop where each print calls 'get' (or 'value')
            ## and thus triggers this function again
            #pass
        
        #else:
            #self._kludge_state = True
        
            #print('\n\n\n\n\n########################################')
            #print('ERROR ENCOUNTERED in {}'.format(extra))
            
            #if value is not None:
                #print('Value is: {}'.format(value))
                
            ## Log to file
            #with open('error.log', 'a') as fout:
                #fout.write('ERROR ENCOUNTERED in {}\n'.format(extra))
                #fout.write(' self.pvname: {}\n'.format(self.pvname))
                #fout.write(' time: {}\n'.format(time.time()))
                #fout.write(' value: {}\n'.format(value))
                #if value==None:
                    #fout.write(' value matches Python None\n'.format(value))
                #if value==b'None':
                    #fout.write(" value matches b'None'\n".format(value))
                #if value=='None':
                    #fout.write(" value matches 'None'\n".format(value))
                
            #print('########################################\n\n\n\n\n')        

    #testing pv output
    
        #save all pv, sig, value into error_test_stage.csv
    #def stage(self) -> List[object]:
    def stage(self, *args, **kwargs):
        """Stage the device for data collection.

        This method is expected to put the device into a state where
        repeated calls to :meth:`~BlueskyInterface.trigger` and
        :meth:`~BlueskyInterface.read` will 'do the right thing'.

        Staging not idempotent and should raise
        :obj:`RedundantStaging` if staged twice without an
        intermediate :meth:`~BlueskyInterface.unstage`.

        This method should be as fast as is feasible as it does not return
        a status object.

        The return value of this is a list of all of the (sub) devices
        stage, including it's self.  This is used to ensure devices
        are not staged twice by the :obj:`~bluesky.run_engine.RunEngine`.

        This is an optional method, if the device does not need
        staging behavior it should not implement `stage` (or
        `unstage`).

        Returns
        -------
        devices : list
            list including self and all child devices staged

        """
        if self._staged == Staged.no:
            pass  # to short-circuit checking individual cases
        elif self._staged == Staged.yes:
            raise RedundantStaging("Device {!r} is already staged. "
                                   "Unstage it first.".format(self))
        elif self._staged == Staged.partially:
            raise RedundantStaging("Device {!r} has been partially staged. "
                                   "Maybe the most recent unstaging "
                                   "encountered an error before finishing. "
                                   "Try unstaging again.".format(self))
        self.log.debug("Staging %s", self.name)
        self._staged = Staged.partially

    
        # Resolve any stage_sigs keys given as strings: 'a.b' -> self.a.b
        stage_sigs = OrderedDict()
        for k, v in self.stage_sigs.items():
            if isinstance(k, str):
                # Device.__getattr__ handles nested attr lookup
                stage_sigs[getattr(self, k)] = v
            else:
                stage_sigs[k] = v

        # Read current values, to be restored by unstage()
        original_vals = {sig: sig.get() for sig in stage_sigs}

        #Warning Warning Warning
        #101218, KY and RL add code below to check the pv error
        os.remove('error_test_stage.log')
        
        for sig, val in original_vals.items():
            #while val == b'None' or val == 'None':
                
            #ttime.sleep(1)
            original_vals[sig] = sig.get() 
            print('================None value in stage============')
            print('val={}'.format(val))
            print('sig={}'.format(sig))
            print('================None value in stage============')
            with open('error_test_stage.log', 'a') as fout:
                #fout.write('ERROR ENCOUNTERED in {}\n'.format(extra))
                fout.write(' self.pvname: {}\n'.format(self.pvname))
                #fout.write(' time: {}\n'.format(time.time()))
                fout.write(' value: {}\n'.format(value))
                if value==None:
                    fout.write(' value matches Python None\n'.format(value))
                if value==b'None':
                    fout.write(" value matches b'None'\n".format(value))
                if value=='None':
                    fout.write(" value matches 'None'\n".format(value)) 
        print('sig and val have been saved')
       # We will add signals and values from original_vals to
        # self._original_vals one at a time so that
        # we can undo our partial work in the event of an error.

        # Apply settings.
        devices_staged = []
        try:
            for sig, val in stage_sigs.items():
                self.log.debug("Setting %s to %r (original value: %r)",
                               self.name,
                               val, original_vals[sig])
                set_and_wait(sig, val)
                # It worked -- now add it to this list of sigs to unstage.
                self._original_vals[sig] = original_vals[sig]
            devices_staged.append(self)

            # Call stage() on child devices.
            for attr in self._sub_devices:
                device = getattr(self, attr)
                if hasattr(device, 'stage'):
                    device.stage()
                    devices_staged.append(device)
        except Exception:
            self.log.debug("An exception was raised while staging %s or "
                           "one of its children. Attempting to restore "
                           "original settings before re-raising the "
                           "exception.", self.name)
            self.unstage()
            raise
        else:
            self._staged = Staged.yes
        return devices_staged

    #def unstage(self) -> List[object]:
    def unstage(self):
        """Unstage the device.

        This method returns the device to the state it was prior to the
        last `stage` call.

        This method should be as fast as feasible as it does not
        return a status object.

        This method must be idempotent, multiple calls (without a new
        call to 'stage') have no effect.

        Returns
        -------
        devices : list
            list including self and all child devices unstaged

        """
        self.log.debug("Unstaging %s", self.name)
        self._staged = Staged.partially
        devices_unstaged = []

        # Call unstage() on child devices.
        for attr in self._sub_devices[::-1]:
            device = getattr(self, attr)
            if hasattr(device, 'unstage'):
                device.unstage()
                devices_unstaged.append(device)

        os.remove('error_test_stage.log')

        # Restore original values.
        for sig, val in reversed(list(self._original_vals.items())):
            self.log.debug("Setting %s back to its original value: %r)",
                           self.name,
                           val)
            # WARNING WARNING WARNING
            # Modification by KY and RL (CMS beamline) 2018-09-24
            # This is a fix to avoid triggering a ValueError when ca.py:put() tries to set an erroneous value.
            #if val==b'None' or val==None:
                #pass
            #else:
                #set_and_wait(sig, val)
        
            with open('error_test_unstage.log', 'a') as fout:
                #fout.write('ERROR ENCOUNTERED in {}\n'.format(extra))
                fout.write(' self.pvname: {}\n'.format(self.pvname))
                #fout.write(' time: {}\n'.format(time.time()))
                fout.write(' value: {}\n'.format(value))
                if value==None:
                    fout.write(' value matches Python None\n'.format(value))
                if value==b'None':
                    fout.write(" value matches b'None'\n".format(value))
                if value=='None':
                    fout.write(" value matches 'None'\n".format(value)) 

           # success = False
           # count = 0
           # while count<10 and not success:
           #     count += 1
           #     try:
           #         set_and_wait(sig, val)
           #         success = True
           #     except:
           #         print("\n\n\n=====================")
           #         print('WARNING: PV bug. count = {}'.format(count))
           #         print('sig.name = {} ; val = {}'.format(sig.name, val))
           #         print(sig)
           #         ttime.sleep(2)
           #         print("=====================\n\n\n")
           #         if count>5:
           #             raise



            
            #original code was: 
            set_and_wait(sig, val)
            
            self._original_vals.pop(sig)
        devices_unstaged.append(self)

        self._staged = Staged.no
        return devices_unstaged        #save all pv, sig, value into error_test_unstage.csv
'''


#class StandardProsilicaWithTIFF(StandardProsilica):
#    tiff = Cpt(TIFFPluginWithFileStore,
#               suffix='TIFF1:',
#               write_path_template='/GPFS/xf11bm/data/%Y/%m/%d/',
#               root='/GPFS/xf11bm/')



## This renaming should be reversed: no correspondance between CSS screens, PV names and ophyd....
#xray_eye1 = StandardProsilica('XF:11IDA-BI{Bpm:1-Cam:1}', name='xray_eye1')
#xray_eye2 = StandardProsilica('XF:11IDB-BI{Mon:1-Cam:1}', name='xray_eye2')
#xray_eye3 = StandardProsilica('XF:11IDB-BI{Cam:08}', name='xray_eye3')
#xray_eye1_writing = StandardProsilicaWithTIFF('XF:11IDA-BI{Bpm:1-Cam:1}', name='xray_eye1')
#xray_eye2_writing = StandardProsilicaWithTIFF('XF:11IDB-BI{Mon:1-Cam:1}', name='xray_eye2')
#xray_eye3_writing = StandardProsilicaWithTIFF('XF:11IDB-BI{Cam:08}', name='xray_eye3')
#fs1 = StandardProsilica('XF:11IDA-BI{FS:1-Cam:1}', name='fs1')
#fs2 = StandardProsilica('XF:11IDA-BI{FS:2-Cam:1}', name='fs2')
#fs_wbs = StandardProsilica('XF:11IDA-BI{BS:WB-Cam:1}', name='fs_wbs')
#dcm_cam = StandardProsilica('XF:11IDA-BI{Mono:DCM-Cam:1}', name='dcm_cam')
#fs_pbs = StandardProsilica('XF:11IDA-BI{BS:PB-Cam:1}', name='fs_pbs')
#elm = Elm('XF:11IDA-BI{AH401B}AH401B:',)

fs1 = StandardProsilicaV33('XF:11BMA-BI{FS:1-Cam:1}', name='fs1')
fs2 = StandardProsilicaV33('XF:11BMA-BI{FS:2-Cam:1}', name='fs2')
fs3 = StandardProsilicaV33('XF:11BMB-BI{FS:3-Cam:1}', name='fs3')
fs4 = StandardProsilicaV33('XF:11BMB-BI{FS:4-Cam:1}', name='fs4')
fs5 = StandardProsilicaV33('XF:11BMB-BI{FS:Test-Cam:1}', name='fs5')

all_standard_pros = [fs1, fs2, fs3, fs4, fs5]

for camera in all_standard_pros:
    camera.read_attrs = ['stats1', 'stats2','stats3','stats4','stats5']
    # camera.tiff.read_attrs = []  # leaving just the 'image'
    for stats_name in ['stats1', 'stats2','stats3','stats4','stats5']:
        stats_plugin = getattr(camera, stats_name)
        stats_plugin.read_attrs = ['total']
        #camera.stage_sigs[stats_plugin.blocking_callbacks] = 1

    #camera.stage_sigs[camera.roi1.blocking_callbacks] = 1
    #camera.stage_sigs[camera.trans1.blocking_callbacks] = 1
    #camera.cam.ensure_nonblocking()
    camera.stage_sigs[camera.cam.trigger_mode] = 'Fixed Rate'


#for camera in [xray_eye1_writing, xray_eye2_writing, xray_eye3_writing]:
#    camera.read_attrs.append('tiff')
#    camera.tiff.read_attrs = []

#pilatus300 section is marked out as the detector sever cannot be reached after AC power outrage. 121417-RL
#pilatus300 section is unmarked.  032018-MF
'''
'''
pilatus300 = PilatusV33('XF:11BMB-ES{Det:SAXS}:', name='pilatus300')
pilatus300.tiff.read_attrs = []
#STATS_NAMES = ['stats1', 'stats2', 'stats3', 'stats4', 'stats5']
#pilatus300.read_attrs = ['tiff'] + STATS_NAMES
#for stats_name in STATS_NAMES:
    #stats_plugin = getattr(pilatus300, stats_name)
    #stats_plugin.read_attrs = ['total']

#pilatus300.cam.ensure_nonblocking()

pilatus2M = Pilatus2MV33('XF:11BMB-ES{Det:PIL2M}:', name='pilatus2M')
pilatus2M.tiff.read_attrs = []
STATS_NAMES2M = ['stats1', 'stats2', 'stats3', 'stats4']
pilatus2M.read_attrs = ['tiff'] + STATS_NAMES2M
for stats_name in STATS_NAMES2M:
    stats_plugin = getattr(pilatus2M, stats_name)
    stats_plugin.read_attrs = ['total']
#pilatus2M.cam.ensure_nonblocking()


for item in pilatus2M.stats1.configuration_attrs:
    item_check = getattr(pilatus2M.stats1, item)
    item_check.kind= 'omitted'

for item in pilatus2M.stats2.configuration_attrs:
    item_check = getattr(pilatus2M.stats2, item)
    item_check.kind= 'omitted'

for item in pilatus2M.stats3.configuration_attrs:
    item_check = getattr(pilatus2M.stats3, item)
    item_check.kind= 'omitted'

for item in pilatus2M.stats4.configuration_attrs:
    item_check = getattr(pilatus2M.stats4, item)
    item_check.kind= 'omitted'

for item in pilatus2M.stats5.configuration_attrs:
    item_check = getattr(pilatus2M.stats5, item)
    item_check.kind= 'omitted'

for item in pilatus2M.tiff.configuration_attrs:
    item_check = getattr(pilatus2M.tiff, item)
    item_check.kind= 'omitted'

for item in pilatus2M.cam.configuration_attrs:
    item_check = getattr(pilatus2M.cam, item)
    item_check.kind= 'omitted'


#STATS_NAMES2M = ['stats3', 'stats4']
#pilatus2M.read_attrs = ['tiff'] + STATS_NAMES2M
##for stats_name in STATS_NAMES2M:
    ##stats_plugin = getattr(pilatus2M, stats_name)
    ##stats_plugin.read_attrs = ['total']
    

pilatus300.stats3.total.kind = 'hinted'
pilatus300.stats4.total.kind = 'hinted'
pilatus2M.stats3.total.kind = 'hinted'
pilatus2M.stats4.total.kind = 'hinted'

#pilatus2M.read_attrs = ['cbf'] + STATS_NAMES2M



for stats_name in STATS_NAMES2M:
    stats_plugin = getattr(pilatus2M, stats_name)
    stats_plugin.read_attrs = ['total']


#define the current pilatus detector: pilatus_name and _Epicsname, instead of
#pilatus300 or pilatus2M
pilatus_name = pilatus2M
pilatus_Epicsname = '{Det:PIL2M}'


#######################################################
# These are test functions added by Julien
# We should remove them once we find the source of the
# current "None"type bug at CMS (TRAC ticket [2284]
def get_stage_sigs(dev, dd):
    for cpt_name in dev.component_names:
        cpt = getattr(dev, cpt_name)
        if hasattr(cpt, 'stage_sigs'):
            dd.update(cpt.stage_sigs)
        if hasattr(cpt, 'component_names'):
            get_stage_sigs(cpt, dd)

def stage_unstage_forever_plan(det):
    i = 0
    print("Started the stage_unstage_plan, running infinite loop...")
    while True:
        i += 1
        #print(f"Staging {i}th time")
        yield from bps.stage(det)
        yield from bps.unstage(det)

def trigger_forever_plan(det):
    i = 0
    print("Started the stage_unstage_plan, running infinite loop...")
    while True:
        i += 1
        #print(f"Staging {i}th time")
        yield from bps.stage(det)
        yield from bps.trigger(det, group="det")
        yield from bps.wait("det")
        yield from bps.unstage(det)

def count_forever_plan(det):
    i = 0
    print("Started the count_forever plan, running infinite loop...")
    while True:
        i += 1
        #print(f"Staging {i}th time")
        yield from bp.count([det])

def stage_unstage_once_plan(det):
    #print(f"Staging {i}th time")
    yield from bps.stage(det)
    yield from bps.unstage(det)

def count_no_save_plan(det):
    #print(f"Staging {i}th time")
    yield from bps.stage(det)
    yield from bps.trigger(det)
    yield from bps.unstage(det)

# to get stage sigs
#from collections import OrderedDict
#stage_sigs = OrderedDict()
#get_stage_sigs(pilatus2M, stage_sigs)


#######################################################

#pilatus_name = pilatus300
#pilatus_Epicsname = '{Det:SAXS}'
