import unittest
import os
import sys

from mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from peachyprinter.api.configuration_api import ConfigurationAPI
from peachyprinter.domain.configuration_manager import ConfigurationManager
from peachyprinter.infrastructure.zaxis import SerialDripZAxis
from peachyprinter.infrastructure.communicator import SerialCommunicator
import test_helpers


class DripperSetupMixInTest(object):

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    def test_start_counting_drips_should_start_getting_drips(self, mock_SerialCommunicator,  mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('printer')

        configuration_API.start_counting_drips()

        mock_SerialCommunicator.return_value.start.assert_called_with()

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    def test_start_counting_drips_should_start_getting_drips_for_microcontroller(self, mock_SerialCommunicator, mock_SerialDripZaxis, mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.dripper.dripper_type ='microcontroller'
        mock_load.return_value = config
        configuration_API.load_printer('printer')
        callback = MagicMock()
        configuration_API.start_counting_drips(callback)

        mock_SerialCommunicator.assert_called_with(config.micro_com.port,config.micro_com.header,config.micro_com.footer,config.micro_com.escape)
        mock_SerialCommunicator.return_value.start.assert_called_with()
        mock_SerialDripZaxis.assert_called_with(mock_SerialCommunicator.return_value, 1, 0, drip_call_back=callback)

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(SerialDripZAxis, 'start')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.NullCommander')
    def test_start_counting_drips_should_pass_call_back_function(self, mock_NullCommander, mock_SerialDripZAxis, mock_SerialCommunicator, mock_start, mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('printer')

        def callback(bla):
            pass

        configuration_API.start_counting_drips(drip_call_back=callback)

        mock_SerialDripZAxis.assert_called_with(
            mock_SerialCommunicator.return_value,
            1,
            0.0,
            drip_call_back=callback
            )

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    def test_stop_counting_drips_should_stop_getting_drips_for_micro(self, mock_SerialCommunicator, mock_SerialDripZaxis, mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.dripper.dripper_type ='microcontroller'
        mock_load.return_value = config
        configuration_API.load_printer('printer')
        callback = MagicMock()
        configuration_API.start_counting_drips(callback)

        configuration_API.stop_counting_drips()

        mock_SerialCommunicator.return_value.close.assert_called_with()

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(SerialDripZAxis, 'start')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    @patch.object(SerialDripZAxis, 'close')
    def test_stop_counting_drips_should_stop_getting_drips(self, mock_close, mock_SerialCommunicator, mock_start, mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('printer')
        configuration_API.start_counting_drips()

        configuration_API.stop_counting_drips()

        mock_close.assert_called_with()

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'load')
    @patch.object(SerialDripZAxis, 'start')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    @patch.object(SerialDripZAxis, 'reset')
    def test_drip_calibration_should_call_reset_when_reset_requested(self, mock_reset, mock_SerialCommunicator, mock_start, mock_load, mock_save):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('printer')

        configuration_API.start_counting_drips()
        configuration_API.reset_drips()

        mock_reset.assert_called_with()

    @patch.object(ConfigurationManager, 'load')
    def test_get_drips_per_mm_should_return_current_setting(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config

        configuration_API.load_printer('Printer')

        actual = configuration_API.get_drips_per_mm()

        self.assertEquals(self.default_config.dripper.drips_per_mm, actual)

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    def test_set_drips_per_mm_should_overwrite_current_setting_and_update_zaxis(self, mock_SerialCommunicator, mock_SerialDripZAxis, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        mock_SerialDripZAxis = mock_SerialDripZAxis.return_value
        expected = 6534.0

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        configuration_API.set_drips_per_mm(expected)
        configuration_API.stop_counting_drips()

        mock_SerialDripZAxis.set_drips_per_mm.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_dripper_type_should_return_current_type(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('Printer')

        actual = configuration_API.get_dripper_type()

        self.assertEquals(self.default_config.dripper.dripper_type, actual)

    @patch.object(ConfigurationManager, 'load')
    def test_set_dripper_type_should_return_current_type(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('Printer')
        expected = 'emulated'
        configuration_API.set_dripper_type(expected)
        actual = configuration_API.get_dripper_type()

        self.assertEquals(expected, actual)

    @patch.object(ConfigurationManager, 'load')
    def test_get_dripper_delay_should_return_current_delay(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('Printer')

        actual = configuration_API.get_photo_zaxis_delay()

        self.assertEquals(self.default_config.dripper.photo_zaxis_delay, actual)

    @patch.object(ConfigurationManager, 'load')
    def test_set_dripper_delay_should_set_current_delay(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('Printer')
        expected = 2.0
        configuration_API.set_photo_zaxis_delay(expected)
        actual = configuration_API.get_photo_zaxis_delay()

        self.assertEquals(expected, actual)

    @patch.object(ConfigurationManager, 'load')
    def test_get_emulated_drips_per_second_should_return(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('Printer')

        actual = configuration_API.get_emulated_drips_per_second()

        self.assertEquals(self.default_config.dripper.emulated_drips_per_second, actual)

    @patch.object(ConfigurationManager, 'load')
    def test_set_emulated_drips_per_second_should_return(self, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        mock_load.return_value = self.default_config
        configuration_API.load_printer('Printer')
        expected = 302.0
        configuration_API.set_emulated_drips_per_second(expected)
        actual = configuration_API.get_emulated_drips_per_second() 

        self.assertEquals(expected, actual)

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.infrastructure.commander.SerialCommander')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    def test_send_dripper_on_command_should_raise_exceptions_if_serial_not_configured(self, mock_SerialCommunicator, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = False
        mock_load.return_value = config

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        with self.assertRaises(Exception):
            configuration_API.send_dripper_on_command()

        self.assertEquals(0, mock_SerialCommander.call_count)

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialCommander')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    def test_send_dripper_on_command_should(self, mock_SerialCommunicator, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = True
        config.serial.port = "COM1"
        config.serial.on_command = "1"
        mock_load.return_value = config
        mock_serial_commander = mock_SerialCommander.return_value

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        configuration_API.send_dripper_on_command()

        mock_SerialCommander.assert_called_with("COM1")
        mock_serial_commander.send_command.assert_called_with("1")

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.infrastructure.commander.SerialCommander')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    def test_send_dripper_off_command_should_raise_exceptions_if_serial_not_configured(self, mock_SerialCommunicator, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = False
        mock_load.return_value = config

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        with self.assertRaises(Exception):
            configuration_API.send_dripper_off_command()

        self.assertEquals(0, mock_SerialCommander.call_count)

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialCommander')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    def test_send_dripper_off_command_should(self, mock_SerialCommunicator, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = True
        config.serial.port = "COM1"
        config.serial.off_command = "0"
        mock_load.return_value = config
        mock_serial_commander = mock_SerialCommander.return_value

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        configuration_API.send_dripper_off_command()

        mock_SerialCommander.assert_called_with("COM1")
        mock_serial_commander.send_command.assert_called_with("0")

    @patch.object(ConfigurationManager, 'load')
    @patch('peachyprinter.api.configuration_api.SerialCommander')
    @patch('peachyprinter.api.configuration_api.SerialDripZAxis')
    @patch('peachyprinter.api.configuration_api.SerialCommunicator')
    def test_stop_counting_drips_should_stop_serial(self, mock_SerialCommunicator, mock_Zaxis, mock_SerialCommander, mock_load):
        configuration_API = ConfigurationAPI(ConfigurationManager())
        config = self.default_config
        config.serial.on = True
        config.serial.port = "COM1"
        config.serial.off_command = "0"
        mock_load.return_value = config
        mock_serial_commander = mock_SerialCommander.return_value

        configuration_API.load_printer('Printer')
        configuration_API.start_counting_drips()
        configuration_API.stop_counting_drips()

        mock_SerialCommander.assert_called_with("COM1")
        mock_serial_commander.close.assert_called_with()


class CureTestSetupMixInTest(object):

    @patch.object(ConfigurationManager, 'load')
    def test_get_cure_test_total_height_must_exceed_base_height(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(10, 1, 1, 2)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 1, 1, 2)

    @patch.object(ConfigurationManager, 'load')
    def test_get_cure_test_final_speed_exceeds_start_speed(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 1)

        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 1, 1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_cure_test_values_must_be_positive_non_0_numbers_for_all_but_base(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_cure_test('a', 10, 10, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 'a', 10, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 'a', 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 'a')
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 1, 'a')
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(-1, 10, 10, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, -10, 10, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, -1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, -1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 1, -1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 0, 10, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 0, 1)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 0)
        with self.assertRaises(Exception):
            configuration_API.get_cure_test(1, 10, 10, 1, 0)

    @patch.object(ConfigurationManager, 'load')
    def test_get_cure_test_returns_a_layer_generator(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        cure_test = configuration_API.get_cure_test(0, 1, 1, 2)
        cure_test.next()

    @patch.object(ConfigurationManager, 'load')
    def test_get_speed_at_height_must_exceed_base_height(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(10, 1, 1, 2, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 1, 1, 2, 1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_speed_at_height_must_have_height_between_total_and_base(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(0, 10, 1, 2, 11)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(2, 10, 1, 2, 0)

    @patch.object(ConfigurationManager, 'load')
    def test_get_speed_at_height_final_speed_exceeds_start_speed(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 1, 1)

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 1, 1, 1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_speed_at_height_values_must_be_positive_non_0_numbers_for_all_but_base(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height('a', 10, 10, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 'a', 10, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 'a', 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 'a', 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 1, 'a', 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(-1, 10, 10, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, -10, 10, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, -1, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, -1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 1, -1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 0, 10, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 0, 1, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 0, 1)
        with self.assertRaises(Exception):
            configuration_API.get_speed_at_height(1, 10, 10, 1, 0, 1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_speed_at_height_returns_a_correct_height(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        speed = configuration_API.get_speed_at_height(0, 1, 10, 20, 0.5)
        self.assertEquals(15, speed)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_speed_should_throw_exception_if_less_then_or_0(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        expected_config = self.default_config
        expected_config.cure_rate.draw_speed = 121.0
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.set_speed(-1)
        with self.assertRaises(Exception):
            configuration_API.set_speed(0)

    @patch.object(ConfigurationManager, 'load')
    def test_get_layer_settings(self, mock_load):
        config = self.default_config
        config.options.use_shufflelayers = True
        config.options.use_sublayers = True
        config.options.use_overlap = True

        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertTrue(configuration_API.get_use_shufflelayers())
        self.assertTrue(configuration_API.get_use_sublayers())
        self.assertTrue(configuration_API.get_use_overlap())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_layer_settings(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        expected = self.default_config
        expected.options.use_shufflelayers = False
        expected.options.use_sublayers = False
        expected.options.use_overlap = False

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_use_shufflelayers(False)
        configuration_API.set_use_sublayers(False)
        configuration_API.set_use_overlap(False)

        self.assertConfigurationEqual(expected, mock_save.mock_calls[0][1][0])

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_get_and_set_cure_test_details(self, mock_save, mock_load):
        expected_base_height = 3.0
        expected_total_height = 33.0
        expected_start_speed = 10.0
        expected_finish_speed = 100.0
        expected_draw_speed = 75.0
        expected_use_draw_speed = False
        expected_override_laser_power = True
        expected_override_laser_power_amount = 0.05

        expected_config = self.default_config

        expected_config.cure_rate.base_height = expected_base_height
        expected_config.cure_rate.total_height = expected_total_height
        expected_config.cure_rate.start_speed = expected_start_speed
        expected_config.cure_rate.finish_speed = expected_finish_speed
        expected_config.cure_rate.draw_speed = expected_draw_speed
        expected_config.cure_rate.use_draw_speed = expected_use_draw_speed
        expected_config.cure_rate.override_laser_power = expected_override_laser_power
        expected_config.cure_rate.override_laser_power_amount = expected_override_laser_power_amount

        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_cure_rate_base_height(expected_base_height)
        configuration_API.set_cure_rate_total_height(expected_total_height)
        configuration_API.set_cure_rate_start_speed(expected_start_speed)
        configuration_API.set_cure_rate_finish_speed(expected_finish_speed)
        configuration_API.set_cure_rate_draw_speed(expected_draw_speed)
        configuration_API.set_cure_rate_use_draw_speed(expected_use_draw_speed)
        configuration_API.set_override_laser_power(expected_override_laser_power)
        configuration_API.set_override_laser_power_amount(expected_override_laser_power_amount)

        configuration_API.save()

        self.assertConfigurationEqual(expected_config, mock_save.mock_calls[0][1][0])

        self.assertEquals(expected_base_height,                     configuration_API.get_cure_rate_base_height())
        self.assertEquals(expected_total_height,                    configuration_API.get_cure_rate_total_height())
        self.assertEquals(expected_start_speed,                     configuration_API.get_cure_rate_start_speed())
        self.assertEquals(expected_finish_speed,                    configuration_API.get_cure_rate_finish_speed())
        self.assertEquals(expected_draw_speed,                      configuration_API.get_cure_rate_draw_speed())
        self.assertEquals(expected_use_draw_speed,                  configuration_API.get_cure_rate_use_draw_speed())
        self.assertEquals(expected_override_laser_power,            configuration_API.get_override_laser_power())
        self.assertEquals(expected_override_laser_power_amount,     configuration_API.get_override_laser_power_amount())

    @patch.object(ConfigurationManager, 'load')
    def test_get_and_set_laser_amount_fails_if_out_of_range(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.set_override_laser_power_amount(-0.1)
        with self.assertRaises(Exception):
            configuration_API.set_override_laser_power_amount(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_override_laser_power_amount(1.1)

        configuration_API.set_override_laser_power_amount(0.0)
        # configuration_API.set_override_laser_power_amount(0.5)
        # configuration_API.set_override_laser_power_amount(1.0)
        #TODO FIX THIS AGAIN

class GeneralSetupMixInTest(object):

    @patch.object(ConfigurationManager, 'load')
    def test_get_write_wav_files_folder_returns_write_wav_files_folder(self, mock_load):
        expected = "temp"
        config = self.default_config
        config.options.write_wav_files_folder = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_write_wav_files_folder())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_write_wav_files_sets_write_wav_files(self, mock_save, mock_load):
        expected_write_wave_files = True
        config = self.default_config
        expected = config
        expected.options.write_wav_files = expected_write_wave_files
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_write_wav_files(expected_write_wave_files)

        self.assertEquals(expected_write_wave_files, configuration_API.get_write_wav_files())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_write_wav_files_returns_write_wav_files(self, mock_load):
        expected = True
        config = self.default_config
        config.options.write_wav_files = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_write_wav_files())

    @patch.object(ConfigurationManager, 'load')
    def test_get_wait_after_move_milliseconds_returns_wait_after_move_milliseconds(self, mock_load):
        expected = 7
        config = self.default_config
        config.options.wait_after_move_milliseconds = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_wait_after_move_milliseconds())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_wait_after_move_milliseconds_sets_wait_after_move_milliseconds(self, mock_save, mock_load):
        expected_milliseconds = 7
        config = self.default_config
        expected = config
        expected.options.wait_after_move_milliseconds = expected_milliseconds
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_wait_after_move_milliseconds(expected_milliseconds)

        self.assertEquals(expected_milliseconds, configuration_API.get_wait_after_move_milliseconds())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_pre_layer_delay_returns_delay(self, mock_load):
        expected = 7.0
        config = self.default_config
        config.options.pre_layer_delay = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_pre_layer_delay())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_pre_layer_delay_sets_pre_layer_delay(self, mock_save, mock_load):
        expected_scale = 7.0
        config = self.default_config
        expected = config
        expected.options.pre_layer_delay = expected_scale
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_pre_layer_delay(expected_scale)

        self.assertEquals(expected_scale, configuration_API.get_pre_layer_delay())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_max_lead_distance_mm_returns_max_lead_distance(self, mock_load):
        expected = 0.4
        config = self.default_config
        config.dripper.max_lead_distance_mm = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_max_lead_distance_mm())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_max_lead_distance_mm_sets_max_lead_distance_mm(self, mock_save, mock_load):
        expected = 0.4
        expected_config = self.default_config
        expected_config.dripper.max_lead_distance_mm = expected
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_max_lead_distance_mm(expected)

        self.assertEquals(expected, configuration_API.get_max_lead_distance_mm())
        self.assertConfigurationEqual(expected_config, mock_save.mock_calls[0][1][0])

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_max_lead_distance_mm_sets_max_lead_distance_mm_when_0(self, mock_save, mock_load):
        expected = 0.0
        expected_config = self.default_config
        expected_config.dripper.max_lead_distance_mm = expected
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_max_lead_distance_mm(expected)

        self.assertEquals(expected, configuration_API.get_max_lead_distance_mm())
        self.assertConfigurationEqual(expected_config, mock_save.mock_calls[0][1][0])

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_max_lead_distance_mm_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value = {'name': 'test'}
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.set_max_lead_distance_mm('a')
        with self.assertRaises(Exception):
            configuration_API.set_max_lead_distance_mm(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_max_lead_distance_mm({'a': 'b'})
        with self.assertRaises(Exception):
            configuration_API.set_max_lead_distance_mm(0)
        with self.assertRaises(Exception):
            configuration_API.set_max_lead_distance_mm(1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_laser_thickness_mm_returns_thickness(self, mock_load):
        expected = 7.0
        config = self.default_config
        config.options.laser_thickness_mm = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_laser_thickness_mm())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_laser_thickness_mm_sets_thickness(self, mock_save, mock_load):
        expected_thickness = 7.0
        config = self.default_config
        expected = config
        expected.options.laser_thickness_mm = expected_thickness
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_laser_thickness_mm(expected_thickness)

        self.assertEquals(expected_thickness, configuration_API.get_laser_thickness_mm())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_laser_thickness_mm_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value = {'name': 'test'}
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.set_laser_thickness_mm('a')
        with self.assertRaises(Exception):
            configuration_API.set_laser_thickness_mm(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_laser_thickness_mm({'a': 'b'})
        with self.assertRaises(Exception):
            configuration_API.set_laser_thickness_mm(0)
        with self.assertRaises(Exception):
            configuration_API.set_laser_thickness_mm(1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_scaling_factor_returns_thickness(self, mock_load):
        expected = 7.0
        config = self.default_config
        config.options.scaling_factor = expected
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_scaling_factor())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_scaling_factor_sets_scaling_factor(self, mock_save, mock_load):
        expected_scale = 7.0
        config = self.default_config
        expected = config
        expected.options.scaling_factor = expected_scale
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_scaling_factor(expected_scale)

        self.assertEquals(expected_scale, configuration_API.get_scaling_factor())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_scaling_factor_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value = {'name': 'test'}
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.set_scaling_factor('a')
        with self.assertRaises(Exception):
            configuration_API.set_scaling_factor(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_scaling_factor({'a': 'b'})
        with self.assertRaises(Exception):
            configuration_API.set_scaling_factor(0)
        with self.assertRaises(Exception):
            configuration_API.set_scaling_factor(1)

    @patch.object(ConfigurationManager, 'load')
    def test_sublayer_height_mm_returns_theight(self, mock_load):
        expected = 7.0
        expected_config = self.default_config
        expected_config.options.sublayer_height_mm = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_sublayer_height_mm())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_sublayer_height_mm_returns_height(self, mock_save, mock_load):
        expected_height = 7.0
        config = self.default_config
        expected = config
        expected.options.sublayer_height_mm = expected_height
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_sublayer_height_mm(expected_height)

        self.assertEquals(expected_height, configuration_API.get_sublayer_height_mm())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_sublayer_height_mm_should_go_boom_if_not_positive_float(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        with self.assertRaises(Exception):
            configuration_API.set_sublayer_height_mm('a')
        with self.assertRaises(Exception):
            configuration_API.set_sublayer_height_mm(-1.0)
        with self.assertRaises(Exception):
            configuration_API.set_sublayer_height_mm({'a': 'b'})
        with self.assertRaises(Exception):
            configuration_API.set_sublayer_height_mm(0)
        with self.assertRaises(Exception):
            configuration_API.set_sublayer_height_mm(1)

    @patch.object(ConfigurationManager, 'load')
    def test_get_slew_delay_returns_the_amount(self, mock_load):
        expected = 3
        expected_config = self.default_config
        expected_config.options.slew_delay = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_slew_delay())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_slew_delay_returns_amount(self, mock_save, mock_load):
        slew_delay = 7
        config = self.default_config
        expected = config
        expected.options.slew_delay = slew_delay
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_slew_delay(slew_delay)

        self.assertEquals(slew_delay, configuration_API.get_slew_delay())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_post_fire_delay_returns_the_amount(self, mock_load):
        expected = 3
        expected_config = self.default_config
        expected_config.options.post_fire_delay = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_post_fire_delay())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_post_fire_delay_returns_amount(self, mock_save, mock_load):
        post_fire_delay = 7
        config = self.default_config
        expected = config
        expected.options.post_fire_delay = post_fire_delay
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_post_fire_delay(post_fire_delay)

        self.assertEquals(post_fire_delay, configuration_API.get_post_fire_delay())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_shuffle_amount_returns_the_amount(self, mock_load):
        expected = 0.1
        expected_config = self.default_config
        expected_config.options.shuffle_layers_amount = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_shuffle_layers_amount())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_shuffle_layers_amount_returns_amount(self, mock_save, mock_load):
        shuffle_layers_amount = 7.0
        config = self.default_config
        expected = config
        expected.options.shuffle_layers_amount = shuffle_layers_amount
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_shuffle_layers_amount(shuffle_layers_amount)

        self.assertEquals(shuffle_layers_amount, configuration_API.get_shuffle_layers_amount())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_overlap_amount_mm_returns_the_overlap(self, mock_load):
        expected = 7.0
        expected_config = self.default_config
        expected_config.options.overlap_amount = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_overlap_amount_mm())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_overlap_amount_mm_returns_height(self, mock_save, mock_load):
        overlap_amount = 7.0
        config = self.default_config
        expected = config
        expected.options.overlap_amount = overlap_amount
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_overlap_amount_mm(overlap_amount)

        self.assertEquals(overlap_amount, configuration_API.get_overlap_amount_mm())
        mock_save.assert_called_with(expected)

    @patch.object(ConfigurationManager, 'load')
    def test_get_print_queue_delay_returns_the_delay(self, mock_load):
        expected = 7.0
        expected_config = self.default_config
        expected_config.options.print_queue_delay = expected
        mock_load.return_value = expected_config

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        self.assertEquals(expected, configuration_API.get_print_queue_delay())

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_print_queue_delay_returns_delay(self, mock_save, mock_load):
        print_queue_delay = 7.0
        config = self.default_config
        expected = config
        expected.options.print_queue_delay = print_queue_delay
        mock_load.return_value = config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_print_queue_delay(print_queue_delay)

        self.assertEquals(print_queue_delay, configuration_API.get_print_queue_delay())
        mock_save.assert_called_with(expected)


class EmailSetupMixInTest(object):

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_get_and_set_email_details(self, mock_save, mock_load):
        expected_on = True
        expected_port = 33
        expected_host = "some.host"
        expected_sender = "sender@email.com"
        expected_recipient = "recipient@email.com"
        expected_username = "sender"
        expected_password = "pa55word"

        expected_config = self.default_config

        expected_config.email.on = expected_on
        expected_config.email.port = expected_port
        expected_config.email.host = expected_host
        expected_config.email.sender = expected_sender
        expected_config.email.recipient = expected_recipient
        expected_config.email.username = expected_username
        expected_config.email.password = expected_password

        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_email_on(expected_on)
        configuration_API.set_email_port(expected_port)
        configuration_API.set_email_host(expected_host)
        configuration_API.set_email_sender(expected_sender)
        configuration_API.set_email_recipient(expected_recipient)
        configuration_API.set_email_username(expected_username)
        configuration_API.set_email_password(expected_password)

        configuration_API.save()

        self.assertConfigurationEqual(expected_config, mock_save.mock_calls[0][1][0])

        self.assertEquals(expected_on, configuration_API.get_email_on())
        self.assertEquals(expected_port, configuration_API.get_email_port())
        self.assertEquals(expected_host, configuration_API.get_email_host())
        self.assertEquals(expected_sender, configuration_API.get_email_sender())
        self.assertEquals(expected_recipient, configuration_API.get_email_recipient())
        self.assertEquals(expected_username, configuration_API.get_email_username())
        self.assertEquals(expected_password, configuration_API.get_email_password())


class AdvancedSetupMixInTest(object):

    @patch.object(ConfigurationManager, 'load')
    def test_get_serial_options_loads_correctly(self, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        actual_enabled = configuration_API.get_serial_enabled()
        actual_port = configuration_API.get_serial_port()
        actual_on = configuration_API.get_serial_on_command()
        actual_off = configuration_API.get_serial_off_command()
        actual_layer_start = configuration_API.get_layer_started_command()
        actual_layer_ended = configuration_API.get_layer_ended_command()

        self.assertEquals(self.default_config.serial.on, actual_enabled)
        self.assertEquals(self.default_config.serial.port, actual_port)
        self.assertEquals(self.default_config.serial.on_command, actual_on)
        self.assertEquals(self.default_config.serial.off_command, actual_off)
        self.assertEquals(self.default_config.serial.layer_started, actual_layer_start)
        self.assertEquals(self.default_config.serial.layer_ended, actual_layer_ended)

    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_serial_options_loads_correctly(self, mock_save, mock_load):
        expected_enabled = True
        expected_port = 'com54'
        expected_on = 'GOGOGO'
        expected_off = 'STOPSTOP'
        expected_layer_start = 'S'
        expected_layer_end = 'E'
        expected_print_end = 'Z'

        mock_load.return_value = self.default_config
        expected = self.default_config
        expected.serial.on                = expected_enabled
        expected.serial.port              = expected_port
        expected.serial.on_command        = expected_on
        expected.serial.off_command       = expected_off
        expected.serial.layer_started     = expected_layer_start
        expected.serial.layer_ended       = expected_layer_end
        expected.serial.print_ended       = expected_print_end

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_serial_enabled(expected_enabled)
        configuration_API.set_serial_port(expected_port)
        configuration_API.set_serial_on_command(expected_on)
        configuration_API.set_serial_off_command(expected_off)
        configuration_API.set_layer_started_command(expected_layer_start)
        configuration_API.set_layer_ended_command(expected_layer_end)
        configuration_API.set_print_ended_command(expected_print_end)

        self.assertEquals(expected_enabled, configuration_API.get_serial_enabled())
        self.assertEquals(expected_port, configuration_API.get_serial_port())
        self.assertEquals(expected_on, configuration_API.get_serial_on_command())
        self.assertEquals(expected_off, configuration_API.get_serial_off_command())
        self.assertEquals(expected_layer_start, configuration_API.get_layer_started_command())
        self.assertEquals(expected_layer_end, configuration_API.get_layer_ended_command())
        self.assertEquals(expected_print_end, configuration_API.get_print_ended_command())

        self.assertConfigurationEqual(expected, mock_save.mock_calls[0][1][0])


class CircutSetupMixInTest(object):
    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_circut_type_raises_exception_in_wrong_type(self, mock_save, mock_load):
        mock_load.return_value = self.default_config
        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")
        with self.assertRaises(Exception):
            configuration_API.set_circut_type('Booya')
        configuration_API.set_circut_type('Analog')
        configuration_API.set_circut_type('Digital')


    @patch.object(ConfigurationManager, 'load')
    @patch.object(ConfigurationManager, 'save')
    def test_set_circut_sets_and_gets(self, mock_save, mock_load):
        expected_port          = 'COM55'
        expected_rate          = 8458
        expected_header        = '@'
        expected_footer        = 'A'
        expected_escape        = 'B'
        expected_circut_type   = 'Digital'
        expected_version       = 'r96986'

        mock_load.return_value = self.default_config
        expected = self.default_config
        expected.micro_com.port       = expected_port
        expected.micro_com.rate       = expected_rate
        expected.micro_com.header     = expected_header
        expected.micro_com.footer     = expected_footer
        expected.micro_com.escape     = expected_escape
        expected.circut.circut_type   = expected_circut_type
        expected.circut.version       = expected_version

        configuration_API = ConfigurationAPI(ConfigurationManager())
        configuration_API.load_printer("test")

        configuration_API.set_micro_com_port(expected_port)
        configuration_API.set_micro_com_rate(expected_rate)
        configuration_API.set_micro_com_header(expected_header)
        configuration_API.set_micro_com_footer(expected_footer)
        configuration_API.set_micro_com_escape(expected_escape)
        configuration_API.set_circut_type(expected_circut_type)
        configuration_API.set_circut_version(expected_version)

        self.assertEquals(expected_port,        configuration_API.get_micro_com_port())
        self.assertEquals(expected_rate,        configuration_API.get_micro_com_rate())
        self.assertEquals(expected_header,      configuration_API.get_micro_com_header())
        self.assertEquals(expected_footer,      configuration_API.get_micro_com_footer())
        self.assertEquals(expected_escape,      configuration_API.get_micro_com_escape())
        self.assertEquals(expected_circut_type, configuration_API.get_circut_type())
        self.assertEquals(expected_version,     configuration_API.get_circut_version())


class ConfigurationAPITest(
        unittest.TestCase,
        test_helpers.TestHelpers,
        DripperSetupMixInTest,
        CureTestSetupMixInTest,
        GeneralSetupMixInTest,
        EmailSetupMixInTest,
        AdvancedSetupMixInTest,
        CircutSetupMixInTest,
        ):

    @patch.object(ConfigurationManager, 'new')
    @patch.object(ConfigurationManager, 'save')
    def test_add_printer_should_save_itself(self, mock_save, mock_new):
        capi = ConfigurationAPI(ConfigurationManager())
        mock_new.return_value = "Some Printer Config"

        capi.add_printer("NewName")

        mock_new.assert_called_with("NewName")
        mock_save.assert_called_with("Some Printer Config")

    @patch.object(ConfigurationManager, 'list')
    def test_get_available_printers_lists_printers(self, mock_list):
        printers = ['Tom', 'Dick', 'Harry']
        capi = ConfigurationAPI(ConfigurationManager())
        mock_list.return_value = printers

        actual = capi.get_available_printers()

        mock_list.assert_called_with()
        self.assertEqual(printers, actual)

    def test_current_printer_returns_none_when_no_printer_loaded(self):
        capi = ConfigurationAPI(ConfigurationManager())

        actual = capi.current_printer()

        self.assertEqual(None, actual)

    @patch.object(ConfigurationManager, 'save')
    @patch.object(ConfigurationManager, 'new')
    def test_current_printer_returns_printer_name(self, mock_new, mock_save):
        capi = ConfigurationAPI(ConfigurationManager())
        name = "Spam"
        config = self.default_config
        config.name = name
        mock_new.return_value = config
        capi.add_printer('Spam')

        actual = capi.current_printer()

        self.assertEqual('Spam', actual)

    @patch.object(ConfigurationManager, 'load')
    def test_load_printer_calls_load(self, mock_load):
        printer_name = 'MegaPrint'
        mock_load.return_value = {'name': printer_name}
        capi = ConfigurationAPI(ConfigurationManager())

        capi.load_printer(printer_name)

        mock_load.assert_called_with(printer_name)



if __name__ == '__main__':
    unittest.main()