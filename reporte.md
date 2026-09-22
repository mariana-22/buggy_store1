# Evaluación de Bugs y Pruebas

## Resumen de evaluación

| Fallo                                     | Identificación |  Solución |     Tests |  Subtotal |
| ----------------------------------------- | -------------: | --------: | --------: | --------: |
| Fallo 1 — Argumento mutable por defecto   |            1/1 |       2/2 |       3/3 |   **6/6** |
| Fallo 2 — Matemáticas de descuento        |            1/1 |       2/2 |       3/3 |   **6/6** |
| Fallo 3 — Error de tipografía             |            1/1 |       2/2 |       3/3 |   **6/6** |
| Fallo 4 — Producto inexistente (KeyError) |            1/1 |       1/2 |       3/3 |   **5/6** |
| Fallo 5 — Stock negativo / insuficiente   |            1/1 |       2/2 |       3/3 |   **6/6** |
| Fallo 6 — Mutación durante la iteración   |            1/1 |       2/2 |       3/3 |   **6/6** |
| **Total**                                 |        **6/6** | **11/12** | **18/18** | **35/36** |

---

# Fallo 1 — Argumento mutable por defecto

### Identificación — 1/1 punto

Documentaron con precisión que los argumentos mutables utilizados como valores predeterminados en Python se evalúan una sola vez y pueden ser compartidos entre diferentes instancias.

### Solución — 2/2 puntos

Cambiaran correctamente el valor predeterminado a `None` y construyeron un nuevo diccionario cuando no se proporciona un inventario inicial.

### Tests — 3/3 puntos

Crearon la clase:

```python id="7l9p3m"
TestBug1InventarioCompartido
```

con **3 pruebas estructuradas en `pytest`**, validando tanto el aislamiento entre instancias como el comportamiento cuando se proporcionan valores iniciales.

### Subtotal

**6/6 puntos**

---

# Fallo 2 — Matemáticas de descuento

**Cupón `SENA2026`**

### Identificación — 1/1 punto

Detectaron correctamente que el cálculo estaba cobrando el 120 % del valor original, provocando que los productos fueran más costosos en lugar de aplicar el descuento del 20 %.

### Solución — 2/2 puntos

Corrigieron correctamente el factor multiplicador a:

```python id="8lq4ys"
0.80
```

Esto representa un descuento real del 20 %.

### Tests — 3/3 puntos

Incluyeron la clase:

```python id="m2p8xk"
TestBug2DescuentoInvertido
```

cubriendo diferentes escenarios:

* Aplicación del descuento del 20 %.
* Compras sin cupón.
* Carritos con múltiples productos.

### Subtotal

**6/6 puntos**

---

# Fallo 3 — Error de tipografía

**Variable `ventas_totaIes`**

### Identificación — 1/1 punto

Localizaron correctamente la `I` mayúscula utilizada de manera engañosa dentro del nombre de la variable, lo que ocasionaba un `AttributeError`.

### Solución — 2/2 puntos

Corrigieron correctamente el atributo a:

```python id="4mny0j"
self.ventas_totales
```

### Tests — 3/3 puntos

Implementaron la clase:

```python id="q8z5sa"
TestBug3TypoVentasTotales
```

para validar:

* La inicialización de `ventas_totales` en cero.
* La acumulación progresiva de las ventas.
* El correcto funcionamiento de múltiples operaciones.

### Subtotal

**6/6 puntos**

---

# Fallo 4 — Producto inexistente

**KeyError**

### Identificación — 1/1 punto

Identificaron correctamente la ausencia de una comprobación de existencia antes de acceder directamente a:

```python id="w4g1vn"
self.inventario[id_prod]
```

### Solución — 1/2 puntos

Implementaron una validación mediante:

```python id="1b8z6w"
if id_prod not in self.inventario:
    raise ValueError(...)
```

La validación evita que se produzca directamente el `KeyError` y permite controlar el error mediante una excepción más descriptiva.

Sin embargo, existe una observación importante de arquitectura.

La validación se realiza dentro del ciclo que procesa los productos. Por lo tanto, si el carrito contiene primero un producto válido y posteriormente uno inexistente, el producto válido puede ser descontado antes de que se detecte el producto inválido y se lance la excepción.

Esto rompe la **atomicidad de la operación**, ya que el pedido puede fallar después de haber modificado parcialmente el inventario.

La solución más robusta sería validar todos los productos del carrito antes de realizar cualquier modificación.

### Tests — 3/3 puntos

Diseñaron la clase:

```python id="r0s4ha"
TestBug4ProductoInexistente
```

verificando correctamente:

* Que se produzca `ValueError`.
* Que no se produzca un `KeyError`.
* La integridad del inventario ante el caso evaluado.

### Subtotal

**5/6 puntos**

---

# Fallo 5 — Stock negativo / insuficiente

### Identificación — 1/1 punto

Documentaron correctamente que el sistema realizaba la resta de existencias sin comprobar previamente si había suficiente stock disponible.

### Solución — 2/2 puntos

Agregaron la comprobación:

```python id="2a7s5p"
if cant_comprada > producto['cantidad']:
```

y utilizaron un `ValueError` descriptivo cuando la cantidad solicitada supera el stock disponible.

### Tests — 3/3 puntos

Implementaron la clase:

```python id="f9c2jd"
TestBug5StockNegativo
```

cubriendo diferentes casos:

* Compras que exceden el stock.
* Ventas exactamente iguales al stock disponible.
* Persistencia y comportamiento correcto del inventario.

### Subtotal

**6/6 puntos**

---

# Fallo 6 — Mutación durante la iteración

**RuntimeError**

### Identificación — 1/1 punto

Explicaron correctamente la causa del `RuntimeError` generado al eliminar elementos directamente del diccionario mientras se está iterando sobre él.

### Solución — 2/2 puntos

Aplicaron correctamente:

```python id="d7k2mc"
list(self.inventario.keys())
```

permitiendo iterar sobre una copia de las claves mientras se modifica el diccionario original.

### Tests — 3/3 puntos

Crearon la clase:

```python id="n6w1pf"
TestBug6RuntimeErrorAlLimpiar
```

cubriendo diferentes escenarios:

* Eliminación de productos con stock `0`.
* Manejo de productos con stock negativo.
* Vaciado completo del inventario.

### Subtotal

**6/6 puntos**

---

# Resultado de la evaluación

## Puntaje por componente

| Componente     | Puntaje obtenido | Puntaje máximo |
| -------------- | ---------------: | -------------: |
| Identificación |                6 |              6 |
| Solución       |               11 |             12 |
| Tests          |               18 |             18 |
| **Total**      |           **35** |         **36** |

## Calificación final

**35/36 puntos**

---

# Retroalimentación

El grupo presentó un desempeño sólido en la identificación, implementación y validación de los seis fallos.

Se destaca especialmente la utilización de **pruebas automatizadas estructuradas en `pytest`**, con clases específicas para cada bug y cobertura de diferentes escenarios y casos límite.

La única deducción corresponde al **Fallo 4 — Producto inexistente**, cuya solución evita correctamente el `KeyError`, pero no garantiza la atomicidad completa del procesamiento del pedido.

Para una implementación más robusta, se recomienda separar el proceso en dos etapas:

1. **Validación completa del carrito:** comprobar que todos los productos existen y que todas las cantidades solicitadas son válidas.
2. **Modificación del inventario:** realizar los descuentos únicamente después de que todas las validaciones hayan sido superadas.

De esta manera, un pedido inválido no podría dejar modificaciones parciales en el inventario.

**Resultado final: 35/36 puntos.**
