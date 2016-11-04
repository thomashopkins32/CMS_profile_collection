import ophyd

quad_electrometer1 = ophyd.EpicsSignalRO("XF:11BMA-BI{IM:1}EM180:Current1:MeanValue_RBV", name='quad_electrometer1')
quad_electrometer2 = ophyd.EpicsSignalRO("XF:11BMA-BI{IM:1}EM180:Current2:MeanValue_RBV", name='quad_electrometer2')
quad_electrometer3 = ophyd.EpicsSignalRO("XF:11BMA-BI{IM:1}EM180:Current3:MeanValue_RBV", name='quad_electrometer3')
quad_electrometer4 = ophyd.EpicsSignalRO("XF:11BMA-BI{IM:1}EM180:Current4:MeanValue_RBV", name='quad_electrometer4')

ion_chamber1 = ophyd.EpicsSignalRO("XF:11BMB-BI{IM:3}:IC1_MON", name='ion_chamber1')
ion_chamber2 = ophyd.EpicsSignalRO("XF:11BMB-BI{IM:3}:IC2_MON", name='ion_chamber2')
ion_chamber3 = ophyd.EpicsSignalRO("XF:11BMB-BI{IM:3}:IC3_MON", name='ion_chamber3')
ion_chamber4 = ophyd.EpicsSignalRO("XF:11BMB-BI{IM:3}:IC4_MON", name='ion_chamber4')

