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
        self.ventana_principal.geometry("950x720")
        
        self.g = 9.81
        self.solucion_calculada = None
        self.escenarios_unificados = []  # Lista única de escenarios
        
        self.crear_widgets()
        
    def crear_widgets(self):
        """Crea todos los elementos de la interfaz con Scrollbar."""
        
        # --- CONFIGURACIÓN DEL SCROLLBAR GENERAL ---
        main_container = ttk.Frame(self.ventana_principal)
        main_container.pack(fill=tk.BOTH, expand=True)

        my_canvas = tk.Canvas(main_container)
        my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        my_scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=my_canvas.yview)
        my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        
        scrollable_frame = ttk.Frame(my_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: my_canvas.configure(
                scrollregion=my_canvas.bbox("all")
            )
        )

        my_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_mousewheel(event):
            my_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        my_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        my_canvas.bind_all("<Button-4>", lambda e: my_canvas.yview_scroll(-1, "units"))
        my_canvas.bind_all("<Button-5>", lambda e: my_canvas.yview_scroll(1, "units"))

        # --- WIDGETS ---
        
        marco_principal = ttk.Frame(scrollable_frame, padding="10")
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
        self.entrada_D.insert(0, "120") 
        self.entrada_D.grid(row=0, column=1, padx=5)
        
        ttk.Label(marco_parametros, text="h (m):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entrada_h = ttk.Entry(marco_parametros, width=12)
        self.entrada_h.insert(0, "20")
        self.entrada_h.grid(row=0, column=3, padx=5)
        
        ttk.Label(marco_parametros, text="v (m/s):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.entrada_v = ttk.Entry(marco_parametros, width=12)
        self.entrada_v.insert(0, "25")
        self.entrada_v.grid(row=1, column=1, padx=5)
        
        ttk.Label(marco_parametros, text="φ (grados):").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.entrada_phi = ttk.Entry(marco_parametros, width=12)
        self.entrada_phi.insert(0, "45")
        self.entrada_phi.grid(row=1, column=3, padx=5)
        
        ttk.Label(marco_parametros, text="T (s):").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.entrada_T = ttk.Entry(marco_parametros, width=12)
        self.entrada_T.insert(0, "2.0")
        self.entrada_T.grid(row=2, column=1, padx=5)
        
        # Parámetros de simulación
        marco_sim = ttk.LabelFrame(marco_principal, text="Parámetros de Simulación", padding="10")
        marco_sim.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(marco_sim, text="Intensidad de ruido σ:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.entrada_sigma = ttk.Entry(marco_sim, width=12)
        self.entrada_sigma.insert(0, "0.2")
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
        
        radio_golden = ttk.Radiobutton(marco_metodos, text="Sección Dorada", variable=self.variable_metodo, 
                       value="golden", command=self.actualizar_escenarios)
        radio_golden.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        radio_secant = ttk.Radiobutton(marco_metodos, text="Secante", variable=self.variable_metodo, 
                       value="secant", command=self.actualizar_escenarios)
        radio_secant.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Escenarios
        marco_escenarios = ttk.LabelFrame(marco_principal, text="🎯 Escenarios Predefinidos (Unificados)", padding="10")
        marco_escenarios.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(marco_escenarios, text="Seleccionar escenario:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.combo_escenarios = ttk.Combobox(marco_escenarios, width=50, state="readonly")
        self.combo_escenarios.grid(row=0, column=1, padx=5)
        
        self.label_a = ttk.Label(marco_escenarios, text="Valor de a (m):")
        self.label_a.grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entrada_a = ttk.Entry(marco_escenarios, width=8)
        self.entrada_a.insert(0, "10")
        self.entrada_a.grid(row=0, column=3, padx=5)
        
        self.label_a.grid_remove()
        self.entrada_a.grid_remove()
        
        def on_escenario_change(event):
            if "Relación 3:1" in self.combo_escenarios.get():
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
        scrollbar_texto = ttk.Scrollbar(marco_texto, orient="vertical", command=self.texto_resultados.yview)
        self.texto_resultados.configure(yscrollcommand=scrollbar_texto.set)
        
        self.texto_resultados.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_texto.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Inicializar escenarios
        self.definir_escenarios()
        self.actualizar_escenarios()

    def definir_escenarios(self):
        """Define una lista UNIFICADA de escenarios para ambos métodos."""
        self.escenarios_unificados = [
            "1. Estándar (Distancia Segura) - Muy Estable",
            "2. Tiro desde Altura (h=50m) - Preciso", 
            "3. Larga Distancia (D=150m) - Potencia",
            "4. Intercepción Rápida (T=0.5s) - Veloz",
            "5. Caída Vertical (Ángulo Alto Corregido)",
            "9. Relación 3:1 (x=3a, y=a) - Personalizado"
        ]

    def actualizar_escenarios(self):
        """Actualiza el combobox."""
        self.combo_escenarios['values'] = self.escenarios_unificados
        if self.combo_escenarios.current() == -1:
            self.combo_escenarios.current(0)
        
        if "Relación 3:1" in self.combo_escenarios.get():
            self.label_a.grid()
            self.entrada_a.grid()
        else:
            self.label_a.grid_remove()
            self.entrada_a.grid_remove()

    def limpiar_entradas(self):
        """Limpia todas las entradas de parámetros."""
        for entry in [self.entrada_D, self.entrada_h, self.entrada_v, 
                     self.entrada_phi, self.entrada_T, self.entrada_sigma, 
                     self.entrada_dt, self.entrada_factor_vel]:
            entry.delete(0, tk.END)

    def cargar_escenario_seleccionado(self):
        """Carga el escenario seleccionado en el combobox."""
        seleccion_texto = self.combo_escenarios.get()
        if "Relación 3:1" in seleccion_texto:
            try:
                a = float(self.entrada_a.get())
                if a <= 0:
                    messagebox.showerror("Error", "El valor de 'a' debe ser positivo")
                    return
                self.cargar_escenario_relacion_3_1(a)
            except ValueError:
                messagebox.showerror("Error", "Ingrese un valor numérico válido para 'a'")
        else:
            try:
                numero = int(seleccion_texto.split(".")[0])
                self.cargar_escenario_estandar(numero, None)
            except:
                messagebox.showerror("Error", "No se pudo cargar el escenario")

    def cargar_escenario_estandar(self, numero, metodo):
        """Carga el escenario seleccionado usando valores UNIFICADOS y SEGUROS."""
        self.limpiar_entradas()
        escenarios_data = {
            1: {"D": "120", "h": "20", "v": "25", "phi": "45", "T": "2.0", "desc": "Estándar (Distancia Segura)"},
            2: {"D": "90", "h": "50", "v": "20", "phi": "30", "T": "1.0", "desc": "Tiro desde Altura"},
            3: {"D": "150", "h": "10", "v": "35", "phi": "50", "T": "2.5", "desc": "Larga Distancia"},
            4: {"D": "60", "h": "15", "v": "25", "phi": "60", "T": "0.5", "desc": "Intercepción Rápida"},
            5: {"D": "50", "h": "10", "v": "28", "phi": "70", "T": "1.5", "desc": "Caída Vertical (Controlada)"},
        }
        if numero not in escenarios_data: numero = 1
        data = escenarios_data[numero]
        
        self.entrada_D.insert(0, data["D"])
        self.entrada_h.insert(0, data["h"])
        self.entrada_v.insert(0, data["v"])
        self.entrada_phi.insert(0, data["phi"])
        self.entrada_T.insert(0, data["T"])
        self.entrada_sigma.insert(0, "0.2")
        self.entrada_dt.insert(0, "0.05")
        self.entrada_factor_vel.insert(0, "2.0")
        
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, f"✅ {data['desc']} cargado.\n")
        self.texto_resultados.insert(tk.END, f"🔄 Valores unificados para ambos métodos.\n")
        self.texto_resultados.insert(tk.END, f"📊 Parámetros: D={data['D']}, h={data['h']}, v={data['v']}, φ={data['phi']}°, T={data['T']}\n")

    def cargar_escenario_relacion_3_1(self, a):
        """Genera parámetros que garantizan colisión en x≈3a, y≈a."""
        D, h = 3 * a + 12, a + 10
        v = np.sqrt(2 * self.g * a) * 1.6 
        phi, T = 48, np.sqrt(2 * a / self.g) * 0.35
        D, h, v, T = max(D, 18), max(h, 8), max(v, 15), max(T, 0.25)
        
        self.limpiar_entradas()
        self.entrada_D.insert(0, f"{D:.1f}")
        self.entrada_h.insert(0, f"{h:.1f}")
        self.entrada_v.insert(0, f"{v:.1f}")
        self.entrada_phi.insert(0, f"{phi:.1f}")
        self.entrada_T.insert(0, f"{T:.1f}")
        self.entrada_sigma.insert(0, "0.3")
        self.entrada_dt.insert(0, "0.05")
        self.entrada_factor_vel.insert(0, "2.0")
        
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, f"✅ Relación 3:1 generada con a={a}m\n")
        self.texto_resultados.insert(tk.END, f"📌 Objetivo: Colisión en x≈{3*a:.1f}m, y≈{a:.1f}m\n")

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
            
            if D <= 0: raise ValueError("D debe ser > 0")
            if h < 0: raise ValueError("h no puede ser negativo")
            if v <= 0: raise ValueError("v debe ser > 0")
            if not (0 < phi < 90): raise ValueError("φ debe estar entre 0 y 90 grados")
            if T < 0: raise ValueError("T no puede ser negativo")
            if sigma < 0: raise ValueError("σ no puede ser negativo")
            if dt <= 0: raise ValueError("Δt debe ser > 0")
            
            return D, h, v, np.radians(phi), T, self.g, sigma, dt, factor_vel
        except ValueError as e:
            messagebox.showerror("Error de entrada", f"Entrada inválida: {e}")
            return None

    def calcular_solucion_optima(self):
        """Calcula la solución óptima usando el método seleccionado."""
        entradas = self.validar_entradas()
        if entradas is None: return
        
        D, h, v, phi, T, g, sigma, dt, factor_vel = entradas
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, g)
        if t_max is None or t_max <= 0:
            messagebox.showerror("Error", "No se pudo calcular t_max válido.")
            return
        
        margen_inf = 0.1
        a, b = T + margen_inf, t_max * 0.95
        
        if b <= a:
            messagebox.showerror("Error", f"Intervalo inválido: T={T:.2f} es muy cercano a t_max={t_max:.2f}")
            return
        
        args = (D, h, v, phi, T, g)
        metodo_seleccionado = self.variable_metodo.get()
        tiempo_inicio = time.time()
        
        try:
            if metodo_seleccionado == "golden":
                nombre_metodo = "Sección Dorada"
                tc_optimo, iteraciones = calculos.minimizacion_seccion_dorada(calculos.funcion_velocidad_u, a, b, args)
            else:
                nombre_metodo = "Secante"
                tc_optimo, iteraciones = calculos.minimizacion_metodo_secante(calculos.funcion_velocidad_u, a, b, args)
        except Exception as e:
            messagebox.showerror("Error", f"Error en optimización: {e}")
            return
        
        tiempo_calculo = time.time() - tiempo_inicio
        
        if not np.isfinite(tc_optimo) or tc_optimo <= T:
            messagebox.showerror("Error", "No se encontró tc válido.")
            return
        
        u_optimo = calculos.funcion_velocidad_u(tc_optimo, D, h, v, phi, T, g)
        theta_optimo = calculos.funcion_angulo_theta(tc_optimo, D, h, v, phi, T, g)
        limite_u = 450 
        
        if not np.isfinite(u_optimo) or u_optimo > limite_u:
            messagebox.showerror("Error", f"Velocidad u excesiva ({u_optimo:.1f} m/s).")
            return
        
        x_col, y_col = calculos.posicion_proyectil_A(tc_optimo, D, h, v, phi, g)
        
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, f"=== SOLUCIÓN ÓPTIMA ===\n")
        self.texto_resultados.insert(tk.END, f"Método: {nombre_metodo}\n")
        self.texto_resultados.insert(tk.END, f"Tiempo de cálculo: {tiempo_calculo:.6f} s\n")
        self.texto_resultados.insert(tk.END, f"Iteraciones: {iteraciones}\n\n")
        self.texto_resultados.insert(tk.END, f"Tiempo de colisión (tc): {tc_optimo:.6f} s\n")
        self.texto_resultados.insert(tk.END, f"Velocidad inicial B (u): {u_optimo:.6f} m/s\n")
        self.texto_resultados.insert(tk.END, f"Ángulo de lanzamiento B (θ): {np.degrees(theta_optimo):.6f}°\n\n")
        self.texto_resultados.insert(tk.END, f"Posición de colisión teórica:\n")
        self.texto_resultados.insert(tk.END, f"  x = {x_col:.6f} m\n")
        self.texto_resultados.insert(tk.END, f"  y = {y_col:.6f} m\n")
        
        if "Relación 3:1" in self.combo_escenarios.get():
            try:
                a_val = float(self.entrada_a.get())
                ratio = x_col / y_col if y_col != 0 else float('inf')
                self.texto_resultados.insert(tk.END, f"\n📊 Relación x/y: {ratio:.3f} (Objetivo: ~3.0)\n")
            except: pass
        
        self.texto_resultados.insert(tk.END, f"\n📍 Altura de impacto: {y_col:.2f} m\n")
        
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
        
        simulacion.simular_y_animar_trayectorias(self.solucion_calculada)
    
    def comparar_metodos_numericos(self):
        """Compara ambos métodos numéricos."""
        entradas = self.validar_entradas()
        if entradas is None: return
        
        D, h, v, phi, T, g, sigma, dt, factor_vel = entradas
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, g)
        if t_max is None or t_max <= 0:
            messagebox.showerror("Error", "No se pudo calcular t_max.")
            return
        
        a, b = T + 0.1, t_max * 0.95
        if b <= a:
            messagebox.showerror("Error", "Intervalo inválido.")
            return
        
        args = (D, h, v, phi, T, g)
        metodos = [("Sección Dorada", calculos.minimizacion_seccion_dorada), ("Secante", calculos.minimizacion_metodo_secante)]
        resultados = []
        
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, "Calculando comparación...\n")
        self.ventana_principal.update()
        
        for nombre_metodo, funcion_metodo in metodos:
            tiempo_inicio = time.time()
            try:
                tc_optimo, iteraciones = funcion_metodo(calculos.funcion_velocidad_u, a, b, args)
                tiempo_calculo = time.time() - tiempo_inicio
                u_optimo = calculos.funcion_velocidad_u(tc_optimo, D, h, v, phi, T, g)
                theta_optimo = calculos.funcion_angulo_theta(tc_optimo, D, h, v, phi, T, g)
                x_col, y_col = calculos.posicion_proyectil_A(tc_optimo, D, h, v, phi, g)
                
                resultados.append({
                    'nombre': nombre_metodo, 'tc': tc_optimo, 'u': u_optimo, 'theta': theta_optimo,
                    'tiempo': tiempo_calculo, 'y_col': y_col, 'iteraciones': iteraciones,
                    'valido': np.isfinite(u_optimo) and u_optimo <= 450
                })
            except Exception as e:
                self.texto_resultados.insert(tk.END, f"Error en {nombre_metodo}: {e}\n")
        
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, "=== COMPARACIÓN DE MÉTODOS ===\n\n")
        
        for res in resultados:
            self.texto_resultados.insert(tk.END, f"{res['nombre']}:\n")
            self.texto_resultados.insert(tk.END, f"  Tiempo: {res['tiempo']:.8f} s\n")
            self.texto_resultados.insert(tk.END, f"  Iteraciones: {res['iteraciones']}\n")
            self.texto_resultados.insert(tk.END, f"  tc: {res['tc']:.8f} s\n")
            self.texto_resultados.insert(tk.END, f"  u: {res['u']:.8f} m/s\n")
            self.texto_resultados.insert(tk.END, f"  θ: {np.degrees(res['theta']):.8f}°\n")
            self.texto_resultados.insert(tk.END, f"  ✅ VÁLIDO\n\n" if res['valido'] else f"  ⚠️  DIVERGENTE\n\n")

    def limpiar_resultados(self):
        """Limpia el área de resultados."""
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, "Resultados limpiados.\n")