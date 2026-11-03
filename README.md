# M03 · ¿Este pedido es fraudulento?

**Integrantes:** Ramiro Bales (legajo 1235871)
**IA declarada:** Claude
**Pista:** Agente
**Publicación en LinkedIn:** se publica después de validar; todavía no hay link.

---

## 1. Formulación y PEAS

**La pregunta.** Para cada pedido de la tienda online, antes de despacharlo, ¿es fraudulento? **SÍ** significa: el agente lo trata como fraude y lo frena. **NO** significa: lo despacha.

| PEAS | Su sistema |
|---|---|
| Medida de rendimiento | USD perdidos por pedido, medidos contra el resultado real: un fraude despachado cuesta 0,70 × monto + 20; un pedido legítimo frenado cuesta 0,30 × monto + 10. Menos es mejor. |
| Entorno | La tienda online justo antes del despacho. Parcialmente observable (no ve quién está detrás de la tarjeta), estocástico, episódico (cada pedido se decide por separado) y con un adversario que puede adaptarse. |
| Actuadores | Frenar el pedido (SÍ) o despacharlo (NO). |
| Sensores | Monto del pedido, antigüedad de la cuenta y distancia envío–facturación, los tres disponibles al momento del checkout. |

**Objetivo y métrica.** No son lo mismo. El **objetivo** es que la tienda pierda la menor cantidad de plata posible entre mercadería robada, contracargos, ventas perdidas y clientes enojados. La **métrica principal** es el costo en USD, y la acompañan sensibilidad y especificidad. El costo es un termómetro, no el objetivo: depende de supuestos propios (sección 4) y no captura del todo el daño de un cliente que no vuelve. La exactitud se informa solo contra línea base, porque trata igual dos errores que no cuestan igual.

## 2. El sistema

**Cómo decide.** Es un agente de costo esperado, en tres pasos:

1. **Estima la probabilidad de fraude** con las dos señales: `z = −2,82 + 0,76 × (distancia / 100) − 0,67 × (antigüedad / 100)` y `P = 1 / (1 + e^(−z))`.
2. **Calcula el costo esperado de cada acción:** `Despachar = P × (0,70 × monto + 20)` y `Frenar = (1 − P) × (0,30 × monto + 10)`.
3. **Elige la acción más barata.** Si Frenar < Despachar responde SÍ; si no, responde NO.

Con estos costos, frena cuando P supera cerca de 0,31 (0,312 con monto 50; 0,301 con monto 800), y no 0,50. El umbral sale de las consecuencias: no se ajustó para mejorar una métrica.

**Variables que usa y por qué.**

| Variable | Uso | Por qué |
|---|---|---|
| Distancia envío–facturación | Estima P | Se conoce al decidir. En los casos 1–14 sola da más costo que junto con la antigüedad. |
| Antigüedad de la cuenta | Estima P | Se conoce al decidir. Las cuentas viejas son menos riesgosas. |
| Monto | Solo consecuencias | Se conoce al decidir. No se usa como señal de fraude: en 1–14 los fraudes promedian 279,5 USD y los legítimos 379,6, y agregarlo a P empeoró la validación (730 contra 668 USD). Sí define cuánto hay en juego. |
| **Contracargo registrado** | **Descartada** | **El contracargo lo cobra el banco después de despachar, así que no existe al decidir. Coincide con el resultado real en los 20 casos: usarla daría 100 % en todo y sería fuga de información, no predicción.** Si un caso nuevo trae ese dato, se ignora. |

**De dónde salen los números.** Los pesos salen de una regresión logística con regularización L2 (λ = 1), ajustada solo con los casos 1–14. Comparé candidatos dejando un caso afuera por vez (LOO), también solo con 1–14, y con λ = 0,3, 1 y 3 el resultado de la opción elegida no cambia:

