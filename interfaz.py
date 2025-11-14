import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import time

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
        self.ventana_principal.geometry("800x700")
        
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
        self.entrada_D = ttk.Entry(marco_parametros, width=10)
        self.entrada_D.insert(0, "50")
        self.entrada_D.grid(row=0, column=1, padx=5)
        
        ttk.Label(marco_parametros, text="h (m):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entrada_h = ttk.Entry(marco_parametros, width=10)
        self.entrada_h.insert(0, "10")
        self.entrada_h.grid(row=0, column=3, padx=5)
        
        ttk.Label(marco_parametros, text="v (m/s):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.entrada_v = ttk.Entry(marco_parametros, width=10)
        self.entrada_v.insert(0, "30")
        self.entrada_v.grid(row=1, column=1, padx=5)
        
        ttk.Label(marco_parametros, text="φ (grados):").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.entrada_phi = ttk.Entry(marco_parametros, width=10)
        self.entrada_phi.insert(0, "45")
        self.entrada_phi.grid(row=1, column=3, padx=5)
        
        ttk.Label(marco_parametros, text="T (s):").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.entrada_T = ttk.Entry(marco_parametros, width=10)
        self.entrada_T.insert(0, "2")
        self.entrada_T.grid(row=2, column=1, padx=5)
        
        # Parámetros de viento
        marco_viento = ttk.LabelFrame(marco_principal, text="Parámetros de Viento", padding="10")
        marco_viento.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(marco_viento, text="Intensidad de viento (σ):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.entrada_sigma = ttk.Entry(marco_viento, width=10)
        self.entrada_sigma.insert(0, "0.5")
        self.entrada_sigma.grid(row=0, column=1, padx=5)
        
        ttk.Label(marco_viento, text="Δt (s):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entrada_dt = ttk.Entry(marco_viento, width=10)
        self.entrada_dt.insert(0, "0.1")
        self.entrada_dt.grid(row=0, column=3, padx=5)
        
        # Métodos numéricos
        marco_metodos = ttk.LabelFrame(marco_principal, text="Métodos Numéricos", padding="10")
        marco_metodos.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        self.variable_metodo = tk.StringVar(value="golden")
        ttk.Radiobutton(marco_metodos, text="Sección Dorada", variable=self.variable_metodo, 
                       value="golden").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Radiobutton(marco_metodos, text="Newton (Secante)", variable=self.variable_metodo, 
                       value="secant").grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Botones
        marco_botones = ttk.Frame(marco_principal)
        marco_botones.grid(row=4, column=0, columnspan=4, pady=20)
        
        ttk.Button(marco_botones, text="Calcular Solución", 
                  command=self.calcular_solucion_optima).pack(side=tk.LEFT, padx=10)
        ttk.Button(marco_botones, text="Simular Trayectorias", 
                  command=self.iniciar_simulacion_trayectorias).pack(side=tk.LEFT, padx=10)
        ttk.Button(marco_botones, text="Comparar Métodos", 
                  command=self.comparar_metodos_numericos).pack(side=tk.LEFT, padx=10)
        
        # Resultados
        marco_resultados = ttk.LabelFrame(marco_principal, text="Resultados", padding="10")
        marco_resultados.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        self.texto_resultados = tk.Text(marco_resultados, height=8, width=70)
        self.texto_resultados.grid(row=0, column=0, columnspan=4)
        
        # Configurar expansión
        self.ventana_principal.rowconfigure(0, weight=1)
        self.ventana_principal.columnconfigure(0, weight=1)
        for i in range(6):
            marco_principal.rowconfigure(i, weight=1)
        for i in range(4):
            marco_principal.columnconfigure(i, weight=1)
    
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
            
            if D <= 0 or h < 0 or v <= 0 or phi <= 0 or phi >= 90 or T <= 0 or sigma < 0 or dt <= 0:
                raise ValueError("Todos los valores deben ser positivos y φ entre 0 y 90 grados")
            
            return D, h, v, np.radians(phi), T, sigma, dt
        except ValueError as e:
            messagebox.showerror("Error de entrada", f"Entrada inválida: {e}")
            return None
    
    def calcular_solucion_optima(self):
        """
        Calcula la solución óptima (tc, u, theta) usando el método numérico seleccionado.
        """
        entradas = self.validar_entradas()
        if entradas is None:
            return
        
        D, h, v, phi, T, sigma, dt = entradas
        
        # Encontrar t_max
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, self.g)
        
        # Argumentos para las funciones de optimización
        args = (D, h, v, phi, T, self.g)
        
        # Encontrar tc óptimo usando el método seleccionado
        metodo_seleccionado = self.variable_metodo.get()
        tiempo_inicio = time.time()
        
        if metodo_seleccionado == "golden":
            funcion_minimizacion = calculos.minimizacion_seccion_dorada
            nombre_metodo = "Sección Dorada"
            tc_optimo = funcion_minimizacion(calculos.funcion_velocidad_u, T + 1e-6, t_max, args)
        else:  # secant
            funcion_minimizacion = calculos.minimizacion_metodo_secante
            nombre_metodo = "Newton (Secante)"
            tc_optimo = funcion_minimizacion(calculos.funcion_velocidad_u, T + 1e-6, t_max, args)
        
        tiempo_calculo = time.time() - tiempo_inicio
        
        # Calcular u y theta
        u_optimo = calculos.funcion_velocidad_u(tc_optimo, *args)
        theta_optimo = calculos.funcion_angulo_theta(tc_optimo, *args)
        
        # Mostrar resultados
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, f"Método utilizado: {nombre_metodo}\n")
        self.texto_resultados.insert(tk.END, f"Tiempo de cálculo: {tiempo_calculo:.6f} segundos\n")
        self.texto_resultados.insert(tk.END, f"Tiempo de colisión óptimo (tc): {tc_optimo:.4f} s\n")
        self.texto_resultados.insert(tk.END, f"Velocidad inicial del proyectil B (u): {u_optimo:.4f} m/s\n")
        self.texto_resultados.insert(tk.END, f"Ángulo de lanzamiento del proyectil B (θ): {np.degrees(theta_optimo):.4f}°\n")
        self.texto_resultados.insert(tk.END, f"Posición de colisión:\n")
        
        x_col, y_col = calculos.posicion_proyectil_A(tc_optimo, D, h, v, phi, self.g)
        self.texto_resultados.insert(tk.END, f"  x = {x_col:.4f} m\n")
        self.texto_resultados.insert(tk.END, f"  y = {y_col:.4f} m\n")
        
        # Guardar resultados para la simulación
        self.solucion_calculada = {
            'D': D, 'h': h, 'v': v, 'phi': phi, 'T': T,
            'u': u_optimo, 'theta': theta_optimo, 'tc': tc_optimo,
            'sigma': sigma, 'dt': dt, 'g': self.g
        }
    
    def iniciar_simulacion_trayectorias(self):
        """
        Inicia la simulación y animación de las trayectorias.
        """
        if not self.solucion_calculada:
            messagebox.showwarning("Advertencia", "Primero debe calcular la solución óptima.")
            return
        
        try:
            # Llama a la función de simulación del módulo 'simulacion'
            simulacion.simular_y_animar_trayectorias(self.solucion_calculada)
        except Exception as e:
            messagebox.showerror("Error de Simulación", f"Ocurrió un error al animar: {e}")
    
    def comparar_metodos_numericos(self):
        """
        Compara el rendimiento y resultados de ambos métodos numéricos.
        """
        entradas = self.validar_entradas()
        if entradas is None:
            return
        
        D, h, v, phi, T, sigma, dt = entradas
        
        # Encontrar t_max
        t_max = calculos.encontrar_t_max_proyectil_A(h, v, phi, self.g)
        
        # Argumentos
        args = (D, h, v, phi, T, self.g)
        
        # Comparar ambos métodos
        metodos = [
            ("Sección Dorada", calculos.minimizacion_seccion_dorada),
            ("Newton (Secante)", calculos.minimizacion_metodo_secante)
        ]
        
        texto_comparacion = "COMPARACIÓN DE MÉTODOS NUMÉRICOS\n\n"
        
        for nombre_metodo, funcion_metodo in metodos:
            tiempo_inicio = time.time()
            tc_optimo = funcion_metodo(calculos.funcion_velocidad_u, T + 1e-6, t_max, args)
            tiempo_calculo = time.time() - tiempo_inicio
            
            u_optimo = calculos.funcion_velocidad_u(tc_optimo, *args)
            theta_optimo = calculos.funcion_angulo_theta(tc_optimo, *args)
            
            texto_comparacion += f"{nombre_metodo}:\n"
            texto_comparacion += f"  Tiempo de cálculo: {tiempo_calculo:.8f} s\n"
            texto_comparacion += f"  tc: {tc_optimo:.8f} s\n"
            texto_comparacion += f"  u: {u_optimo:.8f} m/s\n"
            texto_comparacion += f"  θ: {np.degrees(theta_optimo):.8f}°\n\n"
        
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, texto_comparacion)