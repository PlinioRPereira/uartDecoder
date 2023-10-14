class MWC:
    def __init__(self, seed1, seed2):
        if isinstance(seed1, float):
            self.z = int(seed1 * (2 ** 32 - 1))
        else:
            self.z = seed1

        if isinstance(seed2, float):
            self.w = int(seed2 * (2 ** 32 - 1))
        else:
            self.w = seed2

    def random(self):
        self.z = 36969 * (self.z & 65535) + (self.z >> 16)
        self.w = 18000 * (self.w & 65535) + (self.w >> 16)
        return ((self.z << 16) + self.w) % (2 ** 32)

    def random_normalized(self):
        return self.random() / (2 ** 32 - 1.0)


# Uso
mwc_gen = MWC(seed1=12345, seed2=67890)

# Gera um número pseudoaleatório não normalizado (inteiro)
print(mwc_gen.random())

# Gera um número pseudoaleatório normalizado (float entre 0 e 1)
print(mwc_gen.random_normalized())