| Señales para estimar P | VP | FN | FP | VN | USD |
|---|---|---|---|---|---|
| **Distancia + antigüedad (elegida)** | 5 | 1 | 3 | 5 | **668** |
| Monto + distancia + antigüedad (λ = 1) | 4 | 2 | 2 | 6 | 730 |
| Solo distancia | 4 | 2 | 2 | 6 | 741 |
| Solo antigüedad | 5 | 1 | 3 | 5 | 776 |

**Cómo se corre en vivo.** Hay tres caminos con el mismo resultado:

- **Colab:** [abrir agente_M03.ipynb](https://colab.research.google.com/github/ramirobales-collab/hackaton-iia-uade-2026/blob/main/agente_M03.ipynb), cargar los tres valores en la celda y ejecutar todo.
- **Python:** `python agente_M03.py 500 30 900` (monto, antigüedad y distancia, en ese orden). Para reproducir la medición: `python agente_M03.py --medir`.
- **A mano:** las fórmulas de arriba con una calculadora.

**Dos casos de ejemplo.**

| Caso inventado | Valores | Salida del sistema |
|---|---|---|
| A | Monto 500, antigüedad 30, distancia 900 | P = 0,979; Despachar 362,1 USD contra Frenar 3,4 USD → **SÍ**, frena. Da igual con contracargo 0 o 1. |
| B | Monto 150, antigüedad 600, distancia 100 | P = 0,002; Despachar 0,3 USD contra Frenar 54,9 USD → **NO**, despacha. |

## 3. Medición

**Entrenamiento (casos 1–14)**

| | Predice SÍ | Predice NO |
|---|---|---|
| **Real SÍ** | VP = 5 | FN = 1 |
| **Real NO** | FP = 2 | VN = 6 |

VP: 3, 6, 8, 11, 12. FN: 4. FP: 9, 14. VN: 1, 2, 5, 7, 10, 13. Cierre: 5 + 1 + 2 + 6 = 14, y VP + FN = 6, los fraudes reales del conjunto.

**Prueba (casos 15–20)**

| | Predice SÍ | Predice NO |
|---|---|---|
| **Real SÍ** | VP = 3 | FN = 1 |
| **Real NO** | FP = 0 | VN = 2 |

VP: 15, 17, 20. FN: 18. VN: 16, 19. Cierre: 3 + 1 + 0 + 2 = 6, y VP + FN = 4, los fraudes reales del conjunto.

| Métrica | Entrenamiento | Prueba |
|---|---|---|
| Exactitud | 11/14 = 78,6 % | 5/6 = 83,3 % |
| Precisión | 5/7 = 71,4 % | 3/3 = 100 % |
| Sensibilidad | 5/6 = 83,3 % | 3/4 = 75 % |
| Especificidad | 6/8 = 75 % | 2/2 = 100 % |
| **Costo (USD)** | **584** | **177** |

**Entrenamiento contra prueba.** La prueba sale apenas mejor en exactitud (+4,7 puntos) y peor en sensibilidad (−8,3 puntos). No hay señal de sobreajuste, pero tampoco alcanza para afirmar que generaliza: con 6 casos, un solo caso mueve la exactitud 16,7 puntos, y la especificidad de 100 % sale de solo 2 pedidos legítimos. Además, la prueba tiene 67 % de fraude y el entrenamiento 43 %. Si un solo caso de prueba cambiara de lado, la exactitud quedaría entre 66,7 % y 100 %, y la sensibilidad se movería 25 puntos, porque hay solo 4 fraudes. El intervalo de Wilson al 95 % para la exactitud de prueba va de 44 % a 97 %, así que el 83,3 % no es un número firme. La estimación más prudente es la de LOO sobre 1–14, con exactitud 10/14 = 71,4 %, unos 7 puntos debajo de la medición sobre los mismos datos con los que se ajustó.

**Qué tan ciega fue la prueba.** No fue del todo ciega. La ficha trae los 20 casos en una misma tabla y la IA leyó también las filas 15–20 antes de construir el agente. Los scripts que ajustaron pesos y compararon candidatos usaron solo 1–14, y después de medir la prueba no se cambió ningún parámetro. Pero eso no descarta una influencia por haberlas visto, y el commit de los parámetros quedó registrado después de la primera medición, así que el historial tampoco prueba el orden.

## 4. El error más caro

**El falso negativo.** Según la ficha, despachar un fraude pierde la mercadería y además el banco cobra el contracargo; frenar un pedido legítimo deja un cliente enojado y una venta perdida. Para ponerlo en números, y como la ficha no trae montos, supuse lo siguiente:

| Error | Costo supuesto | Con monto 300 |
|---|---|---|
| Falso negativo | 70 % del monto (mercadería) + 20 USD (cargo del banco) | 230 USD |
| Falso positivo | 30 % del monto (margen perdido) + 10 USD (cliente enojado) | 100 USD |

**Qué cambié por ese error.** Reemplacé el umbral neutro de P ≥ 0,50 por la regla de costo esperado, que frena desde P ≈ 0,31. Lo que pasó fue esto:

| Dónde se mide | Umbral 0,50 | Regla de costos |
|---|---|---|
| LOO en 1–14 | FN = 2, FP = 1, 646 USD | FN = 1, FP = 3, 668 USD |
| Sobre los mismos 1–14 | FN = 1, FP = 0, 425 USD | FN = 1, FP = 2, 584 USD |
| Prueba (informado, no usado para decidir) | FN = 3, FP = 0, 1162 USD | FN = 1, FP = 0, 177 USD |

Hay un costo real: en entrenamiento la regla baja un falso negativo solo en LOO, suma falsos positivos y no ahorra plata. La mantuve porque el umbral sale de las consecuencias declaradas y no de ajustarlo a estos casos. Esos 22 USD de diferencia en LOO no alcanzan para descartarla, y la mejora grande aparece solo en la prueba, que con 6 casos es poca evidencia.

**Sensibilidad a los supuestos** (solo sobre 1–14, sin usar para elegir). Con margen de 10–20 % el agente frena más (FN = 0, FP = 2 a 4); con 30–40 %, FN = 1 y FP = 1 o 2; con 50 %, FN = 1 y FP = 0. La decisión depende bastante de estos supuestos, así que la tienda debería reemplazarlos por su margen real antes de usarlo.

**El error que queda.** El caso 18 (monto 224, antigüedad 96, distancia 317) da P = 0,258 y se despacha. Es casi igual al caso 14, legítimo (monto 143, antigüedad 111, distancia 378): con estas señales no se distinguen. No lo corregí porque sería ajustar el sistema a un caso de prueba; haría falta otra señal.

## 5. ¿Comparado contra qué?

**Línea base trivial.** La clase más frecuente en entrenamiento es NO. También muestro el SÍ constante, que es la clase más frecuente en prueba.

| Sistema | Exactitud entren. | Exactitud prueba | Sens. prueba | Espec. prueba | USD entren. | USD prueba |
|---|---|---|---|---|---|---|
| **Agente** | **78,6 %** | **83,3 %** | **75 %** | **100 %** | **584** | **177** |
| Siempre NO (despacha todo) | 57,1 % | 33,3 % | 0 % | 100 % | 1294 | 1428 |
| Siempre SÍ (frena todo) | 42,9 % | 66,7 % | 100 % | 0 % | 991 | **156** |

El agente supera a las dos bases en exactitud: en prueba, por 50 puntos a Siempre NO y por 16,6 puntos (un caso) a Siempre SÍ. **En costo de prueba pierde contra Siempre SÍ por 21 USD**, porque ahí 4 de 6 pedidos son fraude y los 2 legítimos son baratos de frenar. Sumando los 20 casos, el agente cuesta 761 USD, Siempre SÍ 1147 y Siempre NO 2722. Frenar todo además significa no vender nada legítimo, así que no es una alternativa real, aunque en esos 6 casos salga más barata.

| Checklist (Clase 6) | Respuesta |
|---|---|
| ¿Qué datos? | Los 20 casos inventados de la ficha, con división 14/6 sin cambios. Usa 3 de las 4 variables y descarta el contracargo. |
| ¿Qué métrica? | Costo en USD como principal, con sensibilidad y especificidad. Exactitud y precisión se informan como complemento. |
| ¿Comparado contra qué? | Siempre NO, Siempre SÍ y el umbral 0,50. |
| ¿Quién lo midió? | La IA (Claude), por encargo mío, con su propio script y un recuento caso por caso contra la tabla. No es una medición independiente: quien construyó también midió, yo quiero la nota, y los costos son supuestos propios. El control externo son los casos propios de la mesa. |

## 6. Riesgo: el camino completo

- **Datos:** 20 pedidos inventados con 50 % de fraude. En una tienda real el fraude es mucho menos frecuente, y no aparecen patrones como una cuenta vieja robada que envía cerca.
- **Modelo:** aprende que «cuenta nueva + envío lejos» es sospechoso, lo cual es una correlación y no una causa.
- **Decisión:** frena al cliente nuevo que manda un regalo o se muda a otra provincia. Con un fraude de 2 % (ejemplo ilustrativo, no es dato de la ficha) y las tasas de entrenamiento (sensibilidad 83,3 %, especificidad 75 %), la precisión caería a 6,4 %: unos 94 de cada 100 pedidos frenados serían legítimos.
- **Consecuencia:** la tienda pierde ventas y castiga sistemáticamente a clientes nuevos y a los que viven lejos de su domicilio de facturación. Además, quien comete fraude puede adaptarse enviando más cerca, como en el caso 18.
- **Mitigación:** que SÍ signifique «frenar y revisar», con una persona que libere el pedido antes de cancelar la venta; medir los falsos positivos en producción y recalibrar con la tasa real de fraude.

## 7. Bitácora

**Uso de la IA**

| # | Qué le pedimos | Qué aceptamos | Qué rechazamos y por qué |
|---|---|---|---|
| 1 | Que leyera bases, ficha, forks de otros grupos, apuntes y transcripciones, y que hiciera el trabajo completo en la pista Agente. Delegué la construcción: mi parte es revisarlo y defenderlo. | La ficha M03 por dominio (Comercio Electrónico, IA Claude), los temas de cátedra (PEAS, objetivo contra métrica, checklist) y los tipos de agujero que el bot marcó a otros grupos. | Copiar soluciones de otros grupos, que las bases prohíben. El fork de otro grupo con la misma ficha M03 se salteó al construir; después de fijar y medir el sistema pedí leer todos los README, incluido ese. No se tomó nada de su solución ni se cambió el agente por eso. |
| 2 | Detectar variables no disponibles al decidir. | Descartar el contracargo. | Usarlo aunque da 100 %: se conoce después del despacho y activa el tope de información no disponible. |
| 3 | Elegir cómo estimar P con los casos 1–14. | Logística con distancia y antigüedad, por menor costo en LOO. | Sumar el monto a P (730 contra 668 USD en LOO). Un árbol de dos cortes (distancia ≥ 455 y antigüedad < 357,5), revisado a mano, acierta 14/14: lo rechazamos como memorización, y la IA además vio a mano que falla en los casos de prueba 15, 18 y 20, así que este rechazo no fue ciego. |
| 4 | Pasar de umbral 0,50 a costo esperado. | La regla de costo esperado, porque responde a las consecuencias. | Bajar el margen supuesto a 20 %, que en 1–14 elimina el FN: sería acomodar un supuesto a los datos. Tampoco se tocó nada por el caso 18. |
| 5 | Redactar este README con los resultados. | La redacción, incluidas las partes desfavorables (Siempre SÍ más barato en prueba, regla de costos sin ahorro en entrenamiento). | Afirmar que la prueba fue totalmente ciega, porque no sería cierto. |

**Corridas contra el evaluador**

| Corrida | Nota | Agujero que encontró | Qué cambiamos |
|---|---|---|---|
| 1 | Sin nota todavía: esta es la primera corrida. | Sin datos todavía. | Sin cambios todavía. |
