
"""
Mascota Virtual de Informática - IPET 249 "Nicolás Copérnico"
Laboratorio de Aplicaciones II - 2026

Personaje base: "Bit", un búho programador.
Todo el dibujo de la mascota se hace con formas de pygame (no necesita imágenes)
"""

import math
import os
import random
import sys

import pygame

# --------------------------------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------------------------------
ANCHO, ALTO = 800, 600
FPS = 60

# Paleta institucional
BORDO = (110, 16, 38)
BORDO_OSCURO = (70, 8, 24)
AMARILLO = (255, 204, 0)
ROJO = (214, 40, 40)
BLANCO = (255, 255, 255)
NEGRO = (25, 25, 25)
GRIS = (90, 90, 100)
VERDE_CODIGO = (80, 255, 120)

# Colores de la mascota
PELO = (139, 94, 60)
PELO_OSCURO = (94, 60, 36)
CREMA = (243, 227, 195)
NARANJA = (244, 163, 0)

# Desgaste (puntos por segundo)
DESGASTE_ENERGIA = 1.6
DESGASTE_ANIMO = 2.0
DESGASTE_SALUD = 0.8

# Efecto de cada acción
CAFE_ENERGIA = 25
PROGRAMAR_DURACION = 4.0   # segundos que dura la animación "programando"
PROGRAMAR_ANIMO = 7.0      # puntos de ánimo por segundo mientras programa
PROGRAMAR_ENERGIA = 3.0    # puntos de energía que consume por segundo
LIMPIAR_SALUD = 15
BUG_CLICK_SALUD = 8

DIR = os.path.dirname(os.path.abspath(__file__))


def limitar(valor, minimo=0.0, maximo=100.0):
    return max(minimo, min(maximo, valor))


# --------------------------------------------------------------------------
# LÓGICA DE LA MASCOTA
# --------------------------------------------------------------------------
class Mascota:
    def __init__(self):
        self.energia = 80.0   # Carga de batería
        self.animo = 80.0     # Nivel de código / ánimo
        self.salud = 80.0     # Limpieza de bugs
        self.t_programando = 0.0
        self.bugs = []        # lista de dicts {x, y, vx, vy}
        self.tiempo_bug = 0.0
        self.eventos = []     # nombres de sonidos pendientes de reproducir

    @property
    def estado(self):
        if self.energia <= 20:
            return "cansada"
        if self.t_programando > 0:
            return "programando"
        if self.salud < 35:
            return "bugs"
        if self.animo < 35:
            return "triste"
        return "feliz"

    # --- acciones del jugador ---
    def tomar_cafe(self):
        self.energia = limitar(self.energia + CAFE_ENERGIA)
        self.animo = limitar(self.animo + 3)
        self.eventos.append("cafe")

    def programar(self):
        if self.energia > 10:
            self.t_programando = PROGRAMAR_DURACION
            self.eventos.append("programar")

    def limpiar_bugs(self):
        self.salud = limitar(self.salud + LIMPIAR_SALUD)
        # elimina hasta 2 bugs en pantalla
        del self.bugs[:2]
        self.eventos.append("limpiar")

    def aplastar_bug(self, pos):
        """Minijuego: clic sobre un bug lo elimina. Devuelve True si acertó."""
        for bug in self.bugs:
            if math.hypot(bug["x"] - pos[0], bug["y"] - pos[1]) < 22:
                self.bugs.remove(bug)
                self.salud = limitar(self.salud + BUG_CLICK_SALUD)
                self.eventos.append("bug")
                return True
        return False

    # --- actualización por frame ---
    def actualizar(self, dt, zona):
        """dt en segundos. zona = pygame.Rect donde pueden caminar los bugs."""
        self.energia = limitar(self.energia - DESGASTE_ENERGIA * dt)
        self.animo = limitar(self.animo - DESGASTE_ANIMO * dt)
        # más bugs en pantalla => la salud baja más rápido
        self.salud = limitar(self.salud - (DESGASTE_SALUD + 0.4 * len(self.bugs)) * dt)

        if self.t_programando > 0:
            self.t_programando = max(0.0, self.t_programando - dt)
            self.animo = limitar(self.animo + PROGRAMAR_ANIMO * dt)
            self.energia = limitar(self.energia - PROGRAMAR_ENERGIA * dt)
            if self.energia <= 5:
                self.t_programando = 0.0

        # aparición de bugs cuando la salud es baja
        self.tiempo_bug += dt
        if self.salud < 60 and len(self.bugs) < 8 and self.tiempo_bug > 2.0:
            self.tiempo_bug = 0.0
            self.bugs.append({
                "x": random.randint(zona.left + 20, zona.right - 20),
                "y": random.randint(zona.top + 20, zona.bottom - 20),
                "vx": random.choice([-1, 1]) * random.uniform(30, 80),
                "vy": random.choice([-1, 1]) * random.uniform(30, 80),
            })

        for bug in self.bugs:
            bug["x"] += bug["vx"] * dt
            bug["y"] += bug["vy"] * dt
            if bug["x"] < zona.left + 10 or bug["x"] > zona.right - 10:
                bug["vx"] *= -1
            if bug["y"] < zona.top + 10 or bug["y"] > zona.bottom - 10:
                bug["vy"] *= -1


