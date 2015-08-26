# -*- coding: utf-8 -*-
r"""
Test file for the `quat` module of the "dstauffman" library.  It is intented to contain test
cases to demonstrate functionaliy and correct outcomes for all the functions within the module.

Notes
-----
#.  Written by David C. Stauffer in March 2015.
"""

#%% Imports
from __future__ import print_function
from __future__ import division
import numpy as np
import unittest
import dstauffman as dcs

#%% _quat_assertions
class Test__quat_assertions(unittest.TestCase):
    def setUp(self):
        self.q1 = np.array([0, 0, 0, 1]) # zero quaternion
        self.q2 = np.array([0.5, 0.5, 0.5, 0.5]) # normal 1D quat
        self.q3 = np.array([0.5, -0.5, -0.5, 0.5]) # normal 1D quat with some negative components
        self.q4 = np.column_stack((self.q1, self.q2, self.q3)) # 2D array
        self.q5 = np.array([[0.5],[0.5],[0.5],[0.5]]) # 2D, single quat
        self.q6 = np.array([0, 0, 0, -1]) # zero quaternion with bad scalar
        self.q7 = np.array([-5, -5, 5, 5]) # quat with bad ranges
        self.q8 = np.array([0.5, 0.5j, 0.5, 0.5], dtype=np.complex128)
        self.q9 = np.array([0, 0, 1]) # only a 3 element vector
        self.q10 = np.array([0, 0, 0]) # only a 3 element vector, but with zero magnitude
        self.q11 = np.array([[[0.5],[0.5],[0.5],[0.5]]]) # valid, but 3D instead
        self.q12 = np.column_stack((self.q1, self.q6, self.q7)) # good and bad combined

    def test_nominal1(self):
        dcs.quat._quat_assertions(self.q1)

    def test_nominal2(self):
        dcs.quat._quat_assertions(self.q2)

    def test_nominal3(self):
        dcs.quat._quat_assertions(self.q3)

    def test_array1(self):
        dcs.quat._quat_assertions(self.q4)

    def test_array2(self):
        dcs.quat._quat_assertions(self.q5)

    def test_bad1(self):
        with self.assertRaises(AssertionError):
            dcs.quat._quat_assertions(self.q6)

    def test_bad2(self):
        with self.assertRaises(AssertionError):
            dcs.quat._quat_assertions(self.q7)

    def test_bad3(self):
        with self.assertRaises(AssertionError):
            dcs.quat._quat_assertions(self.q8)

    def test_bad4(self):
        with self.assertRaises(AssertionError):
            dcs.quat._quat_assertions(self.q9)

    def test_bad5(self):
        with self.assertRaises(AssertionError):
            dcs.quat._quat_assertions(self.q10)

    def test_bad6(self):
        with self.assertRaises(AssertionError):
            dcs.quat._quat_assertions(self.q11)

    def test_bad7(self):
        with self.assertRaises(AssertionError):
            dcs.quat._quat_assertions(self.q12)

