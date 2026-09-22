import pytest

from main import TiendaOnline


def _con_inventario(inventario):
    return TiendaOnline(inventario_inicial=inventario)


class TestBug1InventarioCompartido:
    def test_instancias_tienen_inventarios_independientes(self):
        tienda1 = TiendaOnline()
        tienda2 = TiendaOnline()

        tienda1.agregar_producto("P01", "Teclado Mecánico", 150000, 5)

        assert tienda2.inventario == {}
        assert "P01" in tienda1.inventario

    def test_inventario_vacio_por_defecto(self):
        tienda = TiendaOnline()

        assert tienda.inventario == {}

    def test_inventario_inicial_se_usa_cuando_se_proporciona(self):
        inicial = {"A1": {"nombre": "Mouse", "precio": 80000, "cantidad": 3}}
        tienda = TiendaOnline(inventario_inicial=inicial)

        assert tienda.inventario == inicial


class TestBug2DescuentoInvertido:
    def test_cupon_aplica_20_por_ciento_de_descuento(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto", 100, 10)
        carrito = [{"id_producto": "P01", "cantidad": 1}]

        total = tienda.procesar_pedido(carrito, cupon_descuento="SENA2026")

        assert total == 80.0

    def test_sin_cupon_no_hay_descuento(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto", 100, 10)
        carrito = [{"id_producto": "P01", "cantidad": 1}]

        total = tienda.procesar_pedido(carrito)

        assert total == 100.0

    def test_cupon_con_carrito_multiple(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto", 100, 10)
        tienda.agregar_producto("P02", "Producto 2", 200, 10)
        carrito = [
            {"id_producto": "P01", "cantidad": 1},
            {"id_producto": "P02", "cantidad": 1},
        ]

        total = tienda.procesar_pedido(carrito, cupon_descuento="SENA2026")

        assert total == 240.0


class TestBug3TypoVentasTotales:
    def test_venta_se_registra_sin_attributeerror(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto", 200, 10)
        carrito = [{"id_producto": "P01", "cantidad": 1}]

        tienda.procesar_pedido(carrito)

        assert tienda.ventas_totales == 200.0

    def test_ventas_totales_acumulan_pedidos(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto", 100, 10)
        carrito = [{"id_producto": "P01", "cantidad": 1}]

        tienda.procesar_pedido(carrito)
        tienda.procesar_pedido(carrito)

        assert tienda.ventas_totales == 200.0

    def test_ventas_totales_se_inicializan_en_cero(self):
        tienda = TiendaOnline()

        assert tienda.ventas_totales == 0.0


class TestBug4ProductoInexistente:
    def test_pedido_de_producto_inexistente_lanza_valueerror(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto", 100, 10)
        carrito = [{"id_producto": "NO_EXISTE", "cantidad": 1}]

        with pytest.raises(ValueError, match="NO_EXISTE"):
            tienda.procesar_pedido(carrito)

    def test_error_no_es_keyerror(self):
        tienda = TiendaOnline()
        carrito = [{"id_producto": "NO_EXISTE", "cantidad": 1}]

        with pytest.raises(ValueError) as exc_info:
            tienda.procesar_pedido(carrito)

        assert not isinstance(exc_info.value, KeyError)

    def test_inventario_intacto_tras_error(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto", 100, 10)
        carrito = [{"id_producto": "NO_EXISTE", "cantidad": 2}]

        with pytest.raises(ValueError):
            tienda.procesar_pedido(carrito)

        assert tienda.inventario["P01"]["cantidad"] == 10


class TestBug5StockNegativo:
    def test_pedido_mayor_al_stock_lanza_valueerror(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto", 100, 2)
        carrito = [{"id_producto": "P01", "cantidad": 99}]

        with pytest.raises(ValueError, match="Stock insuficiente"):
            tienda.procesar_pedido(carrito)

    def test_stock_intacto_cuando_no_hay_suficiente(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto", 100, 2)
        carrito = [{"id_producto": "P01", "cantidad": 99}]

        with pytest.raises(ValueError):
            tienda.procesar_pedido(carrito)

        assert tienda.inventario["P01"]["cantidad"] == 2

    def test_venta_al_limite_exacto_deja_stock_en_cero(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto", 100, 2)
        carrito = [{"id_producto": "P01", "cantidad": 2}]

        tienda.procesar_pedido(carrito)

        assert tienda.inventario["P01"]["cantidad"] == 0


class TestBug6RuntimeErrorAlLimpiar:
    def test_limpiar_elimina_productos_con_cantidad_cero(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto 1", 100, 0)
        tienda.agregar_producto("P02", "Producto 2", 100, 5)

        tienda.limpiar_agotados()

        assert "P01" not in tienda.inventario
        assert "P02" in tienda.inventario

    def test_limpiar_elimina_productos_con_cantidad_negativa(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto 1", 100, -3)
        tienda.agregar_producto("P02", "Producto 2", 100, 5)

        tienda.limpiar_agotados()

        assert "P01" not in tienda.inventario
        assert "P02" in tienda.inventario

    def test_limpiar_no_lanza_runtimeerror_y_vacia_inventario(self):
        tienda = TiendaOnline()
        tienda.agregar_producto("P01", "Producto 1", 100, 0)
        tienda.agregar_producto("P02", "Producto 2", 100, -1)

        tienda.limpiar_agotados()

        assert tienda.inventario == {}