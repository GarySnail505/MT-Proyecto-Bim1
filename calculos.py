import numpy as np

def posicion_proyectil_A(t, D, h, v, phi, g):
    """Calcula la posición (x, y) del proyectil A en el tiempo t."""
    # ### CORRECCIÓN: Signo negativo para lanzar hacia la izquierda (hacia el origen)
    x = D - v * np.cos(phi) * t  
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
    Calcula la velocidad u necesaria y penaliza colisiones muy bajas.
    """
    # Debe haber tiempo de vuelo para B
    if tc <= T + 0.1:  
        return float('inf')
    
    try:
        # 1. Calcular dónde estará A en el tiempo tc
        # ### CORRECCIÓN: Signo negativo en X
        xA = D - v * np.cos(phi) * tc
        yA = h + v * np.sin(phi) * tc - 0.5 * g * tc**2
        
        # 2. RESTRICCIONES DE ALTURA (Para evitar colisiones en el suelo)
        # Si la colisión es muy baja (ej. menor a 3m), devolvemos infinito 
        # para obligar al optimizador a buscar otro punto más alto.
        altura_minima = 3.0  # Metros
        if yA < altura_minima:
            # Penalización suave: si está bajo, aumentamos el "costo" artificialmente
            # Esto hace que el método numérico prefiera alturas mayores
            return float('inf') 

        # Si xA se volvió negativo (pasó el origen), también es inválido
        if xA < 0:
             return float('inf')

        # 3. Calcular velocidad requerida para B
        delta_t = tc - T
        ux = xA / delta_t
        uy = (yA + 0.5 * g * delta_t**2) / delta_t
        
        u = np.sqrt(ux**2 + uy**2)
        
        return u
        
    except Exception:
        return float('inf')

def funcion_angulo_theta(tc, D, h, v, phi, T, g):
    """Calcula el ángulo theta asociado a la velocidad óptima."""
    if tc <= T + 0.001:
        return np.radians(45.0)
    
    try:
        # ### CORRECCIÓN: Signo negativo en X
        xA = D - v * np.cos(phi) * tc
        yA = h + v * np.sin(phi) * tc - 0.5 * g * tc**2
        
        delta_t = tc - T
        ux = xA / delta_t
        uy = (yA + 0.5 * g * delta_t**2) / delta_t
        
        theta = np.arctan2(uy, ux)
        return theta
    except:
        return np.radians(45.0)

def encontrar_t_max_proyectil_A(h, v, phi, g):
    """Tiempo de vuelo total de A hasta tocar el suelo."""
    a = 0.5 * g
    b = -v * np.sin(phi)
    c = -h
    
    discriminante = b**2 - 4 * a * c
    if discriminante < 0: return 0
    
    t = (-b + np.sqrt(discriminante)) / (2 * a)
    return t

# --- MÉTODOS NUMÉRICOS (Sin cambios mayores, solo robustez) ---

def minimizacion_seccion_dorada(func, a, b, args, tol=1e-5, max_iter=100):
    gr = (np.sqrt(5) - 1) / 2
    c = b - gr * (b - a)
    d = a + gr * (b - a)
    
    for _ in range(max_iter):
        fc = func(c, *args)
        fd = func(d, *args)
        if fc < fd:
            b = d; d = c; c = b - gr * (b - a)
        else:
            a = c; c = d; d = a + gr * (b - a)
        if abs(b - a) < tol: break
    return (a + b) / 2

def minimizacion_metodo_secante(func, a, b, args, tol=1e-5, max_iter=100):
    # El método secante busca raíces (derivada = 0). 
    # Usamos una aproximación numérica de la derivada para encontrar el mínimo.
    
    def derivada_aprox(t):
        h = 1e-4
        return (func(t+h, *args) - func(t-h, *args)) / (2*h)

    x0, x1 = a, b
    f0 = derivada_aprox(x0)
    
    for _ in range(max_iter):
        f1 = derivada_aprox(x1)
        if abs(f1 - f0) < 1e-9: break # Evitar división por cero
        
        # Paso de la secante
        x_new = x1 - f1 * (x1 - x0) / (f1 - f0)
        
        # Limitar búsqueda para que no se salga del rango válido [a, b]
        # Esto evita que el método secante "corra" hacia el cero absoluto del eje Y
        x_new = max(a, min(b, x_new))
        
        if abs(x_new - x1) < tol:
            return x_new
            
        x0, x1 = x1, x_new
        f0 = f1
        
    return x1