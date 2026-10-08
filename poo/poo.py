from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import re

# Función del ejercicio anterior


def calcular_dv(nit: str) -> int:
    nit_limpio = nit.replace('.', '').strip()

    if not nit_limpio:
        raise ValueError("El NIT está vacío después de limpiarlo.")
    if not nit_limpio.isdigit():
        raise ValueError("El NIT contiene caracteres no numéricos.")
    if len(nit_limpio) > 15:
        raise ValueError("El NIT tiene más de 15 dígitos.")

    pesos = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
    sum = 0
    for i, digito in enumerate(reversed(nit_limpio)):
        sum += int(digito) * pesos[i]

    residuo = sum % 11

    if residuo == 0 or residuo == 1:
        dv = residuo
    else:
        dv = 11 - residuo

    return dv


# EXCEPCIONES DE DOMINIO

class CRMError(Exception):
    """Clase base para excepciones del CRM."""
    pass


class ReglaNegocioError(CRMError):
    pass


class TransicionInvalidaError(CRMError):
    pass


# R1: CLIENTES

class Cliente(ABC):
    def __init__(self, id_cliente: int, nombre: str, email: str):
        if not nombre or not nombre.strip():
            raise ReglaNegocioError("El nombre es obligatorio.")
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            raise ReglaNegocioError("El formato del email es inválido.")

        self.id = id_cliente
        self.nombre = nombre
        self.email = email
        self.fecha_creacion = datetime.now()

    @abstractmethod
    def identificacion(self) -> str:
        pass


class PersonaNatural(Cliente):
    def __init__(self, id_cliente: int, nombre: str, email: str, documento: str):
        super().__init__(id_cliente, nombre, email)
        if not documento.isdigit():
            raise ReglaNegocioError("El documento debe contener solo dígitos.")
        self.documento = documento

    def identificacion(self) -> str:
        return f"CC {self.documento}"


class Contacto:
    def __init__(self, nombre: str, cargo: str, email: str, es_principal: bool = False):
        self.nombre = nombre
        self.cargo = cargo
        self.email = email
        self.es_principal = es_principal


class Empresa(Cliente):
    def __init__(self, id_cliente: int, nombre: str, email: str, nit: str):
        super().__init__(id_cliente, nombre, email)

        # Validación y cálculo de DV
        if '-' in nit:
            base_nit, dv_str = nit.split('-', 1)
            dv_calculado = calcular_dv(base_nit)
            if str(dv_calculado) != dv_str:
                raise ReglaNegocioError(
                    f"El DV del NIT es incorrecto. Se esperaba {dv_calculado}.")
            self.nit = nit
        else:
            dv_calculado = calcular_dv(nit)
            self.nit = f"{nit}-{dv_calculado}"

        self._contactos = []

    def agregar_contacto(self, contacto: Contacto):
        if contacto.es_principal and any(c.es_principal for c in self._contactos):
            raise ReglaNegocioError(
                "La empresa ya tiene un contacto principal establecido.")
        self._contactos.append(contacto)

    @property
    def contactos(self):
        return list(self._contactos)

    def identificacion(self) -> str:
        return f"NIT {self.nit}"


# R4: COTIZACIONES Y POLÍTICAS (PATRÓN STRATEGY)

class PoliticaDescuento(ABC):
    @abstractmethod
    def calcular_descuento(self, subtotal: float) -> float:
        pass


class SinDescuento(PoliticaDescuento):
    def calcular_descuento(self, subtotal: float) -> float:
        return 0.0


class DescuentoPorcentual(PoliticaDescuento):
    def __init__(self, porcentaje: float):
        if not (0 < porcentaje <= 15):
            raise ReglaNegocioError(
                "El porcentaje de descuento debe ser mayor a 0 y hasta 15%.")
        self.porcentaje = porcentaje / 100.0

    def calcular_descuento(self, subtotal: float) -> float:
        return subtotal * self.porcentaje


class DescuentoPorVolumen(PoliticaDescuento):
    def calcular_descuento(self, subtotal: float) -> float:
        if subtotal >= 50_000_000:
            return subtotal * 0.08
        if subtotal >= 20_000_000:
            return subtotal * 0.05
        return 0.0


class EstadoCotizacion(Enum):
    BORRADOR = "Borrador"
    ENVIADA = "Enviada"
    ACEPTADA = "Aceptada"
    RECHAZADA = "Rechazada"


