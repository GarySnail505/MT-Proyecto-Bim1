import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def simular_y_animar_trayectorias(solucion):
    """
    Realiza la simulación de trayectorias con ruido (viento) y 
    crea la animación de Matplotlib.
    """
    
    # Configurar la simulación
    t_final = solucion['tc'] + solucion['dt']
    t_valores = np.arange(0, t_final, solucion['dt'])
    g = solucion['g']
    
    # Arrays para almacenar posiciones
    xA, yA = [], []
    xB, yB = [], []
    
    # Velocidades iniciales
    vxA, vyA = solucion['v'] * np.cos(solucion['phi']), solucion['v'] * np.sin(solucion['phi'])
    vxB, vyB = 0, 0
    
    # Posiciones iniciales
    xA_actual, yA_actual = solucion['D'], solucion['h']
    xB_actual, yB_actual = 0, 0
    
    T = solucion['T']
    
    for t in t_valores:
        # Añadir ruido de viento (solo si el proyectil está en el aire)
        ruido_dt = np.sqrt(solucion['dt']) # Escala de ruido correcta para Euler-Maruyama
        
        if yA_actual > 0:
            vxA += np.random.normal(0, solucion['sigma']) * ruido_dt
            vyA += np.random.normal(0, solucion['sigma']) * ruido_dt
        
        if t >= T and yB_actual > 0:
            vxB += np.random.normal(0, solucion['sigma']) * ruido_dt
            vyB += np.random.normal(0, solucion['sigma']) * ruido_dt
        
        # Actualizar posiciones del proyectil A (Método de Euler)
        # La gravedad se aplica como aceleración
        xA_actual += vxA * solucion['dt']
        yA_actual += vyA * solucion['dt']
        vyA -= g * solucion['dt'] # Actualizar velocidad por gravedad
        
        xA.append(xA_actual)
        yA.append(yA_actual)
        
        # Actualizar posiciones del proyectil B
        if t >= T:
            if t < T + solucion['dt']:  # Inicializar proyectil B en t=T
                vxB = solucion['u'] * np.cos(solucion['theta'])
                vyB = solucion['u'] * np.sin(solucion['theta'])
            
            xB_actual += vxB * solucion['dt']
            yB_actual += vyB * solucion['dt']
            vyB -= g * solucion['dt'] # Actualizar velocidad por gravedad
        else:
            xB_actual, yB_actual = 0, 0
        
        xB.append(xB_actual)
        yB.append(yB_actual)
        
        # Detener si algún proyectil toca el suelo
        if yA_actual <= 0 or (t >= T and yB_actual <= 0):
            # Recortar t_valores para que coincida con los datos
            t_valores = t_valores[:len(xA)]
            break
            
    # Crear animación
    crear_animacion(xA, yA, xB, yB, t_valores, solucion)

def crear_animacion(xA, yA, xB, yB, t_valores, solucion):
    """
    Crea y muestra la animación de Matplotlib.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Añadir un margen a los límites
    lim_x_max = max(max(xA, default=0), max(xB, default=0)) * 1.1
    lim_y_max = max(max(yA, default=0), max(yB, default=0)) * 1.1
    # Asegurar que los límites no sean cero
    lim_x_max = max(lim_x_max, solucion['D'] * 1.1, 10)
    lim_y_max = max(lim_y_max, solucion['h'] * 1.1, 10)

    ax.set_xlim(0, lim_x_max)
    ax.set_ylim(0, lim_y_max)
    ax.set_xlabel('Distancia (m)')
    ax.set_ylabel('Altura (m)')
    ax.set_title('Simulación de Colisión de Proyectiles con Efectos de Viento')
    ax.grid(True)
    
    # Crear elementos de la animación
    lineaA, = ax.plot([], [], 'b-', label='Proyectil A')
    lineaB, = ax.plot([], [], 'r-', label='Proyectil B')
    puntoA, = ax.plot([], [], 'bo', markersize=8)
    puntoB, = ax.plot([], [], 'ro', markersize=8)
    texto_tiempo = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    
    ax.legend(loc='upper right')
    
    def init():
        lineaA.set_data([], [])
        lineaB.set_data([], [])
        puntoA.set_data([], [])
        puntoB.set_data([], [])
        texto_tiempo.set_text('')
        return lineaA, lineaB, puntoA, puntoB, texto_tiempo
    
    def animate(i):
        # Actualizar trayectorias
        lineaA.set_data(xA[:i+1], yA[:i+1])
        lineaB.set_data(xB[:i+1], yB[:i+1])
        
        # Actualizar posiciones actuales
        puntoA.set_data([xA[i]], [yA[i]])
        puntoB.set_data([xB[i]], [yB[i]])
        
        texto_tiempo.set_text(f'Tiempo: {t_valores[i]:.2f} s')
        
        return lineaA, lineaB, puntoA, puntoB, texto_tiempo
    
    # Crear animación
    # El intervalo se puede ajustar, 50ms es un buen punto de partida
    intervalo_ms = 1000 * solucion['dt'] 
    
    anim = FuncAnimation(fig, animate, init_func=init,
                       frames=len(xA), interval=intervalo_ms, blit=True,
                       repeat=False)
    
    plt.tight_layout()
    plt.show()