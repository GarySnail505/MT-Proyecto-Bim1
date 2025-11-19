import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import time
import logging
import sys


# Importar funciones de los otros módulos
import calculos
import simulacion

class InterfazSimulacionProyectiles:
    def __init__(self, ventana_principal):
        """
        Inicializa la interfaz gráfica de la simulación.
        """
        self.ventana_principal = ventana_principal
        self.ventana_principal.title("Simulación de Colisión de Proyectiles")
        self.ventana_principal.geometry("900x720")
        
        # Parámetros por defecto
        self.g = 9.81  # gravedad
        self.solucion_calculada = None # Para almacenar los resultados
        
        # Crear la interfaz
        self.crear_widgets()
        
    def crear_widgets(self):
        """
        Crea y posiciona todos los elementos de la interfaz gráfica (widgets).
        """
        # Frame principal
        marco_principal = ttk.Frame(self.ventana_principal, padding="10")
        marco_principal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        titulo_label = ttk.Label(marco_principal, text="Simulación de Colisión de Proyectiles", 
                                font=("Arial", 16, "bold"))
        titulo_label.grid(row=0, column=0, columnspan=4, pady=10)
        
        # Parámetros del proyectil A
        marco_parametros = ttk.LabelFrame(marco_principal, text="Parámetros del Proyectil A", padding="10")
        marco_parametros.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(marco_parametros, text="D (m):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.entrada_D = ttk.Entry(marco_parametros, width=12)
        self.entrada_D.insert(0, "50")
        self.entrada_D.grid(row=0, column=1, padx=5)
        
        ttk.Label(marco_parametros, text="h (m):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entrada_h = ttk.Entry(marco_parametros, width=12)
        self.entrada_h.insert(0, "10")
        self.entrada_h.grid(row=0, column=3, padx=5)
        
        ttk.Label(marco_parametros, text="v (m/s):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.entrada_v = ttk.Entry(marco_parametros, width=12)
        self.entrada_v.insert(0, "30")
        self.entrada_v.grid(row=1, column=1, padx=5)
        
        ttk.Label(marco_parametros, text="φ (grados):").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.entrada_phi = ttk.Entry(marco_parametros, width=12)
        self.entrada_phi.insert(0, "45")
        self.entrada_phi.grid(row=1, column=3, padx=5)
        
        ttk.Label(marco_parametros, text="T (s):").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.entrada_T = ttk.Entry(marco_parametros, width=12)
        self.entrada_T.insert(0, "2")
        self.entrada_T.grid(row=2, column=1, padx=5)
        
        # Parámetros de viento
        marco_viento = ttk.LabelFrame(marco_principal, text="Parámetros de Viento / Ruido", padding="10")
        marco_viento.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(marco_viento, text="Intensidad de ruido σ:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.entrada_sigma = ttk.Entry(marco_viento, width=12)
        self.entrada_sigma.insert(0, "0.5")
        self.entrada_sigma.grid(row=0, column=1, padx=5)
        
        ttk.Label(marco_viento, text="Δt (s):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entrada_dt = ttk.Entry(marco_viento, width=12)
        self.entrada_dt.insert(0, "0.01")
        self.entrada_dt.grid(row=0, column=3, padx=5)
        
        # Métodos numéricos
        marco_metodos = ttk.LabelFrame(marco_principal, text="Métodos Numéricos", padding="10")
        marco_metodos.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        self.variable_metodo = tk.StringVar(value="golden")
        ttk.Radiobutton(marco_metodos, text="Sección Dorada", variable=self.variable_metodo, 
                       value="golden").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Radiobutton(marco_metodos, text="Newton (Secante)", variable=self.variable_metodo, 
                       value="secant").grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Botones mejorados
        marco_botones = ttk.Frame(marco_principal)
        marco_botones.grid(row=4, column=0, columnspan=4, pady=20)
        
        ttk.Button(marco_botones, text="Calcular Solución Básica", 
                  command=self.calcular_solucion_optima).pack(side=tk.LEFT, padx=5)
        ttk.Button(marco_botones, text="Calcular con Análisis", 
                  command=self.calcular_solucion_optima_mejorada).pack(side=tk.LEFT, padx=5)
        ttk.Button(marco_botones, text="Simular Trayectorias", 
                  command=self.iniciar_simulacion_trayectorias).pack(side=tk.LEFT, padx=5)
        ttk.Button(marco_botones, text="Comparar Métodos", 
                  command=self.comparar_metodos_numericos).pack(side=tk.LEFT, padx=5)
        ttk.Button(marco_botones, text="Limpiar Resultados", 
                  command=self.limpiar_resultados).pack(side=tk.LEFT, padx=5)
        
        # Resultados
        marco_resultados = ttk.LabelFrame(marco_principal, text="Resultados", padding="10")
        marco_resultados.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        # Añadir scrollbar a los resultados
        marco_texto = ttk.Frame(marco_resultados)
        marco_texto.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.texto_resultados = tk.Text(marco_texto, height=12, width=85)
        scrollbar = ttk.Scrollbar(marco_texto, orient="vertical", command=self.texto_resultados.yview)
        self.texto_resultados.configure(yscrollcommand=scrollbar.set)
        
        self.texto_resultados.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # En el método crear_widgets(), reemplaza el marco_viento:

        # Parámetros de viento
        marco_viento = ttk.LabelFrame(marco_principal, text="Parámetros de Viento / Animación", padding="10")
        marco_viento.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(marco_viento, text="Intensidad de ruido σ:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.entrada_sigma = ttk.Entry(marco_viento, width=12)
        self.entrada_sigma.insert(0, "0.5")
        self.entrada_sigma.grid(row=0, column=1, padx=5)

        ttk.Label(marco_viento, text="Δt (s):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entrada_dt = ttk.Entry(marco_viento, width=12)
        self.entrada_dt.insert(0, "0.05")  # Valor por defecto aumentado
        self.entrada_dt.grid(row=0, column=3, padx=5)

        ttk.Label(marco_viento, text="Velocidad animación:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.entrada_factor_vel = ttk.Entry(marco_viento, width=12)
        self.entrada_factor_vel.insert(0, "2.0")  # 2x velocidad por defecto
        self.entrada_factor_vel.grid(row=1, column=1, padx=5)
        ttk.Label(marco_viento, text="(1=lento, 5=muy rápido)", font=("Arial", 8)).grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=5)

    def validar_entradas(self):
        """
        Valida todas las entradas del usuario y las devuelve como flotantes.
        Muestra un error si alguna entrada es inválida.
        """
        try:
            D = float(self.entrada_D.get())
            h = float(self.entrada_h.get())
            v = float(self.entrada_v.get())
            phi = float(self.entrada_phi.get())
            T = float(self.entrada_T.get())
            sigma = float(self.entrada_sigma.get())

            dt = float(self.entrada_dt.get())
            if dt <= 0:
                raise ValueError("Δt debe ser > 0")
            if dt < 0.01:
                if not messagebox.askyesno("Advertencia", 
                                        "Δt muy pequeño puede hacer la animación lenta. ¿Continuar?"):
                    return None

            factor_vel = float(self.entrada_factor_vel.get())
            if factor_vel <= 0:
                raise ValueError("Factor de velocidad debe ser > 0")
            if factor_vel > 10:
                if not messagebox.askyesno("Advertencia", 
                                        "Factor de velocidad muy alto (>10x). ¿Continuar?"):
                    return None
            
            # Validaciones básicas
            if D <= 0:
                raise ValueError("D debe ser > 0")
            if h < 0:
                raise ValueError("h no puede ser negativo")
            if v <= 0:
                raise ValueError("v debe ser > 0")
            if not (0 < phi < 90):
                raise ValueError("φ debe estar entre 0 y 90 grados (no incluidos)")
            if T < 0:
                raise ValueError("T no puede ser negativo")
            if sigma < 0:
                raise ValueError("σ no puede ser negativo")
            if dt <= 0:
                raise ValueError("Δt debe ser > 0")
            
            return D, h, v, np.radians(phi), T, self.g, sigma, dt
        except ValueError as e:
            messagebox.showerror("Error de entrada", f"Entrada inválida: {e}")
            return None

    def validar_entradas_mejorada(self):
        """
        Validación mejorada de entradas con verificación física.
        """
        try:
            # Validaciones básicas existentes
            entradas = self.validar_entradas()
            if entradas is None:
                return None
                
            D, h, v, phi, T, g, sigma, dt = entradas
            
            # Verificación de factibilidad física
            es_factible, mensaje = self.verificar_factibilidad(D, h, v, phi, T, g)
            if not es_factible:
                messagebox.showerror("Error de parámetros", 
                                   f"Los parámetros no permiten una solución física:\n{mensaje}")
                return None
            
            # Verificación adicional de rangos
            if v > 500:  # Velocidad máxima razonable
                if not messagebox.askyesno("Advertencia", 
                                         "Velocidad muy alta (>500 m/s). ¿Continuar?"):
                    return None
            
            if T > 60:   # Tiempo máximo razonable
                if not messagebox.askyesno("Advertencia",
                                         "Tiempo T muy grande (>60 s). ¿Continuar?"):
                    return None
            
            return entradas
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en validación: {e}")
            return None

    def verificar_factibilidad(self, D, h, v, phi, T, g):
        """
        Verifica si existe solución factible para los parámetros dados.
        """
        try:
            # Verificar que el proyectil A esté en el aire en t=T
            y_en_T = h + v * np.sin(phi) * T - 0.5 * g * T**2
            if y_en_T <= 0:
                return False, "El proyectil A ya cayó al suelo en t=T"
            
            # Verificar que existe t_max > T
            t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, g)
            if t_max is None or t_max <= T:
                return False, "No existe tiempo de colisión válido (t_max <= T)"
            
            return True, ""
        except Exception as e:
            return False, f"Error en verificación de factibilidad: {e}"

    def calcular_solucion_optima(self):
        """
        Calcula la solución óptima (tc, u, theta) usando el método numérico seleccionado.
        Versión básica sin análisis de convergencia.
        """
        entradas = self.validar_entradas()
        if entradas is None:
            return
        
        D, h, v, phi, T, g, sigma, dt = entradas
        
        # Encontrar t_max
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, g)
        if t_max is None:
            messagebox.showerror("Error", "No se pudo calcular t_max (discriminante negativo). Revisa parámetros.")
            return
        
        # Definir intervalo de búsqueda: debe ser mayor que T
        a = max(T + 1e-6, 1e-6)
        b = t_max
        if b <= a:
            messagebox.showerror("Error", "Intervalo de búsqueda inválido (t_max <= T). Ajusta parámetros.")
            return
        
        args = (D, h, v, phi, T, g)
        
        metodo_seleccionado = self.variable_metodo.get()
        tiempo_inicio = time.time()
        
        try:
            if metodo_seleccionado == "golden":
                nombre_metodo = "Sección Dorada"
                tc_optimo = calculos.minimizacion_seccion_dorada(calculos.funcion_velocidad_u, a, b, args)
            else:  # secant
                nombre_metodo = "Newton (Secante)"
                tc_optimo = calculos.minimizacion_metodo_secante(calculos.funcion_velocidad_u, a, b, args)
        except Exception as e:
            messagebox.showerror("Error de optimización", f"Ocurrió un error en la optimización: {e}")
            return
        
        tiempo_calculo = time.time() - tiempo_inicio
        
        if not np.isfinite(tc_optimo) or tc_optimo <= T:
            messagebox.showerror("Error", "No se encontró un tc válido. Revisa parámetros.")
            return
        
        # Calcular u y theta
        u_optimo = calculos.funcion_velocidad_u(tc_optimo, D, h, v, phi, T, g)
        theta_optimo = calculos.funcion_angulo_theta(tc_optimo, D, h, v, phi, T, g)
        
        # Mostrar resultados
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, f"=== SOLUCIÓN BÁSICA ===\n")
        self.texto_resultados.insert(tk.END, f"Método utilizado: {nombre_metodo}\n")
        self.texto_resultados.insert(tk.END, f"Tiempo de cálculo: {tiempo_calculo:.6f} segundos\n")
        self.texto_resultados.insert(tk.END, f"Tiempo de colisión óptimo (tc): {tc_optimo:.6f} s\n")
        self.texto_resultados.insert(tk.END, f"Velocidad inicial del proyectil B (u): {u_optimo:.6f} m/s\n")
        self.texto_resultados.insert(tk.END, f"Ángulo de lanzamiento del proyectil B (θ): {np.degrees(theta_optimo):.6f}°\n")
        self.texto_resultados.insert(tk.END, f"Posición de colisión (según A):\n")
        
        x_col, y_col = calculos.posicion_proyectil_A(tc_optimo, D, h, v, phi, g)
        self.texto_resultados.insert(tk.END, f"  x = {x_col:.6f} m\n")
        self.texto_resultados.insert(tk.END, f"  y = {y_col:.6f} m\n")
        
        # Guardar resultados para la simulación
        self.solucion_calculada = {
            'D': D, 'h': h, 'v': v, 'phi': phi, 'T': T,
            'u': u_optimo, 'theta': theta_optimo, 'tc': tc_optimo,
            'sigma': sigma, 'dt': dt, 'g': g
        }

    def calcular_solucion_optima_mejorada(self):
        """
        Versión mejorada con análisis de convergencia y LOGGING.
        """
        entradas = self.validar_entradas_mejorada()
        if entradas is None:
            return
        
        D, h, v, phi, T, g, sigma, dt = entradas
        
        # LOGGING
        logging.info(f"\n{'='*60}")
        logging.info(f"CALCULANDO SOLUCIÓN ÓPTIMA")
        logging.info(f"{'='*60}")
        logging.info(f"Parámetros de entrada: D={D}, h={h}, v={v}, phi={np.degrees(phi):.2f}°, T={T}")
        
        # Encontrar t_max
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, g)
        logging.info(f"t_max calculado: {t_max:.4f}s")
        
        a = max(T + 1e-3, 1e-3)
        b = t_max
        logging.info(f"Intervalo de búsqueda: [{a:.4f}, {b:.4f}]")
        
        args = (D, h, v, phi, T, g)
        metodo_seleccionado = self.variable_metodo.get()
        
        tiempo_inicio = time.time()
        try:
            # Ejecutar con análisis de convergencia
            tc_optimo, num_iteraciones, errores = self.analizar_convergencia(
                metodo_seleccionado, calculos.funcion_velocidad_u, a, b, args)
            
            tiempo_calculo = time.time() - tiempo_inicio
            
            # Calcular resultados
            u_optimo = calculos.funcion_velocidad_u(tc_optimo, D, h, v, phi, T, g)
            theta_optimo = calculos.funcion_angulo_theta(tc_optimo, D, h, v, phi, T, g)
            
            logging.info(f"Resultados:")
            logging.info(f"  tc_optimo: {tc_optimo:.6f}s")
            logging.info(f"  u_optimo: {u_optimo:.6f}m/s")
            logging.info(f"  theta_optimo: {np.degrees(theta_optimo):.6f}°")
            
            # Verificar que la solución es físicamente razonable
            if u_optimo < 1e-3:
                logging.warning(f"¡VELOCIDAD U MUY BAJA! Puede indicar error en optimización")
                messagebox.showwarning("Advertencia", 
                                    f"La velocidad calculada es muy baja ({u_optimo:.4f} m/s). "
                                    f"Revisa los parámetros o el método numérico.")
            
            self.mostrar_analisis_convergencia(tc_optimo, u_optimo, theta_optimo, 
                                            tiempo_calculo, num_iteraciones, errores,
                                            metodo_seleccionado)
            
            # Guardar resultados con logging adicional
            self.solucion_calculada = {
                'D': D, 'h': h, 'v': v, 'phi': phi, 'T': T,
                'u': u_optimo, 'theta': theta_optimo, 'tc': tc_optimo,
                'sigma': sigma, 'dt': dt, 'g': g,
                'factor_velocidad': float(self.entrada_factor_vel.get())
            }
            
            logging.info(f"Solución guardada exitosamente")
            
        except Exception as e:
            logging.error(f"Error en cálculo: {e}")
            messagebox.showerror("Error de optimización", 
                            f"El método numérico no convergió: {e}")

    def analizar_convergencia(self, metodo, funcion, a, b, args, tol=1e-6):
        """
        Analiza la convergencia del método numérico.
        """
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
            resultado = calculos.minimizacion_seccion_dorada(funcion_con_trazado, a, b, args, tol)
        else:
            resultado = calculos.minimizacion_metodo_secante(funcion_con_trazado, a, b, args, tol)
        
        return resultado, len(iteraciones), errores

    def mostrar_analisis_convergencia(self, tc, u, theta, tiempo, iteraciones, errores, metodo):
        """
        Muestra análisis detallado de la convergencia.
        """
        self.texto_resultados.delete(1.0, tk.END)
        
        self.texto_resultados.insert(tk.END, f"=== ANÁLISIS DE CONVERGENCIA ===\n")
        self.texto_resultados.insert(tk.END, f"Método utilizado: {metodo}\n")
        self.texto_resultados.insert(tk.END, f"Tiempo de cálculo: {tiempo:.6f} s\n")
        self.texto_resultados.insert(tk.END, f"Iteraciones realizadas: {iteraciones}\n")
        
        if errores:
            convergencia = "Sí" if errores[-1] < 1e-6 else "No"
            self.texto_resultados.insert(tk.END, f"Convergió: {convergencia}\n")
            self.texto_resultados.insert(tk.END, f"Error final: {errores[-1]:.2e}\n")
            
            # Mostrar evolución del error
            if len(errores) > 1:
                self.texto_resultados.insert(tk.END, f"Tasa de convergencia: {errores[-1]/errores[-2]:.4f}\n")
        
        self.texto_resultados.insert(tk.END, f"\n=== SOLUCIÓN ÓPTIMA ===\n")
        self.texto_resultados.insert(tk.END, f"Tiempo de colisión (tc): {tc:.6f} s\n")
        self.texto_resultados.insert(tk.END, f"Velocidad de B (u): {u:.6f} m/s\n")
        self.texto_resultados.insert(tk.END, f"Ángulo de B (θ): {np.degrees(theta):.6f}°\n")
        
        # Análisis de complejidad
        self.texto_resultados.insert(tk.END, f"\n=== ANÁLISIS DE COMPLEJIDAD ===\n")
        if metodo == "golden":
            self.texto_resultados.insert(tk.END, f"Complejidad teórica: O(log(1/tol))\n")
            self.texto_resultados.insert(tk.END, f"Convergencia: Lineal (0.618)\n")
        else:
            self.texto_resultados.insert(tk.END, f"Complejidad teórica: O(n) - Superlineal\n")
            self.texto_resultados.insert(tk.END, f"Convergencia: Superlineal (~1.618)\n")
        
        self.texto_resultados.insert(tk.END, f"Eficiencia: {iteraciones/tiempo if tiempo > 0 else 'N/A'} iteraciones/s\n")
        
        # Mostrar posición de colisión
        x_col, y_col = calculos.posicion_proyectil_A(tc, self.solucion_calculada['D'], 
                                                   self.solucion_calculada['h'], 
                                                   self.solucion_calculada['v'], 
                                                   self.solucion_calculada['phi'], 
                                                   self.solucion_calculada['g'])
        self.texto_resultados.insert(tk.END, f"\nPosición de colisión:\n")
        self.texto_resultados.insert(tk.END, f"  x = {x_col:.6f} m\n")
        self.texto_resultados.insert(tk.END, f"  y = {y_col:.6f} m\n")
    
    # En el método iniciar_simulacion_trayectorias(), reemplaza la validación:

    def iniciar_simulacion_trayectorias(self):
        """Inicia la simulación con validación robusta."""
        if not self.solucion_calculada:
            messagebox.showwarning("Advertencia", "Primero debe calcular la solución óptima.")
            return
        
        try:
            tc = float(self.solucion_calculada['tc'])
            T = float(self.solucion_calculada['T'])
            u = float(self.solucion_calculada['u'])
            sigma = float(self.solucion_calculada.get('sigma', 0.0))
            
            # VALIDACIONES CRÍTICAS
            if tc <= T:
                messagebox.showerror("Error", f"tc ({tc:.3f}s) debe ser mayor que T ({T:.3f}s)")
                return
            
            if u < 1.0:
                messagebox.showwarning("Advertencia", 
                                    f"Velocidad B muy baja ({u:.2f} m/s). Colisión puede fallar.")
            
            # Verificar altura de colisión
            D = self.solucion_calculada['D']
            h = self.solucion_calculada['h']
            v = self.solucion_calculada['v']
            phi = self.solucion_calculada['phi']
            g = self.solucion_calculada['g']
            
            x_col, y_col = calculos.posicion_proyectil_A(tc, D, h, v, phi, g)
            
            if y_col < 3.0:  # Altura mínima razonable
                messagebox.showwarning("Advertencia", 
                                    f"Colisión teórica muy baja: y={y_col:.2f}m\n"
                                    f"Esto puede indicar que el optimizador encontró una solución "
                                    f"poco realista. Considere aumentar φ o reducir T.")
            
            # Advertencia sobre ruido
            if sigma > 0.5 and u < 30:
                messagebox.showinfo("Información", 
                                f"Ruido alto (σ={sigma}) con velocidad baja (u={u:.1f}) "
                                f"puede prevenir colisión. Reduzca σ o aumente u.")
            
            simulacion.simular_y_animar_trayectorias(self.solucion_calculada)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en simulación: {e}")
    
    def comparar_metodos_numericos(self):
        """
        Compara el rendimiento y resultados de ambos métodos numéricos.
        """
        entradas = self.validar_entradas_mejorada()
        if entradas is None:
            return
        
        D, h, v, phi, T, g, sigma, dt = entradas
        
        # Encontrar t_max
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, g)
        if t_max is None:
            messagebox.showerror("Error", "No se pudo calcular t_max (discriminante negativo). Revisa parámetros.")
            return
        
        a = max(T + 1e-6, 1e-6)
        b = t_max
        if b <= a:
            messagebox.showerror("Error", "Intervalo de búsqueda inválido (t_max <= T). Ajusta parámetros.")
            return
        
        args = (D, h, v, phi, T, g)
        
        # Comparar ambos métodos
        metodos = [
            ("Sección Dorada", calculos.minimizacion_seccion_dorada),
            ("Newton (Secante)", calculos.minimizacion_metodo_secante)
        ]
        
        texto_comparacion = "COMPARACIÓN DE MÉTODOS NUMÉRICOS\n\n"
        resultados = []
        
        for nombre_metodo, funcion_metodo in metodos:
            tiempo_inicio = time.time()
            try:
                tc_optimo = funcion_metodo(calculos.funcion_velocidad_u, a, b, args)
                tiempo_calculo = time.time() - tiempo_inicio
                
                u_optimo = calculos.funcion_velocidad_u(tc_optimo, D, h, v, phi, T, g)
                theta_optimo = calculos.funcion_angulo_theta(tc_optimo, D, h, v, phi, T, g)
                
                resultados.append({
                    'nombre': nombre_metodo,
                    'tc': tc_optimo,
                    'u': u_optimo,
                    'theta': theta_optimo,
                    'tiempo': tiempo_calculo
                })
                
            except Exception as e:
                texto_comparacion += f"{nombre_metodo}: Error en optimización: {e}\n\n"
                continue
        
        # Mostrar comparación
        for resultado in resultados:
            texto_comparacion += f"{resultado['nombre']}:\n"
            texto_comparacion += f"  Tiempo de cálculo: {resultado['tiempo']:.8f} s\n"
            texto_comparacion += f"  tc: {resultado['tc']:.8f} s\n"
            texto_comparacion += f"  u: {resultado['u']:.8f} m/s\n"
            texto_comparacion += f"  θ: {np.degrees(resultado['theta']):.8f}°\n\n"
        
        # Calcular diferencias si ambos métodos tuvieron éxito
        if len(resultados) == 2:
            diff_tc = abs(resultados[0]['tc'] - resultados[1]['tc'])
            diff_u = abs(resultados[0]['u'] - resultados[1]['u'])
            diff_theta = abs(resultados[0]['theta'] - resultados[1]['theta'])
            
            texto_comparacion += "DIFERENCIAS:\n"
            texto_comparacion += f"  Δtc: {diff_tc:.2e} s\n"
            texto_comparacion += f"  Δu: {diff_u:.2e} m/s\n"
            texto_comparacion += f"  Δθ: {np.degrees(diff_theta):.2e}°\n"
        
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, texto_comparacion)

    def limpiar_resultados(self):
        """
        Limpia el área de resultados.
        """
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, "Resultados limpiados.\n")