class LineaCotizacion:
    def __init__(self, descripcion: str, cantidad: int, precio_unitario: float):
        if cantidad <= 0:
            raise ReglaNegocioError("La cantidad debe ser > 0.")
        if precio_unitario < 0:
            raise ReglaNegocioError(
                "El precio unitario no puede ser negativo.")
        self.descripcion = descripcion
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario

    def total(self) -> float:
        return self.cantidad * self.precio_unitario


class Cotizacion:
    def __init__(self):
        self._lineas = []
        self.politica_descuento = SinDescuento()
        self.estado = EstadoCotizacion.BORRADOR

    def agregar_linea(self, linea: LineaCotizacion):
        if self.estado != EstadoCotizacion.BORRADOR:
            raise ReglaNegocioError(
                "Solo se pueden modificar líneas en estado Borrador.")
        self._lineas.append(linea)

    def cambiar_politica(self, politica: PoliticaDescuento):
        if self.estado != EstadoCotizacion.BORRADOR:
            raise ReglaNegocioError(
                "Solo se puede cambiar la política de descuento en estado Borrador.")
        self.politica_descuento = politica

    def enviar(self):
        if not self._lineas:
            raise ReglaNegocioError(
                "No se puede enviar una cotización sin líneas.")
        if self.estado != EstadoCotizacion.BORRADOR:
            raise TransicionInvalidaError(
                "Solo una cotización en Borrador se puede enviar.")
        self.estado = EstadoCotizacion.ENVIADA

    def aceptar(self):
        if self.estado != EstadoCotizacion.ENVIADA:
            raise TransicionInvalidaError(
                "Solo se puede aceptar una cotización Enviada.")
        self.estado = EstadoCotizacion.ACEPTADA

    def rechazar(self):
        if self.estado != EstadoCotizacion.ENVIADA:
            raise TransicionInvalidaError(
                "Solo se puede rechazar una cotización Enviada.")
        self.estado = EstadoCotizacion.RECHAZADA

    @property
    def subtotal(self) -> float:
        return round(sum(l.total() for l in self._lineas), 2)

    @property
    def descuento(self) -> float:
        return round(self.politica_descuento.calcular_descuento(self.subtotal), 2)

    @property
    def base(self) -> float:
        return round(self.subtotal - self.descuento, 2)

    @property
    def iva(self) -> float:
        return round(self.base * 0.19, 2)

    @property
    def total(self) -> float:
        return round(self.base + self.iva, 2)


# R3: ACTIVIDADES
class Actividad(ABC):
    def __init__(self, fecha: datetime, asesor: str, descripcion: str):
        self.fecha = fecha
        self.asesor = asesor
        self.descripcion = descripcion

    @abstractmethod
    def resumen(self) -> str: pass

    @abstractmethod
    def minutos_invertidos(self) -> int: pass


class Llamada(Actividad):
    def __init__(self, fecha: datetime, asesor: str, descripcion: str, duracion: int, contesto: bool):
        super().__init__(fecha, asesor, descripcion)
        self.duracion = duracion
        self.contesto = contesto

    def resumen(self) -> str:
        estado = "contestada" if self.contesto else "no contestada"
        return f"Llamada {estado} ({self.duracion} min): {self.descripcion}"

    def minutos_invertidos(self) -> int:
        return self.duracion


class Reunion(Actividad):
    def __init__(self, fecha: datetime, asesor: str, descripcion: str, duracion: int, asistentes: list, presencial: bool):
        super().__init__(fecha, asesor, descripcion)
        if not asistentes:
            raise ReglaNegocioError(
                "Una reunión debe tener al menos un asistente.")
        self.duracion = duracion
        self.asistentes = asistentes
        self.presencial = presencial

    def resumen(self) -> str:
        modo = "presencial" if self.presencial else "virtual"
        return f"Reunión {modo} con {len(self.asistentes)} asistentes: {self.descripcion}"

    def minutos_invertidos(self) -> int:
        return self.duracion + (30 if self.presencial else 0)


class Correo(Actividad):
    def __init__(self, fecha: datetime, asesor: str, descripcion: str, asunto: str, enviado: bool):
        super().__init__(fecha, asesor, descripcion)
        self.asunto = asunto
        self.enviado = enviado

    def resumen(self) -> str:
        dir_str = "Enviado" if self.enviado else "Recibido"
        return f"Correo {dir_str}: {self.asunto}"

    def minutos_invertidos(self) -> int:
        return 5


# R2: OPORTUNIDADES

