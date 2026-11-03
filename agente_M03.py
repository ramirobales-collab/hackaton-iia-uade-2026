"""Agente antifraude M03: ante cada pedido elige la accion de menor costo esperado.

Caso nuevo:  python agente_M03.py <monto_usd> <antiguedad_dias> <distancia_km>
Medicion:    python agente_M03.py --medir

Si dan un cuarto dato (contracargo) se ignora: no existe antes de despachar.
Parametros fijados solo con los casos 1 a 14.
"""
import csv
import math
import os
import sys

# Estimacion de P(fraude): regresion logistica L2 (lambda=1) sobre casos 1-14.
SESGO = -2.82
PESO_DISTANCIA = 0.76   # por cada 100 km
PESO_ANTIGUEDAD = -0.67 # por cada 100 dias

# Consecuencias: supuestos propios, la ficha no da montos. Ver README seccion 4.
COSTO_MERCADERIA = 0.70  # fraccion del monto que cuesta reponer la mercaderia
CARGO_CONTRACARGO = 20   # USD que cobra el banco
MARGEN = 0.30            # ganancia perdida por venta frenada
CLIENTE_ENOJADO = 10     # USD de valor futuro perdido


def prob_fraude(antiguedad, distancia):
    z = SESGO + PESO_DISTANCIA * distancia / 100 + PESO_ANTIGUEDAD * antiguedad / 100
    return 1 / (1 + math.exp(-z))


def costo_fn(monto):
    return COSTO_MERCADERIA * monto + CARGO_CONTRACARGO


def costo_fp(monto):
    return MARGEN * monto + CLIENTE_ENOJADO


def decidir(monto, antiguedad, distancia):
    """Devuelve (SI/NO, P, costo esperado de despachar, costo esperado de frenar)."""
    p = prob_fraude(antiguedad, distancia)
    despachar = p * costo_fn(monto)
    frenar = (1 - p) * costo_fp(monto)
    return ("SI" if frenar < despachar else "NO"), p, despachar, frenar


def resumen(nombre, casos, predice):
    vp = fn = fp = vn = 0
    usd = 0.0
    for monto, real, pred in ((c[0], c[3], predice(c)) for c in casos):
        if real and pred:
            vp += 1
        elif real:
            fn += 1
            usd += costo_fn(monto)
        elif pred:
            fp += 1
            usd += costo_fp(monto)
        else:
            vn += 1
    div = lambda a, b: f"{100 * a / b:.1f}%" if b else "n/d"
    print(f"{nombre:<28} VP={vp} FN={fn} FP={fp} VN={vn} | exact {div(vp + vn, len(casos))}"
          f" prec {div(vp, vp + fp)} sens {div(vp, vp + fn)} espec {div(vn, vn + fp)} | USD {usd:.0f}")


def medir():
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", "M03.csv")
    with open(ruta, encoding="utf-8") as f:
        filas = list(csv.reader(f))[1:]
    tomar = lambda grupo: [(float(r[2]), float(r[3]), float(r[4]), int(r[6]), int(r[0]), int(r[5]))
                           for r in filas if r[1] == grupo]
    sistemas = [
        ("Agente", lambda c: decidir(c[0], c[1], c[2])[0] == "SI"),
        ("Siempre NO (despachar todo)", lambda c: False),
        ("Siempre SI (frenar todo)", lambda c: True),
    ]
    for grupo in ("entrenamiento", "prueba"):
        print(f"\n== {grupo} ==")
        for nombre, f in sistemas:
            resumen(nombre, tomar(grupo), f)
        for c in tomar(grupo):
            d, p, cd, cf = decidir(c[0], c[1], c[2])
            print(f"  caso {c[4]:>2} m={c[0]:>3.0f} a={c[1]:>3.0f} d={c[2]:>4.0f} P={p:.3f} "
                  f"Cdesp={cd:6.1f} Cfren={cf:6.1f} -> {d:<2} real={'SI' if c[3] else 'NO'}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--medir"]:
        medir()
    elif len(sys.argv) in (4, 5):
        m, a, d = (float(x) for x in sys.argv[1:4])
        s, p, cd, cf = decidir(m, a, d)
        print(f"P(fraude) = {p:.3f}")
        print(f"Costo esperado de DESPACHAR = {p:.3f} x {costo_fn(m):.1f} = {cd:.1f} USD")
        print(f"Costo esperado de FRENAR    = {1 - p:.3f} x {costo_fp(m):.1f} = {cf:.1f} USD")
        print(f"Respuesta: {s} -> {'FRENAR' if s == 'SI' else 'DESPACHAR'}")
    else:
        print(__doc__)