#%% qrot
class Test_qrot(unittest.TestCase):
    r"""
    Tests the qrot function with the following cases:
        Single input case
        Single axis, multiple angles
        Multiple axes, single angle (Not working)
        Multiple axes, multiple angles (Not working)
    """
    def setUp(self):
        self.axis   = np.array([1, 2, 3])
        self.angle  = np.pi/2
        self.angle2 = np.pi/3
        r2o2        = np.sqrt(2)/2
        r3o2        = np.sqrt(3)/2
        self.quat   = np.array([[r2o2, 0, 0, r2o2], [0, r2o2, 0, r2o2], [0, 0, r2o2, r2o2]])
        self.quat2  = np.array([[ 0.5, 0, 0, r3o2], [0,  0.5, 0, r3o2], [0, 0,  0.5, r3o2]])
        self.null   = np.array([])
        self.null_quat = np.zeros((4, 0))

    def test_single_inputs(self):
        for i in range(len(self.axis)):
            quat = dcs.qrot(self.axis[i], self.angle)
            self.assertEqual(quat.ndim, 1)
            np.testing.assert_almost_equal(quat, self.quat[i, :])

    def test_single_axis(self):
        for i in range(len(self.axis)):
            quat = dcs.qrot(self.axis[i], np.array([self.angle, self.angle2]))
            self.assertEqual(quat.ndim, 2)
            np.testing.assert_almost_equal(quat, np.column_stack((self.quat[i, :], self.quat2[i, :])))

    def test_single_angle(self):
        quat = dcs.qrot(self.axis, self.angle)
        self.assertEqual(quat.ndim, 2)
        np.testing.assert_almost_equal(quat, self.quat.T)

    def test_all_vector_inputs(self):
        quat = dcs.qrot(self.axis, np.array([self.angle, self.angle, self.angle2]))
        np.testing.assert_almost_equal(quat, np.column_stack((self.quat[0,:], self.quat[1,:], self.quat2[2,:])))

    def test_null1(self):
        quat = dcs.qrot(self.axis[0], self.null)
        np.testing.assert_almost_equal(quat, self.null_quat)

    def test_null2(self):
        quat = dcs.qrot(self.null, self.angle)
        np.testing.assert_almost_equal(quat, self.null_quat)

    def test_vector_mismatch(self):
        with self.assertRaises(AssertionError):
            dcs.qrot(self.axis, np.array([self.angle, self.angle2]))

#%% quat_angle_diff
class test_quat_angle_diff(unittest.TestCase):
    r"""
    Tests the quat_angle_diff function with the following cases:
        TBD
    """
    def setUp(self):
        self.quat1 = np.array([0.5, 0.5, 0.5, 0.5])
        self.dq1   = dcs.qrot(1, 0.001)
        self.dq2   = dcs.qrot(2, 0.05)
        self.dqq1  = dcs.quat_mult(self.dq1, self.quat1)
        self.dqq2  = dcs.quat_mult(self.dq2, self.quat1)
        self.theta = np.array([0.001, 0.05])
        self.comp  = np.array([[0.001, 0], [0, 0.05], [0, 0]])

    def test_nominal1(self):
        (theta, comp) = dcs.quat_angle_diff(self.quat1, self.dqq1)
        np.testing.assert_almost_equal(theta, self.theta[0])
        np.testing.assert_almost_equal(comp, self.comp[:, 0])

    def test_nominal2(self):
        (theta, comp) = dcs.quat_angle_diff(self.quat1, self.dqq2)
        np.testing.assert_almost_equal(theta, self.theta[1])
        np.testing.assert_almost_equal(comp, self.comp[:, 1])

    def test_array1(self):
        (theta, comp) = dcs.quat_angle_diff(np.column_stack((self.dqq1, self.dqq2)), self.quat1)
        np.testing.assert_almost_equal(theta, self.theta)
        np.testing.assert_almost_equal(comp, -self.comp)

    def test_array2(self):
        (theta, comp) = dcs.quat_angle_diff(self.quat1, np.column_stack((self.dqq1, self.dqq2)))
        np.testing.assert_almost_equal(theta, self.theta)
        np.testing.assert_almost_equal(comp, self.comp)

    def test_array3(self):
        (theta, comp) = dcs.quat_angle_diff(np.column_stack((self.quat1, self.quat1, self.dqq1, self.dqq2)), \
            np.column_stack((self.dqq1, self.dqq2, self.quat1, self.quat1)))
        np.testing.assert_almost_equal(theta, self.theta[[0, 1, 0, 1]])
        np.testing.assert_almost_equal(comp, self.comp[:,[0, 1, 0, 1]] * np.array([1, 1, -1, -1]))

    def test_zero_diff1(self):
        (theta, comp) = dcs.quat_angle_diff(self.quat1, self.quat1)
        np.testing.assert_almost_equal(theta, 0)
        np.testing.assert_almost_equal(comp, 0)

    def test_zero_diff2(self):
        (theta, comp) = dcs.quat_angle_diff(self.quat1, np.column_stack((self.quat1, self.quat1)))
        np.testing.assert_almost_equal(theta, 0)
        np.testing.assert_almost_equal(comp, 0)

    def test_zero_diff3(self):
        (theta, comp) = dcs.quat_angle_diff(np.column_stack((self.quat1, self.quat1)), self.quat1)
        np.testing.assert_almost_equal(theta, 0)
        np.testing.assert_almost_equal(comp, 0)

    def test_zero_diff4(self):
        temp = np.column_stack((self.quat1, self.dq1, self.dq2, self.dqq1, self.dqq2))
        (theta, comp) = dcs.quat_angle_diff(temp, temp)
        np.testing.assert_almost_equal(theta, 0)
        np.testing.assert_almost_equal(comp, 0)

