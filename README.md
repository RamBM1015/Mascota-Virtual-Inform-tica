# Bit – Mascota Virtual de Informática

**Institución:** IPET 249 "Nicolás Copérnico"
**Especialidad:** Informática
**Asignatura:** Laboratorio de Aplicaciones II
**Año:** 2026
**Alumno:** _Ramiro Busto Molina_ – 6° G

<p align="center"><img src="assets/buho_bit.svg" width="600" alt="Bit, el búho programador"></p>

## Manual de uso
**Requisitos:** Python 3 y pygame.
```bash
pip install pygame
python main.py
```
**Controles**
| Tecla / acción | Efecto |
|---|---|
| `1` o botón *Café* | Sube la Energía (batería) |
| `2` o botón *Programar* | Bit programa unos segundos: sube el Ánimo y gasta Energía |
| `3` o botón *Limpiar bugs* | Sube la Salud y elimina bugs |
| Clic sobre un bug | Lo aplasta (minijuego) y sube la Salud |
| `M` | Silenciar / activar el sonido |
| `ESC` | Salir |

**Necesidades de la mascota** (bajan con el tiempo): Energía (carga de batería), Ánimo (nivel de código) y Salud (limpieza de bugs). Según sus valores, Bit cambia de expresión: feliz, triste, cansada, programando o con bugs.

## Sonidos
Los efectos están en `assets/sonidos/` (`cafe`, `programar`, `limpiar`, `bug` y `alerta`, en formato `.wav`). Se generaron con el script `generar_sonidos.py` (solo librería estándar de Python): `python generar_sonidos.py`. Para usar sonidos propios, reemplazá los archivos manteniendo los nombres. Si falta algún archivo o no hay audio, el juego funciona igual, sin ese sonido.

## Concepto de la mascota
Bit es un búho, símbolo de sabiduría y de quienes se quedan programando hasta tarde. Lleva anteojos redondos, auriculares gamer y una laptop con código, y viste un buzo con capucha con el símbolo `</>`. Su escenario es la sala de computación del colegio. Usa los colores del colegio (bordó, amarillo, rojo y blanco) y muestra el escudo del IPET 249. Representa a Informática porque sus necesidades son las de un programador: batería/energía, ánimo para escribir código y un sistema libre de bugs.

## Estructura del repositorio
```
main.py        # código del juego
assets/        # escudo.png, buho_bit.svg y sonidos/ (.wav)
generar_sonidos.py  # crea los efectos de sonido
GDD.md         # documento de diseño
IA_LOG.md      # ficha de transparencia de IA
README.md
```
