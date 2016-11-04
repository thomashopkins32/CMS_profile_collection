#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi: ts=4 sw=4




################################################################################
#  Code for querying and controlling beamline components that 'affect' the
# beam. (Beam energy, beam flux, etc.)
################################################################################
# Known Bugs:
#  N/A
################################################################################
# TODO:
#  Search for "TODO" below.
################################################################################


# Notes
################################################################################
# verbosity=0 : Output nothing
# verbosity=1 : Output only final (minimal) result
# verbosity=2 : Output 'regular' amounts of information/data
# verbosity=3 : Output all useful information
# verbosity=4 : Output marginally useful things (e.g. essentially redundant/obvious things)
# verbosity=5 : Output everything (e.g. for testing)



# These imports are not necessary if part of the startup sequence.
# If this file is called separately, some of these may be needed.
#import numpy as np
#from epics import caget, caput
#from time import sleep

#from ophyd import EpicsMotor, Device, Component as Cpt
#from ophyd.commands import * # For mov, movr


class BeamlineElement(object):
    
    def __init__(self, name, zposition, description="", **args):
        
        self.name = name
        self.zposition = zposition
        self.description = description
        
        
    def state(self):
        """
        Returns the current state of the beamline element. Common states:
        out - Element is out of the way of the beam (and should not be blocking).
        in - Element is in the beam (but should not be blocking).
        block - Element is in the beam, and should be blocking the beam.
        undefined - Element is in an unexpected state.
        """
        
        return "out"

    
    def transmission(self):
        """
        Returns the predicted transmission of this beamline element, based on 
        its current state.
        """
        
        # Assume a generic beamline element doesn't block/perturb the beam
        return 1.0
        
        
    def flux(self, verbosity=3):
        
        reading = self.reading(verbosity=0)
        flux = self.conversion_factor*reading # ph/s
        
        if verbosity>=2:
            print('flux = {:.4g} ph/s')
        
        return flux        
        
        
class Shutter(BeamlineElement):
    
    pass


class Monitor(BeamlineElement):
    
    pass


class GateValve(BeamlineElement):
    
    def open(self, verbosity=3):
        pass
    
    def close(self, verbosity=3):
        pass


class ThreePoleWiggler(BeamlineElement):
    
    def __init__(self, name='3PW', zposition=0.0, description='Three-pole wiggler source of x-rays', **args):
        
        # TODO: Find out the right conversion factor
        self.conversion_factor = 3e18/500.0 #(ph/s)/mA
        
        super().__init__(name=name, zposition=zposition, description=description, **args)

    def state(self):
        """
        Returns the current state of the beamline element. Common states:
        out - Element is out of the way of the beam (and should not be blocking).
        in - Element is in the beam (but should not be blocking).
        block - Element is in the beam, and should be blocking the beam.
        undefined - Element is in an unexpected state.
        """
        
        position = caget('SR:C11-ID:G5{3PW:1}Mtr.RBV')
        
        # TODO: Instead use the 'inserted' flag?
        # caget('SR:C11-ID:G5{3PW:1}InsertedFlag')
        
        if abs(position-0)<3:
            return "in"
        
        elif abs(position - -189.0)<10:
            return "out"
        
        else:
            return "undefined"
        
        
    def reading(self, verbosity=3):
        
        if self.state() is 'in':
            
            ring_current = caget('SR:OPS-BI{DCCT:1}I:Real-I')
            if verbosity>=2:
                print('{:s} is inserted; ring current = {:.1f} mA'.format(self.name, ring_current))
                
            return ring_current
        
        else:
            if verbosity>=2:
                print('{:s} is not inserted.'.format(self.name))
                
            return 0
        

        
        

