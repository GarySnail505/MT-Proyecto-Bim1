import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import calculos
import logging

def simular_y_animar_trayectorias(solucion):
    try:
        # Extraer parámetros
        dt = float(solucion['dt'])
        T = float(solucion['T'])
        tc_teorico = float(solucion['tc'])
        g = float(solucion['g'])
        sigma = float(solucion.get('sigma', 0.0))
        factor_velocidad = float(solucion.get('factor_velocidad', 2.0))
        
        D = solucion['D']
        h = solucion['h']
        v = solucion['v']
        phi = solucion['phi']
        u = solucion['u']
        theta = solucion['theta']

        # Calcular posición TEÓRICA de colisión
        x_col_teo, y_col_teo = calculos.posicion_proyectil_A(tc_teorico, D, h, v, phi, g)

        # Configuración de tiempo
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, g)
        t_final = min(tc_teorico + 1.5, t_max) 
        t_array = np.arange(0, t_final, dt)
        
        # Arrays para guardar trayectoria REAL (con ruido)
        xA_real, yA_real = [], []
        xB_real, yB_real = [], []
        
        # Condiciones iniciales
        # A: posición (D, h), velocidad (-v*cos, v*sin) <-- OJO AL SIGNO
        posA = np.array([float(D), float(h)])
        velA = np.array([-v * np.cos(phi), v * np.sin(phi)]) 
        
        posB = np.array([0.0, 0.0])
        velB = np.array([0.0, 0.0]) # Se define al lanzarse
        
        b_lanzado = False
        colision_detectada = False
        pos_colision_real = (0,0)

        # --- BUCLE DE SIMULACIÓN PREVIA (Cálculo de física) ---
        for t in t_array:
            # Ruido del viento (aleatorio)
            ruido_A = np.random.normal(0, sigma, 2) * dt
            ruido_B = np.random.normal(0, sigma, 2) * dt if b_lanzado else np.zeros(2)
            
            # Física Proyectil A
            velA += np.array([0, -g]) * dt + ruido_A
            posA += velA * dt
            xA_real.append(posA[0])
            yA_real.append(posA[1])
            
            # Física Proyectil B
            if t >= T:
                if not b_lanzado:
                    # Instante de lanzamiento: calcular velocidad inicial
                    velB = np.array([u * np.cos(theta), u * np.sin(theta)])
                    b_lanzado = True
                
                velB += np.array([0, -g]) * dt + ruido_B
                posB += velB * dt
                xB_real.append(posB[0])
                yB_real.append(posB[1])
                
                # Detectar colisión (Distancia < 3m)
                dist = np.sqrt((posA[0]-posB[0])**2 + (posA[1]-posB[1])**2)
                if dist < 3.0 and not colision_detectada:
                    colision_detectada = True
                    pos_colision_real = (posA[0], posA[1])
            else:
                xB_real.append(0)
                yB_real.append(0)

        # Convertir a numpy para graficar
        xA_real = np.array(xA_real)
        yA_real = np.array(yA_real)
        xB_real = np.array(xB_real)
        yB_real = np.array(yB_real)

        # --- CONFIGURACIÓN GRÁFICA ---
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.set_title(f"Simulación con Viento (σ={sigma})", fontsize=14)
        ax.set_xlabel("Distancia X (m)")
        ax.set_ylabel("Altura Y (m)")
        ax.grid(True, alpha=0.3)
        
        # Límites del gráfico
        max_x = max(D, np.max(xB_real)) * 1.1
        max_y = max(h, np.max(yB_real), np.max(yA_real)) * 1.2
        ax.set_xlim(-5, max_x) # Un poco de margen a la izquierda
        ax.set_ylim(0, max_y)
        
        # Elementos gráficos
        lineA, = ax.plot([], [], 'b-', label='Proyectil A (Objetivo)', alpha=0.6)
        lineB, = ax.plot([], [], 'r-', label='Proyectil B (Intercepto)', alpha=0.6)
        puntoA, = ax.plot([], [], 'bo', markersize=8)
        puntoB, = ax.plot([], [], 'ro', markersize=8)
        
        # Marcador de colisión TEÓRICA (Referencia)
        ax.plot(x_col_teo, y_col_teo, 'gx', markersize=10, label='Colisión Teórica') # 
        
        # Texto de información
        info_template = (
            "Tiempo: {:.2f} s\n"
            "Colisión Teórica: ({:.1f}, {:.1f}) m\n"
            "{}" # Espacio para info de colisión real
        )
        texto_info = ax.text(0.02, 0.95, "", transform=ax.transAxes, 
                           bbox=dict(facecolor='white', alpha=0.8))

        def init():
            lineA.set_data([], [])
            lineB.set_data([], [])
            puntoA.set_data([], [])
            puntoB.set_data([], [])
            texto_info.set_text("")
            return lineA, lineB, puntoA, puntoB, texto_info

        def animate(i):
            # Actualizar líneas y puntos
            lineA.set_data(xA_real[:i], yA_real[:i])
            puntoA.set_data([xA_real[i]], [yA_real[i]])
            
            lineB.set_data(xB_real[:i], yB_real[:i])
            puntoB.set_data([xB_real[i]], [yB_real[i]])
            
            # Texto dinámico
            t_actual = t_array[i]
            estado_colision = "Buscando impacto..."
            
            # ### CORRECCIÓN: Mostrar impacto estimado o real en la leyenda
            if b_lanzado and i < len(xB_real):
                dist = np.sqrt((xA_real[i]-xB_real[i])**2 + (yA_real[i]-yB_real[i])**2)
                if dist < 3.0 or (colision_detectada and t_actual > tc_teorico):
                    estado_colision = f"¡IMPACTO!\nPos. Real: ({xB_real[i]:.1f}, {yB_real[i]:.1f}) m\nError: {dist:.2f} m"
                else:
                    estado_colision = f"Distancia: {dist:.2f} m"
            
            texto_info.set_text(info_template.format(t_actual, x_col_teo, y_col_teo, estado_colision))
            
            return lineA, lineB, puntoA, puntoB, texto_info

        # Crear animación
        intervalo = int(1000 * dt / factor_velocidad)
        anim = FuncAnimation(fig, animate, init_func=init, frames=len(t_array), 
                           interval=intervalo, blit=True, repeat=False)
        
        ax.legend(loc='upper right')
        plt.tight_layout()
        plt.show()

    except Exception as e:
        logging.error(f"Error en animación: {e}")
        print(f"Error: {e}")