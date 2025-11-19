import numpy as np
import logging

def posicion_proyectil_A(t, D, h, v, phi, g):
    """Calcula la posición (x, y) del proyectil A en el tiempo t."""
    x = D + v * np.cos(phi) * t
    y = h + v * np.sin(phi) * t - 0.5 * g * t**2
    return x, y

def posicion_proyectil_B(t, T, u, theta, g):
    """Calcula la posición (x, y) del proyectil B en el tiempo t."""
    if t < T:
        return 0.0, 0.0
    dt = t - T
    x = u * np.cos(theta) * dt
    y = u * np.sin(theta) * dt - 0.5 * g * dt**2
    return x, y

def funcion_velocidad_u(tc, D, h, v, phi, T, g):
    """
    FUNCIÓN CRÍTICAMENTE CORREGIDA - Penaliza colisiones cerca del suelo.
    
    Devuelve la magnitud de velocidad u requerida para que B alcance a A en tc.
    Ahora INCLUYE PENALIZACIÓN para evitar que y(colisión) ≈ 0.
    """
    if tc <= T + 1e-3:  # Debe haber tiempo después de T
        return float('inf')
    
    try:
        # Posición del proyectil A en tc
        xA = D + v * np.cos(phi) * tc
        yA = h + v * np.sin(phi) * tc - 0.5 * g * tc**2
        
        # === CORRECCIÓN CLAVE: Penalización por baja altura ===
        # Si la colisión es muy baja, penalizar exponencialmente
        if yA < 2.0:  # Menor a 2m: rechazar completamente
            return float('inf')
        elif yA < 5.0:  # Entre 2m y 5m: penalización fuerte
            # Penalización cuadrática: cuanto más bajo, más penalizado
            penalizacion_altura = (5.0 / yA)**4  # Exponente 4 para penalización agresiva
        else:
            penalizacion_altura = 1.0  # Sin penalización para y >= 5m
            
        # Verificar que A está en el aire
        if yA <= 0:
            return float('inf')
        
        # Tiempo de vuelo de B
        delta_t = tc - T
        if delta_t < 1e-6:
            return float('inf')
        
        # Componentes de velocidad requeridas para B
        ux = xA / delta_t
        uy = (yA + 0.5 * g * delta_t**2) / delta_t
        
        # Magnitud de velocidad
        u = np.sqrt(ux**2 + uy**2)
        
        # Penalización para velocidades muy bajas (evita soluciones degeneradas)
        if u < 1e-3:
            return float('inf')
        
        penalizacion_baja_vel = 1.0 + (1.0 / (u + 0.1))
        
        # Verificar límites físicos
        if not np.isfinite(u) or u > 5000:
            return float('inf')
            
        # === APLICAR PENALIZACIONES ===
        return u * penalizacion_altura * penalizacion_baja_vel
        
    except Exception:
        return float('inf')

def funcion_angulo_theta(tc, D, h, v, phi, T, g):
    """
    Calcula el ángulo 'theta' del proyectil B.
    Usa la misma lógica que funcion_velocidad_u para consistencia.
    """
    if tc <= T:
        return np.radians(45.0)
    
    try:
        delta_t = tc - T
        if delta_t < 1e-6:
            return np.radians(45.0)
        
        # Posición de A en tc
        xA = D + v * np.cos(phi) * tc
        yA = h + v * np.sin(phi) * tc - 0.5 * g * tc**2
        
        if yA <= 0:
            return np.radians(45.0)
        
        # Componentes de velocidad para B
        ux = xA / delta_t
        uy = (yA + 0.5 * g * delta_t**2) / delta_t
        
        # Calcular ángulo
        theta = np.arctan2(uy, ux)
        
        # Normalizar ángulo al rango [0, π/2]
        if theta < 0:
            theta = abs(theta)
        if theta > np.pi / 2:
            theta = np.pi - theta
            
        return theta
        
    except Exception:
        return np.radians(45.0)

