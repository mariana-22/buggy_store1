# Descripciones para los 6 Pull Requests

Copie el bloque de cada PR en el formulario de GitHub (título + descripción).
Cada rama contiene **únicamente** la corrección del bug correspondiente sobre `main`.

---

## PR #1 — Rama: `fix/bug-1-inventario-compartido`

### Título
Fix bug 1: inventario compartido entre instancias por argumento mutable por defecto

### Descripción
**Error:** al crear dos tiendas sin inventario inicial, los productos agregados en
la primera aparecían en el inventario de la segunda.

**Causa:** `__init__` usaba `inventario_inicial={}` como valor por defecto. En Python
los valores por defecto se evalúan una sola vez y los objetos mutables quedan
compartidos entre **todas** las instancias. Todas las tiendas apuntaban al mismo dict.

```python
def __init__(self, inventario_inicial={}):  # {} es COMPARTIDO
    self.inventario = inventario_inicial
```

**Solución:** usar `None` como valor por defecto y crear un dict nuevo por instancia:

```python
def __init__(self, inventario_inicial=None):
    if inventario_inicial is None:
        self.inventario = {}
    else:
        self.inventario = inventario_inicial
```

**Pruebas ejecutadas (resultado: ✅ todas pasan):**
- `TiendaOnline()` → inventario vacío e independiente por instancia.
- Agregar un producto en la tienda 1 y crear la tienda 2 → `tienda2.inventario == {}`.

**Pruebas automatizadas (pytest — `test_main.py`):**
- Clase `TestBug1InventarioCompartido` con 3 casos:
  - `test_instancias_tienen_inventarios_independientes`
  - `test_inventario_vacio_por_defecto`
  - `test_inventario_inicial_se_usa_cuando_se_proporciona`
- Ejecutar: `python -m pytest test_main.py -k Bug1`
- Resultado: ✅ 3/3 pasan (suite completa: 18/18).

---

## PR #2 — Rama: `fix/bug-2-cupon-descuento`

### Título
Fix bug 2: el cupón SENA2026 recargaba 20% en lugar de descontar 20%

### Descripción
**Error:** los clientes pagaban $120 por un producto de $100 al usar el cupón, es
decir, pagaban **20% de más** en vez de recibir un 20% de descuento.

**Causa:** el cupón se aplicaba con `* 1.20` (recargo del 20%) en lugar de un
descuento del 20% (pagar el 80%):

```python
if cupon_descuento == "SENA2026":
    total_pedido = total_pedido * 1.20  # BUG: INCREMENTA el total
```

**Solución:**

```python
if cupon_descuento == "SENA2026":
    total_pedido = total_pedido * 0.80  # 20% de descuento (paga el 80%)
```

**Pruebas ejecutadas (resultado: ✅ todas pasan):**
- Producto de $100 con cupón → total $80.0.
- Producto de $100 sin cupón → total $100.0 (sin descuento).

**Pruebas automatizadas (pytest — `test_main.py`):**
- Clase `TestBug2DescuentoInvertido` con 3 casos:
  - `test_cupon_aplica_20_por_ciento_de_descuento`
  - `test_sin_cupon_no_hay_descuento`
  - `test_cupon_con_carrito_multiple`
- Ejecutar: `python -m pytest test_main.py -k Bug2`
- Resultado: ✅ 3/3 pasan (suite completa: 18/18).

---

## PR #3 — Rama: `fix/bug-3-typo-ventas-totales`

### Título
Fix bug 3: typo `ventas_totaIes` crasheaba el sistema con AttributeError

### Descripción
**Error:** al procesar el primer pedido, el sistema lanzaba
`AttributeError: 'TiendaOnline' object has no attribute 'ventas_totaIes'` y el
proceso colapsaba. Además, las ventas totales nunca se registraban.

**Causa:** el atributo se escribió con un typo (`ventas_tota**I**es` con "I"
mayúscula), distinto del nombre correcto `ventas_totales` inicializado en `__init__`:

```python
self.ventas_totaIes += total_pedido  # BUG: no existe este atributo
```

**Solución:**

```python
self.ventas_totales += total_pedido
```

**Pruebas ejecutadas (resultado: ✅ todas pasan):**
- Procesar pedido de $200 → `ventas_totales == 200.0`, sin excepciones.
- Pedido posterior → el total se acumula correctamente.

**Pruebas automatizadas (pytest — `test_main.py`):**
- Clase `TestBug3TypoVentasTotales` con 3 casos:
  - `test_venta_se_registra_sin_attributeerror`
  - `test_ventas_totales_acumulan_pedidos`
  - `test_ventas_totales_se_inicializan_en_cero`
- Ejecutar: `python -m pytest test_main.py -k Bug3`
- Resultado: ✅ 3/3 pasan (suite completa: 18/18).

---

## PR #4 — Rama: `fix/bug-4-producto-inexistente`

### Título
Fix bug 4: KeyError al pedir un producto que no existe en el inventario

