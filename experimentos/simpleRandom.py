import math

def pseudoRandom(seed):
    seed += 1
    x = math.sin(seed) * 10000
    return x - math.floor(x)

# Exemplo de uso
seed = 1
for _ in range(5):
    print(pseudoRandom(seed))
    seed += 1
