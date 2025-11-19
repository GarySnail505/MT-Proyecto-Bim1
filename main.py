import tkinter as tk
from interfaz import InterfazSimulacionProyectiles
import logging

def configurar_logging():
    """Configura el sistema de logging para diagnóstico."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('simulacion_proyectiles.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """
    Función principal mejorada con manejo de errores robusto.
    """
    try:
        configurar_logging()
        logging.info("Iniciando aplicación de simulación de proyectiles")
        
        ventana_principal = tk.Tk()
        app = InterfazSimulacionProyectiles(ventana_principal)
        
        # Configurar cierre graceful
        def on_closing():
            logging.info("Cerrando aplicación")
            ventana_principal.destroy()
            
        ventana_principal.protocol("WM_DELETE_WINDOW", on_closing)
        ventana_principal.mainloop()
        
    except Exception as e:
        logging.error(f"Error crítico al iniciar la aplicación: {e}")
        tk.messagebox.showerror("Error Fatal", 
                              f"No se pudo iniciar la aplicación:\n{e}")

if __name__ == "__main__":
    main()
