import numpy as np

def posicion_proyectil_A(t, D, h, v, phi, g):
    """
    Calcula la posición (x, y) del proyectil A en el tiempo t.
    """
    x = D + v * np.cos(phi) * t
    y = h + v * np.sin(phi) * t - 0.5 * g * t**2
    return x, y

def posicion_proyectil_B(t, T, u, theta, g):
    """
    Calcula la posición (x, y) del proyectil B en el tiempo t.
    Se lanza en t=T.
    """
    if t < T:
        return 0, 0
    dt = t - T  # Tiempo transcurrido desde el lanzamiento de B
    x = u * np.cos(theta) * dt
    y = u * np.sin(theta) * dt - 0.5 * g * dt**2
    return x, y

def funcion_velocidad_u(tc, D, h, v, phi, T, g):
    """
    Función de la velocidad 'u' del proyectil B que se debe minimizar.
    Calculada en función del tiempo de colisión 'tc'.
    """
    if tc <= T:
        return float('inf') # La colisión debe ser después de T
    
    # Posición de colisión (calculada desde el proyectil A)
    x_col, y_col_A = posicion_proyectil_A(tc, D, h, v, phi, g)
    
    # Ecuaciones de B en t=tc
    # x_col = u * cos(theta) * (tc - T)
    # y_col_A = u * sin(theta) * (tc - T) - 0.5 * g * (tc - T)**2
    
    # Despejamos y_col de B
    # y_col_B = y_col_A + 0.5 * g * (tc - T)**2
    y_col_B = y_col_A + 0.5 * g * (tc - T)**2
    
    # u * cos(theta) = x_col / (tc - T)
    # u * sin(theta) = y_col_B / (tc - T)
    
    # u^2 = (u*cos)^2 + (u*sin)^2
    u_cuadrado = (x_col / (tc - T))**2 + (y_col_B / (tc - T))**2
    
    # Ecuación original (corregida según el desarrollo matemático implícito)
    # El desarrollo en tu código original es diferente, vamos a usar ese
    # para mantener la consistencia:
    
    # x_col = D + v * cos(phi) * tc
    # y_col = h + v * sin(phi) * tc - 0.5 * g * tc^2
    
    # x_col = u * cos(theta) * (tc - T)
    # y_col = u * sin(theta) * (tc - T) - 0.5 * g * (tc - T)^2
    
    # (1) u * cos(theta) = x_col / (tc - T)
    # (2) u * sin(theta) = (y_col + 0.5 * g * (tc - T)^2) / (tc - T)
    
    # u^2 = (u*cos)^2 + (u*sin)^2
    # u^2 = [x_col^2 + (y_col + 0.5 * g * (tc - T)^2)^2] / (tc - T)^2
    # u = sqrt[x_col^2 + (y_col + 0.5 * g * (tc - T)^2)^2] / (tc - T)
    
    x_col = D + v * np.cos(phi) * tc
    y_col = h + v * np.sin(phi) * tc - 0.5 * g * tc**2
    
    numerador_y = y_col + 0.5 * g * (tc - T)**2
    
    u = np.sqrt(x_col**2 + numerador_y**2) / (tc - T)
    
    # La función original era:
    # num_x = D + v * np.cos(phi) * tc
    # num_y = h + v * np.sin(phi) * tc - self.g * tc * T + 0.5 * self.g * T**2
    # u = np.sqrt(num_x**2 + num_y**2) / (tc - T)
    
    # Derivacion esta derivación:
    # y_col + 0.5 * g * (tc - T)**2
    # = (h + v*sin*tc - 0.5*g*tc^2) + 0.5*g*(tc^2 - 2*tc*T + T^2)
    # = h + v*sin*tc - 0.5*g*tc^2 + 0.5*g*tc^2 - g*tc*T + 0.5*g*T^2
    # = h + v*sin*tc - g*tc*T + 0.5*g*T^2
    
    numerador_x = D + v * np.cos(phi) * tc
    numerador_y = h + v * np.sin(phi) * tc - g * tc * T + 0.5 * g * T**2
    
    u = np.sqrt(numerador_x**2 + numerador_y**2) / (tc - T)
    return u

def funcion_angulo_theta(tc, D, h, v, phi, T, g):
    """
    Calcula el ángulo 'theta' del proyectil B en función del tiempo de colisión 'tc'.
    """
    # (1) u * cos(theta) = x_col / (tc - T)
    # (2) u * sin(theta) = (y_col + 0.5 * g * (tc - T)^2) / (tc - T)
    # tan(theta) = (2) / (1)
    
    # El numerador_y de la función anterior es (y_col + 0.5 * g * (tc - T)^2)
    # El numerador_x de la función anterior es x_col
    
    numerador_x = D + v * np.cos(phi) * tc
    numerador_y = h + v * np.sin(phi) * tc - g * tc * T + 0.5 * g * T**2
    
    theta = np.arctan2(numerador_y, numerador_x)
    return theta

def encontrar_t_max_proyectil_A(h, v, phi, g):
    """
    Encuentra el tiempo en que el proyectil A toca el suelo (y=0).
    y = h + v*sin(phi)*t - 0.5*g*t^2 = 0
    0.5*g*t^2 - v*sin(phi)*t - h = 0
    Usando la fórmula cuadrática: t = [-b ± sqrt(b^2 - 4ac)] / 2a
    """
    a = 0.5 * g
    b = -v * np.sin(phi)
    c = -h
    
    discriminante = b**2 - 4*a*c
    # Solo nos interesa la raíz positiva
    t_max = (-b + np.sqrt(discriminante)) / (2 * a)
    return t_max

def minimizacion_seccion_dorada(func, a, b, args, tol=1e-6, max_iter=100):
    """
    Método de minimización de la sección dorada.
    """
    gr = (np.sqrt(5) - 1) / 2  # Proporción áurea
    
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

def minimizacion_metodo_secante(func, a, b, args, tol=1e-6, max_iter=100):
    """
    Método de minimización de Newton (variante Secante).
    Encuentra el cero de la primera derivada.
    """
    # Derivada numérica (fórmula de la diferencia central)
    def derivada(t, func_deriv, args_deriv, h=1e-6):
        return (func_deriv(t + h, *args_deriv) - func_deriv(t - h, *args_deriv)) / (2 * h)
    
    x0, x1 = a, b
    f0 = derivada(x0, func, args)
    
    for _ in range(max_iter):
        f1 = derivada(x1, func, args)
        
        if abs(f1 - f0) < 1e-12: # Evitar división por cero
            break
            
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        
        if abs(x2 - x1) < tol:
            return x2
            
        x0, x1 = x1, x2
        f0 = f1
    
    return x1