# CMSBeam
################################################################################
# This class represents the 'beam' at the beamline. This collects together aspects
# of querying or changing beam properties, including the energy (or wavelength), 
# the beam intensity (or measuring flux), and so forth.
class CMSBeam(object):
    
    def __init__(self):
        
        
        self.mono_bragg_pv = 'XF:11BMA-OP{Mono:DMM-Ax:Bragg}Mtr.RBV'
        
        # (planck constant * speed of light)/(electronic charge)
        self.hc_over_e = 1.23984197e-6 # m^3 kg s^-3 Amp^-1 = eV*m
        self.hc_over_e_keVpA = self.hc_over_e*1e7 # = 12.4 keV*Angstrom
        
        # DMM bilayer pitch in Angstroms, according to Rigaku metrology report
        self.dmm_dsp = 20.1 # Angstroms
        
        
        self.elements = []
        self.elements.append(ThreePoleWiggler())
        self.elements.append(BeamlineElement('test02', 10.0))
        self.elements.append(BeamlineElement('test01', 5.0))
        
        
        # Sort by position along the beam
        self.elements.sort(key=lambda o: o.zposition, reverse=False)
    
    
    # Monochromator
    ########################################
    
    def energy(self, verbosity=3):
        """
        Returns the current x-ray photon energy (in keV).
        """
        
        # Current angle of monochromator multilayer crystal
        Bragg_deg = caget(self.mono_bragg_pv)
        Bragg_rad = np.radians(Bragg_deg)
        
        wavelength_A = 2.*self.dmm_dsp*np.sin(Bragg_rad)
        wavelength_m = wavelength_A*1e-10

        energy_eV = self.hc_over_e/wavelength_m
        energy_keV = energy_eV/1000.
        
        if verbosity>=3:
            print('E = {:.2f} keV, wavelength = {:.4f} Å, Bragg = {:.6f} rad = {:.4f} deg'.format(energy_keV, wavelength_A, Bragg_rad, Bragg_deg))
            
        elif verbosity>=1:
            print('E = {:.3f} keV'.format(energy_keV))
        
        return energy_keV
        
        
    def wavelength(self, verbosity=3):
        """
        Returns the current x-ray photon wavelength (in Angstroms).
        """
        
        # Current angle of monochromator multilayer crystal
        Bragg_deg = caget(self.mono_bragg_pv)
        Bragg_rad = np.radians(Bragg_deg)
        
        wavelength_A = 2.*self.dmm_dsp*np.sin(Bragg_rad)
        wavelength_m = wavelength_A*1e-10

        # (planck constant * speed of light)/(electronic charge)
        
        energy_eV = self.hc_over_e/wavelength_m
        energy_keV = energy_eV/1000.
        
        if verbosity>=3:
            print('wavelength = {:.4f} Å, E = {:.2f} keV, Bragg = {:.6f} rad = {:.4f} deg'.format(wavelength_A, energy_keV, Bragg_rad, Bragg_deg))
            
        elif verbosity>=1:
            print('wavelength = {:.5f} Å'.format(wavelength_A))
        
        return wavelength_A
    
    
    def set_energy(self, energy_keV, verbosity=3):
        """
        Set the x-ray beam to the specified energy (by changing the
        monochromator angle.
        """
        
        energy_eV = energy_keV*1000.
        wavelength_m = self.hc_over_e/energy_eV
        wavelength_A = wavelength_m*1.e10
        
        self.set_wavelength(wavelength_A, verbosity=verbosity)
        
        return self.energy(verbosity=0)
    
    
    def set_wavelength(self, wavelength_A, verbosity=3):
        """
        Set the x-ray beam to the specified wavelength (by changing the
        monochromator angle.
        """
        
        Bragg_deg_initial = caget(self.mono_bragg_pv)
        
        wavelength_m = wavelength_A*1.e-10
        Bragg_rad = np.arcsin(wavelength_A/(2.*self.dmm_dsp))
        Bragg_deg = np.degrees(Bragg_rad)
        
        print('mono_bragg will move to {:.4f}g deg'.format(Bragg_deg))
        response = input('    Are you sure? (y/[n]) ')
        if response is 'y' or response is 'Y':
            
            mov(mono_bragg, Bragg_deg)
            
            if verbosity>=1:
                print('mono_bragg moved from {.4f} deg to {.4f} deg'.format(Bragg_deg_initial, Bragg_deg))
        
        elif verbosity>=1:
            print('No move was made.')
            
        return self.wavelength(verbosity=verbosity)
    
    
    # Attenuator/Filter Box
    ########################################

    def transmission(self, verbosity=3):
        """
        Returns the current beam transmission through the attenuator/filter box.
        """
        
        energy_keV = self.energy(verbosity=0)
        
        if energy_keV < 6.0 or energy_keV > 18.0:
            print('Transmission data not available at the current X-ray energy ({.2f} keV).'.format(energy_keV))
            
        else:
            
            # The states of the foils in the filter box
            N = [ caget('XF:11BMB-OP{{Fltr:{:d}}}Pos-Sts'.format(ifoil)) for ifoil in range(1, 8+1) ]
            
            tr_tot = self.calc_transmission_filters(N, verbosity=verbosity)
                    
            return tr_tot


    def calc_transmission_filters(self, filter_settings, energy_keV=None, verbosity=3):
        """
        Returns the computed transmission value for the given configuration of
        foils. Note that the foils are not actually moved. This is just a
        calculation.
        
        Parameters
        ----------
        filter_settings : array of length 8
            Each element must be either a zero (foil removed) or a 1 (foil blocking 
            beam)
        energy_keV : float
            If 'None', the current energy is used. If specified, the calculation 
            is performed for the requested energy.
            
        Returns
        -------
        transmission : float
            The computed transmission value of the x-ray beam through the filter box.
        """
        
        if energy_keV is None:
            energy_keV = self.energy(verbosity=0)
            
        if len(filter_settings) != 8:
            print('States for all eight foils must be specified.')

        else:
            N = filter_settings
            
            E = energy_keV
            E2 = np.square(E)
            E3 = np.power(E, 3)
                
            # foil thickness blocking the beam
            N_Al = N[0] + 2*N[1] + 4*N[2] + 8*N[3]
            N_Nb = N[4] + 2*N[5] + 4*N[6] + 8*N[7]

            d_Nb = 0.1      # Thickness [mm] of one Nb foil 
            d_Al = 0.25     # Thickness [mm] of one Al foil 

            # Absorption length [mm] based on fits to LBL CXRO data for 6 < E < 19 keV
            l_Nb = 1.4476e-3 - 5.6011e-4 * E + 1.0401e-4 * E2 + 8.7961e-6 * E3
            l_Al = 5.2293e-3 - 1.3491e-3 * E + 1.7833e-4 * E2 + 1.4001e-4 * E3

            # transmission factors
            tr_Nb = np.exp(-N_Nb*d_Nb/l_Nb)
            tr_Al = np.exp(-N_Al*d_Al/l_Al)
            tr_tot = tr_Nb*tr_Al
                
            if verbosity>=5:
                print('  state:      {} T = {:.6g}'.format(filter_settings, tr_tot))
            if verbosity>=4:
                print('{:d} × 0.25 mm Al ({:.4g}) and {:d} × 0.10 mm Nb ({:.4g})'.format(N_Al, tr_Al, N_Nb, tr_Nb) )
            if verbosity>=1:
                print('transmission = {:.6g}'.format(tr_tot))
                
            return tr_tot
            
        

    def set_attenuation_filters(self, filter_settings, verbosity=3):
        """
        Sets the positions (in/out) for each of the foils in the attenuator/
        filter box. The input 'filter_settings' should be an array of length
        8, where each element is either a zero (foil removed) or a 1 (foil
        blocking beam).
        """
        
        if verbosity>=4:
            print('Filters:')
            # The states of the foils in the filter box
            filters_initial = [ caget('XF:11BMB-OP{{Fltr:{:d}}}Pos-Sts'.format(ifoil)) for ifoil in range(1, 8+1) ]
            print('  initial:    {} T = {:.6g}'.format(filters_initial, self.calc_transmission_filters(filters_initial, verbosity=0)))
            print('  requested:  {} T = {:.6g}'.format(filter_settings, self.calc_transmission_filters(filter_settings, verbosity=0)))
        
        if len(filter_settings) != 8:
            print('States for all eight foils must be specified.')
            
        else:
            
            for i, state in enumerate(filter_settings):
                
                ifoil = i+1
                
                if state==1:
                    # Put foil #ifoil into the beam
                    caput( 'XF:11BMB-OP{{Fltr:{:d}}}Cmd:In-Cmd'.format(ifoil) , 1 )
                    
                elif state==0:
                    # Remove foil #ifoil
                    caput( 'XF:11BMB-OP{{Fltr:{:d}}}Cmd:Out-Cmd'.format(ifoil) , 1 )
                    
                else:
                    if verbosity>=3:
                        state_actual = caget( 'XF:11BMB-OP{{Fltr:{:d}}}Pos-Sts'.format(ifoil) )
                        state_actual_str = 'IN' if state_actual is 1 else 'OUT'
                        print('WARNING: Filter state {} not recognized. Filter {:d} is {:s}.'.format(state, ifoil, state_actual_str))
                    

        
            sleep(1.) # Wait for filter box to settle
            
        if verbosity>=4:
            filters_final = [ caget('XF:11BMB-OP{{Fltr:{:d}}}Pos-Sts'.format(ifoil)) for ifoil in range(1, 8+1) ]
            print('  final:      {} T = {:.6g}'.format(filters_final, self.calc_transmission_filters(filters_final, verbosity=0)))

        
    def set_transmission(self, transmission, verbosity=3):
        """
        Sets the transmission through the attenuator/filter box.
        Because the filter box has a discrete set of foils, it is impossible to
        exactly match a given transmission value. A nearby value will be
        selected.
        """
        
        energy_keV = self.energy(verbosity=0)
        
        if energy_keV < 6.0 or energy_keV > 18.0:
            print('Transmission data not available at the current X-ray energy ({.2f} keV).'.format(energy_keV))
            
        elif transmission > 1.0:
            print('A transmission above 1.0 is not possible.')
            
        elif transmission < 1e-10:
            print('A transmission this low ({:g}) cannot be reliably achieved.'.format(transmission))
            
        else:
            
            E = energy_keV
            E2 = np.square(E)
            E3 = np.power(E, 3)
            
            d_Nb = 0.1      # Thickness [mm] of one Nb foil 
            d_Al = 0.25     # Thickness [mm] of one Al foil 

            # Absorption length [mm] based on fits to LBL CXRO data for 6 < E < 19 keV
            l_Nb = 1.4476e-3 - 5.6011e-4 * E + 1.0401e-4 * E2 + 8.7961e-6 * E3
            l_Al = 5.2293e-3 - 1.3491e-3 * E + 1.7833e-4 * E2 + 1.4001e-4 * E3

            d_l_Nb = d_Nb/l_Nb
            d_l_Al = d_Al/l_Al

            # Number of foils to be inserted (equivalent to "XIA_attn.mac" from X9) 
            #N_Nb = int(-log(transmission)/d_l_Nb)
            ##N_Al = int((-log(transmission) - N_Nb*d_l_Nb)/(d_l_Al-0.5))
            #N_Al = int((-log(transmission) - N_Nb*d_l_Nb)/d_l_Al)

            # Number of foils to be inserted (picks a set that gives smallest deviation from requested transmission)
            dev = []
            for i in np.arange(16):
                for j in np.arange(16):
                    dev_ij = abs(transmission - exp(-i*d_l_Nb)*exp(-j*d_l_Al))
                    dev.append(dev_ij)
                    if (dev_ij == min(dev)):
                        N_Nb = i                    # number of Nb foils selected
                        N_Al = j                    # number of Al foils selected


            N = []
            state = N_Al
            for i in np.arange(4):
                N.append(state % 2)
                state = int(state/2)

            state = N_Nb
            for i in np.arange(4):
                N.append(state % 2)
                state = int(state/2)

            self.set_attenuation_filters(N, verbosity=verbosity)

        
        return self.transmission(verbosity=verbosity)


    def __set_transmission_alternative_deprecated(self, transmission, verbosity=3):
        """
        Sets the transmission through the attenuator/filter box.
        Because the filter box has a discrete set of foils, it is impossible to
        exactly match a given transmission value. A nearby value will be
        selected.
        """
        
        energy_keV = self.energy(verbosity=0)
        
        if energy_keV < 6.0 or energy_keV > 18.0:
            print('Transmission data not available at the current X-ray energy ({.2f} keV).'.format(energy_keV))
            
        elif transmission > 1.0:
            print('A transmission above 1.0 is not possible.')
            
        elif transmission < 1e-10:
            print('A transmission this low ({:g}) cannot be reliably achieved.'.format(transmission))
            
        else:
            
            num_foils = 8
            
            min_deviation=1e300
            best_N = []
            
            # Check every possible filter combination
            # (This takes 0.17s (instead of 0.003s for other method);
            # but either is small compared to the wait-time for the
            # pneumatics on the filter box.)
            for num in range(2**num_foils):
                N = [int(d) for d in bin(num)[2:].zfill(num_foils)] # Convert (binary) number to array of 0/1
                trans_N = self.calc_transmission_filters(N, verbosity=0)
                if verbosity>=5:
                    print('{} T = {:.6g}'.format(N, trans_N))
                    
                deviation = abs(transmission-trans_N)
                if deviation<min_deviation:
                    min_deviation = deviation
                    best_N = N
            
            # Set the filter box to the best combination
            self.set_attenuation_filters(best_N, verbosity=verbosity)
        
        return self.transmission(verbosity=verbosity)


    # Flux estimates at various points along the beam
    ########################################
    
    # TBD
    
    
    # Flux diagnostics
    ########################################
    
    def fluxes(self, verbosity=3):
        """
        Outputs a list of fluxes at various points along the beam. Also checks 
        the state (in or out of the beam) of various components, to help identify
        if anything could be blocking the beam.
        """
        
        if verbosity>=1:
            print('+--------+------------------+-----+-------------+-------------+-------------+')
            print('| pos    | name             |path | reading     | flux (ph/s) | expected    |')
            print('|--------|------------------|-----|-------------|-------------|-------------|')
            
        
        last_z = -100
        beam = True
        
        for element in self.elements:
            
            state = element.state()
            if state is 'block':
                beam = False
            
            if verbosity>=4:
                if element.zposition >= 0 and last_z < 0:
                    print('| Front End                 |     |             |             |             |')
                if element.zposition > 25 and last_z < 25:
                    print('| FOE                       |     |             |             |             |')
                if element.zposition > 50 and last_z < 50:
                    print('| Endstation                |     |             |             |             |')
            last_z = element.zposition
            
            if verbosity>=1:
                
                
                if state is 'in':
                    if beam:
                        path = '(|)'
                    else:
                        path = '(-)'
                elif state is 'out':
                    if beam:
                        path = ' | '
                    else:
                        path = '---'
                elif state is 'block':
                    path = '[X]'
                
                elif state is 'undefined':
                    if beam:
                        path = '?|?'
                    else:
                        path = '?-?'
                
                else:
                    path = '???'
                    
                
                flux_expected = 1.23456789e12 # TODO: Fix
                
                if callable(getattr(element, 'reading', None)):
                    reading_str = '{:11.3g}'.format(element.reading(verbosity=0))
                    flux_str = '{:11.3g}'.format(element.flux(verbosity=0))
                else:
                    reading_str = ''
                    flux_str = ''
                    
                flux_expected_str = ''
                
                print('|{:5.1f} m | {:16.16} | {:s} | {:11.11} | {:11.11} | {:11.11} |'.format(element.zposition, element.name, path, reading_str, flux_str, flux_expected_str))
                
                
        if verbosity>=1:
            print('+--------+------------------+-----+-------------+-------------+-------------+')

            
            


    # End class CMSBeam(object)
    ########################################
    




beam = CMSBeam()




# To test:
# cd /opt/ipython_profiles/profile_collection/startup
# ipython
#from ophyd import EpicsMotor, Device, Component as Cpt
#armx = EpicsMotor('XF:11BMB-ES{SM:1-Ax:X}Mtr', name='armx')
#armx.user_setpoint.set(-3)
#armx.user_readback.value


