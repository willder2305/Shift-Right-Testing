import streamlit as st
import time
from datetime import datetime
from html import escape


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Mi Lista de Tareas",
    page_icon="Tareas",
    layout="centered"
)


# =========================================================
# INICIALIZACIÓN DEL ESTADO DE LA SESIÓN
# =========================================================

def inicializar_estado():
    """Inicializa las variables necesarias en st.session_state."""

    if "tareas" not in st.session_state:
        st.session_state.tareas = []

    if "logs" not in st.session_state:
        st.session_state.logs = []

    if "next_id" not in st.session_state:
        st.session_state.next_id = 1

    if "total_acciones" not in st.session_state:
        st.session_state.total_acciones = 0

    if "total_errores" not in st.session_state:
        st.session_state.total_errores = 0

    if "tiempos_respuesta" not in st.session_state:
        st.session_state.tiempos_respuesta = []

    if "ultimo_tiempo" not in st.session_state:
        st.session_state.ultimo_tiempo = 0.0

    # Permite registrar "Aplicación iniciada" solamente una vez.
    if "aplicacion_iniciada" not in st.session_state:
        st.session_state.aplicacion_iniciada = True

        hora = datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.append(
            f"[{hora}] Aplicación iniciada"
        )


inicializar_estado()


# =========================================================
# FUNCIONES DE MONITOREO
# =========================================================

def registrar_log(mensaje, es_error=False, tiempo_ms=None):
    """
    Registra una acción dentro del sistema de monitoreo.
    Opcionalmente registra el tiempo de respuesta.
    """

    hora = datetime.now().strftime("%H:%M:%S")

    if tiempo_ms is not None:
        mensaje = f"{mensaje} | Tiempo: {tiempo_ms:.4f} ms"

        st.session_state.tiempos_respuesta.append(tiempo_ms)
        st.session_state.ultimo_tiempo = tiempo_ms

    st.session_state.logs.append(
        f"[{hora}] {mensaje}"
    )

    st.session_state.total_acciones += 1

    if es_error:
        st.session_state.total_errores += 1


def calcular_tiempo_promedio():
    """Calcula el tiempo promedio de las operaciones medidas."""

    tiempos = st.session_state.tiempos_respuesta

    if not tiempos:
        return 0.0

    return sum(tiempos) / len(tiempos)


# =========================================================
# FUNCIONES PARA LAS TAREAS
# =========================================================

