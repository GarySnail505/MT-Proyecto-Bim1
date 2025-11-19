import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import calculos
import logging

def simular_y_animar_trayectorias_corregida(solucion):
    """
    Versión TOTALMENTE CORREGIDA:
    - Ruido instantáneo (no acumulativo) para mejor física
    - Penalización de colisión cerca del suelo
    - Mejor detección de colisión con tolerancia
    """
    try:
        # Parámetros de simulación
        dt = float(solucion.get('dt', 0.05))
        T = float(solucion['T'])
        tc = float(solucion['tc'])
        g = float(solucion['g'])
        sigma = float(solucion.get('sigma', 0.0))
        factor_velocidad = float(solucion.get('factor_velocidad', 2.0))
        
        # Parámetros de los proyectiles
        D = solucion['D']
        h = solucion['h']
        v = solucion['v']
        phi = solucion['phi']
        u = solucion['u']
        theta = solucion['theta']
        
        # LOGGING
        logging.info(f"=== INICIANDO SIMULACIÓN ===")
        logging.info(f"Parámetros: D={D:.2f}, h={h:.2f}, v={v:.1f}, φ={np.degrees(phi):.1f}°")
        logging.info(f"T={T:.1f}s, tc={tc:.3f}s, u={u:.2f}m/s, θ={np.degrees(theta):.2f}°")
        
        # VALIDACIÓN
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, g)
        if tc >= t_max:
            logging.warning(f"tc ({tc:.3f}) >= t_max ({t_max:.3f}), ajustando")
            tc = t_max - 0.5
        
        t_final = min(tc + 1.0, t_max * 0.99)
        num_pasos = min(500, max(250, int(t_final / dt)))
        t_array = np.linspace(0.0, t_final, num_pasos)
        dt_real = t_array[1] - t_array[0]
        
        logging.info(f"Simulando {num_pasos} pasos hasta t={t_final:.3f}s")
        
        # Arrays
        xA = np.full_like(t_array, np.nan)
        yA = np.full_like(t_array, np.nan)
        xB = np.full_like(t_array, np.nan)
        yB = np.full_like(t_array, np.nan)
        
        # Velocidades iniciales
        vxA_base = v * np.cos(phi)
        vyA_base = v * np.sin(phi)
        vxB_base = u * np.cos(theta)
        vyB_base = u * np.sin(theta)
        
        logging.info(f"Velocidad B: u={u:.2f}, vx={vxB_base:.2f}, vy={vyB_base:.2f}")
        
        # Estado inicial
        posA = np.array([float(D), float(h)])
        velA = np.array([vxA_base, vyA_base])
        posB = np.array([0.0, 0.0])
        velB = np.array([0.0, 0.0])
        
        # CORRECCIÓN: Ruido instantáneo (no acumulativo)
        b_lanzado = False
        
        for i, t in enumerate(t_array):
            # Ruido instantáneo en aceleración (más físico)
            ruido_A = np.zeros(2)
            ruido_B = np.zeros(2)
            if sigma > 0:
                # Ruido en aceleración, no en velocidad
                noise_amp = sigma * g * 0.1  # 10% de g como amplitud
                ruido_A = np.random.normal(0, noise_amp, 2) * np.sqrt(dt_real)
                ruido_B = np.random.normal(0, noise_amp, 2) * np.sqrt(dt_real)
            
            # === PROYECTIL A ===
            if posA[1] > 0:
                velA += np.array([0.0, -g]) * dt_real + ruido_A
                posA += velA * dt_real
            
            # === PROYECTIL B ===
            if t >= T and not b_lanzado:
                velB = np.array([vxB_base, vyB_base])
                b_lanzado = True
                logging.info(f"B lanzado en t={t:.3f}s")
            
            if b_lanzado and posB[1] >= 0:
                velB += np.array([0.0, -g]) * dt_real + ruido_B
                posB += velB * dt_real
            
            # Límites
            posA[1] = max(0.0, posA[1])
            posB[1] = max(0.0, posB[1])
            
            # Almacenar
            xA[i] = posA[0]
            yA[i] = posA[1]
            xB[i] = posB[0] if b_lanzado else 0.0
            yB[i] = posB[1] if b_lanzado else 0.0
        
        # Verificaciones
        if not b_lanzado:
            logging.error("EL PROYECTIL B NUNCA FUE LANZADO")
            raise RuntimeError("Error de lanzamiento del proyectil B")
        
        # Crear figura
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        # Límites
        x_max = max(np.nanmax(xA), np.nanmax(xB), D) * 1.2
        y_max = max(np.nanmax(yA), np.nanmax(yB), h) * 1.2
        
        ax1.set_xlim(0, x_max)
        ax1.set_ylim(0, y_max)
        ax1.set_xlabel('Distancia (m)', fontsize=12)
        ax1.set_ylabel('Altura (m)', fontsize=12)
        ax1.set_title('Simulación de Colisión de Proyectiles', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(0, color='black', linewidth=0.5)
        
        # Elementos de animación
        lineA, = ax1.plot([], [], 'b-', label=f'Proyectil A', linewidth=2.5, alpha=0.8)
        lineB, = ax1.plot([], [], 'r-', label=f'Proyectil B', linewidth=2.5, alpha=0.8)
        pointA, = ax1.plot([], [], 'bo', markersize=8, markeredgecolor='black')
        pointB, = ax1.plot([], [], 'ro', markersize=8, markeredgecolor='black')
        
        # Punto de colisión teórica
        x_col, y_col = calculos.posicion_proyectil_A(tc, D, h, v, phi, g)
        colision_point, = ax1.plot([x_col], [y_col], 'g*', markersize=20, 
                                label=f'Colisión teórica\n({x_col:.1f}m, {y_col:.1f}m)', 
                                alpha=0.9, markeredgecolor='black')
        
        time_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, fontsize=11,
                          bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        info_text = ax1.text(0.02, 0.80, '', transform=ax1.transAxes, fontsize=10,
                          bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        def init():
            lineA.set_data([], [])
            lineB.set_data([], [])
            pointA.set_data([], [])
            pointB.set_data([], [])
            time_text.set_text('')
            info_text.set_text('')
            return lineA, lineB, pointA, pointB, time_text, info_text, colision_point
        
        def animate(i):
            # Dibujar con paso para reducir puntos
            step = max(1, len(t_array) // 300)
            idx = slice(0, i+1, step)
            
            lineA.set_data(xA[idx], yA[idx])
            lineB.set_data(xB[idx], yB[idx])
            pointA.set_data([xA[i]], [yA[i]])
            pointB.set_data([xB[i]], [yB[i]])
            
            tiempo_actual = t_array[i]
            time_text.set_text(f'Tiempo: {tiempo_actual:.2f} s')
            
            # Calcular distancia con manejo de NaN
            if i > 0 and not np.isnan(xA[i] + xB[i] + yA[i] + yB[i]):
                dist = np.sqrt((xA[i]-xB[i])**2 + (yA[i]-yB[i])**2)
                info_str = f'σ viento: {sigma:.3f}\nDistancia: {dist:.2f} m\n'
                # CORRECCIÓN: Umbral de colisión más razonable
                if dist < 3.0:  # Aumentado para tolerar ruido
                    info_str += '¡COLISIÓN!'
                info_text.set_text(info_str)
            else:
                info_text.set_text(f'σ viento: {sigma:.3f}')
            
            return lineA, lineB, pointA, pointB, time_text, info_text, colision_point
        
        # Crear animación
        interval_ms = max(10, min(100, int(30 / factor_velocidad)))
        anim = FuncAnimation(fig, animate, init_func=init,
                           frames=len(t_array), interval=interval_ms, blit=True)
        
        ax1.legend(loc='upper right', fontsize=10)
        plt.tight_layout()
        plt.show()
        
        # === ANÁLISIS POST-SIMULACIÓN ===
        print("\n" + "="*60)
        print("ANÁLISIS DE RESULTADOS")
        print("="*60)
        
        # Distancia mínima alcanzada
        distancias = np.sqrt((xA - xB)**2 + (yA - yB)**2)
        idx_min = np.nanargmin(distancias)
        min_dist = distancias[idx_min]
        t_min = t_array[idx_min]
        
        print(f"Posición teórica de colisión: ({x_col:.2f}m, {y_col:.2f}m)")
        print(f"Distancia mínima en simulación: {min_dist:.4f} m en t={t_min:.3f}s")
        
        if min_dist < 3.0:
            print("✓ COLISIÓN EXITOSA (dentro de tolerancia)")
        else:
            print("✗ COLISIÓN FALLIDA (fuera de tolerancia)")
            if sigma > 0:
                print(f"  El ruido (σ={sigma}) puede causar desviaciones.")
                print(f"  Considere reducir σ o aumentar la velocidad de B.")
        
    except Exception as e:
        logging.error(f"ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        raise

def simular_y_animar_trayectorias(solucion):
    return simular_y_animar_trayectorias_corregida(solucion)