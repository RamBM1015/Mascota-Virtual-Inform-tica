
import math
import os
import random
import struct
import wave

RATE = 22050
DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sonidos")


def silencio(dur):
    return [0.0] * int(RATE * dur)


def tono(freq, dur, vol=0.5, forma="seno"):
    n = int(RATE * dur)
    out = []
    for i in range(n):
        onda = math.sin(2 * math.pi * freq * i / RATE)
        if forma == "cuadrada":
            onda = 1.0 if onda >= 0 else -1.0
        ataque = min(1.0, i / (RATE * 0.005))
        caida = math.exp(-3.0 * i / n)
        out.append(onda * vol * ataque * caida)
    return out


def barrido(f0, f1, dur, vol=0.5):
    n = int(RATE * dur)
    out, fase = [], 0.0
    for i in range(n):
        f = f0 + (f1 - f0) * i / n
        fase += 2 * math.pi * f / RATE
        ataque = min(1.0, i / (RATE * 0.005))
        out.append(math.sin(fase) * vol * ataque * (1 - i / n))
    return out


def ruido(dur, vol=0.4):
    n = int(RATE * dur)
    return [random.uniform(-1, 1) * vol * math.exp(-6.0 * i / n) for i in range(n)]


def guardar(nombre, muestras):
    os.makedirs(DESTINO, exist_ok=True)
    ruta = os.path.join(DESTINO, nombre + ".wav")
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        datos = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, m)) * 32767)) for m in muestras)
        w.writeframes(datos)
    print(f"{ruta}  ({len(muestras) / RATE:.2f} s)")


def main():
    random.seed(249)

    # Café: dos "glup" ascendentes
    guardar("cafe", barrido(250, 520, 0.12) + silencio(0.05) + barrido(250, 560, 0.14))

    # Programar: ráfaga de teclas
    teclas = []
    for _ in range(9):
        teclas += ruido(0.025, 0.5) + tono(1800, 0.02, 0.2) + silencio(random.uniform(0.03, 0.08))
    guardar("programar", teclas)

    # Limpiar bugs: arpegio brillante
    guardar("limpiar", sum((tono(f, 0.09, 0.4) for f in (523, 659, 784, 1047)), []))

    # Aplastar bug: "splat"
    guardar("bug", ruido(0.06, 0.6) + barrido(420, 90, 0.14, 0.6))

    # Alerta: tres notas descendentes
    guardar("alerta", tono(440, 0.15, 0.3, "cuadrada") + tono(330, 0.15, 0.3, "cuadrada")
            + tono(220, 0.3, 0.3, "cuadrada"))


if __name__ == "__main__":
    main()
