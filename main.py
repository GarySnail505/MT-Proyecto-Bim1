import tkinter as tk
from interfaz import InterfazSimulacionProyectiles

def main():
    """Función principal de la aplicación."""
    try:
        ventana_principal = tk.Tk()
        app = InterfazSimulacionProyectiles(ventana_principal)
        ventana_principal.mainloop()
        
    except Exception as e:
        tk.messagebox.showerror("Error Fatal", f"No se pudo iniciar la aplicación:\n{e}")

if __name__ == "__main__":
    main()