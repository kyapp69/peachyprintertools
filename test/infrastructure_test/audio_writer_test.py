import unittest
import sys
import os
import pyaudio
from mock import patch
import numpy

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

import test_helpers
from infrastructure.audio_writer import AudioWriter


class AudioWriterTests(unittest.TestCase, test_helpers.TestHelpers):

    @patch('pyaudio.PyAudio')
    def test_should_terminate_when_close_is_called(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        
        audio_writer = AudioWriter(48000,16)
        audio_writer.close()
        mock_py_audio.is_format_supported.return_value = True
        mock_py_audio.terminate.assert_called_with()

    @patch('pyaudio.PyAudio')
    def test_should_open_a_stream_with_correct_data(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_rate = 16
        expected_format = pyaudio.paInt16
        expected_channels = 2
        expected_rate = 48000
        expected_frames_per_buffer = expected_rate / 8
        expected_output = True

        audio_writer = AudioWriter(sampling_frequency,bit_rate)
        mock_py_audio.is_format_supported.return_value = True
        mock_py_audio.open.assert_called_with(format=expected_format,
                                                channels=expected_channels,
                                                rate=expected_rate,
                                                output=expected_output,
                                                frames_per_buffer=expected_frames_per_buffer )


    @patch('pyaudio.PyAudio')
    def test_verifies_support_for_stream_settings(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_rate = 16
        sample_device_info = {
            'index': 0L, 'name': u'ALSA', 
            'defaultOutputDevice': 12L, 'type': 8L, 
            'deviceCount': 13L, 'defaultInputDevice': 12L, 
            'structVersion': 1L
        }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = True

        audio_writer = AudioWriter(sampling_frequency,bit_rate)

        expected_format = pyaudio.paInt16
        expected_channels = 2
        expected_rate = 48000
        expected_frames_per_buffer = expected_rate / 8
        expected_output = True
        mock_py_audio.is_format_supported.assert_called_with(sampling_frequency,output_device=12,output_channels=2,output_format=pyaudio.paInt16)

    @patch('pyaudio.PyAudio')
    def test_should_throw_exception_for_unpossible_bit_rate(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_rate = 7

        with self.assertRaises(Exception):
            audio_writer = AudioWriter(sampling_frequency,bit_rate)

    @patch('pyaudio.PyAudio')
    def test_should_throw_exception_when_settings_unsupported(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_rate = 16
        sample_device_info = {
            'index': 0L, 'name': u'ALSA', 
            'defaultOutputDevice': 12L, 'type': 8L, 
            'deviceCount': 13L, 'defaultInputDevice': 12L, 
            'structVersion': 1L
        }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = False

        with self.assertRaises(Exception):
            audio_writer = AudioWriter(sampling_frequency,bit_rate)


    @patch('pyaudio.PyAudio')
    def test_stream_should_be_started(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_rate = 16
        sample_device_info = { 'defaultInputDevice': 12L, }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = True
        mock_outstream = mock_py_audio.open.return_value

        audio_writer = AudioWriter(sampling_frequency,bit_rate)

        mock_outstream.start_stream.assert_called_with()

    @patch('pyaudio.PyAudio')
    def test_stream_should_be_stopped_when_writer_stopped(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_rate = 16
        sample_device_info = { 'defaultInputDevice': 12L, }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = True
        mock_outstream = mock_py_audio.open.return_value
        
        audio_writer = AudioWriter(sampling_frequency,bit_rate)
        audio_writer.close()

        mock_outstream.stop_stream.assert_called_with()

    @patch('pyaudio.PyAudio')
    def test_write_chunk_should_write_correct_frame_values(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_rate = 16
        sample_device_info = { 'defaultInputDevice': 12L, }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = True
        mock_outstream = mock_py_audio.open.return_value
        mock_outstream.get_write_available.return_value = 2048
        
        audio_writer = AudioWriter(sampling_frequency,bit_rate)
        audio_writer.write_chunk(numpy.array([[1,1],[0,0],[-1,-1],[0.5,0.5]]))

        expected_frames = numpy.array([[32767,32767],[0,0],[-32767,-32767],[16384,16384]]).astype(numpy.dtype('<i2'))
        mock_outstream.write.assert_called_with(expected_frames.tostring())

    @patch('pyaudio.PyAudio')
    def test_write_chunk_should_not_over_flow_the_buffer(self, mock_PyAudio):
        mock_py_audio = mock_PyAudio.return_value
        sampling_frequency = 48000
        bit_rate = 16
        sample_device_info = { 'defaultInputDevice': 12L, }

        mock_py_audio.get_default_host_api_info.return_value = sample_device_info
        mock_py_audio.is_format_supported.return_value = True
        mock_outstream = mock_py_audio.open.return_value
        write_available_results = [10, 1024]
        def get_write_available_results():
            return write_available_results.pop(0)

        mock_outstream.get_write_available.side_effect = get_write_available_results

        audio_writer = AudioWriter(sampling_frequency,bit_rate)
        audio_writer.write_chunk(numpy.array([[1,1],[0,0],[-1,-1],[0.5,0.5]]))

        expected_frames = numpy.array([[32767,32767],[0,0],[-32767,-32767],[16384,16384]]).astype(numpy.dtype('<i2')).tostring()
        expected_frames_1, expected_frames_2 = expected_frames[:9], expected_frames[9:]

        self.assertEquals(2, mock_outstream.write.call_count)
        self.assertEquals(expected_frames_1, mock_outstream.write.call_args_list[0][0][0])
        self.assertEquals(expected_frames_2, mock_outstream.write.call_args_list[1][0][0])

if __name__ == '__main__':
    unittest.main()