import numpy as np

def posicion_proyectil_A(t, D, h, v, phi, g):
    """Calcula la posición (x, y) del proyectil A en el tiempo t."""
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
    Calcula la velocidad u necesaria para colisión en tiempo tc.
    """
    if tc <= T + 0.001:  
        return float('inf')
    
    try:
        # Calcular dónde estará A en el tiempo tc
        xA = D - v * np.cos(phi) * tc
        yA = h + v * np.sin(phi) * tc - 0.5 * g * tc**2
        
        # Si xA es negativo (pasó el origen), es inválido
        if xA < 0:
             return float('inf')
        
        # Si yA es negativo (tocó el suelo), es inválido
        if yA < 0:
            return float('inf')

        # Calcular velocidad requerida para B
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
    if discriminante < 0: 
        return 0
    
    t = (-b + np.sqrt(discriminante)) / (2 * a)
    return t

# --- MÉTODOS NUMÉRICOS OPTIMIZADOS ---

def minimizacion_seccion_dorada(func, a, b, args, tol=1e-5, max_iter=100):
    """Método de la Sección Dorada para minimización. Retorna (valor_optimo, iteraciones)"""
    gr = (np.sqrt(5) - 1) / 2
    c = b - gr * (b - a)
    d = a + gr * (b - a)
    
    for i in range(max_iter):
        fc = func(c, *args)
        fd = func(d, *args)
        if fc < fd:
            b = d
            d = c
            c = b - gr * (b - a)
        else:
            a = c
            c = d
            d = a + gr * (b - a)
        if abs(b - a) < tol: 
            break
    return (a + b) / 2, i + 1  

def minimizacion_metodo_secante(func, a, b, args, tol=1e-5, max_iter=100):
    """
    Método de la Secante robusto. Retorna (valor_optimo, iteraciones)
    """
    def derivada_aprox(t):
        h_step = 1e-5
        if t - h_step <= a or t + h_step >= b: return float('inf')
        
        f_mas = func(t + h_step, *args)
        f_menos = func(t - h_step, *args)
        
        if not (np.isfinite(f_mas) and np.isfinite(f_menos)): return float('inf')
        return (f_mas - f_menos) / (2 * h_step)

    x0, x1 = a + (b - a) * 0.3, a + (b - a) * 0.7
    f0 = derivada_aprox(x0)
    
    for i in range(max_iter):
        f1 = derivada_aprox(x1)
        
        if not np.isfinite(f1) or not np.isfinite(f0): return (x0 + x1) / 2, i + 1
        if abs(f1 - f0) < 1e-12: break
        if abs(f1 - f0) < 1e-15: return x1, i + 1
        
        try: 
            x_new = x1 - f1 * (x1 - x0) / (f1 - f0)
        except ZeroDivisionError: 
            x_new = (a + b) / 2
        
        if x_new < a or x_new > b: x_new = (a + b) / 2
        
        if abs(x_new - x1) < tol: return x_new, i + 1
        
        x0, x1, f0 = x1, x_new, f1
        
    return x1, i + 1  