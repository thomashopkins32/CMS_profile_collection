caput(beam.mono_bragg_pv, 1.03953)
caput("XF:11BMB-ES{Det:PIL2M}:TIFF1:CreateDirectory", -20)
sam = SampleGISAXS('test')
detselect(pilatus2M)

pilatus2M.cam.num_images.put(1)