#%% quat_from_euler
class test_quat_from_euler(unittest.TestCase):
    r"""
    Tests the quat_from_euler function with the following cases:
        TBD
    """
    def setUp(self):
        self.a      = np.array([0.01, 0.02, 0.03])
        self.b      = np.array([0.04, 0.05, 0.06])
        self.angles = np.column_stack((self.a, self.b))
        self.seq    = np.array([3, 2, 1])
        self.quat   = np.array([\
            [0.01504849, 0.03047982],
            [0.00992359, 0.02438147],
            [0.00514916, 0.02073308],
            [0.99982426, 0.99902285]])

    def test_nominal(self):
        quat = dcs.quat_from_euler(self.angles, self.seq)
        np.testing.assert_almost_equal(quat, self.quat)

#%% quat_interp
class test_quat_interp(unittest.TestCase):
    r"""
    Tests the quat_interp function with the following cases:
        TBD
    """
    def setUp(self):
        self.time  = np.array([1, 3, 5])
        self.quat  = np.array([[0, 0, 0, 1], [0, 0, 0.19611951356252125, 0.98058], [0.5, -0.5, -0.5, 0.5]]).T
        self.ti    = np.array([1, 2, 4.5, 5])
        self.qout  = np.array([\
            [ 0., 0.        ,  0.41748421,  0.5 ],
            [ 0., 0.        , -0.41748421, -0.5 ],
            [ 0., 0.09853933, -0.35612271, -0.5 ],
            [ 1., 0.99513316,  0.72428619,  0.5 ]])

    def test_nominal(self):
        qout = dcs.quat_interp(self.time, self.quat, self.ti)
        np.testing.assert_almost_equal(qout, self.qout)

    def test_empty(self):
        q2 = dcs.quat_interp(self.time, self.quat, np.array([]))
        self.assertEqual(q2.size, 0)

    def test_scalar1(self):
        q2 = dcs.quat_interp(self.time, self.quat, self.ti[0])
        np.testing.assert_almost_equal(q2, np.expand_dims(self.qout[:,0],1))

#    def test_scalar2(self):
#        q2 = dcs.quat_interp(self.time, self.quat, self.ti[1])
#        np.testing.assert_almost_equal(q2, np.expand_dims(self.qout[:,1],1))

