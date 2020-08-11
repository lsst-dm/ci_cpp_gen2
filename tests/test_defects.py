# This file is part of ci_cpp_gen2.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os
import numpy as np
import unittest

import lsst.afw.math as afwMath
import lsst.daf.persistence as dafPersist
import lsst.ip.isr as ipIsr
import lsst.utils.tests

from lsst.utils import getPackageDir


# TODO: DM-26396
#       Update these tests to validate calibration construction.
class DefectTestCases(lsst.utils.tests.TestCase):

    def setUpClass(self):
        """Setup butler and generate an ISR processed exposure.

        Notes
        -----
        DMTN-101 3.1:

        Divide each resulting master frame by its median.
        """
        repoDir = os.path.join(getPackageDir('ci_cpp_gen2'), "DATA")
        calibDir = os.path.join(getPackageDir('ci_cpp_gen2'), "DATA", "calibs")
        butler = dafPersist.Butler(repoDir, calibRoot=calibDir)

        self.config = ipIsr.IsrTaskConfig()
        self.config.doSaturation = True
        self.config.doSuspect = True
        self.config.doSetBadRegions = True
        self.config.doOverscan = True
        self.config.doBias = True
        self.config.doVariance = True
        self.config.doDark = True
        self.config.doFlat = True
        self.config.doDefect = True

        self.config.doLinearize = False
        self.config.doCrosstalk = False
        self.config.doWidenSaturationTrails = False
        self.config.doBrighterFatter = False
        self.config.doSaturationInterpolation = False
        self.config.doStrayLight = False
        self.config.doApplyGains = False
        self.config.doFringe = False
        self.config.doMeasureBackground = False
        self.config.doVignette = False
        self.config.doAttachTransmissionCurve = False
        self.config.doUseOpticsTransmission = False
        self.config.doUseFilterTransmission = False
        self.config.doUseSensorTransmission = False
        self.config.doUseAtmosphereTransmission = False

        self.isrTask = ipIsr.IsrTask(config=self.config)
        # This is not an independent frame.
        self.dataRef = butler.dataRef('raw', dataId={'detector': 0, 'expId': 2020012800028})
        results = self.isrTask.runDataRef(self.dataRef)
        self.exposure = results.outputExposure

    def test_masterFrameLevel(self):
        """Test image Mean

        Notes
        -----
        DMTN-101 3.2

        For each master frame, confirm that the median level is 1.0 to
        within statistical noise (after masking known defects)

        """
        mean = afwMath.makeStatistics(self.exposure.getImage(), afwMath.MEAN).getValue()
        median = afwMath.makeStatistics(self.exposure.getImage(), afwMath.MEDIAN).getValue()
        sigma = afwMath.makeStatistics(self.exposure.getImage(), afwMath.STDEV).getValue()

        self.assertLess(np.abs(mean/median - 1.0), sigma, msg=f"Test 3.2: {mean} {sigma}")


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
