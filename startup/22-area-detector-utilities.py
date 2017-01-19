
def xp_set(seconds):
#    sleep_time=0.002
    caput('XF:11BMB-ES{Det:SAXS}:cam1:AcquireTime',seconds)
#    sleep(sleep_time)
    caput('XF:11BMB-ES{Det:SAXS}:cam1:AcquirePeriod',seconds+0.1)

def xp(seconds):
    sleep_time=0.1
    caput('XF:11BMB-ES{Det:SAXS}:cam1:Acquire',1)
    sleep(seconds+sleep_time)


