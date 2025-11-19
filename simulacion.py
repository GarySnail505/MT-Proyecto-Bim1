import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import calculos

def simular_y_animar_trayectorias(solucion):
    """
    Simula y anima las trayectorias de ambos proyectiles.
    Al final muestra comparación entre posición teórica vs real.
    """
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

        # Calcular posición TEÓRICA de colisión (sin ruido)
        x_col_teo, y_col_teo = calculos.posicion_proyectil_A(tc_teorico, D, h, v, phi, g)

        # Configuración de tiempo
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, g)
        t_final = min(tc_teorico + 1.5, t_max) 
        t_array = np.arange(0, t_final, dt)
        
        # Arrays para guardar trayectoria REAL (con ruido)
        xA_real, yA_real = [], []
        xB_real, yB_real = [], []
        
        # Condiciones iniciales
        posA = np.array([float(D), float(h)])
        velA = np.array([-v * np.cos(phi), v * np.sin(phi)]) 
        
        posB = np.array([0.0, 0.0])
        velB = np.array([0.0, 0.0])
        
        b_lanzado = False
        colision_detectada = False
        pos_colision_real = None
        tiempo_colision_real = None

        # SIMULACIÓN CON RUIDO
        for i, t in enumerate(t_array):
            # Ruido del viento
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
                    pos_colision_real = ((posA[0] + posB[0])/2, (posA[1] + posB[1])/2)
                    tiempo_colision_real = t
            else:
                xB_real.append(0)
                yB_real.append(0)

        # Convertir a numpy
        xA_real = np.array(xA_real)
        yA_real = np.array(yA_real)
        xB_real = np.array(xB_real)
        yB_real = np.array(yB_real)

        # CONFIGURACIÓN GRÁFICA
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_title(f"Simulación con Viento (σ={sigma})", fontsize=14)
        ax.set_xlabel("Distancia X (m)")
        ax.set_ylabel("Altura Y (m)")
        ax.grid(True, alpha=0.3)
        
        # Límites del gráfico
        max_x = max(D, np.max(xB_real)) * 1.1
        max_y = max(h, np.max(yB_real), np.max(yA_real)) * 1.2
        ax.set_xlim(-5, max_x)
        ax.set_ylim(0, max_y)
        
        # Elementos gráficos
        lineA, = ax.plot([], [], 'b-', label='Proyectil A (Objetivo)', alpha=0.6, linewidth=2)
        lineB, = ax.plot([], [], 'r-', label='Proyectil B (Interceptor)', alpha=0.6, linewidth=2)
        puntoA, = ax.plot([], [], 'bo', markersize=10)
        puntoB, = ax.plot([], [], 'ro', markersize=10)
        
        # Marcador de colisión TEÓRICA
        ax.plot(x_col_teo, y_col_teo, 'g*', markersize=15, 
                label=f'Colisión Teórica ({x_col_teo:.1f}, {y_col_teo:.1f})m')
        
        # Texto de información
        texto_info = ax.text(0.02, 0.95, "", transform=ax.transAxes, 
                           verticalalignment='top',
                           bbox=dict(facecolor='white', alpha=0.8),
                           fontsize=10)

        def init():
            lineA.set_data([], [])
            lineB.set_data([], [])
            puntoA.set_data([], [])
            puntoB.set_data([], [])
            texto_info.set_text("")
            return lineA, lineB, puntoA, puntoB, texto_info

        def animate(i):
            lineA.set_data(xA_real[:i], yA_real[:i])
            puntoA.set_data([xA_real[i]], [yA_real[i]])
            
            lineB.set_data(xB_real[:i], yB_real[:i])
            puntoB.set_data([xB_real[i]], [yB_real[i]])
            
            t_actual = t_array[i]
            
            # Información dinámica
            info_text = f"Tiempo: {t_actual:.2f} s\n"
            info_text += f"Posición Teórica: ({x_col_teo:.1f}, {y_col_teo:.1f}) m\n"
            
            if b_lanzado and i < len(xB_real):
                dist = np.sqrt((xA_real[i]-xB_real[i])**2 + (yA_real[i]-yB_real[i])**2)
                
                if colision_detectada and t_actual >= tiempo_colision_real:
                    info_text += f"\n¡COLISIÓN DETECTADA!\n"
                    info_text += f"Posición Real: ({pos_colision_real[0]:.1f}, {pos_colision_real[1]:.1f}) m\n"
                    info_text += f"Tiempo Real: {tiempo_colision_real:.2f} s\n"
                    error_x = abs(pos_colision_real[0] - x_col_teo)
                    error_y = abs(pos_colision_real[1] - y_col_teo)
                    info_text += f"Error X: {error_x:.2f} m\n"
                    info_text += f"Error Y: {error_y:.2f} m"
                else:
                    info_text += f"Distancia actual: {dist:.2f} m"
            
            texto_info.set_text(info_text)
            
            return lineA, lineB, puntoA, puntoB, texto_info

        # Crear animación
        intervalo = int(1000 * dt / factor_velocidad)
        anim = FuncAnimation(fig, animate, init_func=init, frames=len(t_array), 
                           interval=intervalo, blit=True, repeat=False)
        
        ax.legend(loc='upper right', fontsize=9)
        plt.tight_layout()
        
        # MOSTRAR COMPARACIÓN FINAL
        if colision_detectada:
            print("\n" + "="*60)
            print("RESULTADOS DE LA SIMULACIÓN")
            print("="*60)
            print(f"Colisión Teórica (sin ruido):")
            print(f"  Posición: ({x_col_teo:.3f}, {y_col_teo:.3f}) m")
            print(f"  Tiempo: {tc_teorico:.3f} s")
            print(f"\nColisión Real (con ruido σ={sigma}):")
            print(f"  Posición: ({pos_colision_real[0]:.3f}, {pos_colision_real[1]:.3f}) m")
            print(f"  Tiempo: {tiempo_colision_real:.3f} s")
            print(f"\nError de Posición:")
            print(f"  Error en X: {abs(pos_colision_real[0] - x_col_teo):.3f} m")
            print(f"  Error en Y: {abs(pos_colision_real[1] - y_col_teo):.3f} m")
            print(f"  Error en Tiempo: {abs(tiempo_colision_real - tc_teorico):.3f} s")
            print("="*60 + "\n")
        else:
            print("\n" + "="*60)
            print("ADVERTENCIA: No se detectó colisión en la simulación")
            print("="*60)
            print(f"Colisión Teórica esperada en:")
            print(f"  Posición: ({x_col_teo:.3f}, {y_col_teo:.3f}) m")
            print(f"  Tiempo: {tc_teorico:.3f} s")
            print(f"\nEl ruido (σ={sigma}) pudo haber impedido la colisión.")
            print("Intente reducir σ o ajustar los parámetros.")
            print("="*60 + "\n")
        
        plt.show()

    except Exception as e:
        print(f"Error en simulación: {e}")
        import traceback
        traceback.print_exc()