#%% quat_inv
class test_quat_inv(unittest.TestCase):
    r"""
    Tests the quat_inv function with the following cases:
        Single quat (x2 different quats)
        Quat array
        Null (x2 different null sizes)
    """
    def setUp(self):
        self.q1_inp = dcs.qrot(1, np.pi/2)
        self.q1_out = np.array([-np.sqrt(2)/2, 0, 0, np.sqrt(2)/2])
        self.q2_inp = dcs.qrot(2, np.pi/3)
        self.q2_out = np.array([0, -0.5, 0, np.sqrt(3)/2])
        self.q3_inp = np.column_stack((self.q1_inp, self.q2_inp))
        self.q3_out = np.column_stack((self.q1_out, self.q2_out))
        self.null   = np.array([])
        self.null_quat = np.ones((dcs.QUAT_SIZE, 0))

    def test_single_quat1(self):
        q1_inv = dcs.quat_inv(self.q1_inp)
        np.testing.assert_almost_equal(q1_inv, self.q1_out)
        self.assertEqual(q1_inv.ndim, 1)
        np.testing.assert_equal(q1_inv.shape, self.q1_out.shape)

    def test_single_quat2(self):
        q2_inv = dcs.quat_inv(self.q2_inp)
        np.testing.assert_almost_equal(q2_inv, self.q2_out)
        self.assertEqual(q2_inv.ndim, 1)
        np.testing.assert_equal(q2_inv.shape, self.q2_out.shape)

    def test_quat_array(self):
        q3_inv = dcs.quat_inv(self.q3_inp)
        np.testing.assert_almost_equal(q3_inv, self.q3_out)
        self.assertEqual(q3_inv.ndim, 2)
        np.testing.assert_equal(q3_inv.shape, self.q3_out.shape)

    def test_null_input1(self):
        null_inv = dcs.quat_inv(self.null_quat)
        np.testing.assert_equal(null_inv, self.null_quat)
        np.testing.assert_equal(null_inv.shape, self.null_quat.shape)

    def test_null_input2(self):
        null_inv = dcs.quat_inv(self.null)
        np.testing.assert_equal(null_inv, self.null)
        np.testing.assert_equal(null_inv.shape, self.null.shape)