class Etapa(Enum):
    PROSPECTO = (1, 0.10)
    CALIFICADA = (2, 0.25)
    PROPUESTA = (3, 0.50)
    NEGOCIACION = (4, 0.75)
    GANADA = (5, 1.00)
    PERDIDA = (6, 0.00)


class RegistroHistorial:
    def __init__(self, anterior: Etapa, nueva: Etapa):
        self.anterior = anterior
        self.nueva = nueva
        self.fecha_hora = datetime.now()


class Oportunidad:
    def __init__(self, id_op: int, cliente: Cliente, asesor: str, titulo: str, valor_estimado: float):
        if valor_estimado <= 0:
            raise ReglaNegocioError("El valor estimado debe ser > 0.")
        self.id = id_op
        self.cliente = cliente
        self.asesor = asesor
        self.titulo = titulo
        self.valor_estimado = valor_estimado
        self.fecha_creacion = datetime.now()
        self.etapa = Etapa.PROSPECTO

        self._historial = []
        self._actividades = []
        self._cotizaciones = []

    @property
    def cerrada(self) -> bool:
        return self.etapa in (Etapa.GANADA, Etapa.PERDIDA)

    def avanzar(self):
        if self.cerrada:
            raise TransicionInvalidaError(
                "No se puede avanzar una oportunidad cerrada.")

        transiciones = {
            Etapa.PROSPECTO: Etapa.CALIFICADA,
            Etapa.CALIFICADA: Etapa.PROPUESTA,
            Etapa.PROPUESTA: Etapa.NEGOCIACION
        }

        if self.etapa not in transiciones:
            raise TransicionInvalidaError(
                f"No se puede avanzar directamente desde {self.etapa.name}.")

        nueva = transiciones[self.etapa]
        self._historial.append(RegistroHistorial(self.etapa, nueva))
        self.etapa = nueva

    def ganar(self):
        if self.cerrada:
            raise TransicionInvalidaError("La oportunidad ya está cerrada.")
        if self.etapa != Etapa.NEGOCIACION:
            raise TransicionInvalidaError(
                "Para ganar, la oportunidad debe estar en etapa de Negociación.")

        cot_aceptada = next(
            (c for c in self._cotizaciones if c.estado == EstadoCotizacion.ACEPTADA), None)
        if not cot_aceptada:
            raise ReglaNegocioError(
                "No se puede ganar sin una cotización en estado Aceptada.")

        self.valor_estimado = cot_aceptada.base
        self._historial.append(RegistroHistorial(self.etapa, Etapa.GANADA))
        self.etapa = Etapa.GANADA

    def perder(self, motivo: str):
        if self.cerrada:
            raise TransicionInvalidaError("La oportunidad ya está cerrada.")
        if not motivo or not motivo.strip():
            raise ReglaNegocioError("El motivo de pérdida es obligatorio.")

        self.motivo_perdida = motivo
        self._historial.append(RegistroHistorial(self.etapa, Etapa.PERDIDA))
        self.etapa = Etapa.PERDIDA

    def agregar_actividad(self, actividad: Actividad):
        if self.cerrada:
            raise ReglaNegocioError(
                "No se admiten nuevas actividades en una oportunidad cerrada.")
        self._actividades.append(actividad)

    def agregar_cotizacion(self, cotizacion: Cotizacion):
        if self.cerrada:
            raise ReglaNegocioError(
                "No se admiten nuevas cotizaciones en una oportunidad cerrada.")
        self._cotizaciones.append(cotizacion)

    @property
    def historial(self): return list(self._historial)
    @property
    def actividades(self): return list(self._actividades)
    @property
    def cotizaciones(self): return list(self._cotizaciones)


# R5: SERVICIO DE PIPELINE

class PipelineService:
    def __init__(self):
        self._oportunidades = []

    def registrar_oportunidad(self, op: Oportunidad):
        self._oportunidades.append(op)

    def pronostico_ponderado(self, asesor: str) -> float:
        return sum(op.valor_estimado * op.etapa.value[1]
                   for op in self._oportunidades
                   if op.asesor == asesor and not op.cerrada)

    def oportunidades_estancadas(self, dias: int, hoy: datetime) -> list:
        estancadas = []
        for op in self._oportunidades:
            if op.cerrada:
                continue

            ultima_fecha = op.fecha_creacion
            if op.actividades:
                ultima_fecha = max(act.fecha for act in op.actividades)

            if (hoy - ultima_fecha).days > dias:
                estancadas.append(op)
        return estancadas

    def resumen_por_etapa(self) -> dict:
        resumen = {etapa.name: {"cantidad": 0, "valor": 0.0}
                   for etapa in Etapa}
        for op in self._oportunidades:
            resumen[op.etapa.name]["cantidad"] += 1
            resumen[op.etapa.name]["valor"] += op.valor_estimado
        return resumen