def agregar_tarea(texto):
    """Agrega una nueva tarea."""

    inicio = time.perf_counter()

    texto = texto.strip()

    # Validación de tarea vacía
    if not texto:
        fin = time.perf_counter()
        tiempo_ms = (fin - inicio) * 1000

        registrar_log(
            "ERROR: Se intentó agregar una tarea vacía",
            es_error=True,
            tiempo_ms=tiempo_ms
        )

        return False

    tarea = {
        "id": st.session_state.next_id,
        "texto": texto,
        "completada": False,
        "fecha_creacion": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    st.session_state.tareas.append(tarea)
    st.session_state.next_id += 1

    fin = time.perf_counter()
    tiempo_ms = (fin - inicio) * 1000

    registrar_log(
        f"Tarea creada: {texto}",
        tiempo_ms=tiempo_ms
    )

    return True


def cambiar_estado_tarea(tarea_id, nuevo_estado):
    """Cambia una tarea entre pendiente y completada."""

    inicio = time.perf_counter()

    for tarea in st.session_state.tareas:

        if tarea["id"] == tarea_id:

            tarea["completada"] = nuevo_estado

            fin = time.perf_counter()
            tiempo_ms = (fin - inicio) * 1000

            if nuevo_estado:
                registrar_log(
                    f"Tarea completada: {tarea['texto']}",
                    tiempo_ms=tiempo_ms
                )
            else:
                registrar_log(
                    f"Tarea cambiada a pendiente: {tarea['texto']}",
                    tiempo_ms=tiempo_ms
                )

            break


def eliminar_tarea(tarea_id):
    """Elimina únicamente la tarea seleccionada."""

    inicio = time.perf_counter()

    tarea_encontrada = None

    for tarea in st.session_state.tareas:
        if tarea["id"] == tarea_id:
            tarea_encontrada = tarea
            break

    if tarea_encontrada:

        st.session_state.tareas.remove(tarea_encontrada)

        # Elimina el estado del checkbox si todavía existe.
        clave_checkbox = f"checkbox_{tarea_id}"

        if clave_checkbox in st.session_state:
            del st.session_state[clave_checkbox]

        fin = time.perf_counter()
        tiempo_ms = (fin - inicio) * 1000

        registrar_log(
            f"Tarea eliminada: {tarea_encontrada['texto']}",
            tiempo_ms=tiempo_ms
        )

        return tarea_encontrada["texto"]

    return None


def limpiar_logs():
    """
    Limpia únicamente la información de monitoreo.
    Las tareas permanecen intactas.
    """

    st.session_state.logs = []
    st.session_state.total_acciones = 0
    st.session_state.total_errores = 0
    st.session_state.tiempos_respuesta = []
    st.session_state.ultimo_tiempo = 0.0


# =========================================================
# ESTILOS
# =========================================================

st.markdown(
    """
    <style>

    .titulo-principal {
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitulo {
        text-align: center;
        color: #777;
        margin-bottom: 30px;
    }

    .tarea-pendiente {
        font-size: 17px;
        padding-top: 7px;
    }

    .tarea-completada {
        font-size: 17px;
        padding-top: 7px;
        text-decoration: line-through;
        opacity: 0.6;
    }

    .fecha-tarea {
        font-size: 11px;
        opacity: 0.6;
    }

    .log-box {
        max-height: 350px;
        overflow-y: auto;
        border: 1px solid rgba(128, 128, 128, 0.25);
        padding: 12px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TÍTULO
# =========================================================

st.markdown(
    '<h1 class="titulo-principal"> Mi Lista de Tareas</h1>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitulo">listado de tareas</p>',
    unsafe_allow_html=True
)


# =========================================================
# FORMULARIO PARA AGREGAR TAREA
# =========================================================

# clear_on_submit limpia automáticamente el campo después del envío.
with st.form(
    key="formulario_nueva_tarea",
    clear_on_submit=True
):

    nueva_tarea = st.text_input(
        "Nueva tarea:",
        placeholder="Ejemplo: Tender Cama"
    )

    boton_agregar = st.form_submit_button(
        "➕ Agregar tarea",
        use_container_width=True
    )


if boton_agregar:

    if agregar_tarea(nueva_tarea):
        st.success("Tarea agregada correctamente.")
    else:
        st.warning("Debes escribir una tarea antes de agregarla.")


st.divider()


# =========================================================
# CONTADORES
# =========================================================

total = len(st.session_state.tareas)

completadas = sum(
    1
    for tarea in st.session_state.tareas
    if tarea["completada"]
)

pendientes = total - completadas


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total",
        total
    )

with col2:
    st.metric(
        "Pendientes",
        pendientes
    )

with col3:
    st.metric(
        "Completadas",
        completadas
    )


st.divider()


# =========================================================
# LISTADO DE TAREAS
# =========================================================

st.subheader("Tareas")


if not st.session_state.tareas:

    st.info(
        "Todavía no existen tareas. "
        "Agrega una utilizando el campo superior."
    )

else:

    # Se utiliza una copia para evitar problemas al eliminar
    # elementos mientras se recorre la lista.
    tareas_actuales = list(st.session_state.tareas)

    for tarea in tareas_actuales:

        tarea_id = tarea["id"]

        col_check, col_texto, col_eliminar = st.columns(
            [0.7, 5, 1.5]
        )

        # -------------------------------------------------
        # CHECKBOX
        # -------------------------------------------------

        with col_check:

            nuevo_estado = st.checkbox(
                "Completada",
                value=tarea["completada"],
                key=f"checkbox_{tarea_id}",
                label_visibility="collapsed"
            )

        # Detectar cambio de estado.
        if nuevo_estado != tarea["completada"]:

            cambiar_estado_tarea(
                tarea_id,
                nuevo_estado
            )

            st.rerun()

        # -------------------------------------------------
        # TEXTO DE LA TAREA
        # -------------------------------------------------

        with col_texto:

            texto_seguro = escape(tarea["texto"])

            if tarea["completada"]:

                st.markdown(
                    f"""
                    <div class="tarea-completada">
                        {texto_seguro}
                    </div>

                    <div class="fecha-tarea">
                        Creada: {tarea["fecha_creacion"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div class="tarea-pendiente">
                        {texto_seguro}
                    </div>

                    <div class="fecha-tarea">
                        Creada: {tarea["fecha_creacion"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # -------------------------------------------------
        # BOTÓN ELIMINAR
        # -------------------------------------------------

        with col_eliminar:

            if st.button(
                "Eliminar",
                key=f"eliminar_{tarea_id}",
                use_container_width=True
            ):

                texto_eliminado = eliminar_tarea(tarea_id)

                if texto_eliminado:

                    st.session_state["mensaje_eliminacion"] = (
                        f"Tarea eliminada: {texto_eliminado}"
                    )

                st.rerun()

        st.divider()


# Mostrar mensaje de eliminación después del rerun.
if "mensaje_eliminacion" in st.session_state:

    st.success(
        st.session_state.mensaje_eliminacion
    )

    del st.session_state["mensaje_eliminacion"]


# =========================================================
# PANEL SHIFT RIGHT TESTING
# =========================================================

with st.expander(
    "Monitoreo - Shift Right Testing",
    expanded=False
):

    st.markdown(
        """
        Este panel permite observar el comportamiento de la aplicación
        mientras está funcionando, simulando un monitoreo básico
        utilizado durante **Shift Right Testing**.
        """
    )

    # -----------------------------------------------------
    # MÉTRICAS
    # -----------------------------------------------------

    st.subheader("Métricas")

    promedio = calcular_tiempo_promedio()

    metrica1, metrica2 = st.columns(2)

    with metrica1:

        st.metric(
            "Total de acciones",
            st.session_state.total_acciones
        )

    with metrica2:

        st.metric(
            "Errores registrados",
            st.session_state.total_errores
        )

    metrica3, metrica4 = st.columns(2)

    with metrica3:

        st.metric(
            "Último tiempo",
            f"{st.session_state.ultimo_tiempo:.4f} ms"
        )

    with metrica4:

        st.metric(
            "Tiempo promedio",
            f"{promedio:.4f} ms"
        )

    st.divider()

    # -----------------------------------------------------
    # ACTIVIDAD DEL SISTEMA
    # -----------------------------------------------------

    st.subheader("Actividad del sistema")

    if st.session_state.logs:

        # Mostrar primero los registros más recientes.
        logs_invertidos = list(
            reversed(st.session_state.logs)
        )

        contenido_logs = "<br>".join(
            escape(log)
            for log in logs_invertidos
        )

        st.markdown(
            f"""
            <div class="log-box">
                {contenido_logs}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.info(
            "No existen registros de monitoreo."
        )

    st.divider()

    # -----------------------------------------------------
    # BOTONES DE PRUEBAS
    # -----------------------------------------------------

    boton1, boton2 = st.columns(2)

    with boton1:

        if st.button(
            "Simular error",
            key="simular_error",
            use_container_width=True
        ):

            inicio = time.perf_counter()

            # Simulación controlada.
            mensaje_error = (
                "ERROR SIMULADO: "
                "Fallo al procesar una operación"
            )

            fin = time.perf_counter()
            tiempo_ms = (fin - inicio) * 1000

            registrar_log(
                mensaje_error,
                es_error=True,
                tiempo_ms=tiempo_ms
            )

            st.error(
                "Error simulado detectado. "
                "La aplicación continúa funcionando normalmente."
            )

    with boton2:

        if st.button(
            "Limpiar registros",
            key="limpiar_logs",
            use_container_width=True
        ):

            limpiar_logs()

            st.success(
                "Registros de monitoreo eliminados. "
                "Las tareas no fueron modificadas."
            )

            st.rerun()