#%% quat_mult
class test_quat_mult(unittest.TestCase):
    r"""
    Tests the quat_mult function with the following cases:
        Single quat (x2 different quats)
        Reverse order
        Quat array times scalar (x2 orders + x1 array-array)
        Null (x8 different null size and order permutations)
    """
    def setUp(self):
        self.q1 = dcs.qrot(1, np.pi/2)
        self.q2 = dcs.qrot(2, -np.pi)
        self.q3 = dcs.qrot(3, np.pi/3)
        self.q4 = np.array([ 0, -np.sqrt(2)/2, np.sqrt(2)/2, 0]) # q1*q2
        self.q5 = np.array([0.5, -np.sqrt(3)/2, 0, 0]) # q2*q3
        self.q6 = np.array([0.5, 0.5, 0.5, 0.5]) # q6 * q6 = q6**-1, and triggers negative scalar component
        self.q_array_in1 = np.column_stack((self.q1, self.q2))
        self.q_array_in2 = np.column_stack((self.q2, self.q3))
        self.q_array_out = np.column_stack((self.q4, self.q5))
        self.null        = np.array([])
        self.null_quat   = np.ones((dcs.QUAT_SIZE, 0))

    def test_nominal1(self):
        quat = dcs.quat_mult(self.q1, self.q2)
        self.assertEqual(quat.ndim, 1)
        np.testing.assert_almost_equal(quat, self.q4)
        np.testing.assert_equal(quat.shape, self.q4.shape)

    def test_nominal2(self):
        quat = dcs.quat_mult(self.q2, self.q3)
        self.assertEqual(quat.ndim, 1)
        np.testing.assert_almost_equal(quat, self.q5)
        np.testing.assert_equal(quat.shape, self.q5.shape)

    def test_nominal3(self):
        quat = dcs.quat_mult(self.q6, self.q6)
        self.assertEqual(quat.ndim, 1)
        np.testing.assert_almost_equal(quat, dcs.quat_inv(self.q6))
        np.testing.assert_equal(quat.shape, self.q6.shape)

    def test_reverse(self):
        quat1 = dcs.quat_mult(self.q2, self.q1)
        quat2 = dcs.quat_inv(dcs.quat_mult(dcs.quat_inv(self.q1), dcs.quat_inv(self.q2)))
        np.testing.assert_almost_equal(quat1, quat2)

    def test_array_scalar1(self):
        quat = dcs.quat_mult(self.q_array_in1, self.q2)
        self.assertEqual(quat.ndim, 2)
        np.testing.assert_almost_equal(quat[:,0], self.q4)
        np.testing.assert_equal(quat.shape, self.q_array_out.shape)

    def test_array_scalar2(self):
        quat = dcs.quat_mult(self.q1, self.q_array_in2)
        self.assertEqual(quat.ndim, 2)
        np.testing.assert_almost_equal(quat[:,0], self.q4)
        np.testing.assert_equal(quat.shape, self.q_array_out.shape)

    def test_array_scalar3(self):
        quat = dcs.quat_mult(self.q6, np.column_stack((self.q6, self.q6)))
        self.assertEqual(quat.ndim, 2)
        np.testing.assert_almost_equal(quat, np.column_stack((dcs.quat_inv(self.q6), dcs.quat_inv(self.q6))))
        np.testing.assert_equal(quat.shape, (4, 2))

    def test_array(self):
        quat = dcs.quat_mult(self.q_array_in1, self.q_array_in2)
        self.assertEqual(quat.ndim, 2)
        np.testing.assert_almost_equal(quat, self.q_array_out)
        np.testing.assert_equal(quat.shape, self.q_array_out.shape)

    def test_null_input1(self):
        quat = dcs.quat_mult(self.null_quat, self.q2)
        np.testing.assert_equal(quat, self.null_quat)
        np.testing.assert_equal(quat.shape, self.null_quat.shape)

    def test_null_input2(self):
        quat = dcs.quat_mult(self.null, self.q2)
        np.testing.assert_equal(quat, self.null)
        np.testing.assert_equal(quat.shape, self.null.shape)

    def test_null_input3(self):
        quat = dcs.quat_mult(self.q1, self.null_quat)
        np.testing.assert_equal(quat, self.null_quat)
        np.testing.assert_equal(quat.shape, self.null_quat.shape)

    def test_null_input4(self):
        quat = dcs.quat_mult(self.q2, self.null)
        np.testing.assert_equal(quat, self.null)
        np.testing.assert_equal(quat.shape, self.null.shape)

    def test_null_input5(self):
        quat = dcs.quat_mult(self.null_quat, self.null_quat)
        np.testing.assert_equal(quat, self.null_quat)
        np.testing.assert_equal(quat.shape, self.null_quat.shape)

    def test_null_input6(self):
        quat = dcs.quat_mult(self.null, self.null)
        np.testing.assert_equal(quat, self.null)
        np.testing.assert_equal(quat.shape, self.null.shape)

    def test_null_input7(self):
        quat = dcs.quat_mult(self.null_quat, self.null)
        np.testing.assert_equal(quat, self.null)
        np.testing.assert_equal(quat.shape, self.null.shape)

    def test_null_input8(self):
        quat = dcs.quat_mult(self.null, self.null_quat)
        np.testing.assert_equal(quat, self.null)
        np.testing.assert_equal(quat.shape, self.null.shape)