# R6: DEMOSTRACIÓN OBLIGATORIA

if __name__ == "__main__":
    print("=== INICIANDO DEMOSTRACIÓN CRM ===")

    # 1. Crear clientes
    empresa = Empresa(1, "Logística Andina SAS",
                      "contacto@andina.com", "900373913")
    empresa.agregar_contacto(
        Contacto("Juan", "Gerente", "juan@andina.com", True))
    persona = PersonaNatural(
        2, "Mariana López", "mariana@gmail.com", "1144123456")

    pipeline = PipelineService()

    # 2. Oportunidad 1: Implementación CRM
    op_andina = Oportunidad(1, empresa, "Laura",
                            "Implementación CRM", 30_000_000)
    pipeline.registrar_oportunidad(op_andina)

    op_andina.agregar_actividad(
        Llamada(datetime.now(), "Laura", "Primer contacto", 20, True))
    op_andina.agregar_actividad(Reunion(datetime.now(
    ), "Laura", "Toma requerimientos", 60, ["Juan", "Laura", "Pedro"], True))

    # 3. Avanzar y Cotizar
    op_andina.avanzar()  # -> Calificada
    op_andina.avanzar()  # -> Propuesta
    op_andina.avanzar()  # -> Negociacion

    cot = Cotizacion()
    cot.cambiar_politica(DescuentoPorVolumen())
    cot.agregar_linea(LineaCotizacion(
        "Licencias (10 usuarios)", 10, 1_200_000))
    cot.agregar_linea(LineaCotizacion("Implementación", 1, 18_000_000))

    op_andina.agregar_cotizacion(cot)
    cot.enviar()
    cot.aceptar()
    op_andina.ganar()

    # 4. Mostrar resultados requeridos
    print(f"\n--- OPORTUNIDAD GANADA ---")
    print(f"Cliente: {empresa.identificacion()}")
    print(f"Subtotal: ${cot.subtotal:,.2f}")
    print(f"Descuento: ${cot.descuento:,.2f}")
    print(f"Base: ${cot.base:,.2f}")
    print(f"IVA: ${cot.iva:,.2f}")
    print(f"Total Cotización: ${cot.total:,.2f}")
    print(f"Valor final Oportunidad: ${op_andina.valor_estimado:,.2f}")

    print("\nMinutos invertidos totales:")
    total_min = sum(a.minutos_invertidos() for a in op_andina.actividades)
    print(f"{total_min} minutos en {len(op_andina.actividades)} actividades.")

    print("\nHistorial Oportunidad:")
    for h in op_andina.historial:
        print(f" - De {h.anterior.name} a {h.nueva.name}")

    # 5. Oportunidad 2: Mariana López
    op_mariana = Oportunidad(2, persona, "Laura", "Soporte anual", 8_000_000)
    pipeline.registrar_oportunidad(op_mariana)
    op_mariana.avanzar()  # -> Calificada

    print(f"\n--- PRONÓSTICO ASESOR LAURA ---")
    print(
        f"Pronóstico ponderado Laura: ${pipeline.pronostico_ponderado('Laura'):,.2f}")

    # --- PRUEBAS DE ERRORES DE DOMINIO ---
    print("\n--- PRUEBAS DE FALLOS (ERRORES DE DOMINIO) ---")

    # 1. Intentar perder oportunidad ganada
    try:
        op_andina.perder("Se arrepintió")
    except TransicionInvalidaError as e:
        print("PASS (1/4):", e)

    # 2. Agregar línea a cotización ya enviada/aceptada
    try:
        cot.agregar_linea(LineaCotizacion("Extra", 1, 1000))
    except ReglaNegocioError as e:
        print("PASS (2/4):", e)

    # 3. Avanzar oportunidad que está en negociación
    try:
        op_mariana.avanzar()  # a Propuesta
        op_mariana.avanzar()  # a Negociación
        op_mariana.avanzar()  # de Negociación falla
    except TransicionInvalidaError as e:
        print("PASS (3/4):", e)

    # 4. Crear descuento porcentual fuera de rango
    try:
        DescuentoPorcentual(20)  # 20% no permitido
    except ReglaNegocioError as e:
        print("PASS (4/4):", e)

    print("\n=== DEMO FINALIZADA CON ÉXITO ===")
