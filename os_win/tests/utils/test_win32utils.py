# Copyright 2015 Cloudbase Solutions Srl
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
from oslotest import base

from os_win import exceptions
from os_win.utils import win32utils


class Win32UtilsTestCase(base.BaseTestCase):
    def setUp(self):
        super(Win32UtilsTestCase, self).setUp()
        self._setup_lib_mocks()

        self._win32_utils = win32utils.Win32Utils()

        self.addCleanup(mock.patch.stopall)

    def _setup_lib_mocks(self):
        self._ctypes = mock.Mock()
        # This is used in order to easily make assertions on the variables
        # passed by reference.
        self._ctypes.byref = lambda x: (x, "byref")

        mock.patch.multiple(win32utils,
                            ctypes=self._ctypes, kernel32=mock.DEFAULT,
                            wintypes=mock.DEFAULT, create=True).start()

    @mock.patch.object(win32utils.Win32Utils, 'get_error_message')
    @mock.patch.object(win32utils.Win32Utils, 'get_last_error')
    def _test_run_and_check_output(self, mock_get_last_err, mock_get_err_msg,
                                   ret_val=None, expected_exc=None,
                                   **kwargs):
        mock_func = mock.Mock()
        mock_func.return_value = ret_val

        if expected_exc:
            self.assertRaises(expected_exc,
                              self._win32_utils.run_and_check_output,
                              mock_func,
                              mock.sentinel.arg,
                              kwarg=mock.sentinel.kwarg,
                              **kwargs)
        else:
            actual_ret_val = self._win32_utils.run_and_check_output(
                mock_func,
                mock.sentinel.arg,
                kwarg=mock.sentinel.kwarg,
                **kwargs)
            self.assertEqual(ret_val, actual_ret_val)

        mock_func.assert_called_once_with(mock.sentinel.arg,
                                          kwarg=mock.sentinel.kwarg)

        return mock_get_last_err, mock_get_err_msg

    def test_run_and_check_output(self):
        self._test_run_and_check_output(ret_val=0)

    def test_run_and_check_output_fail_on_nonzero_ret_val(self):
        ret_val = 1

        (mock_get_last_err,
         mock_get_err_msg) = self._test_run_and_check_output(
            ret_val=ret_val,
            expected_exc=exceptions.VHDWin32APIException,
            failure_exc=exceptions.VHDWin32APIException)

        mock_get_err_msg.assert_called_once_with(ret_val)

    def test_run_and_check_output_explicit_error_ret_vals(self):
        ret_val = 1
        error_ret_vals = [ret_val]

        (mock_get_last_err,
         mock_get_err_msg) = self._test_run_and_check_output(
            ret_val=ret_val,
            error_ret_vals=error_ret_vals,
            ret_val_is_err_code=False,
            expected_exc=exceptions.Win32Exception)

        mock_get_err_msg.assert_called_once_with(
            mock_get_last_err.return_value)

    def test_run_and_check_output_ignored_error(self):
        ret_val = 1
        ignored_err_codes = [ret_val]

        self._test_run_and_check_output(ret_val=ret_val,
                                        ignored_error_codes=ignored_err_codes)

    def test_run_and_check_output_kernel32_lib_func(self):
        ret_val = 0
        self._test_run_and_check_output(ret_val=ret_val,
                                        expected_exc=exceptions.Win32Exception,
                                        kernel32_lib_func=True)

    def test_get_error_message(self):
        err_msg = self._win32_utils.get_error_message(mock.sentinel.err_code)

        fake_msg_buff = win32utils.ctypes.c_char_p.return_value

        expected_flags = (win32utils.FORMAT_MESSAGE_FROM_SYSTEM |
                          win32utils.FORMAT_MESSAGE_ALLOCATE_BUFFER |
                          win32utils.FORMAT_MESSAGE_IGNORE_INSERTS)

        win32utils.kernel32.FormatMessageA.assert_called_once_with(
            expected_flags, None, mock.sentinel.err_code, 0,
            win32utils.ctypes.byref(fake_msg_buff), 0, None)
        self.assertEqual(fake_msg_buff.value, err_msg)

    def test_get_last_error(self):
        last_err = self._win32_utils.get_last_error()

        self.assertEqual(win32utils.kernel32.GetLastError.return_value,
                         last_err)
        win32utils.kernel32.SetLastError.assert_called_once_with(0)

    def test_hresult_to_err_code(self):
        # This could differ based on the error source.
        # Only the last 2 bytes of the hresult the error code.
        fake_file_exists_hres = -0x7ff8ffb0
        file_exists_err_code = 0x50

        ret_val = self._win32_utils.hresult_to_err_code(fake_file_exists_hres)
        self.assertEqual(file_exists_err_code, ret_val)

    @mock.patch.object(win32utils.Win32Utils, 'hresult_to_err_code')
    def test_get_com_err_code(self, mock_hres_to_err_code):
        mock_excepinfo = [None] * 5 + [mock.sentinel.hres]
        mock_com_err = mock.Mock(excepinfo=mock_excepinfo)

        ret_val = self._win32_utils.get_com_err_code(mock_com_err)

        self.assertEqual(mock_hres_to_err_code.return_value, ret_val)
        mock_hres_to_err_code.assert_called_once_with(mock.sentinel.hres)

    def test_get_com_err_code_missing_excepinfo(self):
        ret_val = self._win32_utils.get_com_err_code(None)
        self.assertIsNone(ret_val)