#%% quat_norm
class test_quat_norm(unittest.TestCase):
    r"""
    Tests the quat_norm function with the following cases:
        Single quat (x3 different quats)
        Quat array
        Null (x2 different null sizes)
    """
    def setUp(self):
        self.q1_inp = dcs.qrot(1, np.pi/2)
        self.q1_out = np.array([np.sqrt(2)/2, 0, 0, np.sqrt(2)/2])
        self.q2_inp = dcs.qrot(2, np.pi/3)
        self.q2_out = np.array([0, 0.5, 0, np.sqrt(3)/2])
        self.q3_inp = np.array([0.1, 0, 0, 1])
        self.q3_out = np.array([0.09950372, 0, 0, 0.99503719])
        self.q4_inp = np.column_stack((self.q1_inp, self.q2_inp, self.q3_inp))
        self.q4_out = np.column_stack((self.q1_out, self.q2_out, self.q3_out))
        self.null   = np.array([])
        self.null_quat = np.ones((dcs.QUAT_SIZE, 0))

    def test_nominal1(self):
        quat_norm = dcs.quat_norm(self.q1_inp)
        np.testing.assert_almost_equal(quat_norm, self.q1_out)
        self.assertEqual(quat_norm.ndim, 1)
        np.testing.assert_equal(quat_norm.shape, self.q1_out.shape)

    def test_nominal2(self):
        quat_norm = dcs.quat_norm(self.q2_inp)
        np.testing.assert_almost_equal(quat_norm, self.q2_out)
        self.assertEqual(quat_norm.ndim, 1)
        np.testing.assert_equal(quat_norm.shape, self.q2_out.shape)

    def test_nominal3(self):
        quat_norm = dcs.quat_norm(self.q3_inp)
        np.testing.assert_almost_equal(quat_norm, self.q3_out)
        self.assertEqual(quat_norm.ndim, 1)
        np.testing.assert_equal(quat_norm.shape, self.q3_out.shape)

    def test_array(self):
        quat_norm = dcs.quat_norm(self.q4_inp)
        np.testing.assert_almost_equal(quat_norm, self.q4_out)
        self.assertEqual(quat_norm.ndim, 2)
        np.testing.assert_equal(quat_norm.shape, self.q4_out.shape)

    def test_null_input1(self):
        quat_norm = dcs.quat_norm(self.null_quat)
        np.testing.assert_equal(quat_norm, self.null_quat)
        np.testing.assert_equal(quat_norm.shape, self.null_quat.shape)

    def test_null_input2(self):
        quat_norm = dcs.quat_norm(self.null)
        np.testing.assert_equal(quat_norm, self.null)
        np.testing.assert_equal(quat_norm.shape, self.null.shape)

#%% quat_prop
class test_quat_prop(unittest.TestCase):
    r"""
    Tests the quat_prop function with the following cases:
        TBD
    """
    def setUp(self):
        self.quat      = np.array([0, 0, 0, 1])
        self.delta_ang = np.array([0.01, 0.02, 0.03])
        self.quat_new  = np.array([0.00499913, 0.00999825, 0.01499738, 0.99982505])

    def test_nominal(self):
        quat_new = dcs.quat_prop(self.quat, self.delta_ang)
        np.testing.assert_almost_equal(quat_new, self.quat_new)

#%% quat_times_vector
class test_quat_times_vector(unittest.TestCase):
    r"""
    Tests the quat_times_vector function with the following cases:
        TBD
    """
    def setUp(self):
        self.quat = np.array([[0, 1, 0, 0], [1, 0, 0, 0]]).T
        self.v = np.array([[1, 0, 0], [2, 0, 0]]).T
        self.vec = np.array([[-1, 2], [0, 0], [0, 0]])

    def test_nominal(self):
        vec = dcs.quat_times_vector(self.quat, self.v)
        np.testing.assert_almost_equal(vec, self.vec)

#%% quat_to_dcm
class test_quat_to_dcm(unittest.TestCase):
    r"""
    Tests the quat_to_dcm function with the following cases:
        TBD
    """
    def setUp(self):
        self.quat = np.array([0.5, -0.5, 0.5, 0.5])
        self.dcm  = np.array([\
            [ 0.,  0.,  1.],
            [-1.,  0.,  0.],
            [ 0., -1.,  0.]])

    def test_nominal(self):
        dcm = dcs.quat_to_dcm(self.quat)
        np.testing.assert_almost_equal(dcm, self.dcm)

#%% quat_to_euler
class test_quat_to_euler(unittest.TestCase):
    r"""
    Tests the quat_to_euler function with the following cases:
        TBD
    """
    def setUp(self):
        self.quat  = np.array([[0, 1, 0, 0], [0, 0, 1, 0]]).T
        self.seq   = [3, 1, 2]
        self.euler = np.array([\
            [-0.        , -3.14159265],
            [ 0.        ,  0.        ],
            [ 3.14159265, -0.        ]])

    def test_nominal(self):
        euler = dcs.quat_to_euler(self.quat, self.seq)
        np.testing.assert_almost_equal(euler, self.euler)

#%% Unit test execution
if __name__ == '__main__':
    unittest.main(exit=False)
