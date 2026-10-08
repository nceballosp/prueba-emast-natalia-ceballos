from collections import defaultdict

# 1.1 Digito de verificacion del NIT


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


def validar_nit(nit_con_dv: str) -> bool:
    try:
        base, dv = nit_con_dv.rsplit("-", 1)
        dv = dv.strip()

        if not dv.isdigit() or len(dv) != 1:
            return False

        return calcular_dv(base) == int(dv)

    except Exception:
        return False


print(calcular_dv("900373913"))
print(calcular_dv("890.903.938"))
print(calcular_dv("800197268"))
print(validar_nit("900373913-4"))
print(validar_nit("900.373.913-5"))
# print(calcular_dv("90037A913"))
print("La prueba 6 esta comentada para que se imprima lo de los otros ejercicios")
print("-----------")

# 1.2 Espacios libres en la agenda del asesor


def a_minutos(hora):
    return int(hora[:2]) * 60 + int(hora[3:])


def a_texto(minutos):
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def bloques_ocupados(reuniones):
    intervalos = [[720, 780]]

    for r in reuniones:
        inicio, fin = r.split('-')
        ini_m = max(480, a_minutos(inicio))
        fin_m = min(1080, a_minutos(fin))

        if ini_m < fin_m:
            intervalos.append([ini_m, fin_m])

    intervalos.sort()

    bloques = []

    for inv in intervalos:
        if bloques and inv[0] <= bloques[-1][1]:
            bloques[-1][1] = max(bloques[-1][1], inv[1])
        else:
            bloques.append(inv)

    return [f"{a_texto(i)}-{a_texto(f)}" for i, f in bloques]


def espacios_libres(reuniones, duracion_min):
    ocupados = bloques_ocupados(reuniones)
    libres = []
    tiempo_actual = 480

    for bloque in ocupados:
        inicio_str, fin_str = bloque.split('-')
        inicio_ocupado = a_minutos(inicio_str)

        if inicio_ocupado - tiempo_actual >= duracion_min:
            libres.append(f"{a_texto(tiempo_actual)}-{inicio_str}")

        tiempo_actual = a_minutos(fin_str)

    if 1080 - tiempo_actual >= duracion_min:
        libres.append(f"{a_texto(tiempo_actual)}-18:00")

    return libres


reuniones = ["09:00-10:00", "09:30-10:30", "10:30-11:00",
             "14:00-15:15", "07:00-08:30", "16:45-17:30", "11:50-12:20"]
print(bloques_ocupados(reuniones))
print(espacios_libres(reuniones, 30))
print(espacios_libres(reuniones, 60))
print(espacios_libres([], 60))
print("-----------")

# 1.3 Detección de clientes duplicados


def normalizar_email(email):
    if not email:
        return ""
    return str(email).strip().lower()


def normalizar_telefono(telefono):
    if not telefono:
        return ""

    digitos = "".join(filter(str.isdigit, str(telefono)))

    if len(digitos) == 12 and digitos.startswith("57"):
        return digitos[2:]
    return digitos


def agrupar_duplicados(registros):
    email_a_ids = defaultdict(list)
    telefono_a_ids = defaultdict(list)
    todos_los_ids = []

    for id_reg, nombre, email, telefono in registros:
        todos_los_ids.append(id_reg)

        email_norm = normalizar_email(email)
        if email_norm:
            email_a_ids[email_norm].append(id_reg)

        tel_norm = normalizar_telefono(telefono)
        if tel_norm:
            telefono_a_ids[tel_norm].append(id_reg)

    grafo = defaultdict(set)

    def conectar(diccionario):
        for ids in diccionario.values():
            if len(ids) > 1:
                primer_id = ids[0]
                for otro_id in ids[1:]:
                    grafo[primer_id].add(otro_id)
                    grafo[otro_id].add(primer_id)

    conectar(email_a_ids)
    conectar(telefono_a_ids)

    visitados = set()
    grupos_finales = []

    for id_reg in todos_los_ids:
        if id_reg not in visitados:
            pila = [id_reg]
            componente = []

            while pila:
                actual = pila.pop()
                if actual not in visitados:
                    visitados.add(actual)
                    componente.append(actual)

                    for vecino in grafo[actual]:
                        if vecino not in visitados:
                            pila.append(vecino)

            if len(componente) > 1:
                grupos_finales.append(sorted(componente))

    return sorted(grupos_finales, key=lambda x: x[0])


registros = [  # (id, nombre, email, telefono)
    (1, "Ana Gómez", "ana.gomez@acme.co", "+57 300 123 4567"),
    (2, "Ana M. Gómez", " ANA.GOMEZ@acme.co ", "3001234567"),
    (3, "Carlos Ruiz", "cruiz@beta.com", "(604) 444-5566"),
    (4, "Distribuciones Beta", "compras@beta.com", "604 444 5566"),
    (5, "A. Gómez", "agomez@gmail.com", "573001234567"),
    (6, "Luisa Pérez", "", ""),
    (7, "Luisa Perez", "", None),
    (8, "Compras Beta", "COMPRAS@BETA.COM", ""),
    (9, "Pedro Díaz", "pdiaz@gamma.co", "310 999 8877"),
    (10, "Pedro A. Díaz", "pedro.diaz@gamma.co", "57 310 999 88 77"),
]

print(agrupar_duplicados(registros))
