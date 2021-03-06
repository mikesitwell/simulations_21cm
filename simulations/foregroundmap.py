
import numpy as np
import scipy.linalg as la

import gaussianfield

from cosmoutils import nputil
from maps import *




class ForegroundMap(Sky3d):
    r"""Simulate foregrounds with a seperable angular and frequency
    covariance.

    Used to simulate foregrounds that can be modeled by angular
    covariances of the form:
    .. math:: C_l(\nu,\nu') = A_l B(\nu, \nu')
    """
    
    _weight_gen = False

    def angular_ps(self, l):
        r"""The angular function A_l. Must be a vectorized function
        taking either np.ndarrays or scalars.
        """
        pass


    def frequency_covariance(self, nu1, nu2):
        pass


    def angular_powerspectrum(self, l, nu1, nu2):
        return (self.angular_ps(l) * self.frequency_covariance(nu1, nu2))


    def generate_weight(self, regen = False):
        r"""Pregenerate the k weights array.

        Parameters
        ==========
        regen : boolean, optional
            If True, force regeneration of the weights, to be used if
            parameters have been changed,
        """
        
        if self._weight_gen and not regen:
            return
        
        f1, f2 = np.meshgrid(self.nu_pixels, self.nu_pixels)

        ch = self.frequency_covariance(f1, f2)

        self._freq_weight, self._num_corr_freq = nputil.matrix_root_manynull(ch)

        rf = gaussianfield.RandomFieldA2.like_map(self)

        ## Construct a lambda function to evalutate the array of
        ## k-vectors.
        rf.powerspectrum = lambda karray: self.angular_ps((karray**2).sum(axis=2)**0.5)

        self._ang_field = rf
        self._weight_gen = True


    def getfield(self):

        self.generate_weight()

        aff = np.fft.rfftn(self._ang_field.getfield())

        s2 = (self._num_corr_freq,) + aff.shape

        norm = np.tensordot(self._freq_weight, np.random.standard_normal(s2), axes = (1,0))

        return np.fft.irfft(np.fft.ifft(norm * aff[np.newaxis,:,:], axis = 1), axis=2)

        
        
        
        
