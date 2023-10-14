import numpy as np
import scipy.signal as sps
import sounddevice as sd


class FonemeGenerator:
    def __init__(self):
        self.Fs = 44100  # taxa de amostragem

    def _generate_glottal_wave(self, f0: float, duration: float) -> np.ndarray:
        t = np.linspace(0, duration, int(self.Fs * duration))
        return np.sin(2 * np.pi * f0 * t)

    def _apply_filter(self, signal: np.ndarray, low_cutoff: float, high_cutoff: float) -> np.ndarray:
        b, a = sps.butter(4, [low_cutoff / (self.Fs / 2), high_cutoff / (self.Fs / 2)], btype='band')
        return sps.lfilter(b, a, signal)

    def generate_foneme(self, f0: float, duration: float, low_cutoff: float, high_cutoff: float) -> np.ndarray:
        glottal_wave = self._generate_glottal_wave(f0, duration)
        return self._apply_filter(glottal_wave, low_cutoff, high_cutoff)

    def generate_pause(self, duration: float) -> np.ndarray:
        return np.zeros(int(self.Fs * duration))

    def play_fonemes(self, fonemes: list):
        audio = np.concatenate(fonemes)
        sd.play(audio, self.Fs)
        sd.wait()

    def peak_to_foneme(self, peak_amplitude: float) -> np.ndarray:
        low_cutoff = 100 + peak_amplitude * 10
        high_cutoff = 500 + peak_amplitude * 20
        return self.generate_foneme(100, 0.2, low_cutoff, high_cutoff)


# Exemplo de uso
if __name__ == "__main__":
    generator = FonemeGenerator()

    # Fonemas simulados para cada sílaba. Valores de cutoff são arbitrários
    O = generator.generate_foneme(100, 0.1, 100, 700)
    la = generator.generate_foneme(100, 0.1, 200, 800)

    tu = generator.generate_foneme(100, 0.1, 200, 800)
    do = generator.generate_foneme(100, 0.1, 100, 700)

    be = generator.generate_foneme(100, 0.1, 300, 900)
    m = generator.generate_foneme(100, 0.1, 100, 600)

    # Pausas para simular espaço e vírgula
    comma_pause = generator.generate_pause(0.2)
    space_pause = generator.generate_pause(0.1)

    # Frase: "Olá, tudo bem?"
    frase = [O, la, comma_pause, tu, space_pause, do, space_pause, be, m]

    generator.play_fonemes(frase)