# --------------------------------------------------------------------------
# INTERFAZ: BOTONES
# --------------------------------------------------------------------------
class Boton:
    def __init__(self, rect, texto, tecla, accion):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.tecla = tecla
        self.accion = accion

    def dibujar(self, pantalla, fuente, mouse):
        color = AMARILLO if self.rect.collidepoint(mouse) else BLANCO
        pygame.draw.rect(pantalla, color, self.rect, border_radius=12)
        pygame.draw.rect(pantalla, ROJO, self.rect, 3, border_radius=12)
        img = fuente.render(self.texto, True, BORDO_OSCURO)
        pantalla.blit(img, img.get_rect(center=self.rect.center))


# --------------------------------------------------------------------------
# DIBUJO
# --------------------------------------------------------------------------
def cargar_escudo():
    ruta = os.path.join(DIR, "assets", "escudo.png")
    if os.path.exists(ruta):
        try:
            img = pygame.image.load(ruta).convert_alpha()
            return pygame.transform.smoothscale(img, (90, 90))
        except pygame.error:
            pass
    # Escudo de reemplazo (si falta assets/escudo.png)
    surf = pygame.Surface((90, 90), pygame.SRCALPHA)
    pts = [(5, 5), (85, 5), (85, 50), (45, 88), (5, 50)]
    pygame.draw.polygon(surf, AMARILLO, pts)
    pygame.draw.polygon(surf, ROJO, pts, 4)
    fuente = pygame.font.SysFont("arial", 28, bold=True)
    txt = fuente.render("249", True, BORDO)
    surf.blit(txt, txt.get_rect(center=(45, 42)))
    return surf


def dibujar_barra(pantalla, fuente, x, y, valor, color, etiqueta):
    ancho, alto = 220, 22
    pygame.draw.rect(pantalla, BORDO_OSCURO, (x, y, ancho, alto), border_radius=8)
    relleno = int(ancho * valor / 100)
    c = ROJO if valor < 25 else color
    if relleno > 0:
        pygame.draw.rect(pantalla, c, (x, y, relleno, alto), border_radius=8)
    pygame.draw.rect(pantalla, BLANCO, (x, y, ancho, alto), 2, border_radius=8)
    txt = fuente.render(f"{etiqueta}  {int(valor)}%", True, BLANCO)
    pantalla.blit(txt, (x, y - 22))


def dibujar_bug(pantalla, x, y):
    x, y = int(x), int(y)
    pygame.draw.ellipse(pantalla, ROJO, (x - 12, y - 9, 24, 18))
    pygame.draw.circle(pantalla, NEGRO, (x + 12, y), 6)
    for dx in (-8, 0, 8):
        pygame.draw.line(pantalla, NEGRO, (x + dx, y - 9), (x + dx - 3, y - 15), 2)
        pygame.draw.line(pantalla, NEGRO, (x + dx, y + 9), (x + dx - 3, y + 15), 2)
    pygame.draw.circle(pantalla, BLANCO, (x - 3, y - 2), 2)


def cargar_sonidos():
    """Carga los .wav de assets/sonidos/. Si falta alguno (o no hay placa de audio),
    el juego sigue funcionando sin ese sonido."""
    sonidos = {}
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except pygame.error:
        return sonidos
    for nombre in ("cafe", "programar", "limpiar", "bug", "alerta"):
        ruta = os.path.join(DIR, "assets", "sonidos", nombre + ".wav")
        if os.path.exists(ruta):
            try:
                sonidos[nombre] = pygame.mixer.Sound(ruta)
                sonidos[nombre].set_volume(0.6)
            except pygame.error:
                pass
    return sonidos