### Descripción
**Error:** si el carrito contenía un producto no registrado, `procesar_pedido`
lanzaba `KeyError` y el sistema se caía, dejando un fallo no controlado.

**Causa:** se accedía directamente a `self.inventario[id_prod]` sin verificar la
existencia del id:

```python
producto = self.inventario[id_prod]  # BUG: KeyError si no existe
```

**Solución:** validar antes de acceder y lanzar un `ValueError` informativo
(implementada en `main.py`, líneas 29-30):

```python
if id_prod not in self.inventario:
    raise ValueError(f"El producto '{id_prod}' no existe en el inventario")
producto = self.inventario[id_prod]
```

**Pruebas ejecutadas (resultado: ✅ todas pasan):**
- Pedido con `NO_EXISTE` → `ValueError` claro (sin `KeyError`), inventario intacto.
- Pedido con producto válido → se procesa normalmente.

**Pruebas automatizadas (pytest — `test_main.py`):**
- Clase `TestBug4ProductoInexistente` con 3 casos:
  - `test_pedido_de_producto_inexistente_lanza_valueerror`
  - `test_error_no_es_keyerror`
  - `test_inventario_intacto_tras_error`
- Ejecutar: `python -m pytest test_main.py -k Bug4`
- Resultado: ✅ 3/3 pasan (suite completa: 18/18).

---

## PR #5 — Rama: `fix/bug-5-stock-negativo`

### Título
Fix bug 5: se podía vender más de lo disponible (stock negativo)

### Descripción
**Error:** comprar 99 unidades de un producto con stock 2 dejaba el inventario en
`-97`, corrompiendo los datos (inconsistencia en inventario y cobros).

**Causa:** `procesar_pedido` descontaba la cantidad comprada sin comprobar primero
que hubiera stock suficiente:

```python
producto['cantidad'] -= cant_comprada  # BUG: puede quedar negativo
```

**Solución:** validar antes de descontar y rechazar con un `ValueError`
(implementada en `main.py`, líneas 34-39):

```python
if cant_comprada > producto['cantidad']:
    raise ValueError(
        f"Stock insuficiente para '{id_prod}' "
        f"(disponible: {producto['cantidad']}, solicitado: {cant_comprada})"
    )
producto['cantidad'] -= cant_comprada
```

**Pruebas ejecutadas (resultado: ✅ todas pasan):**
- Pedido de 99 con stock 2 → `ValueError` y el stock queda intacto (2).
- Venta exacta al límite (stock 2, pedido 2) → stock queda en 0.

**Pruebas automatizadas (pytest — `test_main.py`):**
- Clase `TestBug5StockNegativo` con 3 casos:
  - `test_pedido_mayor_al_stock_lanza_valueerror`
  - `test_stock_intacto_cuando_no_hay_suficiente`
  - `test_venta_al_limite_exacto_deja_stock_en_cero`
- Ejecutar: `python -m pytest test_main.py -k Bug5`
- Resultado: ✅ 3/3 pasan (suite completa: 18/18).

---

## PR #6 — Rama: `fix/bug-6-iteracion-agotados`

### Título
Fix bug 6: RuntimeError al limpiar productos agotados

### Descripción
**Error:** `limpiar_agotados` lanzaba
`RuntimeError: dictionary changed size during iteration` cada vez que había
productos con cantidad ≤ 0, tumbando el proceso de limpieza del inventario.

**Causa:** se eliminaban elementos del dict mientras se iteraba sobre sus propias
claves:

```python
for id_producto in self.inventario.keys():  # BUG: se modifica el dict al iterar
    if self.inventario[id_producto]['cantidad'] <= 0:
        del self.inventario[id_producto]
```

**Solución:** iterar sobre una copia de las claves (implementada en `main.py`,
línea 58):

```python
for id_producto in list(self.inventario.keys()):
```

**Pruebas ejecutadas (resultado: ✅ todas pasan):**
- Productos con cantidad `0` y negativa → eliminados sin excepciones.
- Productos con stock disponible → se conservan.
- Inventario que queda vacío tras limpiar → `{}`.

**Pruebas automatizadas (pytest — `test_main.py`):**
- Clase `TestBug6RuntimeErrorAlLimpiar` con 3 casos:
  - `test_limpiar_elimina_productos_con_cantidad_cero`
  - `test_limpiar_elimina_productos_con_cantidad_negativa`
  - `test_limpiar_no_lanza_runtimeerror_y_vacia_inventario`
- Ejecutar: `python -m pytest test_main.py -k Bug6`
- Resultado: ✅ 3/3 pasan (suite completa: 18/18).

---

## Verificación global (opcional)

Con los 6 fixes aplicados, el bloque de pruebas integrado de `main.py` se ejecuta
sin errores:

```
Iniciando pruebas del sistema...
Inventario tienda 2: {}
Total del pedido (con descuento): $304000.0
```

Además, la suite automatizada completa valida los 6 fallos:

```
python -m pytest test_main.py
```

Resultado: ✅ 18 passed (3 tests por cada uno de los 6 bugs).