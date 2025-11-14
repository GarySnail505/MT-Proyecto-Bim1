import tkinter as tk
from interfaz import InterfazSimulacionProyectiles

def main():
    """
    Función principal para inicializar y ejecutar la aplicación de simulación.
    """
    try:
        ventana_principal = tk.Tk()
        app = InterfazSimulacionProyectiles(ventana_principal)
        ventana_principal.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    main()