def encontrar_t_max_proyectil_A(h, v, phi, g):
    """Encuentra el tiempo cuando el proyectil A toca el suelo."""
    a = 0.5 * g
    b = -v * np.sin(phi)
    c = -h
    
    discriminante = b**2 - 4 * a * c
    
    if discriminante < 0:
        return (v * np.sin(phi) + np.sqrt(max(0, v**2 * np.sin(phi)**2 + 2 * g * h))) / g
    
    t1 = (-b + np.sqrt(discriminante)) / (2 * a)
    t2 = (-b - np.sqrt(discriminante)) / (2 * a)
    
    candidates = [t for t in (t1, t2) if t > 0 and np.isfinite(t)]
    return max(candidates) if candidates else 10.0

def minimizacion_seccion_dorada(func, a, b, args, tol=1e-6, max_iter=200):
    """Método de la sección dorada para minimización."""
    if a >= b:
        raise ValueError("El intervalo [a,b] no es válido (a >= b).")
    
    gr = (np.sqrt(5) - 1) / 2
    c = b - gr * (b - a)
    d = a + gr * (b - a)
    fc = func(c, *args)
    fd = func(d, *args)

    for _ in range(max_iter):
        if fc < fd:
            b = d
            d = c
            c = b - gr * (b - a)
            fd = fc
            fc = func(c, *args)
        else:
            a = c
            c = d
            d = a + gr * (b - a)
            fc = fd
            fd = func(d, *args)

        if abs(b - a) < tol:
            break

    return (a + b) / 2

def minimizacion_metodo_secante(func, a, b, args, tol=1e-6, max_iter=200):
    """Método secante para encontrar mínimo (busca derivada = 0)."""
    if a >= b:
        raise ValueError("El intervalo [a,b] no es válido (a >= b).")

    def derivada(t, f, args_f, h=1e-6):
        return (f(t + h, *args_f) - f(t - h, *args_f)) / (2 * h)

    x0 = a
    x1 = b
    f0 = derivada(x0, func, args)

    for _ in range(max_iter):
        f1 = derivada(x1, func, args)
        denom = (f1 - f0)
        if abs(denom) < 1e-12:
            return 0.5 * (x0 + x1)
        x2 = x1 - f1 * (x1 - x0) / denom

        if not np.isfinite(x2):
            return x1
        if abs(x2 - x1) < tol:
            return x2

        x0, x1 = x1, x2
        f0 = f1

    return x1

def verificar_factibilidad(D, h, v, phi, T, g):
    """Verifica si existe solución factible."""
    # Verificar que el proyectil A esté en el aire en t=T
    y_en_T = h + v * np.sin(phi) * T - 0.5 * g * T**2
    if y_en_T <= 0:
        return False, f"El proyectil A ya cayó al suelo en t=T (y={y_en_T:.2f}m)"
    
    # Verificar que existe t_max > T
    t_max = encontrar_t_max_proyectil_A(h, v, phi, g)
    if t_max is None or t_max <= T + 1.0:  # Debe haber al menos 1s después de T
        return False, "No existe tiempo de colisión válido (t_max <= T + 1s)"
    
    # Verificar que hay tiempo para que B alcance
    if t_max - T < 0.5:  # Menos de 0.5s de vuelo para B
        return False, "Tiempo insuficiente para que B alcance a A"
    
    return True, ""

def analizar_convergencia(metodo, funcion, a, b, args, tol=1e-6):
    """Analiza la convergencia del método numérico."""
    iteraciones = []
    errores = []
    
    def funcion_con_trazado(tc, *args):
        u = funcion(tc, *args)
        iteraciones.append(tc)
        if len(iteraciones) > 1:
            error = abs(iteraciones[-1] - iteraciones[-2])
            errores.append(error)
        return u
    
    if metodo == "golden":
        resultado = minimizacion_seccion_dorada(funcion_con_trazado, a, b, args, tol)
    else:
        resultado = minimizacion_metodo_secante(funcion_con_trazado, a, b, args, tol)
    
    return resultado, len(iteraciones), errores