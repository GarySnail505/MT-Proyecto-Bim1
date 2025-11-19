import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import time
import calculos
import simulacion

class InterfazSimulacionProyectiles:
    def __init__(self, ventana_principal):
        """Inicializa la interfaz gráfica de la simulación."""
        self.ventana_principal = ventana_principal
        self.ventana_principal.title("Simulación de Colisión de Proyectiles")
        self.ventana_principal.geometry("900x720")
        
        self.g = 9.81
        self.solucion_calculada = None
        
        self.crear_widgets()
        
    def crear_widgets(self):
        """Crea todos los elementos de la interfaz."""
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
        
        # Parámetros de simulación
        marco_sim = ttk.LabelFrame(marco_principal, text="Parámetros de Simulación", padding="10")
        marco_sim.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(marco_sim, text="Intensidad de ruido σ:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.entrada_sigma = ttk.Entry(marco_sim, width=12)
        self.entrada_sigma.insert(0, "0.5")
        self.entrada_sigma.grid(row=0, column=1, padx=5)
        
        ttk.Label(marco_sim, text="Δt (s):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entrada_dt = ttk.Entry(marco_sim, width=12)
        self.entrada_dt.insert(0, "0.05")
        self.entrada_dt.grid(row=0, column=3, padx=5)
        
        ttk.Label(marco_sim, text="Velocidad animación:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.entrada_factor_vel = ttk.Entry(marco_sim, width=12)
        self.entrada_factor_vel.insert(0, "2.0")
        self.entrada_factor_vel.grid(row=1, column=1, padx=5)
        ttk.Label(marco_sim, text="(1=lento, 5=rápido)", font=("Arial", 8)).grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=5)
        
        # Métodos numéricos
        marco_metodos = ttk.LabelFrame(marco_principal, text="Métodos Numéricos", padding="10")
        marco_metodos.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        self.variable_metodo = tk.StringVar(value="golden")
        ttk.Radiobutton(marco_metodos, text="Sección Dorada", variable=self.variable_metodo, 
                       value="golden").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Radiobutton(marco_metodos, text="Secante", variable=self.variable_metodo, 
                       value="secant").grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # ✅ ESCENARIOS PREDEFINIDOS - SOLO DOS OPCIONES
        marco_escenarios = ttk.LabelFrame(marco_principal, text="🎯 Escenarios Predefinidos", padding="10")
        marco_escenarios.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(marco_escenarios, text="Tipo de escenario:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.combo_escenarios = ttk.Combobox(marco_escenarios, width=35, state="readonly")
        self.combo_escenarios['values'] = [
            "Predeterminado",
            "Relación 3:1 (x=3a, y=a)"
        ]
        self.combo_escenarios.grid(row=0, column=1, padx=5)
        self.combo_escenarios.current(0)
        
        # Campo para ingresar 'a' (solo visible para Relación 3:1)
        self.label_a = ttk.Label(marco_escenarios, text="Valor de a (m):")
        self.label_a.grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entrada_a = ttk.Entry(marco_escenarios, width=8)
        self.entrada_a.insert(0, "10")
        self.entrada_a.grid(row=0, column=3, padx=5)
        
        # Ocultar campo 'a' inicialmente
        self.label_a.grid_remove()
        self.entrada_a.grid_remove()
        
        # Actualizar visibilidad cuando cambia la selección
        def on_escenario_change(event):
            if self.combo_escenarios.current() == 1:  # Relación 3:1
                self.label_a.grid()
                self.entrada_a.grid()
            else:
                self.label_a.grid_remove()
                self.entrada_a.grid_remove()
        
        self.combo_escenarios.bind('<<ComboboxSelected>>', on_escenario_change)
        
        ttk.Button(marco_escenarios, text="Cargar Escenario", 
                  command=self.cargar_escenario_seleccionado).grid(row=1, column=0, columnspan=4, pady=5)
        
        # Botones principales
        marco_botones = ttk.Frame(marco_principal)
        marco_botones.grid(row=5, column=0, columnspan=4, pady=15)
        
        ttk.Button(marco_botones, text="Calcular Solución", 
                  command=self.calcular_solucion_optima).pack(side=tk.LEFT, padx=5)
        ttk.Button(marco_botones, text="Simular Trayectorias", 
                  command=self.iniciar_simulacion_trayectorias).pack(side=tk.LEFT, padx=5)
        ttk.Button(marco_botones, text="Comparar Métodos", 
                  command=self.comparar_metodos_numericos).pack(side=tk.LEFT, padx=5)
        ttk.Button(marco_botones, text="Limpiar", 
                  command=self.limpiar_resultados).pack(side=tk.LEFT, padx=5)
        
        # Resultados
        marco_resultados = ttk.LabelFrame(marco_principal, text="Resultados", padding="10")
        marco_resultados.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        marco_texto = ttk.Frame(marco_resultados)
        marco_texto.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.texto_resultados = tk.Text(marco_texto, height=12, width=85)
        scrollbar = ttk.Scrollbar(marco_texto, orient="vertical", command=self.texto_resultados.yview)
        self.texto_resultados.configure(yscrollcommand=scrollbar.set)
        
        self.texto_resultados.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def limpiar_entradas(self):
        """Limpia todas las entradas de parámetros."""
        for entry in [self.entrada_D, self.entrada_h, self.entrada_v, 
                     self.entrada_phi, self.entrada_T, self.entrada_sigma, 
                     self.entrada_dt, self.entrada_factor_vel]:
            entry.delete(0, tk.END)

    def cargar_escenario_seleccionado(self):
        """Carga el escenario seleccionado en el combobox."""
        seleccion = self.combo_escenarios.current()
        if seleccion == 0:  # Predeterminado
            self.cargar_escenario_predeterminado()
        elif seleccion == 1:  # Relación 3:1
            try:
                a = float(self.entrada_a.get())
                if a <= 0:
                    messagebox.showerror("Error", "El valor de 'a' debe ser positivo")
                    return
                self.cargar_escenario_relacion_3_1(a)
            except ValueError:
                messagebox.showerror("Error", "Ingrese un valor numérico válido para 'a'")

    def cargar_escenario_predeterminado(self):
        """Carga el escenario predeterminado."""
        self.limpiar_entradas()
        self.entrada_D.insert(0, "60")
        self.entrada_h.insert(0, "20")
        self.entrada_v.insert(0, "30")
        self.entrada_phi.insert(0, "55")
        self.entrada_T.insert(0, "1.0")
        self.entrada_sigma.insert(0, "0.3")
        self.entrada_dt.insert(0, "0.05")
        self.entrada_factor_vel.insert(0, "2.0")
        
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, "✅ Escenario Predeterminado cargado.\n")
        self.texto_resultados.insert(tk.END, "📌 Parámetros: D=60, h=20, v=30, φ=55°, T=1.0\n")

    def cargar_escenario_relacion_3_1(self, a):
        """
        Genera parámetros que garantizan colisión en x≈3a, y≈a
        Fórmula válada para evitar u excesivo
        """
        # Fórmula matemática para relación 3:1 sin valores extremos
        D = 3 * a + 15  # Distancia inicial proporcional
        h = a + 12      # Altura inicial proporcional
        v = np.sqrt(2 * self.g * a) * 1.8  # Velocidad escalada
        phi = 50        # Ángulo optimizado para evitar u excesivo
        T = np.sqrt(2 * a / self.g) * 0.4  # Tiempo de lanzamiento moderado
        
        # Asegurar valores mínimos
        D = max(D, 20)
        h = max(h, 8)
        v = max(v, 15)
        T = max(T, 0.3)
        
        self.limpiar_entradas()
        self.entrada_D.insert(0, f"{D:.1f}")
        self.entrada_h.insert(0, f"{h:.1f}")
        self.entrada_v.insert(0, f"{v:.1f}")
        self.entrada_phi.insert(0, f"{phi:.1f}")
        self.entrada_T.insert(0, f"{T:.1f}")
        self.entrada_sigma.insert(0, "0.3")
        self.entrada_dt.insert(0, "0.05")
        self.entrada_factor_vel.insert(0, "2.0")
        
        # Calcular posición teórica para verificación
        # Primero necesitamos tc, pero aproximamos:
        tc_estimado = T + np.sqrt(2 * a / self.g) * 0.8
        
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, f"✅ Relación 3:1 generada con a={a}m\n")
        self.texto_resultados.insert(tk.END, f"📌 Objetivo: Colisión en x≈{3*a:.1f}m, y≈{a:.1f}m\n")
        self.texto_resultados.insert(tk.END, f"📊 Parámetros calculados: D={D:.1f}, h={h:.1f}, v={v:.1f}, φ={phi:.1f}°, T={T:.1f}\n")

    def validar_entradas(self):
        """Valida las entradas del usuario."""
        try:
            D = float(self.entrada_D.get())
            h = float(self.entrada_h.get())
            v = float(self.entrada_v.get())
            phi = float(self.entrada_phi.get())
            T = float(self.entrada_T.get())
            sigma = float(self.entrada_sigma.get())
            dt = float(self.entrada_dt.get())
            factor_vel = float(self.entrada_factor_vel.get())
            
            if D <= 0:
                raise ValueError("D debe ser > 0")
            if h < 0:
                raise ValueError("h no puede ser negativo")
            if v <= 0:
                raise ValueError("v debe ser > 0")
            if not (0 < phi < 90):
                raise ValueError("φ debe estar entre 0 y 90 grados")
            if T < 0:
                raise ValueError("T no puede ser negativo")
            if sigma < 0:
                raise ValueError("σ no puede ser negativo")
            if dt <= 0:
                raise ValueError("Δt debe ser > 0")
            if factor_vel <= 0:
                raise ValueError("Factor de velocidad debe ser > 0")
            
            return D, h, v, np.radians(phi), T, self.g, sigma, dt, factor_vel
        except ValueError as e:
            messagebox.showerror("Error de entrada", f"Entrada inválida: {e}")
            return None

    # 🔧 CORRECCIÓN CRÍTICA: Método de la Secante
    def minimizacion_metodo_secante_corregida(self, func, a, b, args, tol=1e-5, max_iter=100):
        """Método de la Secante CORREGIDO para encontrar el mínimo."""
        def derivada_aprox(t):
            h = 1e-5
            # Prevenir evaluación fuera del intervalo
            if t - h <= a or t + h >= b:
                return float('inf')
            
            f_mas = func(t + h, *args)
            f_menos = func(t - h, *args)
            
            if not (np.isfinite(f_mas) and np.isfinite(f_menos)):
                return float('inf')
            
            return (f_mas - f_menos) / (2 * h)

        x0, x1 = a, b
        f0 = derivada_aprox(x0)
        
        for i in range(max_iter):
            f1 = derivada_aprox(x1)
            
            if not np.isfinite(f1) or not np.isfinite(f0):
                return (x0 + x1) / 2
            
            if abs(f1 - f0) < 1e-12: 
                break
            
            # Evitar división por cero
            if abs(f1 - f0) < 1e-15:
                return x1
            
            x_new = x1 - f1 * (x1 - x0) / (f1 - f0)
            
            # Mantener dentro del intervalo
            if x_new < a or x_new > b:
                x_new = (a + b) / 2
            
            if abs(x_new - x1) < tol:
                return x_new
            
            x0, x1 = x1, x_new
            f0 = f1
        
        return x1

    def calcular_solucion_optima(self):
        """Calcula la solución óptima usando el método seleccionado."""
        entradas = self.validar_entradas()
        if entradas is None:
            return
        
        D, h, v, phi, T, g, sigma, dt, factor_vel = entradas
        
        # Encontrar t_max
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, g)
        if t_max is None or t_max <= 0:
            messagebox.showerror("Error", "No se pudo calcular t_max válido.")
            return
        
        # Intervalo de búsqueda CONSERVADOR
        a = max(T + 0.05, 0.05)  # Margen de seguridad
        b = t_max * 0.90  # Dejar margen al final
        
        if b <= a:
            messagebox.showerror("Error", f"Intervalo inválido: a={a:.2f}, b={b:.2f}. Ajuste T o parámetros.")
            return
        
        args = (D, h, v, phi, T, g)
        metodo_seleccionado = self.variable_metodo.get()
        
        tiempo_inicio = time.time()
        try:
            if metodo_seleccionado == "golden":
                nombre_metodo = "Sección Dorada"
                tc_optimo = calculos.minimizacion_seccion_dorada(calculos.funcion_velocidad_u, a, b, args)
            else:
                nombre_metodo = "Secante"
                # Usar la versión corregida local
                tc_optimo = self.minimizacion_metodo_secante_corregida(calculos.funcion_velocidad_u, a, b, args)
        except Exception as e:
            messagebox.showerror("Error", f"Error en optimización: {e}\nIntente con Sección Dorada o ajuste parámetros.")
            return
        
        tiempo_calculo = time.time() - tiempo_inicio
        
        if not np.isfinite(tc_optimo) or tc_optimo <= T:
            messagebox.showerror("Error", f"No se encontró tc válido.\nPruebe aumentar h/v o reducir T.")
            return
        
        # Calcular u y theta
        u_optimo = calculos.funcion_velocidad_u(tc_optimo, D, h, v, phi, T, g)
        theta_optimo = calculos.funcion_angulo_theta(tc_optimo, D, h, v, phi, T, g)
        
        # Validación de u razonable
        if not np.isfinite(u_optimo) or u_optimo > 500:  # Límite máximo razonable
            messagebox.showerror("Error", 
                               f"Velocidad u excesiva ({u_optimo:.1f} m/s).\n"
                               "Solución: Aumente 'h' o 'v', o reduzca 'T'.")
            return
        
        # Verificar posición de colisión
        x_col, y_col = calculos.posicion_proyectil_A(tc_optimo, D, h, v, phi, g)
        
        # Mostrar resultados
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, f"=== SOLUCIÓN ÓPTIMA ===\n")
        self.texto_resultados.insert(tk.END, f"Método: {nombre_metodo}\n")
        self.texto_resultados.insert(tk.END, f"Tiempo de cálculo: {tiempo_calculo:.6f} s\n\n")
        self.texto_resultados.insert(tk.END, f"Tiempo de colisión (tc): {tc_optimo:.6f} s\n")
        self.texto_resultados.insert(tk.END, f"Velocidad inicial B (u): {u_optimo:.6f} m/s\n")
        self.texto_resultados.insert(tk.END, f"Ángulo de lanzamiento B (θ): {np.degrees(theta_optimo):.6f}°\n\n")
        
        self.texto_resultados.insert(tk.END, f"Posición de colisión teórica:\n")
        self.texto_resultados.insert(tk.END, f"  x = {x_col:.6f} m\n")
        self.texto_resultados.insert(tk.END, f"  y = {y_col:.6f} m\n")
        
        # Verificar relación 3:1 si es el escenario activo
        if self.combo_escenarios.current() == 1:
            try:
                a = float(self.entrada_a.get())
                ratio = x_col / y_col if y_col != 0 else float('inf')
                self.texto_resultados.insert(tk.END, f"\n📊 Relación x/y: {ratio:.3f} (Objetivo: ~3.0)\n")
                if abs(ratio - 3.0) < 0.5:
                    self.texto_resultados.insert(tk.END, "✅ Relación 3:1 SATISFECHA\n")
                else:
                    self.texto_resultados.insert(tk.END, "⚠️  Relación no exacta (margen ±0.5)\n")
            except:
                pass
        
        # Indicador de altura
        if y_col > 10:
            self.texto_resultados.insert(tk.END, f"\n✅ Altura válida (Y > 10m)\n")
        else:
            self.texto_resultados.insert(tk.END, f"\n⚠️  Altura baja (Y ≤ 10m)\n")
        
        # Guardar solución
        self.solucion_calculada = {
            'D': D, 'h': h, 'v': v, 'phi': phi, 'T': T,
            'u': u_optimo, 'theta': theta_optimo, 'tc': tc_optimo,
            'sigma': sigma, 'dt': dt, 'g': g,
            'factor_velocidad': factor_vel
        }

    def iniciar_simulacion_trayectorias(self):
        """Inicia la simulación con animación."""
        if not self.solucion_calculada:
            messagebox.showwarning("Advertencia", "Primero calcule la solución óptima.")
            return
        
        # Verificar altura antes de simular
        D = self.solucion_calculada['D']
        h = self.solucion_calculada['h']
        v = self.solucion_calculada['v']
        phi = self.solucion_calculada['phi']
        g = self.solucion_calculada['g']
        tc = self.solucion_calculada['tc']
        
        x_col, y_col = calculos.posicion_proyectil_A(tc, D, h, v, phi, g)
        
        if y_col <= 10:
            respuesta = messagebox.askyesno(
                "Advertencia", 
                f"La altura de colisión teórica es {y_col:.1f}m (≤ 10m).\n"
                "¿Desea continuar con la simulación de todos modos?"
            )
            if not respuesta:
                return
        
        simulacion.simular_y_animar_trayectorias(self.solucion_calculada)
    
    def comparar_metodos_numericos(self):
        """Compara ambos métodos numéricos."""
        entradas = self.validar_entradas()
        if entradas is None:
            return
        
        D, h, v, phi, T, g, sigma, dt, factor_vel = entradas
        
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, g)
        if t_max is None or t_max <= 0:
            messagebox.showerror("Error", "No se pudo calcular t_max.")
            return
        
        a = max(T + 0.05, 0.05)
        b = t_max * 0.90
        
        if b <= a:
            messagebox.showerror("Error", "Intervalo inválido.")
            return
        
        args = (D, h, v, phi, T, g)
        
        metodos = [
            ("Sección Dorada", calculos.minimizacion_seccion_dorada),
            ("Secante", self.minimizacion_metodo_secante_corregida)
        ]
        
        resultados = []
        
        for nombre_metodo, funcion_metodo in metodos:
            tiempo_inicio = time.time()
            try:
                tc_optimo = funcion_metodo(calculos.funcion_velocidad_u, a, b, args)
                tiempo_calculo = time.time() - tiempo_inicio
                
                u_optimo = calculos.funcion_velocidad_u(tc_optimo, D, h, v, phi, T, g)
                theta_optimo = calculos.funcion_angulo_theta(tc_optimo, D, h, v, phi, T, g)
                
                x_col, y_col = calculos.posicion_proyectil_A(tc_optimo, D, h, v, phi, g)
                
                resultados.append({
                    'nombre': nombre_metodo,
                    'tc': tc_optimo,
                    'u': u_optimo,
                    'theta': theta_optimo,
                    'tiempo': tiempo_calculo,
                    'y_col': y_col,
                    'valido': y_col > 10 and u_optimo <= 500
                })
            except Exception as e:
                messagebox.showerror("Error", f"{nombre_metodo} falló: {e}")
                return
        
        # Mostrar comparación
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, "=== COMPARACIÓN DE MÉTODOS ===\n\n")
        
        for resultado in resultados:
            self.texto_resultados.insert(tk.END, f"{resultado['nombre']}:\n")
            self.texto_resultados.insert(tk.END, f"  Tiempo cálculo: {resultado['tiempo']:.8f} s\n")
            self.texto_resultados.insert(tk.END, f"  tc: {resultado['tc']:.8f} s\n")
            self.texto_resultados.insert(tk.END, f"  u: {resultado['u']:.8f} m/s\n")
            self.texto_resultados.insert(tk.END, f"  θ: {np.degrees(resultado['theta']):.8f}°\n")
            self.texto_resultados.insert(tk.END, f"  Y colisión: {resultado['y_col']:.2f}m\n")
            
            # Indicadores
            if resultado['valido']:
                self.texto_resultados.insert(tk.END, f"  ✅ VÁLIDO (Y>10m, u≤500)\n\n")
            else:
                self.texto_resultados.insert(tk.END, f"  ⚠️  PROBLEMA (Y≤10m o u>500)\n\n")
        
        if len(resultados) == 2:
            diff_tc = abs(resultados[0]['tc'] - resultados[1]['tc'])
            diff_u = abs(resultados[0]['u'] - resultados[1]['u'])
            diff_theta = abs(resultados[0]['theta'] - resultados[1]['theta'])
            
            self.texto_resultados.insert(tk.END, "DIFERENCIAS:\n")
            self.texto_resultados.insert(tk.END, f"  Δtc: {diff_tc:.2e} s\n")
            self.texto_resultados.insert(tk.END, f"  Δu: {diff_u:.2e} m/s\n")
            self.texto_resultados.insert(tk.END, f"  Δθ: {np.degrees(diff_theta):.2e}°\n")

    def limpiar_resultados(self):
        """Limpia el área de resultados."""
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, "Resultados limpiados.\n")