def dibujar_sala(pantalla, fuente, r):
    """Fondo del escenario: sala de computación del IPET 249."""
    # pared
    pygame.draw.rect(pantalla, (246, 241, 231), r, border_radius=18)
    # zócalo bordó y piso
    pygame.draw.rect(pantalla, BORDO, (r.x, r.y + 185, r.width, 60))
    pygame.draw.line(pantalla, AMARILLO, (r.x, r.y + 185), (r.right - 1, r.y + 185), 4)
    pygame.draw.rect(pantalla, (207, 197, 180), (r.x, r.y + 245, r.width, r.height - 245),
                     border_bottom_left_radius=18, border_bottom_right_radius=18)
    for i in range(1, 6):
        x = r.x + i * (r.width // 6)
        pygame.draw.line(pantalla, (185, 174, 155), (x, r.y + 245), (x + (i - 3) * 14, r.bottom - 4), 2)
    # pizarra con código y reloj
    pygame.draw.rect(pantalla, (22, 32, 42), (r.x + 18, r.y + 14, 120, 58), border_radius=6)
    pygame.draw.rect(pantalla, (196, 154, 98), (r.x + 18, r.y + 14, 120, 58), 4, border_radius=6)
    pantalla.blit(fuente.render("if bug:", True, BLANCO), (r.x + 28, r.y + 22))
    pantalla.blit(fuente.render("   fix()", True, AMARILLO), (r.x + 28, r.y + 44))
    pygame.draw.circle(pantalla, BLANCO, (r.right - 45, r.y + 42), 26)
    pygame.draw.circle(pantalla, BORDO, (r.right - 45, r.y + 42), 26, 4)
    pygame.draw.line(pantalla, NEGRO, (r.right - 45, r.y + 42), (r.right - 45, r.y + 25), 3)
    pygame.draw.line(pantalla, NEGRO, (r.right - 45, r.y + 42), (r.right - 33, r.y + 48), 3)
    # escritorio de fondo con PCs
    pygame.draw.rect(pantalla, (160, 120, 72), (r.x + 10, r.y + 172, r.width - 20, 13))
    for x in (r.x + 20, r.x + 85, r.right - 141, r.right - 76):
        pygame.draw.rect(pantalla, (42, 45, 54), (x, r.y + 120, 56, 38), border_radius=4)
        pygame.draw.rect(pantalla, (15, 18, 24), (x + 4, r.y + 124, 48, 26))
        for k in range(3):
            pygame.draw.line(pantalla, VERDE_CODIGO, (x + 8, r.y + 131 + k * 8),
                             (x + 14 + 10 * (k + 2), r.y + 131 + k * 8), 2)
        pygame.draw.rect(pantalla, (42, 45, 54), (x + 24, r.y + 158, 8, 14))


def dibujar_mascota(pantalla, fuente, cx, cy, estado, t):
    """Dibuja a 'Bit', el búho programador de Informática, según su estado."""
    bob = math.sin(t * 3) * 4 if estado != "cansada" else math.sin(t * 1.2) * 2
    y0 = cy + bob  # centro vertical de la cabeza (con animación)

    # --- alas, cuerpo y buzo institucional ---
    pygame.draw.ellipse(pantalla, PELO_OSCURO, (cx - 125, cy + 55, 42, 105))
    pygame.draw.ellipse(pantalla, PELO_OSCURO, (cx + 83, cy + 55, 42, 105))
    pygame.draw.ellipse(pantalla, PELO, (cx - 105, cy + 20, 210, 170))
    pygame.draw.ellipse(pantalla, BORDO, (cx - 85, cy + 62, 170, 128))
    pygame.draw.rect(pantalla, AMARILLO, (cx - 68, cy + 122, 136, 14))
    code = fuente.render("</>", True, AMARILLO)
    pantalla.blit(code, code.get_rect(center=(cx, cy + 95)))
    for ox in (-40, 10):  # patas
        pygame.draw.ellipse(pantalla, NARANJA, (cx + ox, cy + 182, 32, 18))

    # --- plumas de la cabeza y cabeza ---
    for s in (-1, 1):
        pygame.draw.polygon(pantalla, PELO, [(cx + s * 80, y0 - 45), (cx + s * 88, y0 - 112), (cx + s * 32, y0 - 72)])
        pygame.draw.polygon(pantalla, PELO_OSCURO, [(cx + s * 74, y0 - 55), (cx + s * 80, y0 - 98), (cx + s * 46, y0 - 74)])
    pygame.draw.ellipse(pantalla, PELO, (cx - 90, y0 - 75, 180, 140))
    pygame.draw.polygon(pantalla, PELO_OSCURO, [(cx - 10, y0 - 70), (cx, y0 - 52), (cx + 10, y0 - 70)])

    # --- discos faciales y ojos según estado ---
    ey = int(y0 - 20)
    for s in (-1, 1):
        ex = int(cx + s * 40)
        pygame.draw.circle(pantalla, CREMA, (ex, ey), 38)
        if estado == "cansada":
            pygame.draw.line(pantalla, NEGRO, (ex - 18, ey), (ex + 18, ey), 5)
        elif estado == "bugs":
            pygame.draw.line(pantalla, NEGRO, (ex - 12, ey - 12), (ex + 12, ey + 12), 5)
            pygame.draw.line(pantalla, NEGRO, (ex - 12, ey + 12), (ex + 12, ey - 12), 5)
        else:
            pygame.draw.circle(pantalla, AMARILLO, (ex, ey), 24)
            dy = 6 if estado in ("programando", "triste") else 0
            pygame.draw.circle(pantalla, NEGRO, (ex, ey + dy), 11)
            pygame.draw.circle(pantalla, BLANCO, (ex + 4, ey + dy - 4), 3)
            if estado == "triste":  # cejas caídas
                if s < 0:
                    pygame.draw.line(pantalla, NEGRO, (ex - 18, ey - 24), (ex + 18, ey - 33), 4)
                else:
                    pygame.draw.line(pantalla, NEGRO, (ex - 18, ey - 33), (ex + 18, ey - 24), 4)
        # anteojos
        pygame.draw.circle(pantalla, NEGRO, (ex, ey), 30, 4)
    pygame.draw.line(pantalla, NEGRO, (cx - 10, ey), (cx + 10, ey), 4)
    if estado == "triste":  # lagrimita
        pygame.draw.circle(pantalla, (120, 200, 255), (int(cx - 58), ey + 36), 5)

    # --- pico y mejillas ---
    pygame.draw.polygon(pantalla, NARANJA, [(cx - 9, y0 - 2), (cx + 9, y0 - 2), (cx, y0 + 24)])
    if estado in ("feliz", "programando"):
        for s in (-1, 1):
            pygame.draw.circle(pantalla, (255, 160, 160), (int(cx + s * 62), int(y0 + 14)), 6)

    # --- auriculares gamer ---
    pygame.draw.arc(pantalla, GRIS, (cx - 92, y0 - 100, 184, 150), 0.1, math.pi - 0.1, 8)
    for ox in (-90, 90):
        pygame.draw.ellipse(pantalla, ROJO, (cx + ox - 12, y0 - 40, 24, 46))
        pygame.draw.ellipse(pantalla, AMARILLO, (cx + ox - 12, y0 - 40, 24, 46), 3)
    pygame.draw.line(pantalla, GRIS, (cx - 88, y0 + 4), (cx - 36, y0 + 36), 4)
    pygame.draw.circle(pantalla, NEGRO, (int(cx - 36), int(y0 + 36)), 6)

    # --- extras según estado ---
    if estado == "programando":
        laptop = pygame.Rect(cx - 75, cy + 100, 150, 85)
        pygame.draw.rect(pantalla, GRIS, laptop, border_radius=6)
        pygame.draw.rect(pantalla, NEGRO, laptop.inflate(-12, -12), border_radius=4)
        for i in range(4):  # "líneas de código" que parpadean
            largo = 30 + ((int(t * 6) + i * 3) % 7) * 9
            pygame.draw.line(pantalla, VERDE_CODIGO,
                             (laptop.x + 14, laptop.y + 14 + i * 14),
                             (laptop.x + 14 + largo, laptop.y + 14 + i * 14), 3)
    elif estado == "cansada":
        for i in range(3):
            z = fuente.render("Z", True, NEGRO)
            pantalla.blit(z, (cx + 95 + i * 18, cy - 70 - i * 22 + math.sin(t * 2 + i) * 3))
        # ícono de batería baja
        pygame.draw.rect(pantalla, NEGRO, (cx - 150, cy - 60, 40, 20), 2)
        pygame.draw.rect(pantalla, ROJO, (cx - 148, cy - 58, 8, 16))
        pygame.draw.rect(pantalla, NEGRO, (cx - 110, cy - 54, 4, 8))


def dibujar_texto_centrado(pantalla, fuente, texto, color, x, y):
    img = fuente.render(texto, True, color)
    pantalla.blit(img, img.get_rect(center=(x, y)))


# --------------------------------------------------------------------------
# PROGRAMA PRINCIPAL (GAME LOOP)
# --------------------------------------------------------------------------
def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption('Bit - Mascota Virtual de Informática | IPET 249')
    reloj = pygame.time.Clock()

    f_chica = pygame.font.SysFont("arial", 18, bold=True)
    f_media = pygame.font.SysFont("arial", 22, bold=True)
    f_titulo = pygame.font.SysFont("arial", 26, bold=True)

    escudo = cargar_escudo()
    sonidos = cargar_sonidos()
    silenciado = False
    mascota = Mascota()
    zona_escenario = pygame.Rect(270, 130, 500, 330)

    botones = [
        Boton((30, 520, 170, 55), "[1] Café", pygame.K_1, mascota.tomar_cafe),
        Boton((215, 520, 170, 55), "[2] Programar", pygame.K_2, mascota.programar),
        Boton((400, 520, 170, 55), "[3] Limpiar bugs", pygame.K_3, mascota.limpiar_bugs),
    ]

    estados_txt = {
        "feliz": "¡Bit está feliz!",
        "triste": "Bit está triste... necesita programar",
        "cansada": "Sin batería... ¡dale un café!",
        "programando": "Bit está programando...",
        "bugs": "¡Hay bugs por todos lados!",
    }

    tiempo = 0.0
    estado_anterior = mascota.estado
    ejecutando = True
    while ejecutando:
        dt = reloj.tick(FPS) / 1000.0
        tiempo += dt
        mouse = pygame.mouse.get_pos()

        # ---- eventos ----
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False
                elif evento.key == pygame.K_m:
                    silenciado = not silenciado
                for b in botones:
                    if evento.key == b.tecla:
                        b.accion()
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                clic_en_boton = False
                for b in botones:
                    if b.rect.collidepoint(evento.pos):
                        b.accion()
                        clic_en_boton = True
                if not clic_en_boton:
                    mascota.aplastar_bug(evento.pos)

        # ---- lógica ----
        mascota.actualizar(dt, zona_escenario)

        # ---- sonidos ----
        for nombre in mascota.eventos:
            if nombre in sonidos and not silenciado:
                sonidos[nombre].play()
        mascota.eventos.clear()
        if mascota.estado != estado_anterior:
            if mascota.estado in ("cansada", "bugs", "triste") and "alerta" in sonidos and not silenciado:
                sonidos["alerta"].play()
            estado_anterior = mascota.estado

        # ---- dibujo ----
        pantalla.fill(BORDO)

        # Cabecera institucional
        pygame.draw.rect(pantalla, BORDO_OSCURO, (0, 0, ANCHO, 110))
        pygame.draw.line(pantalla, AMARILLO, (0, 110), (ANCHO, 110), 4)
        pantalla.blit(escudo, (15, 10))
        dibujar_texto_centrado(pantalla, f_titulo, 'IPET 249 "Nicolás Copérnico"', AMARILLO, 450, 35)
        dibujar_texto_centrado(pantalla, f_media, "Especialidad en Informática", BLANCO, 450, 68)
        dibujar_texto_centrado(pantalla, f_chica, "Laboratorio de Aplicaciones II - 2026", BLANCO, 450, 94)

        # Panel de estado
        dibujar_barra(pantalla, f_chica, 30, 165, mascota.energia, AMARILLO, "Energía (batería)")
        dibujar_barra(pantalla, f_chica, 30, 235, mascota.animo, BLANCO, "Ánimo (nivel de código)")
        dibujar_barra(pantalla, f_chica, 30, 305, mascota.salud, ROJO, "Salud (limpieza de bugs)")

        ayuda = ["Controles:", "1: Café", "2: Programar", "3: Limpiar bugs", "Clic en un bug: aplastarlo", "M: sonido  |  ESC: salir"]
        for i, linea in enumerate(ayuda):
            color = AMARILLO if i == 0 else BLANCO
            pantalla.blit(f_chica.render(linea, True, color), (30, 360 + i * 24))

        # Escenario: sala de computación
        dibujar_sala(pantalla, f_chica, zona_escenario)
        pygame.draw.rect(pantalla, AMARILLO, zona_escenario, 5, border_radius=18)

        dibujar_mascota(pantalla, f_media, zona_escenario.centerx, zona_escenario.y + 120,
                        mascota.estado, tiempo)
        for bug in mascota.bugs:
            dibujar_bug(pantalla, bug["x"], bug["y"])

        dibujar_texto_centrado(pantalla, f_media, estados_txt[mascota.estado], AMARILLO,
                               zona_escenario.centerx, 490)

        for b in botones:
            b.dibujar(pantalla, f_chica, mouse)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
