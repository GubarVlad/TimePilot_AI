import unittest
from pathlib import Path


FRONTEND = Path(__file__).resolve().parents[1] / "frontend" / "index.html"


class FrontendVoiceCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = FRONTEND.read_text(encoding="utf-8")

    def test_voice_capture_uses_media_recorder(self):
        self.assertIn("new MediaRecorder(stream", self.html)
        self.assertIn("recorder.start(250)", self.html)

    def test_legacy_script_processor_capture_is_not_used(self):
        self.assertNotIn("createScriptProcessor(", self.html)

    def test_recording_is_decoded_and_converted_to_pcm_wav(self):
        self.assertIn("context.decodeAudioData(encoded.slice(0))", self.html)
        self.assertIn("encodePcmWav(pcm,16000)", self.html)
        self.assertIn("audio/wav", self.html)

    def test_enter_while_recording_stops_and_sends_to_agent(self):
        self.assertGreaterEqual(self.html.count("stopVoiceRecording({sendToAgent:true})"), 2)
        self.assertIn("await sendAgentMessage(transcript)", self.html)

    def test_russian_speech_status_is_visible(self):
        self.assertTrue("Recording… speak now" in self.html or "Запись по-русски" in self.html)
        self.assertTrue("Transcribing speech via NVIDIA Riva" in self.html or "Распознаю русскую речь через NVIDIA" in self.html)

    def test_permission_and_missing_audio_have_helpful_errors(self):
        self.assertTrue("microphone access" in self.html.lower() or "разреши доступ к микрофону" in self.html)
        self.assertTrue("audio signal" in self.html.lower() or "почти нулевой сигнал" in self.html)

    def test_quiet_speech_is_normalized_instead_of_rejected_by_high_rms_gate(self):
        self.assertIn("const gain=Math.min(80,0.78/peak)", self.html)
        self.assertIn("if(peak<0.000002)", self.html)
        self.assertNotIn("if(rms<0.00035)", self.html)

    def test_enter_while_microphone_button_focused_is_handled_in_capture_phase(self):
        self.assertIn("stopPropagation();stopVoiceRecording({sendToAgent:true})", self.html)
        self.assertRegex(self.html, r"addEventListener\('keydown',[\s\S]{0,220},true\)")


if __name__ == "__main__":
    unittest.main()
